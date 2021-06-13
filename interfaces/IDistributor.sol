// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

interface IDistributor {
  function deposit(uint, uint) external;
  function withdraw(uint, uint) external;
  function userInfo(uint, address) external view returns(uint, uint);
}