from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from flask_cors import CORS, cross_origin
import random
import time
import json
import requests
from bs4 import BeautifulSoup as bs
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.api_exception import ApiException
from ibm_watson.natural_language_understanding_v1 import Features, CategoriesOptions, KeywordsOptions, SummarizationOptions
import tweepy
import os
import re

# Initialize Flask app
app = Flask(__name__)
cors = CORS(app)
api = Api(app)

# Initialize Twitter API
twitter_bearer_token = os.getenv('TWITTER_BEARER_TOKEN')
client = tweepy.Client(bearer_token=twitter_bearer_token)

# Initialize Watson NLU
service = NaturalLanguageUnderstandingV1(version='2018-03-16')

def youtube_get_id(url):
    """Extract YouTube video ID from URL."""
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

def get_tweet_text(tweet_url, api=None):
    """Extract text content from a tweet URL.

    Args:
        tweet_url (str): URL of the tweet to extract text from
        api: Twitter API client instance (optional)

    Returns:
        str: The text content of the tweet, or None if unable to fetch
    """
    tweet_user = None
    tweet_id = tweet_url.split("/")[-1]
    print("tweet_id", tweet_id)

    if tweet_id.find('?') == -1 and not tweet_id.isnumeric():
        tweet_user = tweet_id
        print("tweet_user", tweet_user)
    else: 
        tweet_id = tweet_id.split('?')[0]
        print("tweet_id", tweet_id)

    if tweet_user:
        try:
            user = client.get_user(username=tweet_user, user_fields=['description', 'name', 'username'])
            if user.data:
                user_data = user.data
                print("Full user data:", user_data)
                user_description = user_data.description
                user_name = user_data.name
                user_username = user_data.username

                tweet_text = f"Twitter User: {user_name} (@{user_username})"
                if user_description:
                    tweet_text += f"\nDescription: {user_description}"
                print("Extracted User Info:", tweet_text)
                return tweet_text
            return "User not found"
        except Exception as e:
            print("Error fetching user:", e)
            return f"Error fetching user information: {str(e)}"

    try:
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
        if "453" in str(e):
            return "Unable to fetch tweet due to API access restrictions."
        return None

class MainResource(Resource):
    """Handles URL parsing and analysis for natural language processing."""

    def get_url_related(self, url):
        """Process URL and determine its type and extraction parameters."""
        url_type = None
        clean = "true"
        xpath = None
        adj_url = url.strip()

        if adj_url.find("x.com") > 0:
            xpath = "//article"
            url_type = "twitter"
            xpath = get_tweet_text(adj_url)

        elif adj_url.find("youtube.com") > 0 or url.find("youtu.be") > 0:
            from googleapiclient.discovery import build
            from googleapiclient.errors import HttpError

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

                xpath = f"{title}\n\n{description}"
                url_type = "youtube"
                clean = "true"
                adj_url = f"https://www.youtube.com/watch?v={video_id}"
            except HttpError as e:
                print(f"YouTube API error: {e}")
                raise ApiException(code=500, message="YouTube API error")

        return url_type, clean, xpath, adj_url

    def get(self):
        """Handle GET requests for URL analysis."""
        nlu_url = request.args.get('url')
        print("nlu_url", nlu_url)
        url_type, clean_val, xpath_val, nlu_url = self.get_url_related(nlu_url)
        print("adj_url", nlu_url, clean_val, xpath_val)
        response = None

        if url_type in ["twitter", "youtube"]:
            content_text = xpath_val
            try:
                response = service.analyze(
                    text=content_text,
                    return_analyzed_text="true",
                    clean=clean_val,
                    features=Features(
                        categories=CategoriesOptions(),
                        keywords=KeywordsOptions(emotion=True, sentiment=True, limit=2)
                    )).get_result()

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
        else:
            try:
                # If URL is not accessible, try analyzing as direct text
                try:
                    response = service.analyze(
                        return_analyzed_text="true",
                        url=nlu_url,
                        clean=clean_val,
                        xpath=xpath_val,
                        features=Features(
                            metadata=MetadataOptions(), # Modified line
                            categories=CategoriesOptions()
                        )).get_result()
                except ApiException:
                    # Try analyzing as text if URL fails
                    response = service.analyze(
                        text=nlu_url,  # Treat input as text
                        return_analyzed_text="true",
                        features=Features(
                            metadata={},
                            categories=CategoriesOptions()
                        )).get_result()
                print("***nlu success!")

            except ApiException as error:
                print("APIException2", error)
                response = make_response(error.message, error.code)
                return response

        if response:
            ret_url = response['retrieved_url']
            print(ret_url)
            title = response['metadata']['title']
            print("title from metadata", title)
            r = requests.get(ret_url)
            soup = bs(r.content, 'lxml')
            if soup and soup.select_one('title'):
                title2 = soup.select_one('title').text
                print("title from soup", title2)
                if len(title2) > len(title):
                    response['metadata']["title"] = title2
                    print("soup title used!")

        return response

api.add_resource(MainResource, '/analyze')

if __name__ == '__main__':
    random.seed(time)
    app.run()