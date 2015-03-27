import urllib
import datetime
from urllib import request
import sqlite3
import re, time,os,sys
def getLineNum():
    return sys._getframe().f_lineno
class dataBaseOperator(object):
    def __init__(self,conn, tableName):
        self.conn = conn;
        self.tableName =  tableName
        self.cu = self.conn.cursor()

    def searchStockTable(self,):
        cmdLine = "SELECT COUNT(*) FROM sqlite_master where type='table' and name=" + "'" + self.tableName + "'"
        try:
            self.cu.execute(cmdLine)
            lenS = int (str(self.cu.fetchall()[0]).replace('(','').replace(",)",""))
            if lenS == 1:
                return True;
            else:
                return False; 
        except sqlite3.Error as e:
            print("ERROR: searchStockTable error in the dataBaseOperator, please check your param %s! \n" %sys._getframe().f_lineno)
            return False;

    def insertMainTableData(self, name, priceCur, price41MH, price46MH, price452WH, price452WL):
        self.stockID = self.tableName;
        self.name = name;
        self.priceCur = priceCur;
        self.price41MH = price41MH;
        self.price46MH = price46MH;
        self.price452WH = price452WH;
        self.price452WL = price452WL;

        cmdLineInsert = "insert into stockMainTable values((select max(ID) from stockMainTable)+1," + '"' + self.stockID + '"' + "," + '"' + self.name+'"' + "," + '"'+ self.priceCur + '"' + "," + '"' + self.price41MH + '"' + "," + '"' + self.price46MH + '"' + "," + '"' + self.price452WH + '"' + "," + '"' + self.price452WL + '"' + ")"
        print("Update new data: %s" %cmdLineInsert)
        self.cu.execute(cmdLineInsert)
        self.conn.commit()



class dataBase(object):
    def __init__(self, dataBasePath):
        if not os.path.isfile(dataBasePath):
           conn = sqlite3.connect(dataBasePath) 
           cu = conn.cursor()
           cu.execute("create table stockMainTable(id integer primary key autoincrement, stockID varchar(128) UNIQUE, name varchar(128) UNIQUE, priceCur float, price41MH float, price46MH float, price452WH float, price452WL float)")
           conn.close()  
        self.dataBasePath = dataBasePath;

    def connectData(self,):
        return sqlite3.connect(self.dataBasePath); 


    def searchStockFilterSqlite3(self,conn, stockID):
        cur = conn.cursor()
        try:
            cur.execute("select * from stockMainTable where stockID='%s'" %stockID)
            if len(cur.fetchall()) == 0:
                return True;
            else:
                return False;
        except sqlite3.Error as e:
            print("ERROR: searchStockFilterSqlite3 error, please check your param %s! \n" %sys._getframe().f_lineno)
            return False;

class spiderStockPrice(object):
    def __init__(self,stockSymbol, Year, Quarter):
        self.stcokSymbol = "".join(str(i) for i in [int(s) for s in stockSymbol if s.isdigit()])
#        URL="http://money.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/000028.phtml?year=2015&jidu=1"
        URL="http://money.finance.sina.com.cn/corp/go.php/vMS_MarketHistory/stockid/"+str(self.stcokSymbol)+".phtml?year="+str(Year)+"&jidu="+str(Quarter)
        print(URL)
        headers = ('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11');
        opener = urllib.request.build_opener();
        opener.addheaders = [headers];
        data = opener.open(URL).read();
        self.mainData = data.decode("GBK").split('<a target=\'_blank\' href=')[1:];
    
    def getPriceTimeURL(self,):
        PTR=[]
        PTRT=[]
        # whole data for day
        #print(str(self.mainData[0]).replace('\t','').replace('\r\n','').split('</tr>')[0])
        # the latest data
        #str(self.mainData[0]).replace('\t','').replace('\r\n','').split('</tr>')[0].split('<td class="tdr">')[0].replace('</div></td>','').split('<td><div align="center">');

        for i in range(0, len(self.mainData)):
