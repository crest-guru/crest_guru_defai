// SPDX-License-Identifier: LGPL-3.0-only
pragma solidity 0.8.20;

import "../../base/BaseACL.sol";
import "../ACLUtils.sol";
import "./Commands.sol";

contract ShadowAuthorizer is BaseACL {
    bytes32 public constant NAME = "ShadowAuthorizer";
    uint256 public constant VERSION = 1;

    address public constant SHADOW_ROUTER = address(0x92643Dc4F75C374b689774160CDea09A0704a9c2);

    error InvalidRecipient(address recipient);
    error DeadlinePassed();
    error InvalidCommandLength();
    error InvalidCommandType(uint256 commandType);

    constructor(address _owner, address _caller) BaseACL(_owner, _caller) {}

    function _checkOwner(address _recipient) internal view {
        if (_recipient != owner) {
            revert InvalidRecipient(_recipient);
        }
    }

    function execute(
        bytes calldata _commands, 
        bytes[] calldata _inputs, 
        uint256 _deadline
    ) external view {
        

        

        for (uint256 i = 0; i < _commands.length; i++) {
            bytes1 command = _commands[i];
            bytes calldata input = _inputs[i];
            
            uint256 commandType = uint8(command & Commands.COMMAND_TYPE_MASK);

            if (commandType < Commands.FIRST_IF_BOUNDARY) {
                //  0x00-0x07
                if (commandType == Commands.V3_SWAP_EXACT_IN) {
                    (address recipient, , , , ) = abi.decode(input, (address, uint256, uint256, bytes, bool));
                    _checkOwner(recipient);
                } 
                else if (commandType == Commands.V3_SWAP_EXACT_OUT) {
                    (address recipient, , , , ) = abi.decode(input, (address, uint256, uint256, bytes, bool));
                    _checkOwner(recipient);
                }
                else if (commandType == Commands.PERMIT2_TRANSFER_FROM) {
                    (,address recipient,) = abi.decode(input, (address, address, uint160));
                    _checkOwner(recipient);
                }
                else if (commandType == Commands.SWEEP) {
                    (,address recipient,) = abi.decode(input, (address, address, uint256));
                    _checkOwner(recipient);
                }
                else if (commandType == Commands.TRANSFER) {
                    (,address recipient,) = abi.decode(input, (address, address, uint256));
                    _checkOwner(recipient);
                }
                else if (commandType == Commands.PAY_PORTION) {
                    (,address recipient,) = abi.decode(input, (address, address, uint256));
                    _checkOwner(recipient);
                }
            }
            else if (commandType < Commands.SECOND_IF_BOUNDARY) {
                //  0x08-0x0f
                if (commandType == Commands.V2_SWAP_EXACT_IN) {
                    (address recipient, , , , ) = abi.decode(input, (address, uint256, uint256, bytes, bool));
                    _checkOwner(recipient);
                }
                else if (commandType == Commands.V2_SWAP_EXACT_OUT) {
                    (address recipient, , , , ) = abi.decode(input, (address, uint256, uint256, bytes, bool));
                    _checkOwner(recipient);
                }
                else if (commandType == Commands.WRAP_ETH) {
                    (address recipient, ) = abi.decode(input, (address, uint256));
                    _checkOwner(recipient);
                }
                else if (commandType == Commands.UNWRAP_WETH) {
                    (address recipient, ) = abi.decode(input, (address, uint256));
                    _checkOwner(recipient);
                }
            }
            else if (commandType < Commands.THIRD_IF_BOUNDARY) {
                //  0x10-0x17
                if (commandType == Commands.SWEEP_ERC721) {
                    (,address recipient,) = abi.decode(input, (address, address, uint256));
                    _checkOwner(recipient);
                }
            }
            else if (commandType < Commands.FOURTH_IF_BOUNDARY) {
                // 0x18-0x1f
                if (commandType == Commands.SWEEP_ERC1155) {
                    (,address recipient,,) = abi.decode(input, (address, address, uint256, uint256));
                    _checkOwner(recipient);
                }
            }
            else {
                // 0x20+
                if (commandType > 0x3f) {
                    revert InvalidCommandType(commandType);
                }
            }
        }
    }

    function contracts() public view override returns (address[] memory _contracts) {
        _contracts = new address[](1);
        _contracts[0] = SHADOW_ROUTER;
    }
}