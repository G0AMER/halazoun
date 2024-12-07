import json

from flask import Flask, jsonify, request
from flask_cors import CORS
from web3 import Web3

app = Flask(__name__)
CORS(app)

# Connect to local Ethereum node (Ganache)
w3 = Web3(Web3.HTTPProvider('http://127.0.0.1:8545'))
# assert w3.isConnected()

# Load contract ABI and address
with open('build/contracts/SnailMarket.json') as f:
    contract_data = json.load(f)
    abi = contract_data['abi']
    contract_address = contract_data['networks']['5777']['address']

contract = w3.eth.contract(address=contract_address, abi=abi)
owner_address = w3.eth.accounts[0]  # Owner address for transaction signing

print(owner_address)


# Fetch all snails
@app.route('/snails', methods=['GET'])
def get_all_snails():
    try:
        snails = contract.functions.getAllSnails().call()
        snail_details = []
        for i in range(len(snails[0])):
            snail_details.append({
                'id': snails[0][i],
                'name': snails[1][i],
                'price': snails[2][i] * 10e-19,  # from Wei to eth
                'stock': snails[3][i],
            })
        return jsonify(snail_details)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Fetch details of a single snail by id
@app.route('/snail/<int:snail_id>', methods=['GET'])
def get_snail_details(snail_id):
    try:
        snail = contract.functions.getSnailDetails(snail_id).call()
        snail_details = {
            # 'id': snail[0],
            'name': snail[0],
            'price': snail[1] * 10e-19,  # from Wei to eth
            'stock': snail[2],
        }
        return jsonify(snail_details)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Add a new snail to the market
@app.route('/snail', methods=['POST'])
def add_snail():
    try:
        data = request.get_json()
        name = data['name']
        price = data['price']  # price in ETH
        stock = data['stock']

        # Transaction for adding snail
        transaction = contract.functions.addSnail(name, price * 10e19, stock).buildTransaction({
            'from': owner_address,
            'gas': 2000000,
            'gasPrice': 20 * 10e9,
            'nonce': w3.eth.get_transaction_count(owner_address),
        })

        # Sign the transaction
        private_key = '0x50702c8302aecf919bc59c0036a4b507ab205ba9ed4a65aa8be9b04632035c06'  # Replace with private key of the wallet
        signed_txn = w3.eth.account.signTransaction(transaction, private_key)

        # Send transaction
        txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

        return jsonify({'txn_hash': txn_hash.hex(), 'txn_receipt': txn_receipt}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Buy snails
@app.route('/buy', methods=['POST'])
def buy_snails():
    try:
        data = request.get_json()
        print(data)
        snail_id = int(data['snail_id'])
        print(snail_id)
        quantity = int(data['quantity'])
        print(quantity)
        value = int(data['value'])  # Amount of ETH sent
        print((w3.to_wei(value, 'ether')))

        # Transaction for buying snails
        print(w3.eth.get_transaction_count(owner_address))
        transaction = contract.functions.buySnails(snail_id, quantity).buildTransaction({
            'from': owner_address,
            'value': w3.to_wei(value, 'ether'),  # Convert Ether to Wei
            'gas': 2000000,
            'gasPrice': 20 * 10 ** 9,  # Convert Gwei to Wei
            'nonce': w3.eth.get_transaction_count(owner_address),
        })

        print(1)
        # Sign the transaction
        private_key = '0x50702c8302aecf919bc59c0036a4b507ab205ba9ed4a65aa8be9b04632035c06'  # Replace with private key of the wallet
        print(1)
        signed_txn = w3.eth.account.signTransaction(transaction, private_key)
        print(signed_txn)
        # Send transaction
        txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

        return jsonify({'txn_hash': txn_hash.hex(), 'txn_receipt': txn_receipt}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), e


# Get contract balance (ETH sent to the contract)
@app.route('/balance', methods=['GET'])
def get_balance():
    try:
        balance = w3.eth.get_balance(contract.address)
        return jsonify({'balance': balance}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Withdraw contract balance to owner
@app.route('/withdraw', methods=['POST'])
def withdraw_balance():
    try:
        # Transaction for withdrawing balance
        transaction = contract.functions.withdraw().buildTransaction({
            'from': owner_address,
            'gas': 2000000,
            'gasPrice': 20 * 10e9,
            'nonce': w3.eth.get_transaction_count(owner_address),
        })

        # Sign the transaction
        private_key = '0x50702c8302aecf919bc59c0036a4b507ab205ba9ed4a65aa8be9b04632035c06'  # Replace with private key of the wallet
        signed_txn = w3.eth.account.signTransaction(transaction, private_key)

        # Send transaction
        txn_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
        txn_receipt = w3.eth.wait_for_transaction_receipt(txn_hash)

        return jsonify({'txn_hash': txn_hash.hex(), 'txn_receipt': txn_receipt}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