#            dataT = str(self.mainData[i]).replace('\t','').replace('\r\n','').split('</tr>')[0].split('<td class="tdr">')[0].replace('</div></td>','').split('<td><div align="center">');
            dataT = str(self.mainData[i]).replace('\t','').replace('\r\n','').split('</tr>')[0].replace('<td class="tdr">','').replace('</div></td>','').replace('<div align="center">',',').replace('<td>','').strip().split(',')
            price = dataT[3]
            dataTU = str(dataT[0]).strip('\'').strip('</a>').split('\'>')
            time = dataTU[1]
            URL = dataTU[0]
            TA = dataT[-1]
            V = dataT[-2]
            startPrice = dataT[-6]
            priceH = dataT[-5]
            priceL = dataT[-3]
            PTRT.append(time)
            PTRT.append(price)
            PTRT.append(URL)
            PTRT.append(V)
            PTRT.append(TA)
            PTRT.append(startPrice)
            PTRT.append(priceH)
            PTRT.append(priceL)
            PTR.append(PTRT)
            PTRT=[]
        return PTR

class dataBase4Stock(dataBase):
    def __init__(self, dataBasePath,stockSymbol):
        dataBase.__init__(self, dataBasePath);
        self.dataBasePath = dataBasePath;
        self.stockSymbol = stockSymbol
        sql = dataBase(self.dataBasePath) 
        conn = sql.connectData()
        self.conn = conn
        cu = conn.cursor()
        self.cu = cu
    
        if not dataBaseOperator(conn, stockSymbol).searchStockTable(): 
           cmdLine = "create table " + self.stockSymbol + "(id integer primary key autoincrement, time varchar(128) UNIQUE, price float, URL varchar(128), Volume varchar(128), transactionAmount varchar(128), startPrice varchar(128), priceH varchar(128), priceL varchar(128))"
           print(cmdLine)
           try:
                cu.execute(cmdLine)
#                time.sleep(1)
           except sqlite3.Error as e:
                print("Please check dataBase4Stock %s! \n" %sys._getframe().f_lineno)
#           conn.close()  

    def searchStock(self, time):
        l1 = []
        cmdLine = "select time from "+self.stockSymbol+" where time='"+time+"'"
#        print(cmdLine)
        try:
            self.cu.execute(cmdLine)
            l1 = self.cu.fetchall()
            if len(l1) > 0:
                return True;
            else:
                return False;
        except sqlite3.Error as e:
            print("ERROR: searchStock error, please check your param %s! \n" %sys._getframe().f_lineno)
            return False;
        self.conn.close()  

    def insert4Stock(self, date, price, URL, v, ta,startPrice, priceH, priceL):
        self.date = date;
        self.price = price;
        self.url = URL;
        self.Volume = v;
        self.transactionAmount = ta
        self.startp = startPrice
        self.ph = priceH
        self.pl = priceL
        
        cmdLineInsert = "insert into " + self.stockSymbol +" values((select max(ID) from " + self.stockSymbol + ")+1," + '"' + self.date + '"' + "," + '"' + self.price + '"' + "," + '"' + self.url + '"' + "," + '"'+self.Volume+'"'+ "," + '"' + self.transactionAmount + '"'+ "," + '"' + self.startp + '"'+ "," + '"' + self.ph + '"'+ "," + '"' + self.pl + '"'+")"
        print("Insert stock data: %s" %cmdLineInsert)

        if not self.searchStock(date):
            try:
#                time.sleep(1)
                self.cu.execute(cmdLineInsert)
                self.conn.commit()
            except:
                print("Please check insert4Stock %s! \n" %sys._getframe().f_lineno)

class option(dataBase):
    def __init__(self, data, dataBasePath):
        dataBase.__init__(self, dataBasePath);
        self.dataBasePath = dataBasePath;
        self.data= data;

    def insertStockData(self,):
        sql = dataBase(self.dataBasePath) 
        conn = sql.connectData()
        if sql.searchStockFilterSqlite3(conn, self.data[0]):
            if self.data[2] == '-':
                self.data[2] = '0.0'
#            sql.insertMainTableData(conn, str(self.data[0]), self.data[1], self.data[2], str(self.data[4]), str(self.data[5]), str(self.data[6]), str(self.data[7]));
            dataBaseOperator(conn, str(self.data[0])).insertMainTableData(self.data[1], self.data[2], "0", "0", "0", "0");

class parseUrl(object):
    def __init__(self, URL):
        headers = ('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11');
        opener = urllib.request.build_opener();
        opener.addheaders = [headers];
        data = opener.open(URL).read();
        self.mainData = data.decode("UTF-8").split('=')[-1];
        list =eval((self.mainData).replace('pages','"pages"').replace(',date', ',"date"').replace("data:",'"data":'))
        self.pages = list["pages"]
        self.data = list["data"]

    def getPagesNum(self,):
        return self.pages;

    def getData(self,):
        return self.data;

