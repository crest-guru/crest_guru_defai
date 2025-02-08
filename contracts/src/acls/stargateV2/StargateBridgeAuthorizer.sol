// SPDX-License-Identifier: LGPL-3.0-only
pragma solidity ^0.8.19;

import "../../base/BaseACL.sol";
import "./StargateAddressUtils.sol";

contract StargateBridgeAuthorizer is BaseACL {
    bytes32 public constant NAME = "StargateBridgeAuthorizer";
    uint256 public constant VERSION = 2;

    address public immutable PoolNative;
    address public immutable PoolUSDC;
    address public immutable PoolUSDT;

    constructor(address _owner, address _caller) BaseACL(_owner, _caller) {
        (PoolNative, PoolUSDC, PoolUSDT) = getAddresses();
    }

    function toAddress(bytes32 data) public pure returns (address) {
        
        return address(uint160(uint256(data)));
    }

    struct SendParam {
        uint32 dstEid; // Destination endpoint ID.
        bytes32 to; // Recipient address.
        uint256 amountLD; // Amount to send in local decimals.
        uint256 minAmountLD; // Minimum amount to send in local decimals.
        bytes extraOptions; // Additional options supplied by the caller to be used in the LayerZero message.
        bytes composeMsg; // The composed message for the send() operation.
        bytes oftCmd; // The OFT command to be executed, unused in default OFT implementations.
    }

    struct MessagingFee {
        uint256 nativeFee;
        uint256 lzTokenFee;
    }
    function send(
        SendParam calldata _sendParam,
        MessagingFee calldata _fee,
        address _refundAddress
    ) external view  {
        require(_txn().to == PoolNative || _txn().to == PoolUSDC || _txn().to == PoolUSDT);
        require(_txn().to != address(0));
        require(toAddress(_sendParam.to) == owner);
        require(_refundAddress == owner); 
    } 
    

    

    function contracts() public view override returns (address[] memory _contracts) {
        _contracts = new address[](3);
        _contracts[0] = PoolNative;
        _contracts[1] = PoolUSDC;
        _contracts[2] = PoolUSDT;
    }
}
