#!/usr/bin/env python
# encoding: utf-8

import tweepy
import csv
from collections import Counter

# Only 3240 most recent tweets allowed to be scraped using this method

consumer_key = "your_consumer_key"
consumer_secret = "your_consumer_secret"
access_key = "your_access_key"
access_secret = "your_access_secret"

def get_all_tweets(screen_name):
    
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_key, access_secret)
    api = tweepy.API(auth)

    alltweets = []  

    #make initial request for most recent tweets (200 is the maximum allowed count)
    new_tweets = api.user_timeline(screen_name = screen_name,count=200)

    alltweets.extend(new_tweets)

    oldest = alltweets[-1].id - 1

    while len(new_tweets) > 0:
        print "getting tweets before %s" % (oldest)

        new_tweets = api.user_timeline(screen_name = screen_name,count=200,max_id=oldest, tweet_mode='extended')

        alltweets.extend(new_tweets)

        oldest = alltweets[-1].id - 1

        print "...%s tweets downloaded so far" % (len(alltweets))
    
    outtweets = []
    for tweet in alltweets:
        
        try:
            tweet_text = tweet.full_text.encode("utf-8")
        except AttributeError:
            tweet_text = tweet.text.encode("utf-8")
        outtweets.append([tweet.id_str, tweet.created_at, tweet_text])

    list_tweets = []
    all_words = []
    for i in outtweets:
        list_tweets.append(i[2])
        words = i[2].split()
        
        for word in words:            
            all_words.append(word)
        
    # you can remove words from tweets if you want to
    all_words = filter(lambda a: a != 'of', all_words)
    all_words = filter(lambda a: a != 'are', all_words)
    all_words = filter(lambda a: a != 'you', all_words)
    
    # save it!
    with open('list_tweets.txt', 'w') as f:
        for item in list_tweets:
            f.write("%s\n" % item)        

# the use we are scraping the tweets from
screen_name = "elonmusk"

get_all_tweets(screen_name)