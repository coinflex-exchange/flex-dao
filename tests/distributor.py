#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/distributor.py
# VERSION: 	 1.0
# CREATED: 	 2021-09-03 14:07
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contracts ###
from brownie import Distributor, RewardToken
### Third-Party Packages ###
from brownie.network.gas.strategies import GasNowStrategy
from eth_account import Account
from pytest import fixture, mark
### Local Modules ###
from . import *
from .reward_token import deploy_reward_token
from .timelock import deploy_timelock

@fixture
def deploy_distributor(admin: Account, deploy_reward_token: RewardToken) -> Distributor:
  '''
  FIXTURE: Deploy a Distributor contract for given RewardToken  
  at rate of 1 token per block for 10 blocks to be used by other contracts' testing.  

  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: deploy_reward_token  `RewardToken`  the deployed RewardToken contract  
  :returns:  `Distributor`  
  '''
  reward_token: RewardToken = deploy_reward_token
  devfund: Account          = admin
  token_per_block: int      = 1
  start_block: int          = 0
  end_block: int            = 10
  return Distributor.deploy(reward_token, devfund, token_per_block, start_block, end_block, { 'from': admin })

@mark.parametrize('token_per_block, start_block, end_block, gas_speed', (
  ( 1,  0,  10,     'fast'), 
  ( 2,  0,  10, 'standard'),
  ( 3,  3, 100,     'fast'),
  ( 4, 50, 100, 'standard')
))
def test_deploy_distributor(admin: Account, \
  token_per_block: int, start_block: int, end_block: int, \
    gas_speed: str, deploy_reward_token: RewardToken):
  '''
  TEST: Deploy Distributor Contract
  
  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: token_per_block  `int`  the amount of tokens to be distributed per block
  :param: start_block  `int`  the beginning block to begin distribution  
  :param: end_block  `int`  the ending block to be stop distribution  
  :param: gas_speed  `str`  the mock speed key to be used with gas_price object; either `fast` or `standard`  
  :param: deploy_reward_token  `RewardToken`  the deployed RewardToken contract
  '''
  reward_token: RewardToken = deploy_reward_token
  devfund: Account          = admin
  ### Deployment ###
  gas_strategy = GasNowStrategy(gas_speed)
  distributor  = Distributor.deploy(reward_token, devfund, token_per_block, start_block, end_block, { 'from': admin, 'gas_price': gas_strategy })
  print(f'Distributor: { distributor }')
