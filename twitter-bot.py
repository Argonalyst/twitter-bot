# -*- coding: utf-8 -*-
"""
Created on Fri Nov 04 16:55:09 2016

@author: Argonalyst
"""

import tweepy
from tweepy import StreamListener
from tweepy import Stream
import datetime
import time
import random
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import LinearSVC
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.multiclass import OneVsRestClassifier
from sklearn import preprocessing

# Consumer keys and access tokens, used for OAuth
consumer_key = 'your_consumer_key'
consumer_secret = 'your_consumer_secret'
access_token = 'your_access_token'
access_token_secret = 'your_access_token_secret'

def get_api(cfg):

  auth = tweepy.OAuthHandler(cfg['consumer_key'], cfg['consumer_secret'])
  auth.set_access_token(cfg['access_token'], cfg['access_token_secret'])
  
  api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

  return api

def send_tweet(consumer_key, consumer_secret, access_token, access_token_secret, tweet, tweet_id):

  cfg = { 
    "consumer_key"        : consumer_key,
    "consumer_secret"     : consumer_secret,
    "access_token"        : access_token,
    "access_token_secret" : access_token_secret
    }

  api = get_api(cfg)
  status = api.update_status(status=tweet, in_reply_to_status_id=tweet_id)
  # Yes, tweet is called 'status' rather confusing
  
def favorite_tweet(consumer_key, consumer_secret, access_token, access_token_secret, tweet_id):

  cfg = { 
    "consumer_key"        : consumer_key,
    "consumer_secret"     : consumer_secret,
    "access_token"        : access_token,
    "access_token_secret" : access_token_secret
    }

  api = get_api(cfg)
  create_favorite = api.create_favorite(tweet_id)
  
def create_friendship(consumer_key, consumer_secret, access_token, access_token_secret, screen_name, user_id):

  cfg = { 
    "consumer_key"        : consumer_key,
    "consumer_secret"     : consumer_secret,
    "access_token"        : access_token,
    "access_token_secret" : access_token_secret
    }

  api = get_api(cfg)
  create_friendship = api.create_friendship(user_id)

def save_tweet_csv(tweet):
    with open('tweets.csv','a') as f:
        tweet = tweet.replace('\n', ' ').replace('\r', '').replace(',', ' ')
        f.write(tweet)
        f.write("\n")
    f.close()
    
def analyse_tweet_ml(tweet):
    df = pd.read_csv('tweets.csv')
    df.isnull().any()
    
    message = tweet
    
    X_train = df.tweet
                        
    y_train = df.label.astype(str)
    
    lb = preprocessing.MultiLabelBinarizer()
    y_train = lb.fit_transform(y_train)
    
    X_test = np.array([message])
    
    # ML Pipeline
    classifier = Pipeline([
        ('vectorizer', CountVectorizer(max_df=0.5, ngram_range=(1, 2))),
        ('tfidf', TfidfTransformer()),
        ('clf', OneVsRestClassifier(LinearSVC()))])
    classifier.fit(X_train, y_train)
    predicted = classifier.predict(X_test)    
    
    print predicted[0]
    
    count = 0
    label = ""
    for i in predicted[0]:
        if i == 1:
            label = count
        count = count + 1
        
    return label

class StdOutListener(StreamListener):
    ''' Handles data received from the stream. '''
 
    def on_status(self, status):

        tweet_id = status.id
        user_id = status.user.id
        screen_name = status.user.screen_name
        lang = status.lang
        tweet_text = status.text
        
        banned_handles = ['IMudou', 'ImovelAVenda', 'openimob']
        
        if lang == 'pt' and 'RT @' not in tweet_text and screen_name not in banned_handles:
            # Prints the text of the tweet
            print('Tweet text: ' + status.text)
            print('Name: ' + status.user.screen_name)
            print('ID: ' + str(status.id))
            print('User ID: ' + str(status.user.id))
            print('lang: ' + str(status.lang))
            
            # Check if the tweet can be extended to 280 characters
            try:                
                print('Tweet text: ' + status.extended_tweet['full_text'])
                tweet_text = status.extended_tweet['full_text']
            except AttributeError:
                pass
            create_friendship(consumer_key, consumer_secret, access_token, access_token_secret, screen_name, user_id)
            #save_tweet_csv(tweet_text.encode('utf-8'))
            

            # we can use Machine Learning to identify if the tweet has negative emotion or something like that
            # labeled data is needed (you have to label it by your own)
            """
            ml_result = analyse_tweet_ml(tweet_text.encode('utf-8'))            
            if ml_result == 1 or ml_result == 2:
                tweet = reaction_tweets(ml_result)
                tweet = '@'+status.user.screen_name+' '+tweet.decode('utf-8')
                tweet_id = status.id
                print('Envia isto: '+tweet)
                send_tweet(consumer_key, consumer_secret, access_token, access_token_secret, tweet, tweet_id)
            """
             
        return True
 
    def on_error(self, status_code):
        print('Got an error with status code: ' + str(status_code))
        return True
 
    def on_timeout(self):
        print('Timeout...')
        return True
 
if __name__ == '__main__':

    
    listener = StdOutListener()
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
 
    stream = Stream(auth, listener)
    # Keywords to track!
    stream.filter(track=['startup', 'startups', 'innovation'])