import urllib
from urllib import request
import sqlite3
import re, time,os 

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

    def insertMainTableData(self, conn, stockID, name, priceCur, price41MH, price46MH, price452WH, price452WL):
        self.stockID = stockID;
        self.name = name;
        self.priceCur = priceCur;
        self.price41MH = price41MH;
        self.price46MH = price46MH;
        self.price452WH = price452WH;
        self.price452WL = price452WL;

        cu = conn.cursor(); 
        cmdLineInsert = "insert into stockMainTable values((select max(ID) from stockMainTable)+1," + '"' + self.stockID + '"' + "," + '"' + self.name+'"' + "," + '"'+ self.priceCur + '"' + "," + '"' + self.price41MH + '"' + "," + '"' + self.price46MH + '"' + "," + '"' + self.price452WH + '"' + "," + '"' + self.price452WL + '"' + ")"
        print("Update new data: %s" %cmdLineInsert)
        cu.execute(cmdLineInsert)
        conn.commit()

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
            sql.insertMainTableData(conn, str(self.data[0]), self.data[1], self.data[2], "0", "0", "0", "0");

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
    dataBasePath = "./.stockMainTable.db"
    url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx/JS.aspx?type=ct&st=%28BalFlowMain%29&sr=-1&p=1&ps=50&js=var%20pglwSLMJ={pages:%28pc%29,date:%222014-10-22%22,data:%5B%28x%29%5D}&token=894050c76af8597a853f5b408b759f5d&cmd=C._AB&sty=DCFFITA&rt=47466059"
    urlS = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx/JS.aspx?type=ct&st=%28BalFlowMain%29&sr=-1&p="
    urlE = "&ps=50&js=var%20pglwSLMJ={pages:%28pc%29,date:%222014-10-22%22,data:%5B%28x%29%5D}&token=894050c76af8597a853f5b408b759f5d&cmd=C._AB&sty=DCFFITA&rt=47466059"
    urlTmp = "http://app.finance.ifeng.com/data/stock/tab_cccb.php?code="#sh600050"
#    urlTT = "http://app.finance.ifeng.com/data/stock/tab_cccb.php?code=sh600528"
#    print(getPageCount(urlTT).getPricePercent())
#    print(pp)
    pp = []

    for i in range (1, 2): # parseUrl(url).getPagesNum()+1):
#    for i in range (1, parseUrl(url).getPagesNum()+1):
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

            print(parseDataTmp)
            option(parseDataTmp,dataBasePath).insertStockData();
