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
            dataT = str(self.mainData[i]).replace('\t','').replace('\r\n','').split('</tr>')[0].split('<td class="tdr">')[0].replace('</div></td>','').split('<td><div align="center">');
            price = dataT[-1]
            dataTU = str(dataT[0]).strip('\'').strip('</a>').split('\'>')
            time = dataTU[1]
            URL = dataTU[0]
            PTRT.append(time)
            PTRT.append(price)
            PTRT.append(URL)
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
           cmdLine = "create table " + self.stockSymbol + "(id integer primary key autoincrement, time varchar(128) UNIQUE, price float, URL varchar(128) UNIQUE)"
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
            print("ERROR: searchStock error -------->>>>>>>, please check your param %s! \n" %sys._getframe().f_lineno)
            return False;
        self.conn.close()  

    def insert4Stock(self, date, price, URL):
        self.date = date;
        self.price = price;
        self.url = URL;
        
        cmdLineInsert = "insert into " + self.stockSymbol +" values((select max(ID) from " + self.stockSymbol + ")+1," + '"' + self.date + '"' + "," + '"' + self.price + '"' + "," + '"' + self.url + '"' + ")"
        print("Insert stock data: %s" %cmdLineInsert)

        if not self.searchStock(date):
            try:
#                time.sleep(1)
                self.cu.execute(cmdLineInsert)
                self.conn.commit()
            except:
                print("Please check insert4Stock!\n")

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

class other(object):
    def __init__(self,dataBasePath,):
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

    def searchStockMainTable(self,):
        try:
            self.cu.execute("select max(ID) from stockMainTable")
            l1 = (str(self.cu.fetchall()[0]).replace('(','').replace(",)","").replace("'",''))
            if int(l1) >= 0:
                return int(l1);
            else:
                return False;
        except sqlite3.Error as e:
            print("ERROR: searchStockMainTable error, please check your param %s! \n" %sys._getframe().f_lineno)
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
            print("ERROR: searchStockMainTable error, please check your param %s! \n" %sys._getframe().f_lineno)
            return False;

    def searchSymbolPrice(self,stockSymbol, id):
        try:
            self.cu.execute("select price from %s where id='%s'" %(stockSymbol,id))
            l1 = (str(self.cu.fetchall()[0]).replace('(','').replace(",)","").replace("'",''))
            if len(l1) >= 0:
                return l1;
            else:
                return False;
        except sqlite3.Error as e:
            print("ERROR: searchSymbolPrice error, please check your param %s! \n" %sys._getframe().f_lineno)
            return False;
# need to write something
    def searchHalfYearMaxValue(self,stockSymbol):
        try:
            self.cu.execute("select max(ID) from %s" %stockSymbol)
            maxID = (str(self.cu.fetchall()[0]).replace('(','').replace(",)","").replace("'",''))
            maxPrice = int(self.searchSymbolPrice(stockSymbol, 1))
            for id in range(2,maxID+1):
                if maxPrice < int(self.searchSymbolPrice(stockSymbol, id))
                    maxPrice = int(self.searchSymbolPrice(stockSymbol, id))
                

            if len(l1) >= 0:
                return l1;
            else:
                return False;
        except sqlite3.Error as e:
            print("ERROR: searchHalfYearMaxValue error, please check your param %s! \n" %sys._getframe().f_lineno)
            return False;
        pass
        
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

    maxID = oth.searchStockMainTable();
    for i in range(1, maxID+1):
        stockSymbol = oth.searchSymbolByID(int(i));
        timeDN = oth.searchMaxTimeStock(stockSymbol)

        if timeDN: 
            print("max Time is %s, the latest time is %s" %(timeDN,timeC))
            timeDN = timeDN.split('-')
#            print(oth.cmp(timeC, timeDN))
#            print(timeC, timeDN)
            if oths.cmp(timeC, timeDN):
                print('the date is latest!\n')
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
#                time.sleep(5)

                for k in range(0,len(kAcount)):
                    if timeDN:
                        if oths.cmp(kAcount[k][0],timeDN):
                            break;

                    if kAcount[k][1]:
                        dataBase4Stock(dataBasePath, stockSymbol).insert4Stock(kAcount[k][0],kAcount[k][1],kAcount[k][2])

if __name__ == "__main__":
    dataBasePath = "./.stockMain.db"
    urlTmp = "http://app.finance.ifeng.com/data/stock/tab_cccb.php?code="#sh600050"
#    urlTT = "http://app.finance.ifeng.com/data/stock/tab_cccb.php?code=sh600528"
#    print(getPageCount(urlTT).getPricePercent())
#    print(pp)
    pp = []
#    insertMainTable(dataBasePath)
    insertAllStockTable(dataBasePath)
