# Anushka Gupta
# Project : To create my own cryptocurrency 
# Using python, flask and postman


# Creating our blockchain
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# ------------------Building the blockchain---------------------------------------------------------------------

class Blockchain:
    
    # first we need to create a chain that will hold all our blocks, the
    # blocks are stored in an empty list
    
    # New transactions are not originally formed into a block
    # new transactions are first added to a list
    # a block is created, which is mined
    # and after it is mined all the transactions are moved to the blockand the
    # list is emptied allowing it to be reused
    
    def __init__(self):
        self.chain = []

        # Creating a list of transactions before they are added to the block
        self.transactions = []
        
        # Now we need to create our genesis block which is the first block
        # of our blockchain
        self.create_block(proof = 1, previous_hash = '0')
        
        self.nodes = set()

    def create_block(self, proof, previous_hash):
        
        #Our block will be in the form of a dictionary
        # Important elements for a block are : index, time,proof,
        # hash of the pervious block and the list of transactions
        
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash,
                 'transactions' : self.transactions}
        
        # Now we need to empty the list so that pervious transcations are 
        # not added again
        self.transactions = []
        
        #now adding that block to the chain
        self.chain.append(block)
        
        return block

    #Function to return the previous block
    
    def get_previous_block(self):
        
        return self.chain[-1]
    
    #Proof of work is the number or piece or that the miners have to find in
    #order to make a new block
    #it is a number that is hard to find but easy to verify

    def proof_of_work(self, previous_proof):
        
        new_proof = 1
        check_proof = False
        
        # We are using Trial and Error method to find the right POW
        
        while check_proof is False:
            
            # Defining the problems miners need to solve
            # We will use SHA256 to return a 64 char long string
            # And the string will need to start with 4 zeros
            # More the number of leading zeros harder it will be to 
            # Solve the problem
            
            # The operation should be non symetrical
            
            hash_operation = hashlib.sha256(str(new_proof**2 - previous_proof**2).encode()).hexdigest()
            
            if hash_operation[:4] == '0000':
                check_proof = True
            else:
                new_proof += 1
                
        return new_proof
    
    def hash(self, block):
        encoded_block = json.dumps(block, sort_keys = True).encode()
        return hashlib.sha256(encoded_block).hexdigest()
    
    # To check if our blockchain is valid or no
    
    def is_chain_valid(self, chain):
        
        previous_block = chain[0]
        block_index = 1
        
        while block_index < len(chain):
            
            block = chain[block_index]
            
            if block['previous_hash'] != self.hash(previous_block):
                return False
            
            previous_proof = previous_block['proof']
            proof = block['proof']
            hash_operation = hashlib.sha256(str(proof**2 - previous_proof**2).encode()).hexdigest()
            
            if hash_operation[:4] != '0000':
                return False
            
            previous_block = block
            block_index += 1
            
        return True
    
    # To define the format for our blockchain
    def add_transaction(self, sender, receiver, amount):
        
        self.transactions.append({'sender' : sender,
                                  'receiver' : receiver,
                                  'amount': amount})
        
        #returning the index of the block in which these transactions are stored
        previous_block = self.get_previous_block()
        
        return previous_block['index'] + 1
    
    #Creating a function to add node
    def add_node(self, address):
        #address looks somehting like this: http://127.0.0.1:5000/
        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)
        #parsed_url.netloc gives 127.0.0.1:5000
    
    # Consensus system for our blockchain.
    # to replace any chain shorter than the longest chain with longest chain    
    
    def replace_chain(self):
        network = self.nodes
        longest_chain = None
        max_length = len(self.chain)
        
        for nodes in network:
            response = requests.get('http://(node)/get_chain')
            
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']
                
                if length > max_length and self.is_chain_valid(chain):
                    max_length = length
                    longest_chain = chain
                    
        if longest_chain:
            self.chain = longest_chain
            return True
        return False

# ------------------Deploying the blockchain-------------------------------------------------------------------

#-------------------- Creating a Web App
app = Flask(__name__)

# Creating an address for the node on port
# We are creating this address because when a miner mine a block he is rewareded with 
# coins. So coins are sent from the address assigned block to the miner
# We will use uuid4 for generating random unique addresses

node_address = str(uuid4()).replace('-', '')

# Creating a Blockchain
blockchain = Blockchain()

# We then use the route() decorator to tell Flask what URL should trigger our function.
#If GET is present, Flask automatically adds support for the HEAD method and 
#handles HEAD requests according to the HTTP RFC. 

# -------------------- Mining a new block

@app.route('/mine_block', methods = ['GET'])

def mine_block():
    
    # We need to find the previous block
    previous_block = blockchain.get_previous_block()
    
    # We need to find the previous proof
    previous_proof = previous_block['proof']
    
    #The new proof
    proof = blockchain.proof_of_work(previous_proof)
    
    #We have to find the previous hash
    previous_hash = blockchain.hash(previous_block)
    
    #transactions
    blockchain.add_transaction(sender = node_address , receiver = 'Someone', amount = 1)
    
    #Creating the new block
    block = blockchain.create_block(proof, previous_hash)
    
    #Now displaying the content on our user friendly web application
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash'],
                'transactions' : block['transactions']}
    
    # 200 is the an HTTP output if eveything is successful
    return jsonify(response), 200


#------------------Getting the full Blockchain

@app.route('/get_chain', methods = ['GET'])

# Now we are displaying the whole blockchain
def get_chain():
    
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    
    return jsonify(response), 200


#------------------Checking if the Blockchain is valid

@app.route('/is_valid', methods = ['GET'])

def is_valid():
    
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Anushka , we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200

#------------------Adding new transaction to the blockchain

@app.route('/add_transaction', methods = ['POST'])

def add_transaction():
    
    # We will create a json file in post request wehre we will write sender, receiver 
    # and amount
    json = request.get_json()
    transaction_keys = ['sender', 'receiver', 'amount']
    
    # If all the keys in the transaction_keys are not in
    # the json format return an error
    # HTTP code for an erroe is 400
    
    if not all ( key in json for key in transaction_keys):
        return 'Some of the elements are missing', 400
    
    index = blockchain.add_transaction( json['sender'], json['receiver'], json['amount'])
    
    # Creating a response 
    response = {'message' : 'This transaction will be added to the block (index)'}
    
    # To show successful creation HTTP code is 201
    
    return jsonify(response), 201

#------------------Decentralizing our blockchain PART 1

#Connecting new node in our decentralized network

@app.route('/connect_node', methods = ['POST'])

def connect_node():
    json = request.get_json()
    
    # to get address of the node
    nodes = json.get('nodes')
    
    if nodes is None:
        return 'No node', 400
    
    for node in nodes:
        blockchain.add_node(node)
    
    response = {'message' : 'All the nodes are now added to the blockchain. The frootie coin now contains the following nodes',
                'total_nodes' : list(blockchain.nodes)}
    
    return jsonify(response), 201

#------------------Decentralizing our blockchain PART 2

# Replacing the chain by the longest chain if needed 

@app.route('/replace_chain', methods = ['GET'])

def replace_chain():
    is_chain_replaced = blockchain.replace_chain()
    
    if is_chain_replaced:
        response = {'message': 'The nodes had different chains so the chain was replaced by the longest one.',
                    'new_chain': blockchain.chain}
    else:
        response = {'message': 'All good. The chain is the largest one.',
                    'actual_chain': blockchain.chain}
        
    return jsonify(response), 200

#-----------------Running the app----------------------------

app.run(host = '0.0.0.0', port = 5003)

# port 5001 for someone else
# port 5002 for figural
# port 5003 for me
