// SPDX-License-Identifier: LGPL-3.0-only
pragma solidity ^0.8.19;

import "forge-std/Test.sol";
import "forge-std/console.sol";
import "forge-std/Vm.sol";
import "@safe-account/contracts/proxies/SafeProxyFactory.sol";
import "@safe-account/contracts/proxies/SafeProxy.sol";
import "../src/CoboFactory.sol";
import "../src/helper/ArgusAccountHelper.sol";
import "../src/helper/ArgusViewHelper.sol";
import "../src/CoboSafeAccount.sol";
import "../src/role/FlatRoleManager.sol";
import "../src/auth/ArgusRootAuthorizer.sol";
import "../src/acls/shadow/ShadowAuthorizer.sol";
import "../src/Types.sol";


interface ISafe {
    function nonce() external view returns (uint256);
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

    function getThreshold() external view returns (uint256);
    function getOwners() external view returns (address[] memory);
}


contract ShadowAuthorizerTest is Test {
    uint256 SonicFork;
    SafeProxyFactory public safeProxyFactory;
    
    address public coboFactoryOwner = makeAddr("coboFactoryOwner");
    address[] public  owners = new address[](1);
    address public proxy;
    address _singleton = address(0x29fcB43b46531BcA003ddC8FCB67FFE91900C762);

    CoboFactory public factory;
    ArgusAccountHelper public accountHelper;
    ArgusViewHelper public viewHelper;
    CoboSafeAccount public coboAccount;
    FlatRoleManager public roleManager;
    ArgusRootAuthorizer public rootAuthorizer;
    ShadowAuthorizer public shadowAuthorizer;

    address owner;
    uint256 ownerPK;
    function setUp() public {
        SonicFork = vm.createFork("https://rpc.soniclabs.com");
        vm.selectFork(SonicFork);
        (owner, ownerPK) = makeAddrAndKey("owner");
        safeProxyFactory = SafeProxyFactory(address(0x4e1DCf7AD4e460CfD30791CCC4F9c8a4f820ec67));
        
        proxy = createProxy();
        
        factory = new CoboFactory(coboFactoryOwner);
        accountHelper = new ArgusAccountHelper();
        viewHelper = new ArgusViewHelper();
        coboAccount = new CoboSafeAccount(address(0));
        roleManager = new FlatRoleManager(address(0));
        rootAuthorizer = new ArgusRootAuthorizer(address(0), address(0), address(0));
        shadowAuthorizer = new ShadowAuthorizer(address(0), address(0));
        
        vm.startPrank(coboFactoryOwner);
        factory.addImplementation(address(accountHelper));
        factory.addImplementation(address(viewHelper));
        factory.addImplementation(address(coboAccount));
        factory.addImplementation(address(roleManager));
        factory.addImplementation(address(rootAuthorizer));
        factory.addImplementation(address(shadowAuthorizer));
        vm.stopPrank();
        
        
        coboAccount = initCoboAccount();
        console.log("coboAccount", address(coboAccount));

        setupShadowAuthorizer();
        
    }

    function createProxy() public returns (address) {

        vm.startPrank(owner);

        owners[0] = owner;
        bytes memory initData = abi.encodeWithSignature(
            "setup(address[],uint256,address,bytes,address,address,uint256,address)",
            owners,
            1,
            address(0),
            bytes(""),
            address(0),
            address(0),
            0,
            address(0)
            );

        
        proxy = address(safeProxyFactory.createProxyWithNonce(_singleton, initData, 0));


        vm.stopPrank();

        return proxy;
    }

    function initCoboAccount() public returns (CoboSafeAccount) {

        vm.startPrank(owner);
        bytes memory initData = abi.encodeWithSignature(
            "initArgus(address,bytes32)",
            address(factory),
            bytes32(0)
        );

        safeExecute(address(accountHelper), initData);
        address[] memory coboAddress = factory.getAllRecord(address(proxy), "CoboSafeAccount");
         
        return CoboSafeAccount(payable(coboAddress[0]));
        vm.stopPrank();


    }

    function setupShadowAuthorizer() public {
        vm.startPrank(owner);
        address roleManager = coboAccount.roleManager();
        address authorizer = coboAccount.authorizer();
        bytes32 role = bytes32("ShadowAuthorizer");
        bytes32[] memory roleArray = new bytes32[](1);
        

        vm.recordLogs();
        bytes memory txCreateAuthorizer = abi.encodeWithSignature(
            "createAuthorizer(address,address,bytes32,bytes32)",
            address(factory),
            address(coboAccount),
            bytes32("ShadowAuthorizer"),
            bytes32(block.timestamp)
        );

        safeExecute(address(accountHelper), txCreateAuthorizer);
        

        Vm.Log[] memory entries = vm.getRecordedLogs();
        
        address proxyAddress;
        bytes32 PROXY_CREATED_SIGNATURE = 0x532cf4635ae9ff4e1e42ba14917e825d00f602f28297cc654fa3b414b911232b;

        for (uint i = 0; i < entries.length; i++) {
            if (entries[i].topics[0] == PROXY_CREATED_SIGNATURE) {
                // Адрес прокси находится в data
                proxyAddress = address(uint160(uint256(bytes32(entries[i].data))));
                console.log("Found proxy address:", proxyAddress);
                break;
            }
        }

        console.log("proxyAddress", proxyAddress);
        
        
        shadowAuthorizer = ShadowAuthorizer(payable(proxyAddress));

        
        roleArray[0] = "ShadowAuthorizer";

        console.log("coboOwner", coboAccount.owner());
        
        bytes memory txAddRolesData = abi.encodeWithSignature("addRoles(bytes32[])", roleArray);
        safeExecuteNoDelegate(address(roleManager), txAddRolesData);

        bytes memory txAddAuthData = abi.encodeWithSignature("addAuthorizer(address,address,bool,bytes32[])",
            address(coboAccount), 
            address(shadowAuthorizer), 
            false, 
            roleArray
        );
        safeExecute(address(accountHelper), txAddAuthData);

        bytes memory txGrantRolesData = abi.encodeWithSignature("grantRoles(address,bytes32[],address[])", 
            address(coboAccount), 
            roleArray, 
            owners
        );
        safeExecute(address(accountHelper), txGrantRolesData);
        

        // bytes memory txAddRolesData = abi.encodeWithSignature("addRoles(bytes32[])", roleArray);
        // bytes memory txAddRoles = abi.encodePacked(
        //     uint8(0),
        //     address(roleManager),
        //     uint256(0),
        //     uint256(txAddRolesData.length),
        //     txAddRolesData
        // );
        // bytes memory txAddAuthData = abi.encodeWithSignature("addAuthorizer(address,address,bool,bytes32[])",
        //     address(coboAccount), 
        //     address(shadowAuthorizer), 
        //     false, 
        //     roleArray
        // );
        // bytes memory txAddAuth = abi.encodePacked(
        //     uint8(1),
        //     address(authorizer),
        //     uint256(0),
        //     uint256(txAddAuthData.length),
        //     txAddAuthData
        // );
        // bytes memory txGrantRolesData = abi.encodeWithSignature("grantRoles(address,bytes32[],address[])", 
        //     address(coboAccount), 
        //     roleArray, 
        //     owners
        // );
        // bytes memory txGrantRoles = abi.encodePacked(
        //     uint8(1),
        //     address(accountHelper),
        //     uint256(0),
        //     uint256(txGrantRolesData.length),
        //     txGrantRolesData
        // );

        // bytes memory txData = bytes.concat(txAddRoles, txAddAuth, txGrantRoles);
        // bytes memory multisendData = abi.encodeWithSignature("multisend(bytes)", txData);

        // safeExecute(address(0x38869bf66a61cF6bDB996A6aE40D5853Fd43B526), multisendData);
        vm.stopPrank();
    }

    function safeExecute(address to, bytes memory data) public {
        bytes32 txHash = ISafe(proxy).getTransactionHash(
            to,
            0,
            data,
            1,
            0,
            0,
            0,
            address(0),
            payable(address(0)),
            ISafe(proxy).nonce()
        );
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(ownerPK, txHash);
        bytes memory signature = abi.encodePacked(r, s, v);
        
        ISafe(proxy).execTransaction(
            to,
            0,
            data,
            1,
            0,
            0,
            0,
            address(0),
            payable(address(0)),
            signature
        );
    }

    function safeExecuteNoDelegate(address to, bytes memory data) public {
        bytes32 txHash = ISafe(proxy).getTransactionHash(
            to,
            0,
            data,
            0,
            0,
            0,
            0,
            address(0),
            payable(address(0)),
            ISafe(proxy).nonce()
        );
        (uint8 v, bytes32 r, bytes32 s) = vm.sign(ownerPK, txHash);
        bytes memory signature = abi.encodePacked(r, s, v);
        
        ISafe(proxy).execTransaction(
            to,
            0,
            data,
            0,
            0,
            0,
            0,
            address(0),
            payable(address(0)),
            signature
        );
    }
    
    function test_A_setup() public {
        require(proxy != address(0), "Proxy not created");
        console.log("address(proxy)", address(proxy));
    }

    
    function test_B_setupCoboAccount() public {
        console.log("threshold", ISafe(proxy).getThreshold());
        address[] memory coboAddress = factory.getAllRecord(address(proxy), "CoboSafeAccount");
        
    }

    function makeTx(
        address from,
        address to,
        uint256 value,
        bytes memory data
    ) public pure returns (TransactionData memory transaction) {
        transaction.from = from;
        transaction.to = to;
        transaction.value = value;
        transaction.data = data;
    }

    function test_C_ShadowAuthorizer() public {
        
        vm.startPrank(coboAccount.authorizer());
        vm.deal(address(owner), 1000000 ether);
        vm.deal(address(proxy), 1000000 ether);

        

        // address(0x92643Dc4F75C374b689774160CDea09A0704a9c2).call(abi.encodeWithSignature(
        //     "execute(bytes,bytes[],uint256)", 
        //     commands, 
        //     inputs,
        //     block.timestamp + 100000));

         // Подготовка данных для свапа
        bytes memory commands = hex"0b00";
        bytes[] memory inputs = new bytes[](2);
        inputs[0] = abi.encode(
            address(coboAccount.owner()),  // recipient
            1 ether,       // amountIn
            0,       // amountOutMin
            abi.encode(    // path data
                hex"039e2fb66102314ce7b64ce5ce3e5183bc94ad380000323333b97138d4b086720b5ae8a7844b1345a33333"
            ),
            true          // payerIsUser
        );
        inputs[1] = hex"00000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000de0b6b3a7640000000000000000000000000000000000000000000000000000001d17038593b07100000000000000000000000000000000000000000000000000000000000000a00000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000002b039e2fb66102314ce7b64ce5ce3e5183bc94ad380000323333b97138d4b086720b5ae8a7844b1345a33333000000000000000000000000000000000000000000";


        (address recipient, uint256 amountIn,,, bool payerIsUser) = abi.decode(inputs[0], (address, uint256, uint256, bytes, bool));
        console.log("Decoded recipient:", recipient); 

        bytes memory execData = abi.encodeWithSignature(
            "execute(bytes,bytes[],uint256)",
            commands,
            inputs,
            block.timestamp + 100000
        );

        // (bool success, bytes memory result) = address(shadowAuthorizer).call(
        // abi.encodeWithSignature(
        //     "preExecCheck((address,address,uint256,address,uint256,bytes,bytes,bytes))",
        //     proxy,      // from
        //     owner,      // delegate
        //     1,         // flag
        //     address(0x92643Dc4F75C374b689774160CDea09A0704a9c2), // to
        //     1 ether,         // value
        //     execData,  // data
        //     "",        // hint
        //     ""         // extra
        //     )
        // );

        //TransactionData memory txPreExec = makeTx(proxy, address(0x92643Dc4F75C374b689774160CDea09A0704a9c2), 1 ether, execData);
        
        TransactionData memory txPreExec = TransactionData({
                from: proxy,      // от кого идет транзакция
                delegate: owner,  // кто делегирует (owner имеет роль)
                flag: 1,         // обычный call
                to: address(0x92643Dc4F75C374b689774160CDea09A0704a9c2),
                value: 1 ether,
                data: execData,
                hint: "",
                extra: ""
            });

        // Проверяем результат
        AuthorizerReturnData memory authData = shadowAuthorizer.preExecCheck(txPreExec);
        

        vm.stopPrank();
    }



}