class others(object):
    def __init__(self,):
        pass

    def returnWeekDay(self, timeD, day):
        self.day = day
        self.timeD = timeD
        loop = True
        while(loop):
            timeD1 =  datetime.datetime.strptime(self.timeD,'%Y-%m-%d') + datetime.timedelta(days=self.day)
            timeD1T = str(timeD1).split('-')
            timeD1T[2] = timeD1T[2][:-8]
            w = int(datetime.datetime(int(timeD1T[0]),int(timeD1T[1]),int(timeD1T[2])).strftime("%w"));
            if w >= 1 and w <= 5:
                loop = False
            else:
                self.day = self.day + 1

        return str(timeD1).split(' ')[0]

    def getQuarter(self, time):
        if time >=2 and time <=4:
            Quarter = 1
        elif time >=5 and time <=7:
            Quarter = 2
        elif time >=8 and time <=10:
            Quarter = 3
        elif time ==1 or time > 10:
            Quarter = 4
        return Quarter;

    def cmp(self, s1, s2):
        if str(s1).find('-') != -1:
            s1=str(s1).split('-')
        if str(s2).find('-') != -1:
            s2=str(s2).split('-')
#        print("wo cao %s %s" %(s1,s2))
#        print(s1[0],s1[1],s1[2],s2[0],s2[1],s2[2])
        if int(s1[0]) == int(s2[0]) and int(s1[1]) == int(s2[1]) and int(s1[2]) == int(s2[2]): 
            return True
        return False

    def timeMonthDate(self, s1, month):
        if str(s1).find('-') != -1:
            sT=str(s1).split('-')
        m = int(sT[1]) + 12 - int(month) + 1
        if int(m) > 12:
            mT = m - 12
            YT = int(sT[0])
        else:
            mT = m
            YT = int(sT[0]) - 1

        sT[0] = YT
        sT[1] = mT
        sT = (''.join(str(i)+'-'for i in sT)[:-1])
        return sT 

    def timeDf(self, s1, s2):
        if str(s1).find('-') == -1 or str(s2).find('-') == -1:
            return False
        else:
            s1 = int(str(s1).replace('-',''))
            s2 = int(str(s2).replace('-',''))

        if s1 >= s2:
            return True
        return False

    def timeCur(self,):
        timeDY = datetime.date.today()-datetime.timedelta(days=1)
        timeN = int(time.strftime('%H:%M:%S',time.localtime(time.time())).split(':')[0])
        if timeN >= 16:
            timeC = time.strftime('%Y-%m-%d',time.localtime(time.time()))
        else:
            timeC = timeDY
        timeW = datetime.date.today().weekday()
        if int(timeW) == 5:
            timeC = datetime.date.today()-datetime.timedelta(days=1)
        elif int(timeW) == 6:
            timeC = datetime.date.today()-datetime.timedelta(days=2)
        return timeC;

    def insertStockTable(self,dataBasePath, stockSymbol,timeDN):
        timeD = time.strftime('%Y-%m-%d',time.localtime(time.time())).split('-')
        timeTT = int(timeD[1])
        oth = other(dataBasePath)
        oths = others()
        timeC = oths.timeCur() 
        Quarter = oths.getQuarter(timeTT);
        QuarterT = Quarter
        startYear = int(timeD[0]) - 1
        stopYear = int(timeD[0]) + 1

        maxT = False

        if timeDN: 
            timeDN = timeDN.split('-')
            if oths.cmp(timeC, timeDN):
                return

            QuarterT = oths.getQuarter(int(timeDN[1]))
            startYear = int(str(timeDN[0]).replace("'",''));
            maxT = True

        for y in range(startYear, stopYear):
            if y == stopYear - 1:
               if not maxT:
                    QuarterStart = 1;
                    QuarterStop = Quarter + 1
               else:
                    QuarterStart = QuarterT;
                    QuarterStop = Quarter + 1
            elif y < stopYear - 1:
               if not maxT:
                    QuarterStart = Quarter;
                    QuarterStop = 5 
               else:
                    QuarterStart = QuarterT;
                    QuarterStop = 5 
    #        print(startYear, stopYear, QuarterStart, QuarterStop)

            for m in range(QuarterStart, QuarterStop):
                kAcount = spiderStockPrice(stockSymbol,y,m).getPriceTimeURL()

                for k in range(0,len(kAcount)):
                    if timeDN:
                        if oths.cmp(kAcount[k][0],timeDN):
                            break;

                    if kAcount[k][1]:
                        dataBase4Stock(dataBasePath, stockSymbol).insert4Stock(kAcount[k][0],kAcount[k][1],kAcount[k][2],kAcount[k][3],kAcount[k][4])

