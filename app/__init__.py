from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
# First we need the CORS thinymajig
from flask_cors import CORS, cross_origin
import random
import time 

import json
import time
#from datetime import datetime
import random

import requests
from bs4 import BeautifulSoup as bs

from ibm_watson import NaturalLanguageUnderstandingV1, ApiException
#from ibm_watson.natural_language_understanding_v1 import Features, EntitiesOptions, KeywordsOptions, CategoriesOptions, 
from ibm_watson.natural_language_understanding_v1 import Features, CategoriesOptions, KeywordsOptions, SummarizationOptions
#from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# Authentication via IAM
# authenticator = IAMAuthenticator('your_api_key')
# service = NaturalLanguageUnderstandingV1(
#     version='2018-03-16',
#     authenticator=authenticator)
# service.set_service_url('https://gateway.watsonplatform.net/natural-language-understanding/api')

# Authentication via external config like VCAP_SERVICES
service = NaturalLanguageUnderstandingV1(
    version='2018-03-16')
#service.set_service_url('https://gateway.watsonplatform.net/natural-language-understanding/api')

#response = service.analyze(
#    text='Bruce Banner is the Hulk and Bruce Wayne is BATMAN! '
#    'Superman fears not Banner, but Wayne.',
#    features=Features(entities=EntitiesOptions(),
#                      keywords=KeywordsOptions())).get_result()

#print(json.dumps(response, indent=2))


# Put this right after you declare the app

app = Flask(__name__)
cors = CORS(app)
api = Api(app)

import re

