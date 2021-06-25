// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/access/Ownable.sol';
import '@openzeppelin/contracts/token/ERC20/ERC20.sol';

// RewardToken with Governance.
contract RewardToken is ERC20("FLEX Reward", "FLEX"), Ownable {
  /// @notice Creates `_amount` token to `_to`. Must only be called by the owner (Distributor).
  function mint(address _to, uint256 _amount) public onlyOwner {
    _mint(_to, _amount);
  }
}