#-------------------------------------------------------------------------------
# Name:     douban.py
# Purpose:  request book information from douban and store in mysql
#
# Author:   Ruihan Xu
# Created:  23/11/2019
# Modified: 27/11/2019
#-------------------------------------------------------------------------------

import requests
from bs4 import BeautifulSoup
# generate fake useragent. Internet connection required
from fake_useragent import UserAgent

import pymysql

import re
import os

class myRequests:
    # myRequests.__doc__
    "my requests"
    # myRequests class_suite
    index_url="https://book.douban.com/tag/?icn=index-nav"
    category_file="category.txt"
    href="https://book.douban.com/tag/"
    category_urls=[] # category urls
    mydb="gbookdb"
    conn=pymysql.connect(host='localhost',user='root',password='',charset='utf8')
    cnt=300

    def __init__(self):
        with self.conn.cursor() as cursor:
            cursor.execute("USE "+ self.mydb +";")
            cursor.execute("DELETE FROM author;")
            cursor.execute("DELETE FROM book_info;")
        self.conn.commit()

    # use fake useragent to get pages. avoid anti-crawler
    def getPage(self, url):
        ua=UserAgent()
        headers={ "User-Agent":  ua.random }
        return requests.get(url, headers=headers)

    def getCategory(self, index_url=index_url, category_file=category_file):
        web_data=self.getPage(index_url)
        soup=BeautifulSoup(web_data.text, "lxml")
        tags=soup.select("table.tagCol > tbody > tr > td > a")
        for tag in tags:
            # 将列表中的每一个标签信息提取出来
            # 观察一下豆瓣的网址，基本都是这部分加上标签信息，所以我们要组装网址，用于爬取标签详情页
            url=self.href+str(tag.get_text())
            self.category_urls.append(url)
        if category_file:
            with open(category_file,"w", encoding="utf-8") as fout:
                for links in self.category_urls:
                    fout.write(links+"\n")
        return self.category_urls

    # 处理函数
    def getChineseIntro(self, line_tags):
        ChineseIntro = []
        for tag in line_tags:
            ChineseIntro += tag.contents
        ChineseIntro = '\n'.join(ChineseIntro)
        return ChineseIntro

    def getAuthor(self, raw_author):
        parts=raw_author.split('\n')
        return ''.join(map(str.strip,parts))

    def getDetail(self, bookSoup):
        info=bookSoup.select('#info')
        infos=list(info[0].strings)

        ISBN=""
        Author=""
        Publisher=""
        PTime=""
        Score=""
        Price=""
        detailed=True

        Title=bookSoup.select("h1 span")[0].contents[0].strip()
        try:
            ISBN=infos[infos.index('ISBN:') + 1].strip()
        except:
            print("Fail to get ISBN of '"+Title+"', may not be insert")
            detailed=False
        try:
            Author=self.getAuthor(bookSoup.select("#info a")[0].contents[0])
        except:
            print("Fail to get Author of '"+Title+"', miss info in the table 'author'")
            detailed=False
        try:
            Publisher=infos[infos.index('出版社:') + 1].strip()
        except:
            print("Fail to get Publisher of '"+Title+"', bad records")
            detailed=False
        try:
            PTime=infos[infos.index('出版年:') + 1].strip()
        except:
            print("Fail to get Ptime of '"+Title+"', bad records")
            detailed=False
        try:
            Score=float(bookSoup.select(".rating_num")[0].contents[0].strip())
        except:
            print("Fail to get the Score of '"+Title+"', bad records")
            detailed=False
        # coverUrl=bookSoup.select("#mainpic > a > img")[0].attrs['src']
        try:
            Price=infos[infos.index('定价:') + 1].strip()
            Price=float(re.findall(r"\d+\.?\d*",Price)[0])
        except:
            print("Fail to get the price of '"+Title+"', the content in varible now is "+Price)
            Price=0
            detailed=False
        try:
            ChineseIntro=bookSoup.select('#link-report .all .intro p')
            if ChineseIntro==[]:
                ChineseIntro=bookSoup.select('#link-report .intro p')
            ChineseIntro=self.getChineseIntro(ChineseIntro)
        except:
            print("Fail to get the Chinese Intro of '"+Title+"', the content in varible now is "+ChineseIntro)
            detailed=False

        return detailed,[ISBN, Title, Publisher, PTime, Price, Score, ChineseIntro, "No Info"],[ISBN, Author]

    def getBookInfo(self):
        if os.path.exists(self.category_file):
            with open(self.category_file, "r", encoding="utf-8") as fin:
                self.category_urls=fin.read().splitlines()
        else:
            self.category_file=self.getCategory()

        cnt=self.cnt
        for url in self.category_urls:
            web_data=self.getPage(url=url)
            soup=BeautifulSoup(web_data.text.encode("utf-8"), "lxml")
            books=soup.select("li.subject-item h2 a")
            bookinfo=[] # bookinfo
            authorinfo=[] # relationships in author table
            for book in books:
                book_url=book.attrs['href']
                book_data=self.getPage(book_url)
                bookSoup=BeautifulSoup(book_data.text.encode('utf-8'),'lxml')

                bookDetail=self.getDetail(bookSoup)
                if bookDetail[0]==True:
                    bookinfo.append(bookDetail[1])
                    authorinfo.append(bookDetail[2])
                    cnt-=1
            bookinsert_sql='''INSERT IGNORE INTO book (
                ISBN, Title, Publisher, Ptime, Price, Score, ChineseIntro, EnglishIntro
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'''
            authorinsert_sql='''INSERT IGNORE INTO author (
                ISBN, Author
            ) VALUES (%s,%s)'''
            with self.conn.cursor() as cursor:
                cursor.executemany(bookinsert_sql, bookinfo)
                cursor.executemany(authorinsert_sql, authorinfo)
            self.conn.commit()
            if cnt<0:
                break
        self.conn.close()


douban=myRequests()
douban.getBookInfo()
