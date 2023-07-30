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
        # strip query params
        n = request.args.get('nodes')
        if n:
            n = n.strip().split(',')
            nodes = [int(e) for e in n]
            # print(nodes, nodes[0], nodes[1])
            range = request.args.get('range')
            if range and range.lower() == 'true': 
                #print(type(nodes[0]))
                #print(type(nodes[1]))
                #nodes = list(range(nodes[0], nodes[1]))
                nodes[:] = biglist 
                
            shuffle = request.args.get('shuffle')

            balanced = None
            if shuffle and shuffle.lower() == 'true':
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
                    return 'An error occurred, please double check your input!'

            response = make_response(bst.get_output(), 200)
            response.mimetype = 'text/plain'
                
        else:
            response = 'You must supply a comma delimited list of numbers in a \'nodes\' query param!'
        return response


api.add_resource(MainResource, '/')

if __name__ == '__main__':
    random.seed(time)
    app.run()
