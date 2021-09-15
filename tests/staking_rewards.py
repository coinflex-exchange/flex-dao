#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/staking_rewards.py
# VERSION: 	 1.0
# CREATED: 	 2021-09-03 14:07
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contracts ###
from brownie import FLEXCoin, RewardToken, StakingRewards
### Third-Party Packages ###
from brownie.network.gas.strategies import GasNowStrategy
from eth_account import Account
from pytest import fixture, mark
### Local Modules ###
from . import *
from .flex import deploy_flex
from .reward_token import deploy_reward_token

@fixture
def deploy_staking_rewards(admin: Account, deploy_flex: FLEXCoin, deploy_reward_token: RewardToken) -> StakingRewards:
  '''
  FIXTURE: Returns a StakingRewards contract given flex and RewardToken to be used by other contracts' testing.  

  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: deploy_flex  `FLEXCoin`  generic ERC-20 to serve as the Staking Token  
  :param: deploy_reward_token  `RewardToken`  ERC-20 compliant Reward Token to be given out as rewards  
  :returns:  `StakingRewards`  
  '''
  flex: FLEXCoin            = deploy_flex
  reward_token: RewardToken = deploy_reward_token
  gas_strategy              = GasNowStrategy('fast')
  return StakingRewards.deploy(reward_token, flex, { 'from': admin, 'gas_price': gas_strategy })

@mark.parametrize('gas_speed', ('fast', 'standard'))
def test_deploy_staking_rewards(admin: Account,  deploy_flex: FLEXCoin, deploy_reward_token: RewardToken, gas_speed: str):
  '''
  TEST: Deploy a StakingRewards contract given flex and RewardToken

  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: deploy_flex  `FLEXCoin`  generic ERC-20 to serve as the Staking Token  
  :param: deploy_reward_token  `RewardToken`  ERC-20 compliant Reward Token to be given out as rewards  
  :param: gas_speed  `str`  the mock speed key to be used with gas_price object; either `fast` or `standard`  
  '''
  flex: FLEXCoin            = deploy_flex
  reward_token: RewardToken = deploy_reward_token
  gas_strategy              = GasNowStrategy(gas_speed)
  ### Deployment ###
  staking_rewards: StakingRewards = StakingRewards.deploy(reward_token, flex, { 'from': admin, 'gas_price': gas_strategy })
  print(f'StakingRewards: { staking_rewards }')
