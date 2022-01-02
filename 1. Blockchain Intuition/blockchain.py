# Module 1 - Create a Blockchain


# Importing the libraries
import datetime
import hashlib
import json
from flask import Flask, jsonify

# Part 1 - Building a Blockchain
class Blockchain:
    def __init__(self):
        # The list containing the blocks
        self.chain = []
        # Genesis block, the first block of the blockchain
        self.createBlock(proof = 1, prevHash = '0')

    # Use this function after a block is mined
    def createBlock(self, proof, prevHash):
        # Define each block in the Blockchain with the 4 essential keys: idx of
        # the block, timestamp when it was mined, proof of work, previous hash
        block = {
                    'index' : len(self.chain)+1,
                    'timestamp' : str(datetime.datetime.now()),
                    'proof' : proof,
                    'prevHash' : prevHash
                }
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
            if block['prevHash'] != self.hash(prevBlock) : return False

            # Check that the proof of each block is valid
            prevProof = prevBlock['proof']
            currProof = currBlock['proof']
            hashOperation = hashlib.sha256(str(currProof**2 - prevProof**2).encode()).hexdigest()
            # Ensure the hashOperation starts with 4 leading zeroes
            if hashOperation[:4] != '0000' : return = False

            prevBlock = currBlock
            blockIndex += 1

        return True

# Part 2 - Mining our Blockchain
