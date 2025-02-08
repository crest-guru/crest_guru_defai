// SPDX-License-Identifier: LGPL-3.0-only
pragma solidity ^0.8.19;

import "../../base/BaseACL.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";
import "./AaveUtils.sol";

contract AaveAuthorizer is BaseACL {

    bytes32 public constant NAME = "AaveAuthorizer";
    uint256 public constant VERSION = 1;

    address public immutable Pool;
    address public immutable RewardsController;
    address public immutable WTokenGateway;


    constructor (address _owner, address _caller) BaseACL(_owner, _caller){
        (Pool, RewardsController, WTokenGateway) = getAddresses();
    }


    function _checkOwner(address _addr) internal  {
        require(owner == _addr, "AaveAuthorizer: Only owner can call this function");
    }

    function supply(bytes32 args) external {}
    function withdraw(bytes32 args) external {}
    function borrow(bytes32 args) external {}
    function repay(bytes32 args) external {}

    function supply(
        address asset,
        uint256 amount,
        address onBehalfOf,
        uint16 referralCode
        )  external {
            _checkOwner(onBehalfOf);
    }

    function withdraw(
        address asset, 
        uint256 amount, 
        address to
        ) external {
            _checkOwner(to);
    }

    function borrow(
        address asset,
        uint256 amount,
        uint256 interestRateMode,
        uint16 referralCode,
        address onBehalfOf
        ) external  {
            _checkOwner(onBehalfOf);
    }

    function repay(
        address asset,
        uint256 amount,
        uint256 interestRateMode,
        address onBehalfOf
        ) external {
            _checkOwner(onBehalfOf);
    }

    function claimRewards(
        address[] calldata assets,
        uint256 amount,
        address to,
        address reward
        ) external{
        _checkOwner(to);
    }

    function claimAllRewards(
        address[] calldata assets,
        address to
        ) external  {
            _checkOwner(to);
    }

    function depositETH(
        address,
        address onBehalfOf,
        uint16 referralCode
    ) external payable {
        _checkOwner(onBehalfOf);
    }  

    function withdrawETH(
        address,
        uint256 amount,
        address to
    ) external {
        _checkOwner(to);
    }

    function repayETH(
        address,
        uint256 amount,
        uint256 rateMode,
        address onBehalfOf
    ) external payable {
        _checkOwner(onBehalfOf);
    }

    function borrowETH(
        address,
        uint256 amount,
        uint256 interestRateMode,
        uint16 referralCode
    ) external {}

    function contracts() public view override returns (address[] memory _contracts) {
        _contracts = new address[](3);
        _contracts[0] = Pool;
        _contracts[1] = RewardsController;
        _contracts[2] = WTokenGateway;
        }


}