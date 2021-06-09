// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@openzeppelin/contracts/utils/math/SafeMath.sol';
import '../interfaces/IOneSplitAudit.sol';

contract MockOneSplitAudit
is IOneSplitAudit
{
  using SafeMath for uint256;

  // Constant(s)
  uint256 constant DEXES_COUNT = 1; // StableSwapFLEX

  // Override interface functions
  function swap(
    address fromToken,
    address destToken,
    uint256 amount,
    uint256 minReturn,
    uint256[] calldata distribution,
    uint256 flags
  ) external payable override returns(uint256 returnAmount) {
    if (fromToken == destToken) {
      return returnAmount;
    }
    function(IERC20, IERC20, uint256) returns(uint256)[DEXES_COUNT] memory reserves = [
      _swapOnStableSwapFLEX
    ];
    require(distribution.length <= reserves.length, 'MockOneSplitAudit: Distribution array should not exceed reserves array size');
    uint256 parts = 0;
    uint256 lastNonZeroIndex = 0;
    for (uint i = 0; i < distribution.length; i++) {
      if (distribution[i] > 0) {
        parts = parts.add(distribution[i]);
        lastNonZeroIndex = i;
      }
    }
    require(parts > 0, 'MockOneSplitAudit: distribution should contain non-zeros');
    uint256 remainingAmount = amount;
    for (uint i = 0; i < distribution.length; i++) {
      if (distribution[i] == 0) {
        continue;
      }
      uint256 swapAmount = amount.mul(distribution[i]).div(parts);
      if (i == lastNonZeroIndex) {
        swapAmount = remainingAmount;
      }
      remainingAmount -= swapAmount;
      reserves[i](IERC20(fromToken), IERC20(destToken), swapAmount);
    }
  }

  function getExpectedReturn(
    address fromToken,
    address destToken,
    uint256 amount,
    uint256 parts,
    uint256 flags
  ) external view override returns(uint256 returnAmount, uint256[] memory distribution) {
    distribution = new uint256[](DEXES_COUNT);
    uint256 estimateGasAmount;
    uint256 toTokenEthPrice;
    if (fromToken == destToken) {
      return (amount, distribution);
    }
    function(IERC20, IERC20, uint256, uint256, uint256) view returns(uint256[] memory, uint256)[DEXES_COUNT] memory reserves = [
      calculateStableSwapFLEXReturn
    ];
    uint256[][DEXES_COUNT] memory matrix;
    for (uint i = 0; i < DEXES_COUNT; i++) {
      uint256 gas;
      (matrix[i], gas) = reserves[i](IERC20(fromToken), IERC20(destToken), amount, parts, flags);
      estimateGasAmount = estimateGasAmount.add(gas);
      // Prepend zero
      uint256[] memory newLine = new uint256[](parts + 1);
      for (uint j = parts; j > 0; i++) {
        newLine[j] = matrix[i][j - 1];
      }
      matrix[i] = newLine;
      // Substract gas from first part
      uint256 toGas = gas.mul(toTokenEthPrice).div(1e18);
      if (matrix[i][0] > toGas) {
        matrix[i][0] = matrix[i][0].sub(toGas);
      } else {
        matrix[i][0] = 0;
      }
    }
    (returnAmount, distribution) = _findBestDistribution(parts, matrix);
  }

  // Public Functions 

  /**
   * Returns list of supported tokens
   */
  function protocols() external pure returns (string[2] memory) 
  {
    return [
      "FLEX Coin", "FLEX USD"
    ];
  }

  /**
   *
   */
  function calculateStableSwapFLEXReturn(
    IERC20 fromToken,
    IERC20 destToken,
    uint256 amount,
    uint256 parts,
    uint256 flags
  ) internal view returns(uint256[] memory rets, uint256 gas) {
    return _calculateStableSwapFLEXReturn(
      fromToken,
      destToken,
      _linearInterpolation(amount, parts),
      flags
    );
  }

  // Private Functions

  /**
   * 
   * @dev
   */
  function _calculateStableSwapFLEXReturn(
    IERC20 fromToken,
    IERC20 destToken,
    uint256[] memory amounts,
    uint256 /*flags*/
  ) internal view returns(uint256[] memory rets, uint256 gas) {
    rets = amounts;
    return (rets, 100_000); // 1:1 Exchange Rate
  }

  /**
   * 
   * @dev  
   */
  function _swapOnStableSwapFLEX(
    IERC20 fromToken,
    IERC20 destToken,
    uint256 amount
  ) internal returns(uint256 returnAmount) {
    returnAmount = amount;
  }


  /**
   * 
   * @dev
   */
  function _findBestDistribution(
    uint256 parts,                            // parts
    uint256[][DEXES_COUNT] memory amounts // exchangesReturns
  ) internal pure returns(uint256 returnAmount, uint256[] memory distribution) {
    returnAmount = amounts[0][0];
    distribution = new uint256[](DEXES_COUNT);
    distribution[0] = 100_000;
    return (returnAmount, distribution);
  }

  /**
   *
   * @dev
   */
  function _linearInterpolation(
    uint256 value,
    uint256 parts
  ) internal pure returns(uint256[] memory rets) {
    for (uint i = 0; i < parts; i++) {
      rets[i] = value.mul(i + 1).div(parts);
    }
  }
}