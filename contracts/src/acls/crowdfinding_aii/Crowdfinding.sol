// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "../../base/BaseACL.sol";

contract Crowdfinding is BaseACL {

    bytes32 public constant NAME = "CrowdfindingAuthorizer";
    uint256 public constant VERSION = 1;

    address public constant CROWDFINDING_ADDRESS = 0x9303a680bA1A2924Bb6EeE5A7eD804df2E1824f7;

    constructor(address _owner,  address _caller) BaseACL(_owner, _caller) {
    }

    function contribute(uint256 _amount) external view onlyContract(CROWDFINDING_ADDRESS) {
        //pass (in this function we don't need check anything)
    }

    function contracts() public view override returns (address[] memory) {
        address[] memory contracts = new address[](1);
        contracts[0] = CROWDFINDING_ADDRESS;
        return contracts;
    }

}