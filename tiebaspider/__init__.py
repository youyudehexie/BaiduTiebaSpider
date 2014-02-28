#encoding=utf-8
import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

import urllib2
import urllib
import re
#from BeautifulSoup import BeautifulSoup 
import bs4
from bs4 import BeautifulSoup

def _readtopics(filename='topics.txt'):
	try:
		fd = open(filename, 'r')
		content = fd.read()
		return content
	except:
		print 'fail to read topics.txt'

def _writetopics(hrefs, filename='topics.txt'):
	try:
		content = '\n'.join(hrefs)
		fd = open(filename, 'w')
		fd.write(content)
	except:
		print 'fail to write topics.txt'

def _writearticles(content, filename='articles.txt'):
	try:
		fd = open(filename, 'a')
		fd.write(content)
	except:
		print 'fail to write topics.txt'


def _download(url):
	try:
		response = urllib2.urlopen(url).read().decode("gbk")

	except:  
		print 'urllib2 error'
		return

	return response


#----------- 处理页面上的各种标签 -----------
class HTML_Tool:
    # 用非 贪婪模式 匹配 \t 或者 \n 或者 空格 或者 超链接 或者 图片
    BgnCharToNoneRex = re.compile("(\t|\n| |<a.*?>|<img.*?>)")
    
    # 用非 贪婪模式 匹配 任意<>标签
    EndCharToNoneRex = re.compile("<.*?>")

    # 用非 贪婪模式 匹配 任意<p>标签
    BgnPartRex = re.compile("<p.*?>")
    CharToNewLineRex = re.compile("(<br/>|</p>|<tr>|<div>|</div>)")
    CharToNextTabRex = re.compile("<td>")

    # 将一些html的符号实体转变为原始符号
    replaceTab = [("&lt;","<"),("&gt;",">"),("&amp;","&"),("&amp;","\""),("&nbsp;"," ")]
    
    def Replace_Char(self,x):
        x = self.BgnCharToNoneRex.sub("",x)
        x = self.BgnPartRex.sub("\n    ",x)
        x = self.CharToNewLineRex.sub("\n",x)
        x = self.CharToNextTabRex.sub("\t",x)
        x = self.EndCharToNoneRex.sub("",x)

        for t in self.replaceTab:  
            x = x.replace(t[0],t[1])  
        return x  


class TiebaSpider:
	def __init__(self, review = False):
		self.hrefs = []
		self.review = review
		self.myTool = HTML_Tool()

	def start_request(self, **kw):
		tiebas = kw['tieba']
		page = kw['page']

		if not self.review:
			return self.get_topics_list(tiebas, page)
		else:
			self.hrefs = _readtopics().split('\n')
			return self.get_articles()

	def get_topics_list(self, tiebas, page):
		urls = []
		for tieba in tiebas:
			for p in range(page):
				pn = 50 * p
				url_template = 'http://tieba.baidu.com/f?kw=%s&pn=%s' % (tieba, pn)
				urls.append(url_template)

		_writetopics(hrefs=self.hrefs)

		return self.download_topic(urls)

	def parse_topic(self, response):
		hrefPat = re.compile(r'href=\"(.*?)\"')
		titlePat = re.compile(r'title=\"(.*?)\"')

		soup = BeautifulSoup(response)
		topics = soup.body.findAll("div", {"class" : "threadlist_text threadlist_title j_th_tit  notStarList "})
		for topic in topics:
			href = hrefPat.findall(str(topic))
			if href:
				self.hrefs.append(href[0])


	def download_topic(self, urls):
		for url in urls:
			response = _download(url)
			if response:
				self.parse_topic(response)

			else:
				continue

		_writetopics(hrefs=self.hrefs)

		return self.get_articles()

	def download_articles(self, urls):
		for url in urls:
			response = _download(url)
			if response:
				self.parse_articles(response)

			else:
				continue 

	def parse_articles(self, response):
		titlePat = re.compile(r'title\:\"(.*?)\"')
		title = titlePat.findall(str(response))

		bodyPat = re.compile(r'<cc>(.*?)<\/cc>')
		body = bodyPat.findall(str(response))

		items = {}
		if title and body:
			data = self.myTool.Replace_Char(body[0].replace("\n","").encode('utf-8'))
			items['title'] = title[0]
			data = data.replace("\r", "")
			items['body'] = data.split('\n')[0]
			self.output(items)


	def output(self, items):
		content = '%s\t%s\n' % (items['title'], items['body'])
		print '爬取 %s ' % items['title']
		_writearticles(content)

	def get_articles(self):
		hrefs = self.hrefs
		urls = []
		for href in hrefs:
			url_template = 'http://tieba.baidu.com' + href + '?see_lz=1'
			urls.append(url_template)

		self.download_articles(urls)


