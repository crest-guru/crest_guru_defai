// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

import "../../base/BaseACL.sol";
import "./CompoundUtils.sol";    

contract CompoundAuthorizer is BaseACL {
    bytes32 public constant NAME = "CompoundAuthorizer";        
    uint256 public constant VERSION = 1;

    address public immutable cUSDC;
    address public immutable cWETH;
    address public immutable cUSDT;
    address public immutable cwstETH;
    address public immutable cUSDS;
    address public immutable cUSDCe;
    address public immutable cUSDbC;
    address public immutable Bulker;

    constructor (address _owner, address _caller) BaseACL(_owner, _caller){
        (cUSDC, cWETH, cUSDT, cwstETH, cUSDS, cUSDCe, cUSDbC, Bulker) = getCTokenAddress();
    }

    

    function supply(address _cToken, uint256 _amount) external {
        require(_txn().to != address(0), "Invalid target");
    }
    
    function withdraw(address _cToken, uint256 _amount) external {
        require(_txn().to != address(0), "Invalid target");
    }
    
    function allow(address _bulker, bool _isAllowed) external {}

    function invoke(bytes32[] calldata actions, bytes[] calldata data) external {
        for (uint i = 0; i < actions.length; i++) {
            bool res = parseCall(actions[0], data[i]);
        }
    }

    function parseCall(bytes32 action, bytes memory data) public  returns (bool) {
    
        require(data.length >= 4, "Data too short");

        
        

        bytes32 supplyNativeAsset = "ACTION_SUPPLY_NATIVE_TOKEN";
        bytes32 withdrawNativeAsset = "ACTION_WITHDRAW_NATIVE_TOKEN";
        bytes32 claimRewards = "ACTION_CLAIM_REWARD"; 
        

        if (action == supplyNativeAsset) {
            bool result = checkSupplyFunction(data);
            require(result);
        } else if (action == withdrawNativeAsset) {
            bool result = checkWithdrawFunction(data);
            require(result);
        } 
    }

    function checkSupplyFunction(bytes memory data) internal  returns(bool){
        address targetAddress;
        assembly {
            targetAddress := mload(add(data, 64)) 
        }
        require(targetAddress == owner, "Not Owner");
        return true;
    }

    function checkWithdrawFunction(bytes memory data) internal  returns(bool){
        address targetAddress;
        assembly {
            targetAddress := mload(add(data, 64)) 
        }
        require(targetAddress == owner, "Not Owner");
        return true;
    }

    function contracts() public view override returns (address[] memory _contracts) {
        _contracts = new address[](8);
        _contracts[0] = cUSDC;
        _contracts[1] = cWETH;
        _contracts[2] = cUSDT;
        _contracts[3] = cwstETH;
        _contracts[4] = cUSDS;
        _contracts[5] = cUSDCe;
        _contracts[6] = cUSDbC;
        _contracts[7] = Bulker;
    }
    
}
