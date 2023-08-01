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
from ibm_watson.natural_language_understanding_v1 import Features, CategoriesOptions, SummarizationOptions
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

class MainResource(Resource):
    """handles the parsing of the URL for node information

    Args:
        Resource (_type_): _description_
    """    
    def get(self):
        nlu_url = request.args.get('url')
        print("nlu_url", nlu_url)

        nlu_url = nlu_url.strip()
        response = None
        
        try:
            response = service.analyze(
                return_analyzed_text="true", url=nlu_url,
                features=Features(metadata={}, categories=CategoriesOptions(), summarization= SummarizationOptions() \
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
            print(error)
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
                print("title from soup", title2)
                if len(title2) > len(title):
                    response['metadata']["title"] = title2 
        
        return response
    

api.add_resource(MainResource, '/analyze')


if __name__ == '__main__':
    random.seed(time)
    app.run()