class other(object):
    def __init__(self,dataBasePath):
        self.dataBasePath = dataBasePath
        sql = dataBase(dataBasePath) 
        conn = sql.connectData()
        self.conn = conn
        cu = conn.cursor()
        self.cu = cu

    def searchMaxTimeStock(self,stockSymbol):
        l1 = []
        cmdLine = "select max(time) from "+stockSymbol
        try:
            self.cu.execute(cmdLine)
#            l1 = self.cu.fetchall()
            l1 = (str(self.cu.fetchall()[0]).replace('(','').replace(",)","").replace("'",''))
            if len(l1) > 0:
                return l1;
            else:
                return False;
        except sqlite3.Error as e:
            print("ERROR: searchMaxTimeStock error, please check your param %s! \n" %sys._getframe().f_lineno)
            return False;
        self.conn.close()  

    def update(self, stockSymbol, updateKey,keyValue, time, timeValue):
        cmdLine = "UPDATE " + stockSymbol + " SET " + updateKey +"='"+ keyValue + "' where " + time + "='" + timeValue + "'"
        print(cmdLine)
        try:
            self.cu.execute(cmdLine)
            self.conn.commit()
        except sqlite3.Error as e:
            print("ERROR: update error, please check your param %s! \n" %sys._getframe().f_lineno)
            self.conn.rollback()
            return False;

    def searchStock(self,stockSymbol, name, time,timeValue):
        l1=[]
        try:
            cmdLine = "select " + name + " from " + stockSymbol + " where "+time + "='"+ timeValue +"'"
            self.cu.execute(cmdLine)
            print(cmdLine)
            l1 = (str(self.cu.fetchall()).replace('(','').replace(",)","").replace("'",''))
#            print(l1)
            if len(l1) >= 0:
                if l1[1:-1] == "None":
                    return False
                return True;
            else:
                return False;
        except sqlite3.Error as e:
#            print("ERROR: searchStock error, please check your param %s! \n" %sys._getframe().f_lineno)
            return False;
    def searchStockStockIDByPrice(self,):
        l1=[]
        try:
            cmdLine = "select stockID from stockMainTable where priceCur=0.0"
            self.cu.execute(cmdLine)
            print(cmdLine)
            l1 = (str(self.cu.fetchall()))#.replace('(','').replace(",)","").replace("'",''))
            print(l1)
            if len(l1) >= 0:
                return l1;
            else:
                return False;
        except sqlite3.Error as e:
            print("ERROR: searchStockStockIDByPrice error, please check your param %s! \n" %sys._getframe().f_lineno)
            return False;

    def insertColumn(self,stockSymbol,columnName):
        cmdLine = "alter table "+stockSymbol+" add " + columnName + " varchar"
        print(cmdLine)
        try:
            self.cu.execute(cmdLine)
            return True
        except sqlite3.Error as e:
            print("ERROR: insertColumn error, please check your param %s! \n" %sys._getframe().f_lineno)
            return False;

    def searchStockColumnIndex(self,stockSymbol,columnName):
        try:
            self.cu.execute("select %s from %s" %(columnName,stockSymbol))
            l1 = self.cu.fetchall()
            if len(l1) >= 0:
                return True;
            else:
                return False;
        except sqlite3.Error as e:
