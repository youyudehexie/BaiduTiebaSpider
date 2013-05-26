BaiduTiebaSpider
================
#百度贴吧爬虫
爬百度贴吧，获取内容到文件articles.txt

#Example

	from tiebaspider import TiebaSpider

	if __name__ == "__main__":
		spider = TiebaSpider()
		tieba = ['wow', '李毅'] #爬WOW吧，如果多个贴吧 
		spider.start_request(tieba=tieba, page=1) # tieba: 贴吧列表 page:贴吧页数
