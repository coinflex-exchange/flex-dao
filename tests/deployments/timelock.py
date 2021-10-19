#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/deployments/timelock.py
# VERSION: 	 1.0
# CREATED: 	 2021-09-03 14:07
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contracts ###
from brownie import Timelock
### Third-Party Packages ###
from brownie.network.gas.strategies import ExponentialScalingStrategy
from brownie.exceptions import VirtualMachineError
from eth_account import Account
from pytest import mark, raises
### Local Modules ###
from tests import *

@fixture
def deploy_timelock(admin: Account) -> Timelock:
  '''
  FIXTURE: Deploy a Timelock contract for 14 days to be used by other contracts' testing.

  ---
  :param: admin  `Account`  the wallet address to deploy the contract from
  :returns: `Timelock`  
  '''
  delay: int     = 14 * 24 * 60 * 60
  gas_strategy   = ExponentialScalingStrategy('10 gwei', '50 gwei')
  return Timelock.deploy(admin, delay, {'from': admin, 'gas_price': gas_strategy })

@mark.parametrize('delay', (
  2  * 24 * 60 * 60, # 2 days
  14 * 24 * 60 * 60  # 14 days
))
def test_deploy_timelock(admin: Account, delay: int):
  '''
  TEST: Deploy Timelock Contract
  
  ---
  :param: admin  `Account`  the wallet address to deploy the contract from
  :param: delay  `int`  delay in seconds  
  '''
  gas_strategy       = ExponentialScalingStrategy('10 gwei', '50 gwei')
  ### Deployment ###
  timelock: Timelock = Timelock.deploy(admin, delay, { 'from': admin, 'gas_price': gas_strategy })
  print(f'Timelock: { timelock }')

@mark.parametrize('delay', (
  0,                # 0 day
  60 * 24 * 60 * 60 # 60 days
))
def test_failed_deploy_timelock(admin: Account, delay: int):
  '''
  TEST: Failed Deployments of Timelock Contract
  
  ---
  :param: admin  `Account`  the wallet address to deploy the contract from
  :param: delay  `int`  delay in seconds  
  '''
  ### Deployment ###
  with raises(VirtualMachineError) as err:
    timelock = Timelock.deploy(admin, delay, { 'from': admin })
  print(f'Error: { err }')
