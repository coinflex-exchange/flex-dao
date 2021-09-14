#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/reward_token.py
# VERSION: 	 1.0
# CREATED: 	 2021-09-03 14:07
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contracts ###
from brownie import RewardToken
### Third-Party Packages ###
from brownie.network.gas.strategies import GasNowStrategy
from eth_account import Account
from pytest import mark
### Local Modules ###
from . import *

@fixture
def deploy_reward_token(admin: Account) -> RewardToken:
  return RewardToken.deploy({ 'from': admin })

@mark.parametrize('gas_speed', ('fast', 'standard'))
def test_deploy_reward_token(admin: Account, gas_speed: str):
  '''
  TEST: Deploy RewardToken Contract
  
  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: gas_speed  `str`  the mock speed key to be used with gas_price object; either `fast` or `standard`  
  '''
  ### Deployment ###
  gas_strategy = GasNowStrategy(gas_speed)
  reward_token = RewardToken.deploy({ 'from': admin, 'gas_price': gas_strategy })
  assert reward_token.name()   == 'FLEX Reward'
  assert reward_token.symbol() == 'FLEX'
  print(f'Reward Token: { reward_token }')
