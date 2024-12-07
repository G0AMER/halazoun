// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract Migrations {
    address public owner;

    constructor() {
        owner = msg.sender;
    }

    function setCompleted(uint256 completed) public {}
}
