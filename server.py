require('dotenv').config();
const express = require('express');
const Web3 = require('web3');
const bodyParser = require('body-parser');
const fs = require('fs');

// Setup Express
const app = express();
const port =  3000;
app.use(bodyParser.json());

// Initialize Web3
const web3 = new Web3(new Web3.providers.HttpProvider(process.env.RPC_URL));

// Load contract ABI and address
const contractABI = JSON.parse(fs.readFileSync('./abi/SnailMarket.json', 'utf8')).abi;
const contractAddress = process.env.CONTRACT_ADDRESS;
const contract = new web3.eth.Contract(contractABI, contractAddress);

// Get all snails
app.get('/api/snails', async (req, res) => {
    try {
        const snails = await contract.methods.getAllSnails().call();
        res.json({
            ids: snails[0],
            names: snails[1],
            prices: snails[2].map(price => web3.utils.fromWei(price, 'ether')),
            stocks: snails[3]
        });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Buy snail
app.post('/api/buy', async (req, res) => {
    const { snailId, quantity, buyerAddress } = req.body;
    const privateKey = process.env.PRIVATE_KEY;

    try {
        // Prepare transaction
        const price = await contract.methods.snailPrice(snailId).call();
        const totalPrice = web3.utils.toWei((web3.utils.fromWei(price, 'ether') * quantity).toString(), 'ether');

        const transaction = contract.methods.buySnails(snailId, quantity);
        const gas = await transaction.estimateGas({ from: buyerAddress, value: totalPrice });

        // Sign and send the transaction
        const signedTx = await web3.eth.accounts.signTransaction(
            {
                to: contractAddress,
                data: transaction.encodeABI(),
                gas,
                value: totalPrice,
            },
            privateKey
        );

        const receipt = await web3.eth.sendSignedTransaction(signedTx.rawTransaction);
        res.json({ transactionHash: receipt.transactionHash });
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

// Start the server
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
