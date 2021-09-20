// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol';
import '@openzeppelin/contracts/utils/Address.sol';
import '@openzeppelin/contracts/utils/math/SafeMath.sol';
import '../interfaces/IStrategy.sol';
import '../interfaces/IConverter.sol';

contract Controller
{
  using SafeERC20 for IERC20;
  using Address for address;
  using SafeMath for uint256;
  address public governance;
  address public treasury;
  address public timelock;

  // Convenience fee 0.1%
  uint256 public convenienceFee = 100;
  uint256 public constant convenienceFeeMax = 100000;

  mapping(address => address) public vaults;
  mapping(address => address) public strategies;
  mapping(address => mapping(address => address)) public converters;
  mapping(address => mapping(address => bool)) public approvedStrategies;
  mapping(address => bool) public approvedVaultConverters;

  uint256 public split = 500;
  uint256 public constant max = 10000;
  constructor(
    address _governance,
    address _timelock,
    address _treasury
  ) {
    governance = _governance;
    timelock = _timelock;
    treasury = _treasury;
  }

  function setTreasury(address _treasury) public
  {
    require(msg.sender == governance, '!governance');
    treasury = _treasury;
  }


  function setSplit(uint256 _split) public
  {
    require(msg.sender == governance, '!governance');
    require(_split <= max, 'numerator cannot be greater than denominator');
    split = _split;
  }

  function setGovernance(address _governance) public
  {
    require(msg.sender == governance, '!governance');
    governance = _governance;
  }

  function setTimelock(address _timelock) public
  {
    require(msg.sender == timelock, '!timelock');
    timelock = _timelock;
  }

  function setVault(address _token, address _vault) public
  {
    require(msg.sender == governance, '!governance');
    require(vaults[_token] == address(0), 'vault');
    vaults[_token] = _vault;
  }

  function approveVaultConverter(address _converter) public
  {
    require(msg.sender == governance, '!governance');
    approvedVaultConverters[_converter] = true;
  }

  function revokeVaultConverter(address _converter) public
  {
    require(msg.sender == governance, '!governance');
    approvedVaultConverters[_converter] = false;
  }

  function approveStrategy(address _token, address _strategy) public
  {
    require(msg.sender == timelock, '!timelock');
    approvedStrategies[_token][_strategy] = true;
  }

  function revokeStrategy(address _token, address _strategy) public
  {
    require(msg.sender == governance, '!governance');
    require(strategies[_token] != _strategy, 'cannot revoke active strategy');
    approvedStrategies[_token][_strategy] = false;
  }

  function setConvenienceFee(uint256 _convenienceFee) external
  {
    require(msg.sender == timelock, '!timelock');
    convenienceFee = _convenienceFee;
  }

  function setStrategy(address _token, address _strategy) public
  {
    require(msg.sender == governance, '!governance');
    require(approvedStrategies[_token][_strategy] == true, '!approved');
    address _current = strategies[_token];
    if (_current != address(0)) {
      IStrategy(_current).withdrawAll();
    }
    strategies[_token] = _strategy;
  }

  function earn(address _token, uint256 _amount) public
  {
    address _strategy = strategies[_token];
    address _want = IStrategy(_strategy).want();
    if (_want != _token) {
      address converter = converters[_token][_want];
      IERC20(_token).safeTransfer(converter, _amount);
      _amount = IConverter(converter).convert(_strategy);
      IERC20(_want).safeTransfer(_strategy, _amount);
    } else {
      IERC20(_token).safeTransfer(_strategy, _amount);
    }
    IStrategy(_strategy).deposit();
  }

  function balanceOf(address _token) external view returns (uint256)
  {
    return IStrategy(strategies[_token]).balanceOf();
  }

  function withdrawAll(address _token) public
  {
    require(msg.sender == governance, '!governance');
    IStrategy(strategies[_token]).withdrawAll();
  }

  function inCaseTokensGetStuck(address _token, uint256 _amount) public
  {
    require(msg.sender == governance, '!governance');
    IERC20(_token).safeTransfer(msg.sender, _amount);
  }

  function inCaseStrategyTokenGetStuck(address _strategy, address _token)
    public
  {
    require(msg.sender == governance, '!governance');
    IStrategy(_strategy).withdraw(_token);
  }

  function withdraw(address _token, uint256 _amount) public
  {
    require(msg.sender == vaults[_token], '!vault');
    IStrategy(strategies[_token]).withdraw(_amount);
  }

  function _execute(address _target, bytes memory _data)
    internal
    returns (bytes memory response)
  {
    require(_target != address(0), '!target');
    // call contract in current context
    assembly {
      let succeeded := delegatecall(sub(gas(), 5000), _target, add(_data, 0x20), mload(_data), 0, 0)
      let size := returndatasize()
      response := mload(0x40)
      mstore(0x40, add(response, and(add(add(size, 0x20), 0x1f), not(0x1f))))
      mstore(response, size)
      returndatacopy(add(response, 0x20), 0, size)
      switch iszero(succeeded)
        case 1 {
          // throw if delegatecall failed
          revert(add(response, 0x20), size)
        }
    }
  }
}
