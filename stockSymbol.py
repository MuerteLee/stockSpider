import urllib
import datetime
from urllib import request
import sqlite3
import re, time,os 

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
            print("ERROR: searchStockTable error in the dataBaseOperator, please check your param! \n")
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
            print("ERROR: searchStockFilterSqlite3 error, please check your param! \n")
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
           except sqlite3.Error as e:
                print("Please check dataBase4Stock!\n")
           conn.close()  

    def searchStock(self,time):
        lll = []
        cmdLine = "select time from "+stockSymbol+" where time='"+time+"'"
        print(cmdLine)
        try:
            self.cu.execute(cmdLine)
            if len(self.cu.fetchall()) != 0:
                ll = str(self.cu.fetchall()[0]).replace('(\'','').replace("',)","")
                lll.append("".join(str(i) for i in [int(s) for s in ll if s.isdigit()]))
            if len(lll) > 0:
                return True;
            else:
                return False;
        except sqlite3.Error as e:
            print("ERROR: searchStock error, please check your param! \n")
            return False;

    def insert4Stock(self, date, price, URL):
        self.date = date;
        self.price = price;
        self.url = URL;
        
        cmdLineInsert = "insert into " + self.stockSymbol +" values((select max(ID) from " + self.stockSymbol + ")+1," + '"' + self.date + '"' + "," + '"' + self.price + '"' + "," + '"' + self.url + '"' + ")"
        print("Insert stock data: %s" %cmdLineInsert)

        if not self.searchStock(date):
            try:
                time.sleep(1)
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

if __name__ == "__main__":
    dataBasePath = "./.stockMain.db"
    url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx/JS.aspx?type=ct&st=%28BalFlowMain%29&sr=-1&p=1&ps=50&js=var%20pglwSLMJ={pages:%28pc%29,date:%222014-10-22%22,data:%5B%28x%29%5D}&token=894050c76af8597a853f5b408b759f5d&cmd=C._AB&sty=DCFFITA&rt=47466059"
    urlS = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx/JS.aspx?type=ct&st=%28BalFlowMain%29&sr=-1&p="
    urlE = "&ps=50&js=var%20pglwSLMJ={pages:%28pc%29,date:%222014-10-22%22,data:%5B%28x%29%5D}&token=894050c76af8597a853f5b408b759f5d&cmd=C._AB&sty=DCFFITA&rt=47466059"
    urlTmp = "http://app.finance.ifeng.com/data/stock/tab_cccb.php?code="#sh600050"
#    urlTT = "http://app.finance.ifeng.com/data/stock/tab_cccb.php?code=sh600528"
#    print(getPageCount(urlTT).getPricePercent())
#    print(pp)
    pp = []
    timeD = time.strftime('%Y-%m-%d',time.localtime(time.time())).split('-')
    timeDY = datetime.date.today()-datetime.timedelta(days=1)

    if int(timeD[1]) >=2 and int(timeD[1]) <=4:
        Quarter = 1
    elif int(timeD[1]) >=5 and int(timeD[1]) <=7:
        Quarter = 2
    elif int(timeD[1]) >=8 and int(timeD[1]) <=10:
        Quarter = 3
    elif int(timeD[1]) ==1 or int(timeD[1]) > 10:
        Quarter = 4

#    for i in range (1, 2): # parseUrl(url).getPagesNum()+1):
    for i in range (1, parseUrl(url).getPagesNum()+1):
        urlStr = urlS + str(i) + urlE
        print(urlStr)
        if i / 20 == 0:
            time.sleep(5)
        parseData = parseUrl(urlStr).getData()
        time.sleep(1)
        for i in range(0, len(parseData)):
            parseDataTmp = parseData[i].split(',')[:5];
#            print(parseDataTmp)
            if int(parseDataTmp[0]) == 1:
                parseDataTmp[1] = "sh"+parseDataTmp[1]
            elif int(parseDataTmp[0]) == 2:
                parseDataTmp[1] = "sz"+parseDataTmp[1]
 
            del parseDataTmp[0]

            option(parseDataTmp,dataBasePath).insertStockData();

#            sql = dataBase(dataBasePath) 
#            conn = sql.connectData()

            stockSymbol = parseDataTmp[0]

            for y in range(int(timeD[0])-1, int(timeD[0]) + 1):
                if y == int(timeD[0]):
                   QuarterStart = 1;
                   QuarterStop = Quarter + 1
                elif y < int(timeD[0]):
                   QuarterStart = Quarter;
                   QuarterStop = 5 

                for m in range(QuarterStart, QuarterStop):
                    kAcount = spiderStockPrice(stockSymbol,y,m).getPriceTimeURL()
                    time.sleep(5)
                    for k in range(0,len(kAcount)):
                        if kAcount[k][1]:
                            dataBase4Stock(dataBasePath, stockSymbol).insert4Stock(kAcount[k][0],kAcount[k][1],kAcount[k][2])
