"""
以下为对程序的说明：
1.在我的电脑上运行约需30分钟（即一天的新闻约需一分钟）
2.没有artibody/正文模块的链接未能扒出（来自新浪新闻之外的网页），数量极小
"""

dataFile=open("news20081001-20081031.txt","w",encoding="utf-8")
from urllib import request
mediaList=[]
hrefSet=set()#排除重复链接
errorHref="http://tech.sina.com.cn/mobile/n/2008-10-21/0027842330.shtml"#直接提取正文在我的电脑上会发生MemoryError，因此单独提出来在line63-71处理
from bs4 import BeautifulSoup

for i in range(1,32):#得出31个日期
    if i<10:
        date="0"+str(i)
    else:
        date=str(i)

    url=request.urlopen("http://news.sina.com.cn/hotnews/200810" +date+ ".shtml")
    url=BeautifulSoup(url.read().decode("gb18030"),"html.parser")
    charNum=0#计算字数
    imgList=[]#计算图片数量

    url=str(url.find_all("a")).split(",")
    hrefs=""

    for link in url:
        if "comment"not in link:
            hrefs+=link+"\n"

    hrefs=hrefs[hrefs.find(""" <a name="2"></a>"""):hrefs.rfind("""<a href="/guest.html" target="_blank">新闻中心意见反馈留言板""")]

    hrefList=hrefs.split("\n")
    hrefList=hrefList[2:]

    for href in hrefList:
        if "a name" in href:
            hrefList.remove(href)

    hrefList=hrefList[:20]+hrefList[41:61]+hrefList[82:102]+hrefList[123:143]+hrefList[164:184]+hrefList[205:225]+hrefList[246:266]#点击量排行中所有链接

    for href in hrefList:
        href=href[href.find("htt"):href.rfind("tml")+3]
        if href in hrefSet:
            continue

        news=request.urlopen(href)
        news=BeautifulSoup(news.read().decode("gb18030"),"html.parser")
        news=BeautifulSoup(str(news)[str(news).find("正文块"):str(news).rfind("正文内容")],"html.parser")
        if news.h1 is None:#排除“页面不存在”的链接
            continue

        #取出标题、时间和媒体
        title=news.h1.text
        time=news.find_all("span")[1].text
        media=news.find_all("span")[2].text
        if media=="\u3000新华网":
            media="新华网"
        if media!="":
            mediaList.append(media)
        #取出图片
        for pic in news.find_all("img"):
            if "alt" in str(pic) and "video" not in str(pic):#没有"alt"的为图标；有"alt"的图标含有"video"。以此筛选出新闻配图
                imgList.append(pic)
        #获取正文
        body=" "+str(news.find_all("p"))[str(news.find_all("p")).find(">") + 1:str(news.find_all("p")).rfind("<")]
        if href==errorHref:
            body = body[:body.find("[订购热线] 0755－83975848") + len("[订购热线] 0755－83975848")]
            for i in range(1, 50):
                body = body[:body.find("<")] + body[body.find(">") + 1:]
            for i in range(1, 50):
                body = body[:body.find("<")] + body[body.find(">") + 1:]
            for i in range(1, 50):
                body = body[:body.find("<")] + body[body.find(">") + 1:]
            for i in range(1, 10):
                body = body[:body.find("<")] + body[body.find(">") + 1:]
            for i in range(1, 20):
                body = body[:body.rfind("<")] + body[body.rfind(">") + 1:]
            body = body.replace("</p>, <p>　　<!-- [发现广告图片] <center>", "")

        if "相关新闻" in body:
            body=body[:body.find("相关新闻")]
        if "相关报道" in body:
            body=body[:body.find("相关报道")]
        if "相关阅读" in body:
            body=body[:body.find("相关阅读")]
        if "更多精彩内容" in body:
            body=body[:body.rfind("更多精彩内容")]

        if ".blkVideoLink" in body:
            body=body[:body.find(".blkVideoLink")]+body[body.rfind("}")+1:]

        if ".pb" in body:
            body=body[:body.find(".pb")]

        if "<" and ">" in body:
            while True:
                body=body[:body.find("<")] + body[body.find(">") + 1:]#去除html元素
                if body.find("<")==-1:
                    break

        body=body.replace(",", "\n")
        aList=["\n","\t"," ","  ","   ","   ","　　"]#不可算进字数的字符
        for j in aList:
            if j in body:
                char=body.replace(j,"")
        charNum+=len(char)

        print(title, time, media, body,sep="\n",end="\n",file=dataFile)
    print(date,charNum,len(imgList),sep=",")
    hrefSet.union(set(hrefList))#记录已经跑过的链接

mediaDict={}#统计媒体新闻数量
for media in mediaList:
    if media in mediaDict:
        continue
    mediaDict[media]=mediaList.count(media)
print(mediaDict)

