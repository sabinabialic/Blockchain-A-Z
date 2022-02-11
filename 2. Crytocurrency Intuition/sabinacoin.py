# Module 2 - Create a Cryptocurrency
# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify, request
import requests
from uuid import uuid4
from urllib.parse import urlparse

# Part 1 - Building a Blockchain
class Blockchain:
    def __init__(self):
        # The list containing the blocks
        self.chain = []
        # Seperate list for transactions before they are added to the block
        # Must be created before the genesis block is created
        self.transactions = []
        # Genesis block, the first block of the blockchain
        self.createBlock(proof = 1, prevHash = '0')
        # Nodes in the decentralized network
        # All nodes should have a copy of the same blockchain
        self.nodes = set()

    # Use this function after a block is mined
    def createBlock(self, proof, prevHash):
        # Define each block in the Blockchain with the 4 essential keys: idx of
        # the block, timestamp when it was mined, proof of work, previous hash
        block = {
                    'index' : len(self.chain)+1,
                    'timestamp' : str(datetime.datetime.now()),
                    'proof' : proof,
                    'prevHash' : prevHash,
                    'transactions' : self.transactions
                }
        
        # Transactions list must be emptied since they have been added to the block
        self.transactions = []
        
        # Append the block we just created
        self.chain.append(block)
        return block

    # Returns the last block of the current chain
    def getPrevBlock(self):
        return self.chain[-1]

    # Defines the problem which miners need to solve
    # Returns the nonce, aka the proof of work, expected by createBlock()
    def proofOfWork(self, prevProof):
        # To solve the problem, we will increment newProof by 1 until we get the
        # correct proof... solving the problem using trial and error
        newProof = 1
        # Checks if newProof is the right proof
        checkProof = False

        while checkProof is False:
            # Define the problem that the miners will have to solve
            hashOperation = hashlib.sha256(str(newProof**2 - prevProof**2).encode()).hexdigest()
            # Check if the first 4 chars of hashOperation are all 0 and set
            # checkProof to True
            if hashOperation[:4] == '0000' : checkProof = True
            else : newProof += 1

        # Return the proof of work
        return newProof

    # Encode the block
    def hash(self, block):
        # Sort block dictionary by its keys and encode it
        encodedBlock = json.dumps(block, sort_keys = True).encode()
        # Return the cryptographic hash of our block
        return hashlib.sha256(encodedBlock).hexdigest()

    # Verify that the chain is valid
    def isChainValid(self, chain):
        prevBlock = chain[0]
        blockIndex = 1

        # Iterate through the chain
        while blockIndex < len(chain):
            # Get the current block
            currBlock = chain[blockIndex]
            # Check the prevHash of currBlock is the hash of the prevBlock
            if currBlock['prevHash'] != self.hash(prevBlock): 
                return False

            # Check that the proof of each block is valid
            prevProof = prevBlock['proof']
            currProof = currBlock['proof']
            hashOperation = hashlib.sha256(str(currProof**2 - prevProof**2).encode()).hexdigest()
            # Ensure the hashOperation starts with 4 leading zeroes
            if hashOperation[:4] != '0000': 
                return False

            # Increment counter variables
            prevBlock = currBlock
            blockIndex += 1
            
        return True

    # Create a transaction between a sender and a receiver for a specified amount of sabinacoins
    def addTransaction(self, sender, receiver, amount):
        # Append a new transaction to the list of existing transactions
        self.transactions.append({
                                    'sender' : sender,
                                    'receiver' : receiver,
                                    'amount' : amount
                                })
        prevBlock = self.getPrevBlock()
        # Return the index of the block new block that will recieve this transaction
        return prevBlock['index']+1
    
    # Add a node containing an address to our set of nodes
    def addNode(self, address):
        # Parse the node's address
        parsedUrl = urlparse(address)
        # Add the node to the network; a node in the network is identified by parsedUrl.netloc
        self.nodes.add(parsedUrl.netloc)
    
    # Replaes all the chains in the network with the longest chain
    def replaceChain(self):
        # Network containing all the nodes
        network = self.nodes
        # Stores the longest chain in the network
        longestChain = None
        # Finds the longest chain; initialize to the length of the chain we are currently dealing with
        maxLength = len(self.chain)
        
        # Find the largest chain in the network
        for node in network:
            # Get the length of the current chain by sending a request
            response = requests.get(f'http://{node}/getChain')
            
            if response.status_code == 200:
                # Get the chain and its length from the JSON response
                length = response.json()['length']
                chain = response.json()['chain']
                # Check if the length in the response is larger than the max length,
                # and that its corresponding chain is valid
                if length > maxLength and self.isChainValid(chain):
                    # We found a longest chain... update
                    maxLength = length
                    longestChain = chain
                    
        # If longestChain is not null, that means the chain was replaced
        if longestChain:
            # Replace the chain
            self.chain = longestChain
            return True
        # If longestChain = None, nothing was updated
        return False

