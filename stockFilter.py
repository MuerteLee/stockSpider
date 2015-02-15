import urllib
from urllib import request
import re, time,os 
class dataBase(object):
    def __init__(self, dataBasePath):
        super().__init__();
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
        cmdLineInsert = "insert into stockFilter values((select max(ID) from stockFilter)+1," + self.stockID + "," + self.name + "," + self.priceCur + "," + self.price4TwoWeek + "," + self.limitUpNum + ")"
        print("Update new data: %s" %cmdLineInsert)
        cu.execute(cmdLineInsert)
        conn.commit()

    #need to update the stock data for had chanaged stock data.
    def updateStockSpiderData(self, conn, stockID, name, priceCur, price4TwoWeek, limitUpNum):
        cur = conn.cursor()
        try:
            cur.execute("UPDATE stockSpider SET cnt_r0x_ratio=%s where symbol='%s'" %((cnt_r0x_ratio), symbol));
            cur.execute("UPDATE stockSpider SET trade=%s where symbol='%s'" %((trade), symbol));
            cur.execute("UPDATE stockSpider SET changeratio=%s where symbol='%s'" %((changeratio), symbol));
            cur.execute("UPDATE stockSpider SET turnover=%s where symbol='%s'" %((turnover), symbol));
            cur.execute("UPDATE stockSpider SET amount=%s where symbol='%s'" %((amount),symbol));
            cur.execute("UPDATE stockSpider SET netamount=%s where symbol='%s'" %((netamount), symbol));
            cur.execute("UPDATE stockSpider SET ratioamount=%swhere symbol='%s'" %((ratioamount), symbol));
            cur.execute("UPDATE stockSpider SET r0_net=%s where symbol='%s'" %((r0_net), symbol));
            cur.execute("UPDATE stockSpider SET r0x_ratioamount=%s where symbol='%s'" %((r0x_ratio), symbol));
#            cur.execute("UPDATE stockSpider SET cnt_r0x_ratio=%s trade=%s changeratio=%s turnover=%s amount=%s netamount=%s ratioamount=%s r0_net=%s r0x_ratioamount=%s where symbol='%s'" %(locale.atof(cnt_r0x_ratio), locale.atof(trade), locale.atof(changeratio), locale.atof(turnover), locale.atof(amount), locale.atof(netamount), locale.atof(ratioamount), locale.atof(r0_net), locale.atof(r0x_ratio), symbol));
            conn.commit()
        except sqlite3.Error as e:
            print("ERROR: updateSendKeyValue error, please check your param! \n")
            conn.rollback()
            return False;
class getPageCount(object):
    def __init__(self, URL):
        headers = ('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11');
        opener = urllib.request.build_opener();
        opener.addheaders = [headers];
        data = opener.open(URL).read();
        self.mainData = data.decode("UTF-8").split('=')[-1];
        list =eval((self.mainData).replace('pages','"pages"').replace(',date', ',"date"').replace("data:",'"data":'))
        self.pages = list["pages"]

    def getPagesNum(self,):
        return self.pages;

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

        for i in range(0, len(list["data"])):
            print(list["data"][i])

if __name__ == "__main__":
    url = "http://nufm.dfcfw.com/EM_Finance2014NumericApplication/JS.aspx/JS.aspx?type=ct&st=%28BalFlowMain%29&sr=-1&p=1&ps=50&js=var%20pglwSLMJ={pages:%28pc%29,date:%222014-10-22%22,data:%5B%28x%29%5D}&token=894050c76af8597a853f5b408b759f5d&cmd=C._AB&sty=DCFFITA&rt=47466059"
    pageNum = getPageCount(url).getPagesNum()
    print(pageNum)
#    parseUrl(url);
