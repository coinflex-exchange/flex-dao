// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/access/AccessControl.sol';
import '@openzeppelin/contracts/access/Ownable.sol';
import '@openzeppelin/contracts/token/ERC20/ERC20.sol';
import '@openzeppelin/contracts/utils/cryptography/draft-EIP712.sol';
import '@openzeppelin/contracts/utils/math/SafeMath.sol';
import '@openzeppelin/contracts/utils/Context.sol';
import '../interfaces/IChildToken.sol';

// RewardToken with Governance.
contract RewardToken
is IChildToken, Context, ERC20, EIP712, AccessControl, Ownable
{
  // Enumerable Roles 
  bytes32 public constant DEPOSITOR_ROLE = keccak256('DEPOSITOR_ROLE');

  uint8 private _decimals;

  constructor(
    string memory name_,
    string memory symbol_,
    uint8 decimals_,
    address childChainManager,
    address minter
  )
    ERC20(name_, symbol_)
    EIP712(name_, symbol_)
  {
    _decimals = decimals_;
    _setupRole(DEFAULT_ADMIN_ROLE, minter);
    _setupRole(DEPOSITOR_ROLE, childChainManager);
  }

  /**
   * @notice called when token is deposited on root chain
   * @dev Should be callable only by ChildChainManager
   * Should handle deposit by minting the required amount for user
   * Make sure minting is done only by this function
   * @param user user address for whom deposit is being done
   * @param depositData abi encoded amount
   */
  function deposit(address user, bytes calldata depositData)
  external
  override
  {
    require(hasRole(DEPOSITOR_ROLE, _msgSender()), 'RewardToken: must have depositor role to deposit.');
    uint256 amount = abi.decode(depositData, (uint256));
    _mint(user, amount);
  }

  /**
   * @notice called when user wants to withdraw tokens back to root chain
   * @dev Should burn user's tokens. This transaction will be verified when exiting on root chain
   * @param amount amount of tokens to withdraw
   */
  function withdraw(uint256 amount) external {
    _burn(_msgSender(), amount);
  }

  /**
   * @notice Example function to handle minting tokens on matic chain
   * @dev Minting can be done as per requirement,
   * This implementation allows only admin to mint tokens but it can be changed as per requirement
   * @param user user for whom tokens are being minted
   * @param amount amount of token to mint
   */
  function mint(address user, uint256 amount) public
  {
    require(hasRole(DEFAULT_ADMIN_ROLE, _msgSender()), 'RewardToken: must have admin role to mint.');
    _mint(user, amount);
  }

  /**
   * @notice Overrides decimals
   * @dev returns uint8 decimal value set at construction 
   */
  function decimals() public view virtual override returns (uint8)
  {
    return _decimals;
  }
}