'''def youtube_get_id(url):
    ID = ''
    patterns = [
        r'(?<=v=)[^&#]+',
        r'(?<=vi/)[^&#]+',
        r'(?<=youtu\.be/)[^&#]+',
        r'(?<=/v/)[^&#]+',
        r'(?<=/embed/)[^&#]+',
        r'(?<=youtube.com/shorts/)[^?]+'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            ID = match.group()
            break

    return ID
#'''
def youtube_get_id(url):
    ID = ''
    patterns = [
        r'(?<=v=|vi/|youtu\.be/|/v/|/embed/)[^/?&]+',
        r'(?<=youtube.com/shorts/|youtu.be/)[^?&]+'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            ID = match.group()
            break

    return ID
'''
#'''
def youtube_get_id(url):
    video_id = ''
    patterns = [
        r'(?:(?:v|vi|e)/|watch\?v=|youtu\.be/|/v/|/embed/|youtube.com/shorts/)([^/?&]+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break

    return video_id
#'''

tweet_text=  '''
Here’s an analogy: If Moksha (liberation) is the supreme goal of Life, spirituality is the means to achieve it. Similarly if Polymorphism is the supreme goal of OOD/OOP, abstraction is the means to achieve it.

A good object-oriented design (OOD) provides for effective abstraction (a concept enabled by encapsulation, inheritance, composition, aggregation, association) that enables powerful types of polymorphism (behaviour).
'''


import tweepy
import os

# Use your existing Twitter API credentials
consumer_key = os.getenv('TWITTER_CONSUMER_KEY')
consumer_secret = os.getenv('TWITTER_CONSUMER_SECRET')
access_token = os.getenv('TWITTER_ACCESS_TOKEN')
access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')

client = tweepy.Client(bearer_token=twitter_bearer_token)  

# Authenticate with the Twitter API
#auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
#auth.set_access_token(access_token, access_token_secret)

# Create the Tweepy API object
#tweetapi = tweepy.API(auth, wait_on_rate_limit=True)

# Sample tweet URL
#tweet_url = "https://twitter.com/example/status/123456789"
    
def get_tweet_text(tweet_url, api=None):
    """Extract text content from a tweet URL.
    
    Args:
        tweet_url (str): URL of the tweet to extract text from
        api: Twitter API client instance (optional)
        
    Returns:
        str: The text content of the tweet, or None if unable to fetch
    """
    # Extract tweet ID from the URL
    tweet_id = tweet_url.split("/")[-1]
    if tweet_id.find('?') != -1:
        tweet_id = tweet_id.split('?')[0] 
    print("tweet_id", tweet_id)
    # Retrieve the tweet
    try:
        #tweet = api.get_status(tweet_id, tweet_mode="extended")
        tweet = client.get_tweet(
            id=tweet_id,
            expansions=['author_id', 'attachments.media_keys'],  
            tweet_fields=['created_at', 'text', 'public_metrics']
        )

        tweet_text = tweet.data.text
        print("Extracted Tweet Text:", tweet_text)
        return tweet_text
    except tweepy.TweepyException as e:
        print("Error fetching tweet:", e)
        # Return a default response when tweet access is forbidden
        if "453" in str(e):
            return "Unable to fetch tweet due to API access restrictions."
        return None

class MainResource(Resource):
    """Handles URL parsing and analysis for natural language processing.
    
    This resource class processes URLs to extract text content and performs
    natural language analysis using IBM Watson services. It handles different
    types of URLs including Twitter/X posts and YouTube videos.

    Inherits from:
        Resource: Flask-RESTful base resource class
    """    
    
    def get_url_related(self, url):
        """Process URL and determine its type and extraction parameters.
        
        Args:
            url (str): The URL to analyze
            
        Returns:
            tuple: Contains:
                - url_type (str): Type of URL (twitter, youtube, etc.)
                - clean (str): Cleaning flag for text processing
                - xpath (str): XPath for content extraction
                - adj_url (str): Adjusted/processed URL
        """
        url_type = None
        clean = "true"
        xpath = None
        adj_url = url.strip()
        #if adj_url.find("twitter.com") > 0: 
        if adj_url.find("x.com") > 0: 
            #xpath = "//div[@id='react-root']"
            #xpath = "//*[@data-testid='tweetText']" 
            # xpath = "//div[@data-testid]"
            xpath = "//div[@id='react-root']"
            xpath = "//article"
            #clean = "false"
            url_type = "twitter"
            #xpath = get_tweet_text(adj_url, tweetapi)
            xpath = get_tweet_text(adj_url)           #print("xpath:", xpath)
            
        
        elif adj_url.find("youtube.com") > 0 or url.find("youtu.be") > 0:
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError
            import os

            video_id = youtube_get_id(adj_url)
            if len(video_id) == 0:
                print("Bad Video ID") 
                raise ApiException(code=400, message="Invalid YouTube video ID!")

            youtube = build('youtube', 'v3', developerKey=os.getenv('YOUTUBE_API_KEY'))
            
            try:
                video_response = youtube.videos().list(
                    part='snippet',
                    id=video_id
                ).execute()

                if not video_response['items']:
                    raise ApiException(code=404, message="Video not found!")

                video_data = video_response['items'][0]['snippet']
                title = video_data.get('title', '')
                description = video_data.get('description', '')
                
                # Store combined text in xpath for later use
                xpath = f"{title}\n\n{description}"
                url_type = "youtube"
                clean = "true"
                adj_url = f"https://www.youtube.com/watch?v={video_id}"
            except HttpError as e:
                print(f"YouTube API error: {e}")
                raise ApiException(code=500, message="YouTube API error")
                
        return url_type, clean, xpath, adj_url

    def get(self):
        """Handle GET requests for URL analysis.
        
        Processes the provided URL parameter to extract and analyze text content
        using IBM Watson Natural Language Understanding service.
        
        Returns:
            dict: Analysis results from Watson NLU service
            or
            Response: Error response if processing fails
        """
        nlu_url = request.args.get('url')
        print("nlu_url", nlu_url)
        url_type, clean_val, xpath_val, nlu_url = self.get_url_related(nlu_url)
        print("adj_url", nlu_url, clean_val, xpath_val)
        response = None
        tweet_text = ""

        #xpath_val = "//div[@class='wd_title wd_language_left' or @class='wd_subtitle wd_language_left']"
        #xpath_val = "//ytd-text-inline-expander[@id='description-inline-expander']"

        if url_type in ["twitter", "youtube"]:
            content_text = xpath_val
            try:
                response = service.analyze(
                    text=content_text, \
                    return_analyzed_text="true",\
                    clean=clean_val, \
                    features=Features(
                        categories=CategoriesOptions(), \
                        keywords=KeywordsOptions(emotion=True, sentiment=True, limit=2) \
                        )).get_result()

                #print("analyzed", response)
                print("***nlu tweet success!")

                response['retrieved_url'] = nlu_url
                response['metadata'] = dict()
                if url_type == "youtube": 
                    content_text = content_text.split("\n\n", 1)[0]   
                response['metadata']['title'] = content_text
                return response

            except ApiException as error:
                print("APIException1", error)
                response = make_response(error.message, error.code)
                return response 
                # return error.http_response
    
        else:
            try:
                response = service.analyze(
                    #text=tweet_text, \
                    return_analyzed_text="true", url=nlu_url,\
                    clean=clean_val, xpath=xpath_val, 
                    features=Features(
                        metadata={}, \
                        #summarization=SummarizationOptions(), \
                        categories=CategoriesOptions() \
                                    #entities=EntitiesOptions(), \
                                    #keywords=KeywordsOptions() \
                                    )).get_result()
                '''response = service.analyze(
                    url=nlu_url,
                    features=Features(categories=CategoriesOptions(), \
                                    #entities=EntitiesOptions(), \
                                    #keywords=KeywordsOptions() \
                                    )).get_result()
                '''
                print("***nlu success!")
                
            except ApiException as error:
                print("APIException2", error)
                response = make_response(error.message, error.code)
                return response 
                # return error.http_response
    
        if response: 
            # print(json.dumps(response, indent=2))
            ret_url = response['retrieved_url']
            print(ret_url)
            title = response['metadata']['title']
            #response = make_response(nlu_url, 200)
            #response.mimetype = 'text/json'
            print("title from metadata", title)
            r = requests.get(ret_url)
            soup = bs(r.content, 'lxml')
            #print(soup)
            if soup and soup.select_one('title'): 
                title2 = soup.select_one('title').text
                # desc = soup.select_one('description-collapsed').text
                #//*[@id="below"]/ytd-watch-metadata
                print("title from soup", title2)
                if len(title2) > len(title):
                    response['metadata']["title"] = title2 
                    print("soup title used!")
        
        return response
    

api.add_resource(MainResource, '/analyze')


if __name__ == '__main__':
    random.seed(time)
    app.run()



