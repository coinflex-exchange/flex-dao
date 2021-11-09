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
  uint256 public constant INIT_EPOCH_LEN = 17280; // 10 is for test and 17280 is average blocks in 1 day with 5s block interval
  uint256 public startBlockHeight;
  uint256[] public payoutForEpoch;
  uint256[2][] public epochLengthHistory;
  mapping(address => uint256) public claimedEpoches;
  mapping(address => bool) public isDistributor;

  /* ===========   EVENTS  =========== */
  event Claim(address indexed from, uint256 amount, uint256 lastClaimedEpoch, uint256 endingEpoch);
  event IsDistributor(address indexed account, bool status);
  event Distribute(address distributor, uint256 amount);
  event SetEpochLength(uint256 startEpoch, uint256 blocks);
  /* ========== CONSTRUCTOR ========== */
  constructor(address tknAddr, address veAddr)
  {
    require(tknAddr != address(0), 'Token address cannot be zero.');  // FLEX token
    require(veAddr != address(0) , 'Vested address cannot be zero.'); // veFLEX
    token = IERC20(tknAddr);
    vested = IVested(veAddr);
    epochLengthHistory.push([0, INIT_EPOCH_LEN]);
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

 /**
  * @dev
  *   Only necessary in chain average block interval changes.
  *   Adjust epoch length in case the blockchain hash rate changes.
  */
  function setNextEpochLength(uint256 blocks) external onlyOwner {
    uint256 lastEpochBlockLen = epochLengthHistory[epochLengthHistory.length - 1][1];
    require(blocks != 0, '0 blocks is not a valid epoch length');
    require(blocks != lastEpochBlockLen, 'epoch length is the same with last epoch length');
    uint256 startEpoch = getCurrentEpoch() + 1;
    epochLengthHistory.push([startEpoch, blocks]);
    emit SetEpochLength(startEpoch, blocks);
  }

 /**
  * @dev
  *   Only necessary in chain average block interval changes.
  *   Can only update the length of the next epoch 
  *   while you are in the same epoch of calling 
  *   setNextEpochLength func.
  */
  function updateLastEpochLength(uint256 blocks) external onlyOwner {
    uint256 currentEpoch = getCurrentEpoch();
    uint256 lastEpochInEpochHistory = epochLengthHistory[epochLengthHistory.length - 1][0];
    require(lastEpochInEpochHistory - currentEpoch == 1, 'can only update next epoch length');
    uint256 lastEpochBlockLen = epochLengthHistory[epochLengthHistory.length - 1][1];
    require(blocks != 0, '0 blocks is not a valid epoch length');
    require(blocks != lastEpochBlockLen, 'epoch length is the same with last epoch length');
    epochLengthHistory[epochLengthHistory.length - 1][1] = blocks;
    emit SetEpochLength(epochLengthHistory[epochLengthHistory.length - 1][0], blocks);
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
  *   This is not current epoch, but rather the most recent rewarded epoch.
  *   Name not changed for the sake of compatibility with former implementation.
  */
  function currentEpoch() public view returns(uint256) {
    return payoutForEpoch.length;
  }

  function claim(address owner) external {
    require(owner == msg.sender, "can only claim for yourself account");
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
  * @dev 
  *   Rewarded epochs might extend to the future, but can only 
  *   claim until epochs no later than the current acutal epoch.
  */
  function _getClaimableUntilEpoch(address owner, uint256 endingEpoch) internal view returns(uint256, uint256) {
    uint256 amount;
    uint256 i;
    uint256 blockHeightAtEpochStartTime;
    uint256 totalSupply;
    for (i = claimedEpoches[owner]; i <= endingEpoch; i++) {
      blockHeightAtEpochStartTime = getEpochStartBlockHeight(i);
      if (block.number <= blockHeightAtEpochStartTime) break;
      totalSupply = vested.totalSupplyAt(blockHeightAtEpochStartTime);
      if (totalSupply > 0) {
        amount += payoutForEpoch[i].mul(vested.balanceOfAt(owner, blockHeightAtEpochStartTime)).div(totalSupply);
      }
    }
    return (amount, i - 1);
  }

  function _claimUntilEpoch(address owner, uint256 endingEpoch) internal {
    (uint256 amount, uint256 lastClaimedEpoch) = _getClaimableUntilEpoch(owner, endingEpoch);
    claimedEpoches[owner] = lastClaimedEpoch.add(1);
    emit Claim(owner, amount, lastClaimedEpoch, endingEpoch);
    token.safeTransfer(owner, amount);
  }

 /**
  * @dev 
  *   Given epoch number, get the epoch start block height.
  *   If chain block interval changes, function will handle variable epoch lengths.
  */
  function getEpochStartBlockHeight(uint256 epoch) internal view returns(uint256) {
    if (epochLengthHistory.length == 1) {
      return startBlockHeight.add(INIT_EPOCH_LEN.mul(epoch));
    } else {
      uint256 epochBlockHeight = startBlockHeight;
      uint256 epochLength;
      uint256 epochEnd;
      for (uint256 i = epochLengthHistory.length - 1; i >= 0; i--) {
        if (epoch > epochLengthHistory[i][0]) {
          epochEnd = epochLengthHistory[i][0];
          epochLength = epochLengthHistory[i][1];
          epochBlockHeight = epochBlockHeight.add(epochLength.mul(epoch.sub(epochEnd)));
          epoch = epochEnd;
        }
        if(i == 0) break;
      }
      return epochBlockHeight;
    }
  }

/**
  * @dev This is the actual current epoch.
  */
  function getCurrentEpoch() internal view returns(uint256) {
    uint256 i = 0;
    while(true) {
      if (block.number <= getEpochStartBlockHeight(i)) break;
      i++;
    }
    return i - 1;
  }
}