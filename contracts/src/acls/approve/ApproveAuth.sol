// SPDX-License-Identifier: LGPL-3.0-only
pragma solidity ^0.8.19;

import "../../base/BaseACL.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

contract ApproveAuthorizer is BaseACL{

    using EnumerableSet for EnumerableSet.AddressSet;

    bytes32 public constant NAME = "ApproveAuthorizer";
    uint256 public constant VERSION = 1;

    EnumerableSet.AddressSet private AdminsSet;
    EnumerableSet.AddressSet private contractsSet;
    EnumerableSet.AddressSet private spenderSet;

    event newAdmin(address newAdmin);

    constructor (address _owner, address _caller) BaseACL(_owner, _caller){}

    modifier onlyAdmin(address _addr) {
       require(AdminsSet.contains(_addr), "not Admin") ;
        _;
    }

        


    function setAdmin(address _address) external onlyOwner{
        AdminsSet.add(_address);
        emit newAdmin(_address);
    }

    function getAdmins() external view returns(address[] memory) {
        return AdminsSet.values();
    }

    function removeAdmin(address _address) external onlyOwner {
        AdminsSet.remove(_address);
    }

    function addToContracts(address _contract) external onlyAdmin(msg.sender) {
        contractsSet.add(_contract);
    }

    function removeFromContracts(address _contract) external onlyAdmin(msg.sender){
        contractsSet.remove(_contract);
    }

    function getContractsSet() external view returns(address[] memory){
        return contractsSet.values();
    }

    function getSpendersSet() external view returns(address[] memory){
        return spenderSet.values();
    }

    function addToSpenders(address _contract) external onlyAdmin(msg.sender) {
        spenderSet.add(_contract);
    }

    function removeFromSpenders(address _contract) external onlyAdmin(msg.sender){
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