#            print("ERROR: searchStockColumnIndex error, please check your param %s! \n" %sys._getframe().f_lineno)
            return False;


    def searchStockMaxID(self,stockSymbol):
        try:
            self.cu.execute("select max(ID) from %s" %stockSymbol)
            l1 = (str(self.cu.fetchall()[0]).replace('(','').replace(",)","").replace("'",''))
            if int(l1) >= 0:
                return int(l1);
            else:
                return False;
        except sqlite3.Error as e:
            print("ERROR: searchStockMaxID error, please check your param %s! \n" %sys._getframe().f_lineno)
            return False;

    def searchSymbolByID(self,ID):
        try:
            self.cu.execute("select stockID from stockMainTable where ID=%d" %ID)
            l1 = (str(self.cu.fetchall()[0]).replace('(','').replace(",)","").replace("'",''))
            if len(l1) >= 0:
                return l1;
            else:
                return False;
        except sqlite3.Error as e:
            print("ERROR:  searchSymbolByID error, please check your param %s! \n" %sys._getframe().f_lineno)
            return False;

    def searchSymbolPriceTime(self,stockSymbol, id):
        try:
            self.cu.execute("select price,time from %s where id='%s'" %(stockSymbol,id))
            l1 = (str(self.cu.fetchall()[0]).replace('(','').replace(",)","").replace("'",'').replace(')','').strip().split(','))
#            print(l1)
            if len(l1) >= 0:
                return l1;
        except sqlite3.Error as e:
            print("ERROR: searchSymbolPriceTime error, please check your param %s! \n" %sys._getframe().f_lineno)

    def searchHalfYearMaxValue(self,stockSymbol):
        timeN = int(time.strftime('%H:%M:%S',time.localtime(time.time())).split(':')[0])
        oths = others()
        timeC = oths.timeCur();

        maxTime = self.searchMaxTimeStock(stockSymbol)
        maxID = self.searchStockMaxID(stockSymbol);
        maxPrice = float(self.searchSymbolPriceTime(stockSymbol, 1)[0])
        pt=[]
        try:
#            print(timeC,maxTime)
#            print(stockSymbol)
            if not oths.cmp(timeC, maxTime):
                oths.insertStockTable(self.dataBasePath, stockSymbol,maxTime)

            if oths.timeDf(timeC, maxTime):
                for id in range(2,maxID+1):
                    pt = self.searchSymbolPriceTime(stockSymbol, id)
                    if(pt[1],oths.timeMonthDate(timeC, 6)):
                        if maxPrice < float(pt[0]):
                            maxPrice = float(pt[0])
            return maxPrice
        except sqlite3.Error as e:
            print("ERROR: searchHalfYearMaxValue error, please check your param %s! \n" %sys._getframe().f_lineno)
            return False;
    
def insertMainTable(dataBasePath):
    url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx/JS.aspx?type=ct&st=%28BalFlowMain%29&sr=-1&p=1&ps=50&js=var%20pglwSLMJ={pages:%28pc%29,date:%222014-10-22%22,data:%5B%28x%29%5D}&token=894050c76af8597a853f5b408b759f5d&cmd=C._AB&sty=DCFFITA&rt=47466059"

    urlS = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx/JS.aspx?type=ct&st=%28BalFlowMain%29&sr=-1&p="
    urlE = "&ps=50&js=var%20pglwSLMJ={pages:%28pc%29,date:%222014-10-22%22,data:%5B%28x%29%5D}&token=894050c76af8597a853f5b408b759f5d&cmd=C._AB&sty=DCFFITA&rt=47466059"

    for i in range (1, parseUrl(url).getPagesNum()+1):
        urlStr = urlS + str(i) + urlE
        print(urlStr)
        if i / 20 == 0:
            time.sleep(5)
        parseData = parseUrl(urlStr).getData()
#        time.sleep(1)
        for i in range(0, len(parseData)):
            parseDataTmp = parseData[i].split(',')[:5];
#            print(parseDataTmp)
            if int(parseDataTmp[0]) == 1:
                parseDataTmp[1] = "sh"+parseDataTmp[1]
            elif int(parseDataTmp[0]) == 2:
                parseDataTmp[1] = "sz"+parseDataTmp[1]
 
            del parseDataTmp[0]

            option(parseDataTmp,dataBasePath).insertStockData();
 
def insertAllStockTable(dataBasePath):
    timeD = time.strftime('%Y-%m-%d',time.localtime(time.time())).split('-')

    timeTT = int(timeD[1])
    oth = other(dataBasePath)
    oths = others()
    timeC = oths.timeCur() 
    Quarter = oths.getQuarter(timeTT);
    QuarterT = Quarter
    startYear = int(timeD[0]) - 1
    stopYear = int(timeD[0]) + 1

    maxT = False

