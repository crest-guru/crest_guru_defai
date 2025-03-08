// SPDX-License-Identifier: LGPL-3.0-only
pragma solidity ^0.8.19;

import "../../base/BaseACL.sol";

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/utils/structs/EnumerableSet.sol";

interface ISiloRouter {
    // Enum representing different action types
    enum ActionType {
        Deposit,    // Deposit tokens
        Mint,       // Mint (create tokens/shares)
        Repay,      // Repay debt
        RepayShares // Repay shares instead of a specific amount
    }
    
    /// @notice Struct representing additional action parameters
    /// @dev This includes amount and asset type
    struct AnyAction {
        uint256 amount;   // Amount for the action (e.g., deposit or mint)
        uint8 assetType;  // Asset type indicator (e.g., 0 or 1)
    }
    
    /// @notice Struct describing a single action
    struct Action {
        ActionType actionType; // Type of action (Deposit, Mint, Repay, RepayShares)
        address silo;          // Address of the Silo contract being interacted with
        IERC20 asset;          // Token used for the action
        bytes options;         // Additional encoded parameters (using abi.encode with AnyAction)
    }
    
    /// @notice Function to execute one or more actions in batch
    /// @param actions Array of actions to be executed
    function execute(Action[] calldata actions) external payable;
}

contract SiloAuthorizer is BaseACL {
    using EnumerableSet for EnumerableSet.AddressSet;

    EnumerableSet.AddressSet private siloWhitelist;
    

    bytes32 public constant NAME = "SiloAuthorizerV3";
    uint256 public constant VERSION = 1;

    address public constant ROUTER = 0x22AacdEc57b13911dE9f188CF69633cC537BdB76;

    uint256 public MAX_AMOUNT = 10000000000000000000;
    address public ADMIN;

    modifier onlyAdmin() {
        require(msg.sender == ADMIN, "Only admin can call this function");
        _;
    }

    // @notice Constructor for SiloAuthorizer
    /// @param _owner The owner address ( Safe wallet address)
    /// @param _caller The address caller (Cobo account)
    constructor(address _owner, address _caller) BaseACL(_owner, _caller) {}

    /// @notice Function to execute SiloRouter actions.
    /// @dev This function is callable only by the ROUTER via a delegate call (as ensured by onlyContract modifier)
    /// @param actions An array of actions to execute via SiloRouter
    function execute(ISiloRouter.Action[] calldata actions) public view onlyContract(ROUTER) { 
        for (uint256 i = 0; i < actions.length; i++) {
            ISiloRouter.Action memory action = actions[i];
            if (action.actionType == ISiloRouter.ActionType.Deposit) {
                require(_txn().value <= MAX_AMOUNT, "Amount exceeds the maximum allowed");
            }
        }
    }

    function withdraw(uint256 _shares, address _receiver, address _owner) public view {
        _checkRecipient(_receiver);
        _checkRecipient(_owner);
    }
    function deposit(uint256 _shares, address _receiver, address _owner) public view {
        _checkRecipient(_receiver);
        _checkRecipient(_owner);
        require(_shares <= MAX_AMOUNT, "Amount exceeds the maximum allowed");
    }
    function redeem(uint256 _shares, address _receiver, address _owner, uint8 _collateralType) public view {
        _checkRecipient(_receiver);
        _checkRecipient(_owner);
    }

    function repay(uint256 _assetAmount, address _borrower) public view {
        _checkRecipient(_borrower);
    }

    function setAdmin(address _admin) public onlyOwner {
        ADMIN = _admin;
    }

    function setMaxAmount(uint256 _maxAmount) public onlyAdmin {
        MAX_AMOUNT = _maxAmount;
    }

    function addPoolAddress(address _poolAddress) public onlyAdmin {
        siloWhitelist.add(_poolAddress);
    }

    function removePoolAddress(address _poolAddress) public onlyAdmin {
        siloWhitelist.remove(_poolAddress);
    }

    function getPoolAddressWhiteList() public view returns (address[] memory) {
        return siloWhitelist.values();
    }
    function addPoolAddresses(address[] memory _poolAddresses) public onlyAdmin {
        for (uint256 i = 0; i < _poolAddresses.length; i++) {
            siloWhitelist.add(_poolAddresses[i]);
        }
    }

    /// @notice Returns the list of contract addresses for which permissions have been granted.
    ///         This includes the ROUTER and all pool addresses from the whitelist (farmPoolAddressWhitelist).
    /// @return _contracts Array of authorized contract addresses.
    function contracts() public view override returns (address[] memory _contracts) {
        // Retrieve the pool addresses from the whitelist using the inherited getter
        address[] memory poolAddresses = getPoolAddressWhiteList();
        
        // Total contracts count: 1 (for ROUTER) plus the number of pool addresses
        uint256 totalContracts = 1 + poolAddresses.length;
        
        // Initialize a new array with the total number of authorized contracts
        _contracts = new address[](totalContracts);
        
        // First element is always the ROUTER contract
        _contracts[0] = ROUTER;
        
        // Append each pool address from the whitelist to the authorized contracts array
        for (uint256 i = 0; i < poolAddresses.length; i++) {
            _contracts[i + 1] = poolAddresses[i];
        }
    }
}
