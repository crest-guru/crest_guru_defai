// SPDX-License-Identifier: LGPL-3.0-only
pragma solidity ^0.8.19;

function getAddresses() view returns (address PoolNative, address PoolUSDC, address PoolUSDT) {
    uint256 chainId = block.chainid;
    if (chainId == 1) {
        PoolNative = 0x77b2043768d28E9C9aB44E1aBfC95944bcE57931;
        PoolUSDC = 0xc026395860Db2d07ee33e05fE50ed7bD583189C7;
        PoolUSDT = 0x933597a323Eb81cAe705C5bC29985172fd5A3973;
    } else if (chainId == 43114) {
        PoolNative = address(0);
        PoolUSDC = 0x5634c4a5FEd09819E3c46D86A965Dd9447d86e47;
        PoolUSDT = 0x12dC9256Acc9895B076f6638D628382881e62CeE;
    } else if (chainId == 137) {
        PoolNative = address(0);
        PoolUSDC = 0x9Aa02D4Fae7F58b8E8f34c66E756cC734DAc7fe4;
        PoolUSDT = 0xd47b03ee6d86Cf251ee7860FB2ACf9f91B9fD4d7;
    } else if (chainId == 42161) {
        PoolNative = 0xA45B5130f36CDcA45667738e2a258AB09f4A5f7F;
        PoolUSDC = 0xe8CDF27AcD73a434D661C84887215F7598e7d0d3;
        PoolUSDT = 0xcE8CcA271Ebc0533920C83d39F417ED6A0abB7D0;
    } else if (chainId == 10) {
        PoolNative = 0xe8CDF27AcD73a434D661C84887215F7598e7d0d3;
        PoolUSDC = 0xcE8CcA271Ebc0533920C83d39F417ED6A0abB7D0;
        PoolUSDT = 0x19cFCE47eD54a88614648DC3f19A5980097007dD;
    } else if (chainId == 8453) {
        PoolNative = 0xdc181Bd607330aeeBEF6ea62e03e5e1Fb4B6F7C7;
        PoolUSDC = 0x27a16dc786820B16E5c9028b75B99F6f604b5d26;
        PoolUSDT = address(0);
    } else {
        revert("no chain id is matched");
    }
}
