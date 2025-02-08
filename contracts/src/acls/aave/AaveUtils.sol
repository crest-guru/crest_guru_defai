// SPDX-License-Identifier: LGPL-3.0-only
pragma solidity ^0.8.19;

function getAddresses() view returns (address Pool, address RewardsController, address WTokenGateway) {
    uint256 chainId = block.chainid;
    if (chainId == 1) { //mainnet
        Pool = 0x87870Bca3F3fD6335C3F4ce8392D69350B4fA4E2;
        RewardsController = 0x8164Cc65827dcFe994AB23944CBC90e0aa80bFcb;
        WTokenGateway = 0xA434D495249abE33E031Fe71a969B81f3c07950D;
    } else if (chainId == 10) { //op
        Pool = 0x794a61358D6845594F94dc1DB02A252b5b4814aD;
        RewardsController = 0x929EC64c34a17401F460460D4B9390518E5B473e;
        WTokenGateway = 0x60eE8b61a13c67d0191c851BEC8F0bc850160710;
    } else if (chainId == 42161) { //arb
        Pool = 0x794a61358D6845594F94dc1DB02A252b5b4814aD;
        RewardsController = 0x929EC64c34a17401F460460D4B9390518E5B473e;
        WTokenGateway = 0x5760E34c4003752329bC77790B1De44C2799F8C3;
    } else if (chainId == 1088) { //metis
        Pool = 0x90df02551bB792286e8D4f13E0e357b4Bf1D6a57;
        RewardsController = 0x30C1b8F0490fa0908863d6Cbd2E36400b4310A6B;
        WTokenGateway = address(0);
    } else if (chainId == 8453) { //base
        Pool = 0xA238Dd80C259a72e81d7e4664a9801593F98d1c5;
        RewardsController = 0xf9cc4F0D883F1a1eb2c253bdb46c254Ca51E1F44;
        WTokenGateway = 0x729b3EA8C005AbC58c9150fb57Ec161296F06766;
    } else if (chainId == 137) { //polygon
        Pool = 0x794a61358D6845594F94dc1DB02A252b5b4814aD;
        RewardsController = 0x929EC64c34a17401F460460D4B9390518E5B473e;
        WTokenGateway = 0xF5f61a1ab3488fCB6d86451846bcFa9cdc108eB0;
    } else {
         revert("no chain id is matched");
    }
}
