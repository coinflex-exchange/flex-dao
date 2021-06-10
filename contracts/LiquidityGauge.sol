// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/security/ReentrancyGuard.sol';
import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol';
import '@openzeppelin/contracts/utils/Address.sol';
import '@openzeppelin/contracts/utils/math/Math.sol';
import '@openzeppelin/contracts/utils/math/SafeMath.sol';
import '../interfaces/ILiquidityGauge.sol';

contract Gauge is ILiquidityGauge, ReentrancyGuard
{
  using SafeMath for uint256;
  using SafeERC20 for IERC20;

  IERC20 public constant REWARD = IERC20(0x429881672B9AE42b8EbA0E26cD9C73711b891Ca5);
  IERC20 public constant ESCROW = IERC20(0xbBCf169eE191A1Ba7371F30A1C344bFC498b29Cf);
  address public constant TREASURY = address(0x066419EaEf5DE53cc5da0d8702b990c5bc7D1AB3);

  IERC20 public immutable TOKEN;
  address public immutable DISTRIBUTION;
  uint256 public constant DURATION = 7 days;

  uint256 public periodFinish = 0;
  uint256 public rewardRate = 0;
  uint256 public lastUpdateTime;
  uint256 public rewardPerTokenStored;

  modifier onlyDistribution() {
    require(msg.sender == DISTRIBUTION, 'Caller is not RewardsDistribution contract');
    _;
  }

  mapping(address => uint256) public userRewardPerTokenPaid;
  mapping(address => uint256) public rewards;

  uint256 private _totalSupply;
  uint public derivedSupply;
  mapping(address => uint256) private _balances;
  mapping(address => uint256) public derivedBalances;
  mapping(address => uint) private _base;

  constructor(address _token)
  {
    TOKEN = IERC20(_token);
    DISTRIBUTION = msg.sender;
  }

  function totalSupply() external view returns(uint256) {
    return _totalSupply;
  }

  function balanceOf(address account) external view returns(uint256) {
    return _balances[account];
  }

  function lastTimeRewardApplicable() public view returns(uint256) {
    return Math.min(block.timestamp, periodFinish);
  }

  function rewardPerToken() public view returns(uint256) {
    if (_totalSupply == 0) {
      return rewardPerTokenStored;
    }
    return
    rewardPerTokenStored.add(
      lastTimeRewardApplicable().sub(lastUpdateTime).mul(rewardRate).mul(1e18).div(derivedSupply)
    );
  }

  function derivedBalance(address account) public view returns(uint) {
    uint _balance = _balances[account];
    uint _derived = _balance.mul(40).div(100);
    uint _adjusted = (_totalSupply.mul(ESCROW.balanceOf(account)).div(ESCROW.totalSupply())).mul(60).div(100);
    return Math.min(_derived.add(_adjusted), _balance);
  }

  function kick(address account) public {
    uint _derivedBalance = derivedBalances[account];
    derivedSupply = derivedSupply.sub(_derivedBalance);
    _derivedBalance = derivedBalance(account);
    derivedBalances[account] = _derivedBalance;
    derivedSupply = derivedSupply.add(_derivedBalance);
  }

  function earned(address account) public view returns(uint256) {
    return derivedBalances[account].mul(rewardPerToken().sub(userRewardPerTokenPaid[account])).div(1e18).add(rewards[account]);
  }

  function getRewardForDuration() external view returns(uint256) {
    return rewardRate.mul(DURATION);
  }

  function depositAll() external {
    _deposit(TOKEN.balanceOf(msg.sender), msg.sender);
  }

  function deposit(uint256 amount) external {
    _deposit(amount, msg.sender);
  }

  function depositFor(uint256 amount, address account) external {
    _deposit(amount, account);
  }

  function _deposit(uint amount, address account) internal nonReentrant updateReward(account) {
    require(amount > 0, 'Cannot stake 0');
    _totalSupply = _totalSupply.add(amount);
    _balances[account] = _balances[account].add(amount);
    emit Staked(account, amount);
    TOKEN.safeTransferFrom(account, address(this), amount);
  }

  function withdrawAll() external {
    _withdraw(_balances[msg.sender]);
  }

  function withdraw(uint256 amount) external {
    _withdraw(amount);
  }

  function _withdraw(uint amount) internal nonReentrant updateReward(msg.sender) {
    require(amount > 0, 'Cannot withdraw 0');
    _totalSupply = _totalSupply.sub(amount);
    _balances[msg.sender] = _balances[msg.sender].sub(amount);
    TOKEN.safeTransfer(msg.sender, amount);
    emit Withdrawn(msg.sender, amount);
  }

  function getReward() public nonReentrant updateReward(msg.sender) {
    uint256 reward = rewards[msg.sender];
    if (reward > 0) {
      rewards[msg.sender] = 0;
      REWARD.safeTransfer(msg.sender, reward);
      emit RewardPaid(msg.sender, reward);
    }
  }

  function exit() external {
    _withdraw(_balances[msg.sender]);
    getReward();
  }

  function notifyRewardAmount(uint256 reward) override external onlyDistribution updateReward(address(0)) {
    REWARD.safeTransferFrom(DISTRIBUTION, address(this), reward);
    if (block.timestamp >= periodFinish) {
      rewardRate = reward.div(DURATION);
    } else {
      uint256 remaining = periodFinish.sub(block.timestamp);
      uint256 leftover = remaining.mul(rewardRate);
      rewardRate = reward.add(leftover).div(DURATION);
    }

    // Ensure the provided reward amount is not more than the balance in the contract.
    // This keeps the reward rate in the right range, preventing overflows due to
    // very high values of rewardRate in the earned and rewardsPerToken functions;
    // Reward + leftover must be less than 2^256 / 10^18 to avoid overflow.
    uint balance = REWARD.balanceOf(address(this));
    require(rewardRate <= balance.div(DURATION), 'Provided reward too high');

    lastUpdateTime = block.timestamp;
    periodFinish = block.timestamp.add(DURATION);
    emit RewardAdded(reward);
  }

  modifier updateReward(address account) {
    rewardPerTokenStored = rewardPerToken();
    lastUpdateTime = lastTimeRewardApplicable();
    if (account != address(0)) {
      rewards[account] = earned(account);
      userRewardPerTokenPaid[account] = rewardPerTokenStored;
    }
    _;
    if (account != address(0)) {
      kick(account);
    }
  }

  event RewardAdded(uint256 reward);
  event Staked(address indexed user, uint256 amount);
  event Withdrawn(address indexed user, uint256 amount);
  event RewardPaid(address indexed user, uint256 reward);
}