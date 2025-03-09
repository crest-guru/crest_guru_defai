// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "forge-std/Test.sol";
import "forge-std/console.sol";
import "../src/token/Crowdfinding.sol";
import "../src/token/token.sol";
import "lib/openzeppelin-contracts/contracts/proxy/ERC1967/ERC1967Proxy.sol";
contract CrowdfindingTest is Test {
    Crowdfinding public crowdfinding;
    uint256 SonicFork;
    address USDC = 0x29219dd400f2Bf60E5a23d13Be72B486D4038894;
    address owner = 0xDd006633A161deb07661B7e73eCf1fe3DdE3B1ff;
    AIInterface public token;
    ERC1967Proxy public proxy;
    address Alice = makeAddr("Alice");
    address Bob = makeAddr("Bob");

    function setUp() public {
        SonicFork = vm.createFork("https://rpc.soniclabs.com");
        vm.selectFork(SonicFork);
        
        token = new AIInterface();
        proxy = new ERC1967Proxy(address(token), "");
        AIInterface(address(proxy)).initialize(address(Alice), address(Alice), address(Alice), address(Alice));

        console.log("token balance of owner", IERC20(address(proxy)).balanceOf(address(Alice)));

        vm.startPrank(address(Alice));
        address(proxy).call(abi.encodeWithSignature("transfer(address,uint256)", address(crowdfinding), 20000000*10**18));
        vm.stopPrank();

        crowdfinding = new Crowdfinding(USDC, address(proxy), 6666667, owner);


        vm.startPrank(address(Alice));
        address(proxy).call(abi.encodeWithSignature("transfer(address,uint256)", address(crowdfinding), 20000000*10**18));
        vm.stopPrank();

        vm.startPrank(address(0x322e1d5384aa4ED66AeCa770B95686271de61dc3));
        USDC.call(abi.encodeWithSignature("transfer(address,uint256)", address(Bob), 10000*10**6));
    }

    function test_A_convertFromUSDC() public {
        uint256 amount = 150000000;
        uint256 result = crowdfinding.convertFromUSDC(amount);
        console.log("result", result);
    }


    function test_B_contribute() public {
        console.log("block number", block.number);
        vm.startPrank(address(Bob));
        uint256 amount = 1400*10**6;
        address(USDC).call(abi.encodeWithSignature("approve(address,uint256)", address(crowdfinding), 100000000000000000000000000));
        crowdfinding.contribute(amount);

        console.log("balance USDC of owner", IERC20(USDC).balanceOf(address(owner))/10**6);
        console.log("balance token of User", IERC20(address(proxy)).balanceOf(address(Bob))/10**18);
    }

    
    function test_C_SecondContribution() public {
        vm.startPrank(address(Bob));
        uint256 amount = 150*10**6;
        address(USDC).call(abi.encodeWithSignature("approve(address,uint256)", address(crowdfinding), 100000000000000000000000000));
        bool success = crowdfinding.contribute(amount);
        assertTrue(success, "Contribution should fail");
    }

    function test_D_withdraw() public {
        vm.startPrank(address(owner));
        crowdfinding.withdraw();

        
    }

    function test_E_withdrawNonOwner() public {
        vm.startPrank(address(Bob));
        bool success = crowdfinding.withdraw();
        

    }

}