# update table key value


#    oth.searchStockStockIDByPrice()
#    oooo
    skipSymbol=['sz300435','sz002749']
    maxID = oth.searchStockMaxID('stockMainTable');
    
    for i in range(1, maxID+1):
        stockSymbol = oth.searchSymbolByID(int(i));
        timeDN = oth.searchMaxTimeStock(stockSymbol)

#        if not oth.searchStockColumnIndex(stockSymbol,'transactionAmount'):
#            oth.insertColumn(stockSymbol,'transactionAmount')

#       if not oth.searchStockColumnIndex(stockSymbol,'Volume'):
#            oth.insertColumn(stockSymbol,'Volume')

#        oths.insertStockTable(dataBasePath, stockSymbol)
    
#        oth.searchHalfYearMaxValue('sz300435')
#        if str(stockSymbol) != 'sz300435':
#            oth.searchHalfYearMaxValue(stockSymbol)

        if timeDN: 
#            print("max Time is %s, the latest time is %s" %(timeDN,timeC))
            timeDN = timeDN.split('-')
            if oths.cmp(timeC, timeDN):
#                print('the date is latest!\n')
                continue;

            QuarterT = oths.getQuarter(int(timeDN[1]))
            startYear = int(str(timeDN[0]).replace("'",''));
            maxT = True

        for y in range(startYear, stopYear):
            if y == stopYear - 1:
               if not maxT:
                    QuarterStart = 1;
                    QuarterStop = Quarter + 1
               else:
                    QuarterStart = QuarterT;
                    QuarterStop = Quarter + 1
            elif y < stopYear - 1:
               if not maxT:
                    QuarterStart = Quarter;
                    QuarterStop = 5 
               else:
                    QuarterStart = QuarterT;
                    QuarterStop = 5 
#            print(startYear, stopYear, QuarterStart, QuarterStop)

            for m in range(QuarterStart, QuarterStop):
                kAcount = spiderStockPrice(stockSymbol,y,m).getPriceTimeURL()

                for k in range(0,len(kAcount)):
                    if timeDN:
                        if oths.cmp(kAcount[k][0],timeDN):
                            break;

                    if kAcount[k][1]:
                        dataBase4Stock(dataBasePath, stockSymbol).insert4Stock(kAcount[k][0],kAcount[k][1],kAcount[k][2],kAcount[k][3],kAcount[k][4],kAcount[k][5],kAcount[k][6],kAcount[k][7])

                    if not oth.searchStock(stockSymbol,'Volume','time', kAcount[k][0]):
                        oth.update(stockSymbol,'Volume',kAcount[k][3],'time', kAcount[k][0])

                    if not oth.searchStock(stockSymbol,'transactionAmount','time', kAcount[k][0]):
                        oth.update(stockSymbol,'transactionAmount',kAcount[k][4],'time', kAcount[k][0])


def returnThreeDayDate(timeD,stockSymbol):
    timeDT=timeD
    timeD=str(timeD).split('-')
    timeTT = int(timeD[1])
    oths = others()
    Quarter = oths.getQuarter(timeTT);

    kAcount = spiderStockPrice(stockSymbol,int(timeD[0]),Quarter).getPriceTimeURL()
    timeD1 = (oths.returnWeekDay(timeDT,1))
    timeD2 = (oths.returnWeekDay(timeD1,1))

    for k in range(0,len(kAcount)):
        if oths.cmp(kAcount[k][0],timeD):
            print("Time:%s, stopPrice:%s, transactionAmount:%s" %(kAcount[k][0],kAcount[k][1],kAcount[k][4]))

        if oths.cmp(kAcount[k][0],timeD1):
            print("Time:%s, startPrice:%s, priceHigh:%s, priceLow:%s" %(kAcount[k][0],kAcount[k][5],kAcount[k][6],kAcount[k][7]))

        if oths.cmp(kAcount[k][0],timeD2):
            print("Time:%s, stopPrice:%s, priceHigh:%s, priceLow:%s" %(kAcount[k][0],kAcount[k][1],kAcount[k][6],kAcount[k][7]))
    

if __name__ == "__main__":
    dataBasePath = "./.stockMain.db"
#    insertMainTable(dataBasePath)
#    insertAllStockTable(dataBasePath)
    returnThreeDayDate('2015-03-23','sz300383');
