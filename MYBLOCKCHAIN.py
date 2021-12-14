# Creating our blockchain
import datetime
import hashlib
import json
from flask import Flask, jsonify


# ------------------Building the blockchain-----------------------------------
class Blockchain:
    
    # first we need to create a chain that will hold all our blocks, the
    # blocks are stored in an empty list
    
    
    def __init__(self):
        self.chain = []
        
        # Now we need to create our genesis block which is the first block
        # of our blockchain
        
        self.create_block(proof = 1, previous_hash = '0')

    def create_block(self, proof, previous_hash):
        
        #Our block will be in the form of a dictionary
        # Important elements for a block are : index, time,proof and
        # hash of the pervious block
        
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        
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

# ------------------Building the blockchain-----------------------------------

# Creating a Web App
app = Flask(__name__)

# Creating a Blockchain
blockchain = Blockchain()

# We then use the route() decorator to tell Flask what URL should trigger our function.
#If GET is present, Flask automatically adds support for the HEAD method and 
#handles HEAD requests according to the HTTP RFC. 

# Mining a new block

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
    
    #Creating the new block
    block = blockchain.create_block(proof, previous_hash)
    
    #Now displaying the content on our user friendly web application
    response = {'message': 'Congratulations, you just mined a block!',
                'index': block['index'],
                'timestamp': block['timestamp'],
                'proof': block['proof'],
                'previous_hash': block['previous_hash']}
    
    # 200 is the an HTTP output if eveything is successful
    return jsonify(response), 200

#------------------Getting the full Blockchain------------------


@app.route('/get_chain', methods = ['GET'])

# Now we are displaying the whole blockchain
def get_chain():
    
    response = {'chain': blockchain.chain,
                'length': len(blockchain.chain)}
    
    return jsonify(response), 200

#------------------Checking if the Blockchain is valid---------


@app.route('/is_valid', methods = ['GET'])

def is_valid():
    
    is_valid = blockchain.is_chain_valid(blockchain.chain)
    
    if is_valid:
        response = {'message': 'All good. The Blockchain is valid.'}
    else:
        response = {'message': 'Houston, we have a problem. The Blockchain is not valid.'}
    return jsonify(response), 200

#-----------------Running the app----------------------------
app.run(host = '0.0.0.0', port = 5000)
