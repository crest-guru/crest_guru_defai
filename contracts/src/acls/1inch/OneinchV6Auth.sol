// SPDX-License-Identifier: LGPL-3.0-only
pragma solidity ^0.8.19;

import "../../base/BaseACL.sol";


contract OneinchV6Auth is BaseACL{

    bytes32 public constant NAME = "OneinchV6Auth";
    uint256 public constant VERSION = 1;
    address public constant V6AGGREGATOR = 0x111111125421cA6dc452d289314280a0f8842A65;


    constructor (address _owner, address _caller) BaseACL(_owner, _caller) {
        
    }

    struct SwapDescription {
        address srcToken;
        address dstToken;
        address srcReceiver;
        address dstReceiver;
        uint256 amount;
        uint256 minReturnAmount;
        uint256 flags;
    }

    function swap(address,
     SwapDescription calldata desc,
     bytes calldata
     ) external view onlyContract(V6AGGREGATOR){
        require(desc.dstReceiver == owner);
    }

    function unoswap(uint256, uint256, uint256, uint256) external view onlyContract(V6AGGREGATOR) {} 
    function unoswap2(uint256,uint256, uint256, uint256, uint256) external view onlyContract(V6AGGREGATOR) {} 
    function uniswap3(uint256,uint256, uint256, uint256, uint256, uint256) external view  onlyContract(V6AGGREGATOR) {} 



    function contracts() public view override returns (address[] memory _contracts) {
        _contracts = new address[](1);
        _contracts[0] = V6AGGREGATOR;

    }


}