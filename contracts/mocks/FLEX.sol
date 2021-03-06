// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/utils/math/SafeMath.sol';

contract FLEXCoin {
  using SafeMath for uint;
  /// @notice EIP-20 token name for this token
  string public constant name = 'FLEX Coin';
  /// @notice EIP-20 token symbol for this token
  string public constant symbol = 'FLEX';
  /// @notice EIP-20 token decimals for this token
  uint8 public constant decimals = 18;
  /// @notice Total number of tokens in circulation
  uint public totalSupply = 1e24;
  mapping(address => mapping(address => uint)) internal allowances;
  mapping(address => uint) internal balances;
  /// @notice The standard EIP-20 transfer event
  event Transfer(address indexed from, address indexed to, uint amount);
  /// @notice The standard EIP-20 approval event
  event Approval(address indexed owner, address indexed spender, uint amount);

  constructor()
  {
    balances[msg.sender] = 1e24;
    emit Transfer(address(0x0), msg.sender, 1e24);
  }

  /**
   * @notice Get the number of tokens `spender` is approved to spend on behalf of `account`
   * @param account The address of the account holding the funds
   * @param spender The address of the account spending the funds
   * @return The number of tokens approved
   */
  function allowance(address account, address spender) external view returns(uint)
  {
    return allowances[account][spender];
  }

  /**
   * @notice Approve `spender` to transfer up to `amount` from `src`
   * @dev This will overwrite the approval amount for `spender`
   *  and is subject to issues noted [here](https://eips.ethereum.org/EIPS/eip-20#approve)
   * @param spender The address of the account which may transfer tokens
   * @param amount The number of tokens that are approved (2^256-1 means infinite)
   * @return Whether or not the approval succeeded
   */
  function approve(address spender, uint amount) external returns(bool)
  {
    allowances[msg.sender][spender] = amount;

    emit Approval(msg.sender, spender, amount);
    return true;
  }

  /**
   * @notice Get the number of tokens held by the `account`
   * @param account The address of the account to get the balance of
   * @return The number of tokens held
   */
  function balanceOf(address account) external view returns(uint)
  {
    return balances[account];
  }

  /**
   * @notice Transfer `amount` tokens from `msg.sender` to `dst`
   * @param dst The address of the destination account
   * @param amount The number of tokens to transfer
   * @return Whether or not the transfer succeeded
   */
  function transfer(address dst, uint amount) external returns(bool)
  {
    _transferTokens(msg.sender, dst, amount);
    return true;
  }

  /**
   * @notice Transfer `amount` tokens from `src` to `dst`
   * @param src The address of the source account
   * @param dst The address of the destination account
   * @param amount The number of tokens to transfer
   * @return Whether or not the transfer succeeded
   */
  function transferFrom(address src, address dst, uint amount) external returns(bool)
  {
    address spender = msg.sender;
    uint spenderAllowance = allowances[src][spender];
    if (spender != src && spenderAllowance > 0) {
      uint newAllowance = spenderAllowance.sub(amount, 'transferFrom: exceeds spender allowance');
      allowances[src][spender] = newAllowance;
      emit Approval(src, spender, newAllowance);
    }
    _transferTokens(src, dst, amount);
    return true;
  }

  function _transferTokens(address src, address dst, uint amount) internal
  {
    require(src != address(0), '_transferTokens: zero address');
    require(dst != address(0), '_transferTokens: zero address');
    balances[src] = balances[src].sub(amount, '_transferTokens: exceeds balance');
    balances[dst] = balances[dst].add(amount);
    emit Transfer(src, dst, amount);
  }
}