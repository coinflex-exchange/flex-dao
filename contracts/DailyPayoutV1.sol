// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/access/Ownable.sol';
import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol';
import '@openzeppelin/contracts/utils/math/SafeMath.sol';
import '../interfaces/IVested.sol';

contract DailyPayoutV1 is Ownable
{
  using SafeERC20 for IERC20;
  using SafeMath for uint256;

  /* =========  MEMBER VARS ========== */
  IERC20 immutable public token;  // FLEX token
  IVested immutable public vested; // veFLEX
  uint256 public constant EPOCH_BLOCKS = 17280; // average blocks in 1 day with 5s block interval
  uint256 public startBlockHeight;
  uint256[] public payoutForEpoch;
  mapping(address => uint256) public claimedEpoches;
  mapping(address => bool) public isDistributor;

  /* ===========   EVENTS  =========== */
  event Claim(address indexed from, uint256 amount, uint256 endingEpoch);
  event UpdateDistributor(address indexed account, bool status);
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
    emit UpdateDistributor(account, true);
  }

  function removeDistributor(address account) public onlyOwner {
    isDistributor[account] = false;
    emit UpdateDistributor(account, false);
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

  function currentEpoch() public view returns(uint256) {
    return payoutForEpoch.length;
  }

  function claim(address owner) external {
    uint256 epoch = currentEpoch();
    if (epoch > 0) {
      _claimUntilEpoch(owner, epoch.sub(1));
    }
  }

  function getClaimable(address owner) external view returns(uint256) {
    uint256 epoch = currentEpoch();
    if (epoch == 0) return 0;
    return _getClaimableUntilEpoch(owner, epoch.sub(1));
  }

  function _getClaimableUntilEpoch(address owner, uint256 endingEpoch) internal view returns(uint256) {
    uint256 amount = 0;
    for (uint256 i = claimedEpoches[owner]; i <= endingEpoch; i++) {
      uint256 totalSupply = vested.totalSupplyAt(getEpochBlockHeight(i));
      if (totalSupply > 0) {
        amount += payoutForEpoch[i].mul(vested.balanceOfAt(owner, getEpochBlockHeight(i))).div(totalSupply);
      }
    }
    return amount;
  }

  function _claimUntilEpoch(address owner, uint256 endingEpoch) internal {
    uint256 amount = _getClaimableUntilEpoch(owner, endingEpoch);
    claimedEpoches[owner] = endingEpoch.add(1);
    emit Claim(owner, amount, endingEpoch);
    token.safeTransfer(owner, amount);
  }

  function getEpochBlockHeight(uint256 epoch) internal view returns(uint256) {
    return startBlockHeight.add(EPOCH_BLOCKS.mul(epoch));
  }
}