// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol';
import './BaseStakingStrategy.sol';

contract FLEXStakingStrategy is BaseStakingStrategy {
  using SafeERC20 for IERC20;

  constructor(
    address _rewards,
    address _want, // FLEX
    address _governance,
    address _controller,
    address _timelock
  )
    BaseStakingStrategy(_rewards, _want, _governance, _controller, _timelock)
  {
  }

  // **** Views ****

  function getName() external override pure returns (string memory) {
    return 'FLEXStakingStrategy';
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
    uint256 _flexBal = IERC20(want).balanceOf(address(this));
    if (_flexBal > 0) {
      IERC20(want).safeTransfer(
        IController(controller).treasury(),
        IERC20(want).balanceOf(address(this))
      );
    }

    // We want to get back FLEX tokens
    _distributePerformanceFeesAndDeposit();
  }
}