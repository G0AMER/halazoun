// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract SnailMarket {
    // Struct to represent a snail
    struct Snail {
        uint256 id;
        string name;
        uint256 price;
        uint256 stock;
    }

    // Event to log transactions
    event Transaction(
        uint256 indexed snailId,
        address indexed buyer,
        uint256 quantity,
        uint256 totalCost,
        uint256 timestamp
    );

    // Owner of the contract
    address public owner;

    // Mapping to store snails by ID
    mapping(uint256 => Snail) public snails;
    uint256 public nextSnailId;

    // Modifier to restrict access to the owner
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner can perform this action");
        _;
    }

    constructor() {
        owner = msg.sender;
    }

    // Function to add a new snail to the inventory
    function addSnail(string memory name, uint256 price, uint256 stock) public onlyOwner {
        snails[nextSnailId] = Snail(nextSnailId, name, price, stock);
        nextSnailId++;
    }

    // Function to update snail stock
    function updateStock(uint256 snailId, uint256 stock) public onlyOwner {
        require(snails[snailId].id == snailId, "Snail does not exist");
        snails[snailId].stock = stock;
    }

    // Function to buy snails
    function buySnails(uint256 snailId, uint256 quantity) public payable {
        require(snails[snailId].id == snailId, "Snail does not exist");
        Snail storage snail = snails[snailId];
        require(quantity > 0, "Quantity must be greater than zero");
        require(quantity <= snail.stock, "Insufficient stock");
        uint256 totalCost = snail.price * quantity;
        require(msg.value == totalCost, "Incorrect ETH sent");

        // Update stock
        snail.stock -= quantity;

        // Emit transaction event
        emit Transaction(snailId, msg.sender, quantity, totalCost, block.timestamp);
    }

    // Function to withdraw funds from the contract
    function withdrawFunds() public onlyOwner {
        payable(owner).transfer(address(this).balance);
    }

    // Get the details of a snail
    function getSnailDetails(uint256 snailId) public view returns (string memory name, uint256 price, uint256 stock) {
        require(snails[snailId].id == snailId, "Snail does not exist");
        Snail storage snail = snails[snailId];
        return (snail.name, snail.price, snail.stock);
    }
}
