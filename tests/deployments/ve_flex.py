#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/deployments/ve_flex.py
# VERSION: 	 1.0
# CREATED: 	 2021-09-03 14:07
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contracts ###
from brownie import FLEXCoin, veFLEX, reverts
from brownie.network import Chain
### Third-Party Packages ###
from brownie.network.gas.strategies import ExponentialScalingStrategy
from eth_account import Account
from pytest import mark
### Local Modules ###
from tests import *
from .flex import deploy_flex

@fixture
def deploy_ve_flex(admin: Account, deploy_flex: FLEXCoin) -> veFLEX:
  '''
  FIXTURE: Returns deployed veFLEX contract to be used by other contract testing

  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: deploy_flex  `FLEXCoin`  generic ERC-20 to serve as the Staking Token; Preferably FLEX  
  :returns: `veFLEX`
  '''
  flex: FLEXCoin = deploy_flex
  gas_strategy   = ExponentialScalingStrategy('10 gwei', '50 gwei')
  version: str   = 'v1'
  ### Deployment ###
  return veFLEX.deploy(flex, f'vested {flex.name()}', f've{flex.symbol()}', version, { 'from': admin, 'gas_price': gas_strategy })

@mark.parametrize('version', ['v0', 'v1'])
def test_deploy_ve_flex(admin: Account, deploy_flex: FLEXCoin, version: str):
  '''
  TEST: Deploy veFLEX Contract
  
  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: deploy_flex  `FLEXCoin`  generic ERC-20 to serve as the Staking Token; Preferably FLEX  
  '''
  flex: FLEXCoin  = deploy_flex
  gas_strategy    = ExponentialScalingStrategy('10 gwei', '50 gwei')
  ### Deployment ###
  ve_flex: veFLEX = veFLEX.deploy(flex, f'vested {flex.name()}', f've{flex.symbol()}', version, { 'from': admin, 'gas_price': gas_strategy })
  assert ve_flex.name()   == f'vested { flex.name() }'
  assert ve_flex.symbol() == f've{ flex.symbol() }'
  print(f'veFLEX: { ve_flex }')

def test_stake_and_withdraw(admin: Account, deploy_ve_flex: veFLEX):
  ve_flex = deploy_ve_flex
  chain   = Chain()
  
  # admin stake some flex
  unlock_time  = chain.time() + (4 * 7 * 86400) # 4 weeks in seconds
  extent_unlock_time  = chain.time() + (8 * 7 * 86400) # 8 weeks in seconds
  invalid_unlock_time =  chain.time() + (5 * 365 * 86400) # longer than 4 years
  ve_flex.create_lock(1e18, unlock_time, { 'from': admin, 'gas_price': 1e9 })
  assert ve_flex.supply() == 1e18

  # increase amount 
  ve_flex.increase_amount(1e18, { 'from': admin, 'gas_price': 1e9 })
  assert ve_flex.supply() == 2e18

  # increase unlock_time
  ve_flex.increase_unlock_time(extent_unlock_time, { 'from': admin, 'gas_price': 1e9 })

  # set invalid unlock time
  with reverts('Voting lock can be 4 years max'):
    ve_flex.increase_unlock_time(invalid_unlock_time, { 'from': admin, 'gas_price': 1e9 })

  # time travel
  chain.sleep(4 * 7 * 86400)

  # withdraw
  with reverts("The lock didn't expire"):
    ve_flex.withdraw({ 'from': admin, 'gas_price': 1e9 })
  
  # time travel
  chain.sleep(4 * 7 * 86400)
    
  ve_flex.withdraw({ 'from': admin, 'gas_price': 1e9 })
  assert ve_flex.supply() == 0