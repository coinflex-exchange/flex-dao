// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol';
import '@openzeppelin/contracts/utils/Address.sol';
import '@openzeppelin/contracts/utils/math/SafeMath.sol';

import '../../interfaces/IVault.sol';
// import '../interfaces/staking-rewards.sol';
import '../../interfaces/IDistributor.sol';
import '../../interfaces/IController.sol';

// Strategy Contract Basics

abstract contract BaseStrategy {
  using SafeERC20 for IERC20;
  using Address for address;
  using SafeMath for uint256;

  // Perfomance fees - start with 20%
  uint256 public performanceTreasuryFee = 2000;
  uint256 public constant performanceTreasuryMax = 10000;

  // Withdrawal fee 0%
  // - 0% to treasury
  uint256 public withdrawalTreasuryFee = 0;
  uint256 public constant withdrawalTreasuryMax = 100000;

  // Tokens
  address public want;

  // User accounts
  address public governance;
  address public controller;
  address public timelock;

  mapping(address => bool) public harvesters;

  constructor(address _want, address _governance, address _controller, address _timelock)
  {
    require(_want       != address(0));
    require(_governance != address(0));
    require(_controller != address(0));
    require(_timelock   != address(0));
    want       = _want;
    governance = _governance;
    controller = _controller;
    timelock   = _timelock;
  }

  // **** Modifiers **** //

  modifier onlyBenevolent {
    require(harvesters[msg.sender] || msg.sender == governance);
    _;
  }

  // **** Views **** //

  function balanceOfWant() public view returns(uint256) {
    return IERC20(want).balanceOf(address(this));
  }

  function balanceOfPool() public virtual view returns(uint256);

  function balanceOf() public view returns(uint256) {
    return balanceOfWant().add(balanceOfPool());
  }

  function getName() external virtual pure returns(string memory);

  // **** Setters **** //

  function whitelistHarvesters(address[] calldata _harvesters)
    external
  {
    require(msg.sender == governance || harvesters[msg.sender], 'not authorized');
    for (uint i = 0; i < _harvesters.length; i++) {
      harvesters[_harvesters[i]] = true;
    }
  }

  function revokeHarvesters(address[] calldata _harvesters)
    external
  {
    require(msg.sender == governance, 'not authorized');
    for (uint i = 0; i < _harvesters.length; i++) {
      harvesters[_harvesters[i]] = false;
    }
  }

  function setWithdrawalTreasuryFee(uint256 _withdrawalTreasuryFee)
    external
  {
    require(msg.sender == timelock, '!timelock');
    withdrawalTreasuryFee = _withdrawalTreasuryFee;
  }

  function setPerformanceTreasuryFee(uint256 _performanceTreasuryFee)
    external
  {
    require(msg.sender == timelock, '!timelock');
    performanceTreasuryFee = _performanceTreasuryFee;
  }

  function setGovernance(address _governance)
    external
  {
    require(msg.sender == governance, '!governance');
    governance = _governance;
  }

  function setTimelock(address _timelock)
    external
  {
    require(msg.sender == timelock, '!timelock');
    timelock = _timelock;
  }

  function setController(address _controller) external {
    require(msg.sender == timelock, '!timelock');
    controller = _controller;
  }

  // **** State mutations **** //
  function deposit() public virtual;

  // Controller only function for creating additional rewards from dust
  function withdraw(IERC20 _asset) external returns(uint256 balance) {
    require(msg.sender == controller, '!controller');
    require(want != address(_asset), 'want');
    balance = _asset.balanceOf(address(this));
    _asset.safeTransfer(controller, balance);
  }

  // Withdraw partial funds, normally used with a vault withdrawal
  function withdraw(uint256 _amount)
    external
  {
    require(msg.sender == controller, '!controller');
    uint256 _balance = IERC20(want).balanceOf(address(this));
    if (_balance < _amount) {
      _amount = _withdrawSome(_amount.sub(_balance));
      _amount = _amount.add(_balance);
    }
    uint256 _feeTreasury = _amount.mul(withdrawalTreasuryFee).div(
      withdrawalTreasuryMax
    );
    IERC20(want).safeTransfer(
      IController(controller).treasury(),
      _feeTreasury
    );
    address _vault = IController(controller).vaults(address(want));
    require(_vault != address(0), '!vault'); // additional protection so we don't burn the funds
    IERC20(want).safeTransfer(_vault, _amount.sub(_feeTreasury));
  }

  // Withdraw funds, used to swap between strategies
  function withdrawForSwap(uint256 _amount)
    external returns(uint256 balance)
  {
    require(msg.sender == controller, '!controller');
    _withdrawSome(_amount);
    balance = IERC20(want).balanceOf(address(this));
    address _vault = IController(controller).vaults(address(want));
    require(_vault != address(0), '!vault');
    IERC20(want).safeTransfer(_vault, balance);
  }

  // Withdraw all funds, normally used when migrating strategies
  function withdrawAll()
    external returns(uint256 balance)
  {
    require(msg.sender == controller, '!controller');
    _withdrawAll();
    balance = IERC20(want).balanceOf(address(this));
    address _vault = IController(controller).vaults(address(want));
    require(_vault != address(0), '!vault'); // additional protection so we don't burn the funds
    IERC20(want).safeTransfer(_vault, balance);
  }

  function _withdrawAll()
    internal
  {
    _withdrawSome(balanceOfPool());
  }

  function _withdrawSome(uint256 _amount) internal virtual returns(uint256);

  function harvest() public virtual;

  // **** Emergency functions ****

  function execute(address _target, bytes memory _data)
    public
    payable
    returns(bytes memory response)
  {
    require(msg.sender == timelock, '!timelock');
    require(_target != address(0), '!target');
    // call contract in current context
    assembly {
      let succeeded := delegatecall(sub(gas(), 5000), _target, add(_data, 0x20), mload(_data), 0, 0)
      let size := returndatasize()
      response := mload(0x40)
      mstore(0x40, add(response, and(add(add(size, 0x20), 0x1f), not(0x1f))))
      mstore(response, size)
      returndatacopy(add(response, 0x20), 0, size)
      switch iszero(succeeded)
      case 1 {
        // throw if delegatecall failed
        revert(add(response, 0x20), size)
      }
    }
  }

  function _distributePerformanceFeesAndDeposit()
    internal
  {
    uint256 _want = IERC20(want).balanceOf(address(this));
    if (_want > 0) {
      // Treasury fees
      IERC20(want).safeTransfer(
        IController(controller).treasury(),
        _want.mul(performanceTreasuryFee).div(performanceTreasuryMax)
      );
      deposit();
    }
  }
}