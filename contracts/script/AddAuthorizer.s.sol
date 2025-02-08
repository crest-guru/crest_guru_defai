// SPDX-License-Identifier: LGPL-3.0-only
pragma solidity ^0.8.0;

import "forge-std/Script.sol";
import "../src/acls/silo/SiloAuthorizer.sol";


interface ISafe {
    function execTransaction(
        address to, 
        uint256 value, 
        bytes memory data, 
        uint8 operattion, 
        uint256 safeTxGas, 
        uint256 baseGas, 
        uint256 gasPrice, 
        address gasToken, 
        address refundReciver, 
        bytes memory signature) external;

    function getTransactionHash(
        address to, 
        uint256 value, 
        bytes memory data, 
        uint8 operattion, 
        uint256 safeTxGas, 
        uint256 baseGas, 
        uint256 gasPrice, 
        address gasToken, 
        address refundReciver, 
        uint256 nonce
    ) external returns(bytes32);

    function nonce() external returns(uint256);
    function getOwners() external returns(address[] memory);

}

interface ICoboAccount {
    function roleManager() external returns(address);
    function authorizer() external returns(address);
    function execTransaction(CallData calldata callData) external returns (TransactionResult memory result);
    function owner() external returns(address);
    
}

interface ICoboRoleManager{
    function addRoles(bytes32 _role) external;
}

contract AddAuthorizer is Script {
    function run() public {
        vm.startBroadcast();

        ISafe safe = ISafe(0x721c2190ac69741416C368fb83AAEBe66bc51364);
        ICoboAccount account = ICoboAccount(0xDb6E329005b80684Df43E89bF5c3710D3c2C44c5);
        ICoboRoleManager roleManager = ICoboRoleManager(account.roleManager());
        address authorizer = account.authorizer();
        address[] memory owners = safe.getOwners();
        address accountHelper = 0xBBb7412f5dAc3Ed358C42E34b51BA2256fb3EB17;
        SiloAuthorizer siloAuthorizer = SiloAuthorizer(0xCeF16d1749b245c805f04b66CC04Bd17AdecC2BB);

        bytes32 rolesBytes = stringToBytes32("SiloAuthorizer");
        bytes32[] memory rolesData = new bytes32[](1);
        rolesData[0] = rolesBytes;

        

        
        bytes memory tx1Data = abi.encodeWithSignature("addRoles(bytes32[])", rolesData);
        bytes memory tx1 = abi.encodePacked(
            uint8(0),                  
            address(roleManager), 
            uint256(0),                
            uint256(tx1Data.length),   
            tx1Data                    
        );

        
        bytes memory tx2Data = abi.encodeWithSignature("addAuthorizer(address,address,bool,bytes32[])", address(account), address(siloAuthorizer), false, rolesData);
        bytes memory tx2 = abi.encodePacked(
            uint8(1),                  
            address(accountHelper), 
            uint256(0),                
            uint256(tx2Data.length),   
            tx2Data                    
        );

        bytes memory tx3Data = abi.encodeWithSignature("grantRoles(address,bytes32[],address[])", address(account),rolesData,owners);
        bytes memory tx3 = abi.encodePacked(
            uint8(1),                  
            address(accountHelper), 
            uint256(0),                
            uint256(tx3Data.length),   
            tx3Data                    
        );
        

        bytes memory multiSendData = bytes.concat(tx1, tx2, tx3);
        bytes memory multiTXSendData = abi.encodeWithSignature(
            "multiSend(bytes)",
            multiSendData

        );


        bytes32 txHashMulti = safe.getTransactionHash(
            address(0x38869bf66a61cF6bDB996A6aE40D5853Fd43B526),
            0,
            multiTXSendData,
            1,
            0,
            0,
            0,
            address(0),
            payable(address(0)),
            safe.nonce()
        );

        
        (uint8 v1, bytes32 r1, bytes32 s1) = vm.sign(txHashMulti);
        bytes memory signatureMulti = abi.encodePacked(r1, s1, v1);

        
        safe.execTransaction(
            address(0x38869bf66a61cF6bDB996A6aE40D5853Fd43B526),
            0,
            multiTXSendData,
            1,
            0,
            0,
            0,
            address(0),
            payable(address(0)),
            signatureMulti  
        );

        


        vm.stopBroadcast();
    }

     function stringToBytes32(string memory source) public pure returns (bytes32 result) {
        bytes memory tempBytes = bytes(source);
        if (tempBytes.length == 0) {
            return 0x0;
        }

        if (tempBytes.length > 32) {
            revert("String too long, must be less than or equal to 32 bytes.");
        }

        assembly {
            result := mload(add(tempBytes, 32))
        }
        return result;
    }

}
