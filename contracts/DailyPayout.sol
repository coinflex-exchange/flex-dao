// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/access/Ownable.sol';
import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol';
import '@openzeppelin/contracts/utils/math/SafeMath.sol';
import '../interfaces/IVested.sol';

contract DailyPayout is Ownable
{
  using SafeERC20 for IERC20;
  using SafeMath for uint256;

  /* =========  MEMBER VARS ========== */
  IERC20 immutable public token;  // FLEX token
  IVested immutable public vested; // veFLEX
  uint256 public constant EPOCH_BLOCKS = 120; // 10 is for test and 17280 is average blocks in 1 day with 5s block interval
  uint256 public startBlockHeight;
  uint256[] public payoutForEpoch;
  mapping(address => uint256) public claimedEpoches;
  mapping(address => bool) public isDistributor;

  /* ===========   EVENTS  =========== */
  event Claim(address indexed from, uint256 amount, uint256 lastClaimedEpoch, uint256 endingEpoch);
  event IsDistributor(address indexed account, bool status);
  event Distribute(address distributor, uint256 amount);
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
    emit IsDistributor(account, true);
  }

  function removeDistributor(address account) public onlyOwner {
    isDistributor[account] = false;
    emit IsDistributor(account, false);
  }

  function setStartBlockHeight(uint256 blockHeight) public onlyOwner {
    require(startBlockHeight == 0, "start block height already set!");
    startBlockHeight = blockHeight;
  }

  function distribute(uint256 amount) external {
    require(msg.sender == owner() || isDistributor[msg.sender], "distributor not authorized!");
    require(amount > 0, "amount to be distributed must be greater than zero!");
    payoutForEpoch.push(amount);
    emit Distribute(msg.sender, amount);
    token.safeTransferFrom(msg.sender, address(this), amount);
  }

 /**
  * @dev 
  *   This is not current epoch, but rather the number of  claimable epochs .
  *   Name not changed for the sake of compatibility with former implementation.
  */
  function currentEpoch() public view returns(uint256) {
    return payoutForEpoch.length;
  }

  function claim(address owner) external {
    require(owner == msg.sender, "can only claim for own account");
    uint256 epoch = currentEpoch();
    if (epoch > 0) {
      _claimUntilEpoch(owner, epoch.sub(1));
    }
  }

  function getClaimable(address owner) external view returns(uint256) {
    uint256 epoch = currentEpoch();
    if (epoch == 0) return 0;
    (uint256 amount, ) = _getClaimableUntilEpoch(owner, epoch.sub(1));
    return amount;
  }

/**
  * @dev get current epoch for owner
  */
  function getCurrentEpoch() external view onlyOwner returns(uint256) {
    return _getCurrentEpoch();
  }

/**
  * @dev get epoch start block height for owner
  */
  function getEpochStartBlockHeight(uint256 epoch) external view onlyOwner returns(uint256) {
    return _getEpochStartBlockHeight(epoch);
  }


/**
  * @dev 
  *   Rewarded epochs might extend to the future, but can only 
  *   claim until epochs no later than the current acutal epoch.
  */
  function _getClaimableUntilEpoch(address owner, uint256 endingEpoch) internal view returns(uint256, uint256) {
    uint256 amount = 0;
    uint256 epoch = 0;
    uint256 blockHeightAtEpochStartTime;
    uint256 totalSupply;
    for (epoch = claimedEpoches[owner]; epoch <= endingEpoch; epoch++) {
      blockHeightAtEpochStartTime = _getEpochStartBlockHeight(epoch);
      if (block.number <= blockHeightAtEpochStartTime) break;
      totalSupply = vested.totalSupplyAt(blockHeightAtEpochStartTime);
      if (totalSupply > 0) {
        amount += payoutForEpoch[epoch].mul(vested.balanceOfAt(owner, blockHeightAtEpochStartTime)).div(totalSupply);
      }
    }
    return (amount, epoch - 1);
  }

  function _claimUntilEpoch(address owner, uint256 endingEpoch) internal {
    (uint256 amount, uint256 lastClaimedEpoch) = _getClaimableUntilEpoch(owner, endingEpoch);
    claimedEpoches[owner] = lastClaimedEpoch.add(1);
    if (amount > 0) {
      emit Claim(owner, amount, lastClaimedEpoch, endingEpoch);
      token.safeTransfer(owner, amount);
    }
  }

 /**
  * @dev 
  *   Given epoch number, get the epoch start block height.
  */
  function _getEpochStartBlockHeight(uint256 epoch) internal view returns(uint256) {
    return startBlockHeight.add(EPOCH_BLOCKS.mul(epoch));
  }

 /**
  * @dev This is the actual current epoch.
  */
  function _getCurrentEpoch() internal view returns(uint256) {
    require(block.number >= startBlockHeight, 'the payout contract is not started yet');
    return (block.number - startBlockHeight).div(EPOCH_BLOCKS);
  }
} 