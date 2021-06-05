// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IVaultConverter
{
  function convert(
    address _refundExcess, // address to send the excess amount when adding liquidity
    uint256 _amount,
    bytes calldata _data
  ) external returns (uint256);
}
