// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/interfaces/IERC20.sol";

import "./token.sol";

contract Crowdfinding  {

    bool public locked;
    mapping(address => uint256) public contributions;
    address public USDC;
    address public owner;
    uint256 public rate;
    uint256 public amountContributed;
    AIInterface public token;
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Ownable: caller is not the owner");
        _;
    }

    constructor(address _USDC, address _token, uint256 _rate, address _owner) {
        locked = false;
        USDC = _USDC;
        token = AIInterface(_token);
        rate = _rate;
        owner = _owner;
    }
    
    modifier nonReentrancy() {
        require(!locked, "ReentrancyGuard: reentrant call");
        locked = true;
        _;
        locked = false;
    }

    function convertFromUSDC(uint256 amount) public view returns (uint256) {
        uint256 decimalsDiff = 10**12;
        return (amount * rate*decimalsDiff)/10000;
    }
    
    function contribute(uint256 amount) external returns (bool) {
        
        require(IERC20(token).balanceOf(address(this)) > convertFromUSDC(amount), "Insufficient balance");
        uint256 userContribution = contributions[msg.sender];
        require(userContribution < 1501000000, "Max contribution reached");
        (bool success, ) = address(USDC).call(abi.encodeWithSelector(IERC20.transferFrom.selector, msg.sender, address(this), amount));
        require(success, "Transfer failed");

        require(IERC20(USDC).transfer(address(owner), amount), "Transfer failed");
        require(IERC20(token).transfer(address(msg.sender), convertFromUSDC(amount)), "Transfer failed");
        contributions[msg.sender] += amount;
        amountContributed += amount;
        return true;
    }

    function getOwner() public view returns (address) {
        return owner;
    }

    function getAmountContributed() public view returns (uint256) {
        return amountContributed/10**6;
    }

    function withdraw()  external onlyOwner  returns (bool) {
        (bool success, ) = address(token).call(abi.encodeWithSelector(IERC20.transfer.selector, address(owner), IERC20(token).balanceOf(address(this))));
        
        return true;
    }

}
