// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

function getCTokenAddress() view returns (address cUSDC, address cWETH, address cUSDT, address cwstETH, address cUSDS, address cUSDCe, address cUSDbC, address Bulker) {

    uint256 chainId = block.chainid;
    if (chainId == 1) {
        cUSDC = address(0x5D409e56D886231aDAf00c8775665AD0f9897b56);
        cWETH = address(0xA17581A9E3356d9A858b789D68B4d866e593aE94);
        cUSDT = address(0x3Afdc9BCA9213A35503b077a6072F3D0d5AB0840);
        cwstETH = address(0x3D0bb1ccaB520A66e607822fC55BC921738fAFE3);
        cUSDS = address(0x5D409e56D886231aDAf00c8775665AD0f9897b56);
        cUSDCe = address(0);
        cUSDbC = address(0);
        Bulker = address(0x74a81F84268744a40FEBc48f8b812a1f188D80C3);
    } else if (chainId == 137) {
        cUSDC = address(0xF25212E676D1F7F89Cd72fFEe66158f541246445);
        cWETH = address(0);
        cUSDT = address(0xaeB318360f27748Acb200CE616E389A6C9409a07);
        cwstETH = address(0);
        cUSDS = address(0);
        cUSDCe = address(0);
        cUSDbC = address(0);
        Bulker = address(0x59e242D352ae13166B4987aE5c990C232f7f7CD6);
    } else if (chainId == 42161) {
        cUSDC = address(0x9c4ec768c28520B50860ea7a15bd7213a9fF58bf);
        cWETH = address(0x6f7D514bbD4aFf3BcD1140B7344b32f063dEe486);
        cUSDT = address(0xd98Be00b5D27fc98112BdE293e487f8D4cA57d07);
        cwstETH = address(0);
        cUSDS = address(0);
        cUSDCe = address(0xA5EDBDD9646f8dFF606d7448e414884C7d905dCA);
        cUSDbC = address(0);
        Bulker = address(0xbdE8F31D2DdDA895264e27DD990faB3DC87b372d);
    } else if (chainId == 8453) {
        cUSDC = address(0xb125E6687d4313864e53df431d5425969c15Eb2F);
        cWETH = address(0x46e6b214b524310239732D51387075E0e70970bf);
        cUSDT = address(0);
        cwstETH = address(0);
        cUSDS = address(0);
        cUSDCe = address(0);
        cUSDbC = address(0x9c4ec768c28520B50860ea7a15bd7213a9fF58bf);
        Bulker = address(0x78D0677032A35c63D142a48A2037048871212a8C);
    } else if (chainId == 10) {
        cUSDC = address(0x2e44e174f7D53F0212823acC11C01A11d58c5bCB);
        cWETH = address(0xE36A30D249f7761327fd973001A32010b521b6Fd);
        cUSDT = address(0x995E394b8B2437aC8Ce61Ee0bC610D617962B214);
        cwstETH = address(0);
        cUSDS = address(0);
        cUSDCe = address(0);
        cUSDbC = address(0);
        Bulker = address(0xcb3643CC8294B23171272845473dEc49739d4Ba3);
    } else {
        revert("Unsupported chainId");
    }
}   