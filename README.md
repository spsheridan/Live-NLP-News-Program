# Live-NLP-News-Program
This program takes in a live feed of stock market news, and uses natural language processing to filter the news into categories such as tradeable news, or non-relevant news.

## Problem
The goal of this program is to live-test the capabilities of NLP to predict good stock trades based on news headlines. Ideally the output CSV would mark tickers down before their prices change in the favorable direction (price inc for long, price dec for short). While using the RSS feed from a website is a bit hacky, it was the most economical option for a test program in the situation (as opposed to expensive live news APIs).

## Solution and Process
The process of this program is visualized in the diagram below: 
![Blank diagram (2)](https://user-images.githubusercontent.com/118930217/204192404-feff15ae-936e-4eaa-bc64-317056e2634f.jpeg)

The sources of the news is a website's RSS feed, specifically StreetInsider. The program fetches the information from the RSS feed on a customized interval. After it has parsed the information, the headline is sent to the Openai natural language processing model (NLP) (trained/created by me) for processing. The NLP assigns a category to the headline. Once a category is assigned, the headline gets placed into one of three CSVs: 
- Trade news: ticker of news is in tradeable stocks list (low market cap), and the category is impactful
- Public news: ticker of news is not in tradeable stocks list, but ticker is from a public company
- Everything else: no stock ticker attached to news, probably irrelevant however useful in case of mislabeled news

A sample of the trade news is below:
![rssfeedjaunt](https://user-images.githubusercontent.com/118930217/204194035-0fa591db-1a05-4a03-bbec-8976f294d9e7.PNG)

## Results Analysis
The results of the program are useful to the user in the following ways:
- The program makes it easy to inspect potential trade performance when trading off news events
- There are times when a news article publish time is a round number such as 08:00:00, however the true release time is 08:00:13, so the program marking down the time the news was received shows the real time when the trade would have been placed
- By printing the news headline categories, the NLP model can be assessed for accuracy in real-life scenarios

## Challenges
There were two main challenges associated with this project:
- Using Beautifulsoup to access the RSS feed information is something I had not done before, so that took some problem-solving
- Making the program be able to restart without duplicating news that it had already marked into one of the CSVs took some work

## Other applications
This program can be applied to other RSS feeds outside of just the StreetInsider RSS feed with minor tweaking. Overall it is a pretty specific use case. 

## Potential Advancements
There are three potential advancements:
- The program already collects the body of the news article, and I did train NLP models for the bodies of the text as well, so the most obvious advancement would be to add the capability to process the body of the press release as well in the output
- If the source of the information was changed to an API or other more reliable source, the program could be used for more than just testing
- The program could access some kind of stock price API to add in the price change after the news happened so that the user does not have to check manually
