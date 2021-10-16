// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol';
import './BaseStrategy.sol';
import '../../interfaces/IStakingRewards.sol';

abstract contract BaseStakingStrategy is BaseStrategy {
  using SafeERC20 for IERC20;

  address public rewards;

  // **** Getters ****
  constructor(address _rewards, address _want, address _governance, address _controller, address _timelock)
    BaseStrategy(_want, _governance, _controller, _timelock)
  {
    rewards = _rewards;
  }

  function balanceOfPool() public override view returns(uint256) {
    return IStakingRewards(rewards).balanceOf(address(this));
  }

  function getHarvestable() external view returns(uint256) {
    return IStakingRewards(rewards).earned(address(this));
  }

  // **** Setters ****

  function deposit()
    public override
  {
    uint256 _want = IERC20(want).balanceOf(address(this));
    if (_want > 0) {
      IERC20(want).safeApprove(rewards, 0);
      IERC20(want).safeApprove(rewards, _want);
      IStakingRewards(rewards).stake(_want);
    }
  }

  function _withdrawSome(uint256 _amount)
    internal
    override
    returns(uint256)
  {
    IStakingRewards(rewards).withdraw(_amount);
    return _amount;
  }
}