# Part 2 - Mining our Blockchain
# Creating a web app with Flask
app = Flask(__name__)
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = False

# Creating a unique address for the node on port 1000 using uuid4
# Note that when a miner mines a new block, they get some sabinacoins thus there is a 
# transaction from the node to the miner which takes place
nodeAddress = str(uuid4()).replace('-', '')

# Creating a blockchain
blockchain = Blockchain()

# Mining a new block
@app.route('/mineBlock', methods=['GET'])

def mineBlock():
    prevBlock = blockchain.getPrevBlock()
    prevProof = prevBlock['proof']
    prevHash = blockchain.hash(prevBlock)
    
    blockchain.addTransaction(sender = nodeAddress, receiver = 'Sabina', amount = 1)

    proof = blockchain.proofOfWork(prevProof)
    block = blockchain.createBlock(proof, prevHash)

    response = {
                    'message' : 'Congratulations, you have successfully mined a block!',
                    'index' : block['index'],
                    'timestamp' : block['timestamp'],
                    'proof' : block['proof'],
                    'prevHash' : block['prevHash'],
                    'transactions' : block['transactions']
                }
    
    return jsonify(response), 200

# Getting the full blockchain
@app.route('/getChain', methods=['GET'])

def getChain():
    response = {'chain' : blockchain.chain,
                'length' : len(blockchain.chain)}
    return jsonify(response), 200

# Check if the blockchain is valid
@app.route('/isChainValid', methods=['GET'])

def isChainValid():
    isChainValid = blockchain.isChainValid(blockchain.chain)
    if isChainValid :
        return jsonify('The blockchain is valid.'), 200
    else :
        return jsonify('The blockchain is invalid.'), 200
    
# Adding a new transaction to the blockchain
@app.route('/addTransaction', methods=['POST'])

def addTransaction():
    # In PostMan we will create a JSON file with the sender, receiver, and the amount of sabinacoins exchanged
    payload = request.get_json()
    # Make sure all the keys are present in the payload
    transactionKeys = ['sender', 'receiver', 'amount']
    
    if not all (key in payload for key in transactionKeys):
        return jsonify('Some elements of the transaction are missing.'), 400 
    
    index = blockchain.addTransaction(payload['sender'], payload['receiver'], payload['amount'])
    response = {'message' : f'This transaction will be added to Block {index}'}
    
    return jsonify(response), 201

# Part 3 - Decentralizing our Blockchain
# Connecting new nodes
@app.route('/connectNode', methods=['POST'])
# Add new node to the JSON file with already existing nodes then POST the file
def connectNode():
    # Get all the nodes in the decentralized network, including the one we are connecting
    payload = request.get_json()
    # Get the addresses of all the nodes in the network in a list format
    nodes = payload.get('nodes')
    
    if nodes is None:
        return jsonify('There are no nodes.'), 400
    
    # Iterate over the nodes and connect them to the network
    for node in nodes:
        blockchain.addNode(node)
        
    response = {
                    'message' : 'All the nodes are connected. The SabinaCoin Blockchain now contains the following nodes: ',
                    'totalNodes' : list(blockchain.nodes)
                }
    
    return jsonify(response), 201

# Replacing the chain by the longest chain, if needed
@app.route('/replaceChain', methods=['GET'])

def replaceChain():
    isReplaced = blockchain.replaceChain()
    if isReplaced :
        response = { 
                        'message' : 'The nodes have different chains. The chain was replaced by the longest one.',
                        'newChain' : blockchain.chain
                    }
    else :
        response = { 
                        'message' :'All good. The chain is the longest and was not replaced.',
                        'newChain' : blockchain.chain
                    }
    return jsonify(response), 200

# Running the app
app.run(host = '0.0.0.0', port = 1000)
