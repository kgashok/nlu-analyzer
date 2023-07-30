from flask import Flask, request, jsonify, make_response
from flask_restful import Resource, Api
from binarytree import Node, tree
from app.bst import BST
import random
import time 

app = Flask(__name__)
api = Api(app)

# The sample list to be used to generate the BST 
# in case the user specifies range=true on the URL
biglist = list(range(1, 30))

class MainResource(Resource):
    """handles the parsing of the URL for node information

    Args:
        Resource (_type_): _description_
    """    
    def get(self):
        """parses the URL to build a BST and generate 
        a string equivalent of the same for display

        Returns:
           Response: containing the string version of the BST object
           See https://flask.palletsprojects.com/en/2.3.x/api/#flask.Flask.make_response
           and https://flask.palletsprojects.com/en/2.3.x/api/#flask.Response
 
        """        
        # process the query params
        balanced = None
        nodes = list()
        shuffle = "true"
        range = request.args.get('range')
        shuffle = request.args.get('shuffle')
        n = request.args.get('nodes')
            
        if n:
            n = n.strip().split(',')
            try: 
                nodes = [int(e) for e in n]
                # print(nodes, nodes[0], nodes[1])
            except: 
                response = make_response("An error occurred, please double check your input!", 400)
                return response
        else:
            print("No node information given. Using standard list!")
            nodes[:] = biglist 
                            
        if shuffle != "false": # and shuffle.lower() == 'true':
            # do you want a https://kov.ai/linearTree?
            linearTree = random.choice([False, True, False, False, False])
            if linearTree:
                nodes.sort()
                balanced = random.choice([False, True]) 
            else:
                random.shuffle(nodes)

        bst = BST(balanced=balanced)        
        if not balanced: 
            try:
                for n in nodes:
                    bst.binary_insert(int(n))
            except:
                #return 'An error occurred, please double check your input!'
                response = make_response("Cannot generate BST. Check your input!", 400)
                return response

        response = make_response(bst.get_output(), 200)
        response.mimetype = 'text/plain'
                
        return response


api.add_resource(MainResource, '/')

if __name__ == '__main__':
    random.seed(time)
    app.run()
