// SPDX-License-Identifier: MIT
pragma solidity ^0.5.16;
pragma experimental ABIEncoderV2;
contract SnailMarket {
    struct Snail {
        uint256 id;
        string name;
        uint256 price; // Price in wei
        uint256 stock;
    }

    event SnailAdded(uint256 indexed id, string name, uint256 price, uint256 stock);
    event StockUpdated(uint256 indexed id, uint256 oldStock, uint256 newStock);
    event Transaction(
        uint256 indexed snailId,
        address indexed buyer,
        uint256 quantity,
        uint256 totalCost,
        uint256 timestamp
    );

    address payable public owner;
    mapping(uint256 => Snail) private snails;
    uint256 public nextSnailId;

    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }

    constructor() public{
        owner = msg.sender;
    }

    // Add a new type of snail
    function addSnail(string memory name, uint256 price, uint256 stock) public onlyOwner {
        require(bytes(name).length > 0, "Snail name cannot be empty");
        require(price > 0, "Price must be greater than zero");
        require(stock > 0, "Stock must be greater than zero");

        snails[nextSnailId] = Snail(nextSnailId, name, price, stock);
        emit SnailAdded(nextSnailId, name, price, stock);
        nextSnailId++;
    }

    // Update stock for a specific snail
    function updateStock(uint256 snailId, uint256 stock) public onlyOwner {
        Snail storage snail = snails[snailId];
        require(snail.id == snailId, "Snail does not exist");
        require(stock >= 0, "Stock cannot be negative");

        emit StockUpdated(snailId, snail.stock, stock);
        snail.stock = stock;
    }

    // Buy snails with automatic cost validation
    function buySnails(uint256 snailId, uint256 quantity) public payable {
        require(quantity > 0, "Quantity must be greater than zero");

        Snail storage snail = snails[snailId];
        require(snail.id == snailId, "Snail does not exist");
        require(quantity <= snail.stock, "Insufficient stock");

        uint256 totalCost = snail.price * quantity;
        require(msg.value == totalCost, "Incorrect ETH sent");

        snail.stock -= quantity;

        emit Transaction(snailId, msg.sender, quantity, totalCost, block.timestamp);
    }

    // Withdraw funds collected from sales
    function withdrawFunds() public onlyOwner {
        uint256 balance = address(this).balance;
        require(balance > 0, "No funds to withdraw");
        owner.transfer(balance); // Safe to use in Solidity 0.5.16
    }



    // Get details of a specific snail
    function getSnailDetails(uint256 snailId)
    public
    view
    returns (string memory name, uint256 price, uint256 stock)
    {
        Snail storage snail = snails[snailId];
        require(snail.id == snailId, "Snail does not exist");
        return (snail.name, snail.price, snail.stock);
    }

    // Get all snails as an array
    function getAllSnails()
    public
    view
    returns (uint256[] memory ids, string[] memory names, uint256[] memory prices, uint256[] memory stocks)
    {
        ids = new uint256[](nextSnailId);
        names = new string[](nextSnailId);
        prices = new uint256[](nextSnailId);
        stocks = new uint256[](nextSnailId);

        for (uint256 i = 0; i < nextSnailId; i++) {
            Snail storage snail = snails[i];
            ids[i] = snail.id;
            names[i] = snail.name;
            prices[i] = snail.price;
            stocks[i] = snail.stock;
        }

        return (ids, names, prices, stocks);
    }
}
