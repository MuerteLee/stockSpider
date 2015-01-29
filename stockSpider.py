#/usr/bin python3

class parseUrl():
    def __init__(self, URL):
        super.__init__() 
        headers = ('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
        opener = urllib.request.build_opener()
        opener.addheaders = [headers]
        data = opener.open(URL).read()
        self.mainData = data.decode("utf8").split('<div class="sec nav">')[-2].split('class="top"')[-1].split("</a></div></li>")
