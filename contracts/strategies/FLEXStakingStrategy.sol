// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import './BaseStakingStrategy.sol';

abstract contract FLEXStakingStrategy is BaseStakingStrategy {
  // FLEX
  address public flex;

  constructor(
    address _flex,
    address _rewards,
    address _governance,
    address _controller,
    address _timelock
  )
    BaseStakingStrategy(_rewards, _governance, _controller, _timelock)
  {
    flex = _flex;
  }

  // **** State Mutations ****

  function harvest() public override onlyBenevolent {
    // Anyone can harvest it at any given time.
    // I understand the possibility of being frontrun
    // But ETH is a dark forest, and I wanna see how this plays out
    // i.e. will be be heavily frontrunned?
    //      if so, a new strategy will be deployed.

    // Collects veFLEX tokens
    IStakingRewards(rewards).getReward();
    uint256 _flexBal = IERC20(flex).balanceOf(address(this));
    if (_flexBal > 0) {
      IERC20(flex).safeApprove(univ2Router2, 0);
      IERC20(flex).safeApprove(univ2Router2, _flexBal);
      IERC20(flex).safeTransfer(
        IController(controller).treasury(),
        IERC20(flex).balanceOf(address(this))
      );
    }

    // We want to get back FLEX tokens
    _distributePerformanceFeesAndDeposit();
  }
}