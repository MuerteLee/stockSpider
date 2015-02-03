#/usr/bin python3
import urllib
from urllib import request
import re, time,os 
import sqlite3
import locale 

class sqliteOS3(object):
    def __init__(self, dataBasePath):
        super().__init__();
        if not os.path.isfile(dataBasePath):
           conn = sqlite3.connect(dataBasePath) 
           cu = conn.cursor()
           cu.execute("create table stockSpider(id integer primary key autoincrement, symbol varchar(128) UNIQUE, name varchar(128) UNIQUE, cnt_r0x_ratio varchar(128), trade varchar(128), changeratio varchar(128), turnover varchar(128), amount varchar(128), netamount varchar(128), ratioamount varchar(128), r0_net varchar(128), r0x_ratio varchar(128), updateKey integer)")
           conn.close()  

        self.dataBasePath = dataBasePath;

    def connectData(self,):
        return sqlite3.connect(self.dataBasePath); 

    def insertData(self, conn, symbol, name, cnt_r0x_ratio, trade, changeratio, turnover, amount, netamount, ratioamount, r0_net, r0x_ratio, updateKey):
        self.symbol = symbol;
        self.name = name;
        self.cnt_r0x_ratio = cnt_r0x_ratio;
        self.trade = trade;
        self.changeratio = changeratio;
        self.turnover = turnover;
        self.amount = amount;
        self.netamount = netamount;
        self.ratioamount = ratioamount;
        self.r0_net = r0_net;
        self.r0x_ratio = r0x_ratio;
        self.updateKey = updateKey;

        cu = conn.cursor(); 
        cmdLineInsert = "insert into stockSpider values((select max(ID) from stockSpider)+1," + self.symbol + "," + self.name + "," + self.cnt_r0x_ratio + "," + self.trade + "," + self.changeratio + "," + self.turnover + "," + self.amount + "," + self.netamount + "," + self.ratioamount + "," + self.r0_net + "," + self.r0x_ratio + "," + self.updateKey + ")"
        print("Update new data: %s" %cmdLineInsert)
        cu.execute(cmdLineInsert)
        conn.commit()
    #need to update the stock data for had chanaged stock data.
    def updateStockSpiderData(self, conn, symbol, cnt_r0x_ratio, trade, changeratio, turnover, amount,netamount, ratioamount, r0_net, r0x_ratio):
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

    def searchStockSpiderAmount(self, conn, symbol):
        cur = conn.cursor()
        try:
            cur.execute("select amount from stockSpider where symbol='%s'" %symbol)
            return list(cur.fetchall()[0])[0]
        except sqlite3.Error as e:
            print("ERROR: searchStockSpiderAmount error, please check your param! \n")
            return False;
             
    def searchStockSpiderSqlite3(self,conn, symbol):
        cur = conn.cursor()
        try:
            cur.execute("select * from stockSpider where symbol='%s'" %symbol)
            if len(cur.fetchall()) == 0:
                return True;
            else:
                return False;
        except sqlite3.Error as e:
            print("ERROR: searchStockSpiderSqlite3 error, please check your param! \n")
            return False;

    def deleteUpdateData(self, conn, symbol):
        cur = conn.cursor()
        try:
            cur.execute("delete from stockSpider where symbol='%s'" %symbol)
            conn.commit()
            return True;
        except sqlite3.Error as e:
            print("ERROR: deleteUpdatedata error, please check your param! \n")
            conn.rollback()
            return False;
    def closeSqlite3(self, conn):
        conn.close()

class parseUrl(sqliteOS3):
    def __init__(self, URL, dataBasePath):
        sqliteOS3.__init__(self, dataBasePath) 
        headers = ('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        opener = urllib.request.build_opener()
        opener.addheaders = [headers]
        data = opener.open(URL).read()
        self.mainData = data.decode("GB2312").strip('[').strip(']').replace('},','}},').split('},');
        self.dataBasePath = dataBasePath;
        self.updateKeyValue = 0

    def optionData(self,):
        sql = sqliteOS3(self.dataBasePath);
        conn = sql.connectData()
        for i in range(0, len(self.mainData)):
            list =eval((self.mainData[i]).replace('{','{"').replace(':', '":').replace(',',',"'))
            if sql.searchStockSpiderSqlite3(conn, list['symbol']):
                sql.insertData(conn, '"'+list['symbol']+'"', '"'+list['name']+'"', list['cnt_r0x_ratio'], list['trade'], list['changeratio'], list['turnover'], list['amount'], list['netamount'],list['ratioamount'], str(locale.atof(list['r0_net'])), str(locale.atof(list['r0x_ratio'])), str(self.updateKeyValue))
            if locale.atof(list['amount']) != locale.atof(sql.searchStockSpiderAmount(conn, list['symbol'])):
                if sql.deleteUpdateData(conn,list['symbol']):
                    self.updateKeyValue = self.updateKeyValue + 1
                    sql.insertData(conn, '"'+list['symbol']+'"', '"'+list['name']+'"', list['cnt_r0x_ratio'], list['trade'], list['changeratio'], list['turnover'], list['amount'], list['netamount'],list['ratioamount'], str(locale.atof(list['r0_net'])), str(locale.atof(list['r0x_ratio'])), str(self.updateKeyValue))

        sql.closeSqlite3(conn); 
if __name__ == "__main__":
#    parseUrl("http://data.eastmoney.com/bkzj/hy.html");
    dataBasePath = "/home/muerte/stockSpider.db"
    for pageNum in range(1, 132):
        url = "http://vip.stock.finance.sina.com.cn/quotes_service/api/json_v2.php/MoneyFlow.ssl_bkzj_lxjlr?page="+str(pageNum)+"&num=20&sort=cnt_r0x_ratio&asc=0&bankuai="
        print("Parese new URL%d: %s" %(pageNum,url))
        stock = parseUrl(url, dataBasePath);
        stock.optionData()

