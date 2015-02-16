import urllib
from urllib import request
import sqlite3
import re, time,os 

class dataBase(object):
    def __init__(self, dataBasePath):
        if not os.path.isfile(dataBasePath):
           conn = sqlite3.connect(dataBasePath) 
           cu = conn.cursor()
           cu.execute("create table stockFilter(id integer primary key autoincrement, stockID varchar(128) UNIQUE, name varchar(128) UNIQUE, priceCur varchar(128), price4TwoWeek varchar(128), limitUpNum integer)")
           conn.close()  
        self.dataBasePath = dataBasePath;

    def connectData(self,):
        return sqlite3.connect(self.dataBasePath); 

    def insertData(self, conn, stockID, name, priceCur, price4TwoWeek, limitUpNum):
        self.stockID = stockID;
        self.name = name;
        self.priceCur = priceCur;
        self.price4TwoWeek = price4TwoWeek;
        self.limitUpNum = limitUpNum;

        cu = conn.cursor(); 
        cmdLineInsert = "insert into stockFilter values((select max(ID) from stockFilter)+1," + '"' + self.stockID + '"' + "," + '"' + self.name+'"' + "," + '"'+ self.priceCur + '"' + "," + '"' + self.price4TwoWeek + '"' + "," + '"' + self.limitUpNum + '"'+ ")"
        print("Update new data: %s" %cmdLineInsert)
        cu.execute(cmdLineInsert)
        conn.commit()

    #need to update the stock data for had chanaged stock data.
    def updateStockFilterData(self, conn, stockID, priceCur, price4TwoWeek, limitUpNum):
        cur = conn.cursor()
        try:
            cur.execute("UPDATE stockFilter SET priceCur=%s where stockID='%s'" %(priceCur, stockID));
            cur.execute("UPDATE stockFilter SET price4TwoWeek=%s where stockID='%s'" %(price4TwoWeek, stockID));
            cur.execute("UPDATE stockFilter SET limitUpNum=%s where stockID='%s'" %(limitUpNum, stockID)); 
            conn.commit()
        except sqlite3.Error as e:
            print("ERROR: update stock filter data  error, please check your param! \n")
            conn.rollback()
            return False;

    def searchStockFilterSqlite3(self,conn, stockID):
        cur = conn.cursor()
        try:
            cur.execute("select * from stockFilter where stockID='%s'" %stockID)
            if len(cur.fetchall()) == 0:
                return True;
            else:
                return False;
        except sqlite3.Error as e:
            print("ERROR: searchStockFilterSqlite3 error, please check your param! \n")
            return False;

    def searchStockFilterResult(self,conn):
        cur = conn.cursor()
        try:
            cur.execute("select * from stockFilter where limitUpNum >= 2")
            if len(cur.fetchall()) == 0:
                return cur.fetchall();
            else:
                return False;
        except sqlite3.Error as e:
            print("ERROR: searchStockFilterResult error, please check your param! \n")
            return False;

class getPageCount(object):
    def __init__(self, URL):
        headers = ('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11');
        opener = urllib.request.build_opener();
        opener.addheaders = [headers];
        data = opener.open(URL).read();
        self.mainData = data.decode("UTF-8")
        findstr = re.compile(r'<td class="h\d+\sbr">.*</td>') 
        tmp = findstr.findall(self.mainData)
        fs = re.compile(r'>.*\d\.\d.*<')
        cn = 0;
        price = []
        percent = []
        for i in range(0, len(tmp)):
            tmpp = fs.findall(tmp[i])
            cn = cn + 1 
            if cn == 7:
                price.append(float(str(tmpp).replace('>','').replace('<','').replace('[','').replace(']','').replace("'",'')))
            elif cn == 8:
                percent.append(float(str(tmpp).replace('>','').replace('<','').replace('[','').replace(']','').replace("'",'').replace('%','')))
                cn = 0;
        percent = percent[10:]
        self.PricePercent = []
        maxPrice = max(price)
        self.PricePercent.append(maxPrice)
        percentN = 0
        for i in percent:
            if i >= 9.8:
                percentN = percentN + 1;
        self.PricePercent.append(percentN)

#        print(maxPrice)
#        print(percentN)

    def getPricePercent(self,):
        return self.PricePercent;

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

class option(dataBase):
    def __init__(self, data, dataBasePath):
        dataBase.__init__(self, dataBasePath);
        self.dataBasePath = dataBasePath;
        self.data= data;

    def insertStockData(self,):
        sql = dataBase(self.dataBasePath) 
        conn = sql.connectData()
        if sql.searchStockFilterSqlite3(conn, self.data[0]):
            sql.insertData(conn, str(self.data[0]), self.data[1],self.data[2], str(self.data[4]), str(self.data[5]));

    def returnFilter(self,):
        sql = dataBase(self.dataBasePath) 
        conn = sql.connectData()
        print(sql.searchStockFilterResult(conn));

if __name__ == "__main__":
    dataBasePath = "/tmp/stockFilter.db"
    url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx/JS.aspx?type=ct&st=%28BalFlowMain%29&sr=-1&p=1&ps=50&js=var%20pglwSLMJ={pages:%28pc%29,date:%222014-10-22%22,data:%5B%28x%29%5D}&token=894050c76af8597a853f5b408b759f5d&cmd=C._AB&sty=DCFFITA&rt=47466059"
    urlS = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx/JS.aspx?type=ct&st=%28BalFlowMain%29&sr=-1&p="
    urlE = "&ps=50&js=var%20pglwSLMJ={pages:%28pc%29,date:%222014-10-22%22,data:%5B%28x%29%5D}&token=894050c76af8597a853f5b408b759f5d&cmd=C._AB&sty=DCFFITA&rt=47466059"
    urlTmp = "http://app.finance.ifeng.com/data/stock/tab_cccb.php?code="#sh600050"
#    urlTT = "http://app.finance.ifeng.com/data/stock/tab_cccb.php?code=sh600528"
#    print(getPageCount(urlTT).getPricePercent())
#    print(pp)
    pp = []

    for i in range (1, 2): # parseUrl(url).getPagesNum()+1):
        urlStr = urlS + str(i) + urlE
        print(urlStr)
        parseData = parseUrl(urlStr).getData()
        for i in range(0, len(parseData)):
            parseDataTmp = parseData[i].split(',')[:5];
            if int(parseDataTmp[0]) == 1:
                parseDataTmp[1] = "sh"+parseDataTmp[1]
            elif int(parseDataTmp[0]) == 2:
                parseDataTmp[1] = "sz"+parseDataTmp[1]
 
            del parseDataTmp[0]
            urlT = urlTmp + parseDataTmp[0]
            pp = getPageCount(urlT).getPricePercent()
            parseDataTmp = parseDataTmp + pp;
            print(parseDataTmp) 
            option(parseDataTmp,dataBasePath).insertStockData();

    option(parseDataTmp,dataBasePath).searchStockFilterResult();
