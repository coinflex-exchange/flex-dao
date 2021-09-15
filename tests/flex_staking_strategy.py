#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/flex_staking_strategy.py
# VERSION: 	 1.0
# CREATED: 	 2021-09-15 15:40
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contracts ###
from brownie import FLEXStakingStrategy, Controller, DAOToken, StakingRewards, Timelock
### Third-Party Packages ###
from brownie.network.gas.strategies import GasNowStrategy
from eth_account import Account
from pytest import mark
### Local Modules ###
from . import *
from .controller import deploy_controller
from .daotoken import deploy_daotoken
from .reward_token import deploy_reward_token # used by deploy_staking_rewards
from .staking_rewards import deploy_staking_rewards
from .timelock import deploy_timelock

@fixture
def test_deploy_flex_staking_strategy(admin: Account, governance: Account, \
  deploy_daotoken: DAOToken, deploy_controller: Controller, \
    deploy_staking_rewards: StakingRewards, deploy_timelock: Timelock) -> FLEXStakingStrategy:
  '''
  FIXTURE: Returns a deployed FLEXStakingStrategy contract using given Controller (DAO), Timelock, 
  StakingRewards and use DAOToken as want to be used by other contract testing.

  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: governance  `Account`  the wallet address defined as DAO Controller governance  
  :param: deploy_daotoken  `DAOToken`  a generic ERC-20 Token used as want for the given Strategy; Preferably FLEX  
  :param: deploy_controller  `Controller`  the main contract of the DAO  
  :param: deploy_staking_rewards  `StakingRewards`  a deployed StakingRewards contract denoting ratio and reward due to users  
  :param: deploy_timelock  `Timelock`  a deployed Timelock contract to limit the distribution of RewardToken  
  :returns:  `FLEXStakingStrategy`
  '''
  controller   = deploy_controller
  timelock     = deploy_timelock
  rewards      = deploy_staking_rewards
  want         = deploy_daotoken
  gas_strategy = GasNowStrategy('fast')
  ### Deployment ###
  return FLEXStakingStrategy.deploy(rewards, want, governance, controller, timelock, { 'from': admin, 'gas_price': gas_strategy })

@mark.parametrize('gas_speed', ('standard', 'fast'))
def test_deploy_flex_staking_strategy(admin: Account, governance: Account, \
  deploy_daotoken: DAOToken, deploy_controller: Controller, \
    deploy_staking_rewards: StakingRewards, deploy_timelock: Timelock, gas_speed: str):
  '''
  TEST: Deploy a FLEXStakingStrategy contract using given Controller (DAO), Timelock, StakingRewards and use DAOToken as want

  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: governance  `Account`  the wallet address defined as DAO Controller governance  
  :param: deploy_daotoken  `DAOToken`  a generic ERC-20 Token used as want for the given Strategy; Preferably FLEX  
  :param: deploy_controller  `Controller`  the main contract of the DAO  
  :param: deploy_staking_rewards  `StakingRewards`  a deployed StakingRewards contract denoting ratio and reward due to users  
  :param: deploy_timelock  `Timelock`  a deployed Timelock contract to limit the distribution of RewardToken  
  :param: gas_speed  `str`  the mock speed key to be used with gas_price object; either `fast` or `standard`  
  '''
  controller   = deploy_controller
  timelock     = deploy_timelock
  rewards      = deploy_staking_rewards
  want         = deploy_daotoken
  gas_strategy = GasNowStrategy(gas_speed)
  ### Deployment ###
  flex_staking_strategy: FLEXStakingStrategy = FLEXStakingStrategy.deploy(rewards, want, governance, controller, timelock, { 'from': admin, 'gas_price': gas_strategy })
  print(f'FLEXStakingStrategy: { flex_staking_strategy }')
