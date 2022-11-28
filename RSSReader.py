import feedparser
import time
from bs4 import BeautifulSoup
from urllib.request import urlopen, Request
import csv
from datetime import datetime
import openai

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.3'}

def has_numbers(inputString):
    return any(char.isdigit() for char in inputString)

def get_pr_body(url):
    req = Request(url=url, headers=headers) 
    page = urlopen(req).read()
    html = page
    soup = BeautifulSoup(html, "html.parser")
    body_html = soup.find("div", {"class": "article_body"})
    body = body_html.getText()
    return body

rss_url = 'https://www.streetinsider.com/custom_feed.php?custom=1&key=115E61A'

####TAKE IN TRADEABLE STOCKS CSV, AND PUT THEM INTO ARRAY
tradeable_stocks = []
with open('tradeable_stocks_list.csv', 'r', newline = '', encoding = 'utf8') as csvfile1:
    ticker_sourcer = csv.reader(csvfile1, delimiter = ',', quotechar = '|')
    for row in ticker_sourcer:
        ticker_from_tradeable_stocks = row[0]
        tradeable_stocks.append(ticker_from_tradeable_stocks)

####LOAD NEWS THAT IS ALREADY IN NEWS CSVs
old_news = []
with open('trade_news.csv', 'r', newline = '', encoding = 'utf8') as csvfile5:
    with open('public_news.csv', 'r', newline = '', encoding = 'utf8') as csvfile6:
        with open('everything_else_news.csv', 'r', newline = '', encoding = 'utf8') as csvfile7:
            trade_news_reader = csv.reader(csvfile5, delimiter = ',', quotechar = '|')
            public_news_reader = csv.reader(csvfile6, delimiter = ',', quotechar = '|')
            everything_else_news_reader = csv.reader(csvfile7, delimiter = ',', quotechar = '|')

            for news_row in trade_news_reader:
                if len(news_row) > 1:
                    old_headline = news_row[2]
                    print(old_headline)
                    old_news.append(old_headline)
            for public_row in public_news_reader:
                if len(public_row) > 1:
                    old_headline = public_row[2]
                    print(old_headline)
                    old_news.append(old_headline)
            for everything_else_row in everything_else_news_reader:
                if len(everything_else_row) > 1:
                    old_headline = everything_else_row[2]
                    print(old_headline)
                    old_news.append(old_headline)
print(old_news)

####LIST ARRAY OF TRADEABLE NLP CATEGORIES THAT NEED THE PR BODY
need_body_nlp_preds = ['private', 'price', 'buy', 'contract', 'get', 'license', 'money', 'part', 'report', 'sell', 'sent', 'trial', 'update']

with open('trade_news.csv', 'a', newline = '', encoding = 'utf8') as csvfile2:
    with open('public_news.csv', 'a', newline = '', encoding = 'utf8') as csvfile3:
        with open('everything_else_news.csv', 'a', newline = '', encoding = 'utf8') as csvfile4:

            writer_trade_signals = csv.writer(csvfile2, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
            writer_public = csv.writer(csvfile3, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)
            writer_everything_else = csv.writer(csvfile4, delimiter = ',', quotechar = '|', quoting = csv.QUOTE_MINIMAL)

            while True:
####GRAB RSS INFORMATION
                feed = feedparser.parse(rss_url)
                items = feed["items"]
####LABEL INFORMATION
                for item in items:
                    headline = item["title"]
                    link = item["link"]
                    pub_date = item["published"]
####DE-DUPLICATE BY CHECKING CSVs IF THE NEWS IS ALREADY IN THERE
                    headline_no_commas = headline.replace(',', '')
                    if headline_no_commas in old_news:
                        continue
                    else:
                        old_news.append(headline_no_commas)
####GET TICKERS ASSOCIATED WITH NEWS          
                    categories = [t.term for t in item.get('tags', [])]
                    tickers = []            

                    if len(categories) > 0:
                        for x in categories:
                            if not has_numbers(x):
                                tickers.append(x)
                                print(x)          
####CHECK IF TICKERS ARE IN TRADEABLE STOCKS LIST, IF ONE OF THEM IS THEN SEND THAT TO THE NLP CATEGORIZATION
                    nlp_pred = 'N/A'
                    for v in tickers:
                        if v in tradeable_stocks:
                            print(v + " is in tradeable stocks list")
                            nlp_start_time=time.time() 
                            nlp_pred_table = openai.Completion.create(
                                model = "davinci:ft-personal-2022-07-25-08-07-36",
                                prompt = headline + '\n\n###\n\n', 
                                max_tokens = 1,
                                temperature = 0, 
                            )
                            nlp_pred = nlp_pred_table['choices'][0]['text']
                            nlp_pred = nlp_pred[1:]
                            nlp_functionTime = round(time.time() - nlp_start_time, 2)
                            print("\nNLP Time: %s seconds" % (nlp_functionTime))
                            break
####IF NLP CATEGORY IS ONE OF PRESET LIST THEN SCRAPE PR BODY AND SEND THAT TO NLP
                    if nlp_pred in need_body_nlp_preds:
                        start_time=time.time()    
                        pr_body = get_pr_body(link)
                        functionTime = round(time.time() - start_time, 2)
                        print("PR Body Time: %s seconds \n" % (functionTime))
                        ####SEND PR BODY TO NLP, GET ENTITIES AND PUT INTO ARRAY
                    else:
                        pr_body = 'N/A'

                    now = datetime.now()
                    current_time = now.strftime("%H:%M:%S")
                    
                    headline = headline.replace(',', '')
                    pub_date = pub_date.replace(',', '')
                    pr_body = pr_body.replace(',', '')
                    pr_body = pr_body.replace('\n', ' ')

                    results_array = [pub_date, current_time, headline, nlp_pred, link, pr_body]

                    excel_str = ' '

                    if len(tickers) > 0:
                        for y in tickers:
                            results_array.append(y)
                    else:
                        results_array.append(excel_str)

                    print(headline)
                    print("Done")

####ADD CHECK TO SEE IF NLP CATEGORY IS ONE OF THE TRADEABLE CATEGORIES AND THEN PUT ALL NEWS INTO APPROPRIATE CSVs
                    if nlp_pred != 'fat' and nlp_pred != 'N/A':
                        writer_trade_signals.writerow(results_array)
                    elif len(tickers) > 0:
                        writer_public.writerow(results_array)
                    else:
                        writer_everything_else.writerow(results_array)
                
                now_time_hours = datetime.now()
                current_time_update = now_time_hours.strftime("%H:%M:%S")
                print("Last update: " + current_time_update)
                print("Now Waiting to Update")
                time.sleep(3)  