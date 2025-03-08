// SPDX-License-Identifier: LGPL-3.0-only
pragma solidity ^0.8.19;

import "../../base/BaseACL.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

contract ApproveAuthorizerV2 is BaseACL{

    using EnumerableSet for EnumerableSet.AddressSet;

    bytes32 public constant NAME = "ApproveAuthorizerV2";
    uint256 public constant VERSION = 2;

    bytes32 public constant APPROVELISTMANAGER = "ApproveListManager";

    address public  approveListManager;

    EnumerableSet.AddressSet private contractsSet;
    EnumerableSet.AddressSet private spenderSet;

    event ContractAdded(address indexed _address);
    event ContractRemoved(address indexed _address);
    event SpenderAdded(address indexed _address);
    event SpenderRemoved(address indexed _address);
    
    constructor (address _owner, address _caller) BaseACL(_owner, _caller){
        
    }

    modifier onlyDelegateWithRole(){
        require(msg.sender == approveListManager);
        _;
    }

    function setApproveListManager(address _approveListManager) external onlyOwner{
        approveListManager = _approveListManager;
    }

    function replaceApproveListManager(address _newApproveListManager) external onlyOwner{
        approveListManager = _newApproveListManager;
    }

    function addToContracts(address _contract)  external onlyDelegateWithRole  {
        contractsSet.add(_contract);
    }


    function addContracts(address[] calldata _contracts) external onlyDelegateWithRole  {
        for (uint256 i = 0; i < _contracts.length; i++) {
            address _contract = _contracts[i];
            if (contractsSet.add(_contract)) {
                emit ContractAdded(_contract);
            }
        }
    }

    function removeContracts(address[] calldata _contracts) external onlyDelegateWithRole {
        for (uint256 i = 0; i < _contracts.length; i++) {
            address _contract = _contracts[i];
            if (contractsSet.remove(_contract)) {
                emit ContractRemoved(_contract);
            }
        }
    }


    function addSpenders(address[] calldata _contracts) external onlyDelegateWithRole {
        for (uint256 i = 0; i < _contracts.length; i++) {
            address _spender = _contracts[i];
            if (spenderSet.add(_spender)) {
                emit SpenderAdded(_spender);
            }
        }
    }

    function removeSpenders(address[] calldata _contracts) external onlyDelegateWithRole {
        for (uint256 i = 0; i < _contracts.length; i++) {
            address _spender = _contracts[i];
            if (spenderSet.remove(_spender)) {
                emit SpenderRemoved(_spender);
            }
        }
    }


    function removeFromContracts(address _contract) external onlyDelegateWithRole {
        contractsSet.remove(_contract);
    }

    function getContractsSet() external view returns(address[] memory){
        return contractsSet.values();
    }

    function getSpendersSet() external view returns(address[] memory){
        return spenderSet.values();
    }

    function addToSpenders(address _contract) external onlyDelegateWithRole {
        spenderSet.add(_contract);
    }

    function removeFromSpenders(address _contract) external onlyDelegateWithRole {
        spenderSet.remove(_contract);
    }

    function containContract(address _contract) external view returns(address){
        uint256 l = contractsSet.length();
        for (uint i = 0; i < l; i++) {
            if (contractsSet.at(i) == _contract) {
                
                return contractsSet.at(i);
                
            }
        }
    }

    function approve(address spender, uint256 value) external view  {
        require(contractsSet.contains(_txn().to));
        require(spenderSet.contains(spender));   
    }




    function contracts() public view override returns (address[] memory _contracts) {
           return contractsSet.values();
        }


}