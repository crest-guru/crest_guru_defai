// SPDX-License-Identifier: LGPL-3.0-only
pragma solidity ^0.8.0;

import "forge-std/Script.sol";
import "../src/CoboFactory.sol";
import "../src/helper/ArgusAccountHelper.sol";
import "../src/helper/ArgusViewHelper.sol";
import "../src/CoboSafeAccount.sol";
import "../src/role/FlatRoleManager.sol";
import "../src/auth/ArgusRootAuthorizer.sol";

contract ArgusDeploy is Script {
    function run() public {
        vm.startBroadcast();
        CoboFactory factory = new CoboFactory(tx.origin);
        ArgusAccountHelper accountHelper = new ArgusAccountHelper();
        ArgusViewHelper viewHelper = new ArgusViewHelper();
        CoboSafeAccount coboAccount = new CoboSafeAccount(address(0));
        FlatRoleManager roleManager = new FlatRoleManager(address(0));
        ArgusRootAuthorizer rootAuth = new ArgusRootAuthorizer(address(0), address(0), address(0));

        factory.addImplementation(address(accountHelper));
        factory.addImplementation(address(viewHelper));
        factory.addImplementation(address(coboAccount));
        factory.addImplementation(address(roleManager));
        factory.addImplementation(address(rootAuth));

        vm.stopBroadcast();
    }
}

