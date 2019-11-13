from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from time import sleep
import random
import codecs
import sys
import re
import pymysql
import datetime
import keys

class Scrapper():
    counter = 0
    mysql = pymysql.connect(
    host = keys.mysql_host, 
    port = keys.mysql_port, 
    user = keys.mysql_user, 
    password = keys.mysql_password, 
    database = keys.mysql_database
    )
    cursor = mysql.cursor()

    def setUp(self):
        options = webdriver.ChromeOptions()
        #options.add_argument("headless") #without window
        options.add_argument("window-size=1920x1080")
        options.add_argument("disable-gpu")
        self.driver = webdriver.Chrome(executable_path=r'C:/Users/youngdae/Documents/Python/BigKindsCrawler-master/BigKindsCrawler-master/chromedriver.exe', chrome_options=options)
        # self.driver = webdriver.PhantomJS('../bin/phantomjs')
        self.driver.set_page_load_timeout(30)
        #self.driver.implicitly_wait()

    def test(self, kwd, year, start, end=None):
        self.counter = int(start)
        query = 'CREATE TABLE IF NOT EXISTS `%s`.' % keys.mysql_database + '''`%s` (
                counter INT PRIMARY KEY NOT NULL,
                id VARCHAR(30) NOT NULL,
                title varchar(100) NOT NULL,
                written_at DATE,
                content TEXT NOT NULL,
                scrapped_at datetime NOT NULL
            );''' % year
        self.cursor.execute(query)
        p = 0
        isContinue = False
        if (start != "0"):
            p = int(start) / 100
            p = int(p)+1
            isContinue = True
        self.setUp()
        self.driver.get("https://www.bigkinds.or.kr/v2/news/index.do")
        self.wait = WebDriverWait(self.driver, 10)
        self.driver.find_element_by_css_selector("span.caret").click()
        self.driver.find_element_by_css_selector("button.btn.btn-sm.w-100.main-search-filters__dropdown__btn.date-select-btn").click()
        self.driver.find_element_by_css_selector("button#date-confirm-btn").click()
        sleep(random.randint(5, 20))
        self.driver.find_element_by_css_selector("input#total-search-key").send_keys(kwd)
        sleep(random.randint(5, 20))
        self.driver.find_element_by_css_selector("span.input-group-btn").click()
        sleep(random.randint(20, 30))
        self.driver.find_element_by_css_selector(("input#filter-date-"+str(year)).click())
        sleep(random.randint(20, 30))
        for op in self.driver.find_elements_by_css_selector("option"):
            if op.get_attribute("value") == "100":
                op.click()
                sleep(random.randint(20, 30))
                break
        total = int(self.driver.find_element_by_css_selector("span#total-news-cnt").text.replace(",",""))
        page = int(total/100) +1
        count = 0
        for i in range(1, page+1):
            for pnum in self.driver.find_elements_by_css_selector("a.page-link"):
                if (str(i) == pnum.text):
                    pnum.click()
                    sleep(random.randint(20, 30))
                    break
            if (isContinue):
                if (i < int(p)):
                    count += 100
                    continue
            for article in self.driver.find_elements_by_css_selector("h4.news-item__title.news-detail"):
                count+=1
                if(isContinue):
                    if(count < int(start)):
                        continue
                id = article.get_attribute("data-newsid")
                #fw = codecs.open("C:/Users/ck4ck/Documents/Python/NewsScrapper/"+year+"/"+str(count)+".txt", "w", encoding="utf-8")
                #fw.write(id+"\n")
                #fw.write(article.text+"\n")
                title = article.text
                article.click()
                sleep(random.randint(5, 20))
                temp = ""
                for hitem in self.driver.find_elements_by_css_selector("span.news-detail__header-item"):
                    temp += hitem.text + "\t"
                headline = temp
                try:
                    written_at = re.findall('\d\d\d\d-\d\d-\d\d', headline)[0]
                except Exception as e:
                    written_at = None
                #fw.write(temp + "@@@@@\n")
                #fw.write(self.driver.find_element_by_css_selector("div.news-detail__content").text)
                #fw.close()
                content = self.driver.find_element_by_css_selector("div.news-detail__content").text
                scrapped_at = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.counter += 1
                q = 'SELECT count(counter) FROM `%s` where counter = %s' % (int(year), self.counter)
                while(True):
                    try:
                        cursor.execute(q)
                        checker = cursor.fetchall()[0][0]
                        break
                    except Exception as e:
                        print(e)
                        mysql = pymysql.connect(
                            host = keys.mysql_host, 
                            port = keys.mysql_port, 
                            user = keys.mysql_user, 
                            password = keys.mysql_password, 
                            database = keys.mysql_database
                            )   
                        cursor = mysql.cursor()
                if checker == 0:
                    query = '''INSERT INTO `%s`(counter, id, title, written_at, content, scrapped_at)
                                VALUES (%s, %s, %s, %s, %s, %s);'''
                    values = (int(year), self.counter, id, title, written_at, content, scrapped_at)
                    while(True):
                        try:
                            cursor.execute(query, values)
                            mysql.commit()
                            break
                        except Exception as e:
                            print(e)
                            self.counter -= 1
                            mysql = pymysql.connect(
                                                    host = keys.mysql_host, 
                                                    port = keys.mysql_port, 
                                                    user = keys.mysql_user, 
                                                    password = keys.mysql_password, 
                                                    database = keys.mysql_database
                                                    )
                            cursor = mysql.cursor()
                    print(temp, self.counter + 'articles crawled')
                elif checker == 1:
                    pass
                for a in self.driver.find_elements_by_css_selector("button.btn.btn-default"):
                    if (a.text == "닫기"):
                        a.click()
                        sleep(random.randint(5, 20))
            sleep(random.randint(60, 90))
        self.tearDown()

    def tearDown(self):
        self.driver.close()

if __name__ == '__main__':
    s = Scrapper()
    kwd = "미세먼지"
    s.test(kwd, 2018, "0")
    s.test(kwd, 2019, "0")
