
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import '@openzeppelin/contracts/token/ERC20/IERC20.sol';
import '@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol';
import '@openzeppelin/contracts/utils/math/SafeMath.sol';
import './DAOToken.sol';
import './LiquidityGauge.sol';
import './ProtocolGovernance.sol';
import '../interfaces/IMinter.sol';

contract GaugeProxy is ProtocolGovernance
{
  using SafeMath for uint256;
  using SafeERC20 for IERC20;

  IMinter public constant MASTER = IMinter(0xbD17B1ce622d73bD438b9E658acA5996dc394b0d);
  IERC20 public constant ESCROW = IERC20(0xbBCf169eE191A1Ba7371F30A1C344bFC498b29Cf);
  IERC20 public constant REWARD = IERC20(0x429881672B9AE42b8EbA0E26cD9C73711b891Ca5);

  IERC20 public immutable TOKEN;

  uint public pid;
  uint public totalWeight;

  address[] internal _tokens;
  mapping(address => address) public gauges; // token => gauge
  mapping(address => uint) public weights; // token => weight
  mapping(address => mapping(address => uint)) public votes; // msg.sender => votes
  mapping(address => address[]) public tokenVote; // msg.sender => token
  mapping(address => uint) public usedWeights; // msg.sender => total voting weight of user

  function tokens() external view returns(address[] memory) {
    return _tokens;
  }

  function getGauge(address _token) external view returns(address) {
    return gauges[_token];
  }

  constructor()
  {
    TOKEN = IERC20(address(new DAOToken()));
    governance = msg.sender;
  }

  // Reset votes to 0
  function reset() external {
    _reset(msg.sender);
  }

  // Reset votes to 0
  function _reset(address _owner) internal {
    address[] storage _tokenVote = tokenVote[_owner];
    uint256 _tokenVoteCnt = _tokenVote.length;
    for (uint i = 0; i < _tokenVoteCnt; i++) {
      address _token = _tokenVote[i];
      uint _votes = votes[_owner][_token];
      if (_votes > 0) {
        totalWeight = totalWeight.sub(_votes);
        weights[_token] = weights[_token].sub(_votes);
        votes[_owner][_token] = 0;
      }
    }
    delete tokenVote[_owner];
  }

  // Adjusts _owner's votes according to latest _owner's DAO Token balance
  function poke(address _owner) public
  {
    address[] memory _tokenVote = tokenVote[_owner];
    uint256 _tokenCnt = _tokenVote.length;
    uint256[] memory _weights = new uint[](_tokenCnt);
    uint256 _prevUsedWeight = usedWeights[_owner];
    uint256 _weight = ESCROW.balanceOf(_owner);
    for (uint256 i = 0; i < _tokenCnt; i++) {
      uint256 _prevWeight = votes[_owner][_tokenVote[i]];
      _weights[i] = _prevWeight.mul(_weight).div(_prevUsedWeight);
    }
    _vote(_owner, _tokenVote, _weights);
  }

  function _vote(address _owner, address[] memory _tokenVote, uint256[] memory _weights) internal
  {
    // _weights[i] = percentage * 100
    _reset(_owner);
    uint256 _tokenCnt = _tokenVote.length;
    uint256 _weight = ESCROW.balanceOf(_owner);
    uint256 _totalVoteWeight = 0;
    uint256 _usedWeight = 0;
    for (uint256 i = 0; i < _tokenCnt; i++) {
      _totalVoteWeight = _totalVoteWeight.add(_weights[i]);
    }
    for (uint256 i = 0; i < _tokenCnt; i++) {
      address _token = _tokenVote[i];
      address _gauge = gauges[_token];
      uint256 _tokenWeight = _weights[i].mul(_weight).div(_totalVoteWeight);
      if (_gauge != address(0x0)) {
        _usedWeight = _usedWeight.add(_tokenWeight);
        totalWeight = totalWeight.add(_tokenWeight);
        weights[_token] = weights[_token].add(_tokenWeight);
        tokenVote[_owner].push(_token);
        votes[_owner][_token] = _tokenWeight;
      }
    }
    usedWeights[_owner] = _usedWeight;
  }

  // Vote with DAO Token on a gauge
  function vote(address[] calldata _tokenVote, uint256[] calldata _weights) external
  {
    require(_tokenVote.length == _weights.length);
    _vote(msg.sender, _tokenVote, _weights);
  }

  // Add new token gauge
  function addGauge(address _token) external
  {
    require(msg.sender == governance, "!gov");
    require(gauges[_token] == address(0x0), "exists");
    gauges[_token] = address(new Gauge(_token));
    _tokens.push(_token);
  }


  // Sets Minter PID
  function setPID(uint _pid) external
  {
    require(msg.sender == governance, "!gov");
    require(pid == 0, "pid has already been set");
    require(_pid > 0, "invalid pid");
    pid = _pid;
  }


  // Deposits fTOKEN into Minter
  function deposit() public
  {
    require(pid > 0, "pid not initialized");
    IERC20 _token = TOKEN;
    uint _balance = _token.balanceOf(address(this));
    _token.safeApprove(address(MASTER), 0);
    _token.safeApprove(address(MASTER), _balance);
    MASTER.deposit(pid, _balance);
  }

  // Fetches token
  function collect() public
  {
    (uint _locked, ) = MASTER.userInfo(pid, address(this));
    MASTER.withdraw(pid, _locked);
    deposit();
  }

  function length() external view returns(uint)
  {
    return _tokens.length;
  }

  function distribute() external
  {
    collect();
    uint _balance = REWARD.balanceOf(address(this));
    if (_balance > 0 && totalWeight > 0) {
      for (uint i = 0; i < _tokens.length; i++) {
        address _token = _tokens[i];
        address _gauge = gauges[_token];
        uint _reward = _balance.mul(weights[_token]).div(totalWeight);
        if (_reward > 0) {
          REWARD.safeApprove(_gauge, 0);
          REWARD.safeApprove(_gauge, _reward);
          ILiquidityGauge(_gauge).notifyRewardAmount(_reward);
        }
      }
    }
  }
}