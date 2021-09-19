// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/access/Ownable.sol';
import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol';
import '@openzeppelin/contracts/utils/math/SafeMath.sol';
import '../interfaces/IVested.sol';

contract RewardShare is Ownable
{
  using SafeERC20 for IERC20;
  using SafeMath for uint256;

  /* =========  MEMBER VARS ========== */
  IERC20  public token;  // FLEX token
  IVested public vested; // veFLEX
  uint256 public constant epoch_period = 604800; // a week in seconds
  uint256 public startTime;
  uint256[] public feesForEpoch;
  mapping(address => uint256) public claimedEpoches;
  mapping(address => bool) public isDistributor;

  /* ===========   EVENTS  =========== */
  event Claim(address indexed from, uint256 amount, uint256 endingEpoch);

  /* ========== CONSTRUCTOR ========== */

  constructor(address tknAddr, address veAddr)
  {
    require(tknAddr != address(0), 'Token address cannot be zero.');  // FLEX token
    require(veAddr != address(0) , 'Vested address cannot be zero.'); // veFLEX
    token = IERC20(tknAddr);
    vested = IVested(veAddr);
  }

  function addDistributor(address account) public onlyOwner {
    isDistributor[account] = true;
  }

  function removeDistributor(address account) public onlyOwner {
    isDistributor[account] = false;
  }

  function setStartTime(uint256 timestamp) public onlyOwner {
    require(startTime == 0, "start time already set!");
    startTime = timestamp;
  }

  function distribute(uint256 amount) external {
    // require(msg.sender == owner() || isDistributor[msg.sender], "distributor not authorized!");
    token.safeTransferFrom(msg.sender, address(this), amount);
    feesForEpoch.push(amount);
  }

  function currentEpoch() public view returns(uint256) {
    return feesForEpoch.length;
  }

  function claim(address owner) external {
    uint256 epoch = currentEpoch();
    if (epoch > 0) {
      _claimUntilEpoch(owner, epoch - 1);
    }
  }

  // endingEpoch starts from 0
  function claimUntilEpoch(address owner, uint256 endingEpoch) external {
    _claimUntilEpoch(owner, endingEpoch);
  }

  function getClaimable(address owner) external view returns(uint256) {
    uint256 epoch = currentEpoch();
    if (epoch == 0) return 0;
    return _getClaimableUntilEpoch(owner, currentEpoch().sub(1));
  }

  function getClaimableUntilEpoch(address owner, uint256 endingEpoch) external view returns(uint256) {
    return _getClaimableUntilEpoch(owner, endingEpoch);
  }

  function _getClaimableUntilEpoch(address owner, uint256 endingEpoch) internal view returns(uint256) {
    uint256 amount = 0;
    for (uint256 i = claimedEpoches[owner]; i <= endingEpoch; i++) {
      uint256 epochStartTime = getEpochStartTime(i);
      uint256 totalSupply = dill.totalSupply(epochStartTime);
      if (totalSupply > 0) {
        amount += feesForEpoch[i].mul(dill.balanceOf(owner, epochStartTime)).div(totalSupply);
      }
    }
    return amount;
  }

  function _claimUntilEpoch(address owner, uint256 endingEpoch) internal {
    uint256 amount = _getClaimableUntilEpoch(owner, endingEpoch);
    token.safeTransfer(owner, amount);
    claimedEpoches[owner] = endingEpoch.add(1);
    emit Claim(owner, amount, endingEpoch);
  }

  function getEpochStartTime(uint256 epoch) internal view returns(uint256) {
    return startTime.add(epoch_period.mul(epoch));
  }
}