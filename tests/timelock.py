#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/timelock.py
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
from brownie.exceptions import VirtualMachineError
from eth_account import Account
from pytest import mark, raises
### Local Modules ###
from . import *

@fixture
def deploy_timelock(admin: Account, gas_price: dict) -> Timelock:
  '''
  FIXTURE: Deploy a Timelock contract for 14 days to be used by other contracts' testing.

  ---
  :param: admin  `Account`  the wallet address to deploy the contract from
  :param: gas_price  `dict`  the mock gas_price object as it would be like to receive from Gas Station API  
  :returns: `Timelock`  
  '''
  delay: int     = 14 * 24 * 60 * 60
  gas_speed: str = 'fast'
  return Timelock.deploy(admin, delay, {'from': admin, 'gas_limit': gas_price[gas_speed] })

@mark.parametrize('delay, gas_speed', (
  (2  * 24 * 60 * 60, 'fast'),     # 2 days
  (14 * 24 * 60 * 60, 'standard'), # 14 days
))
def test_deploy_timelock(admin: Account, delay: int, gas_price: dict, gas_speed: str):
  '''
  TEST: Deploy Timelock Contract
  
  ---
  :param: admin  `Account`  the wallet address to deploy the contract from
  :param: delay  `int`  delay in seconds  
  :param: gas_price  `dict`  the mock gas_price object as it would be like to receive from Gas Station API
  :param: gas_speed  `str`  the mock speed key to be used with gas_price object; either `fast` or `standard`
  '''
  limit = Timelock.deploy.estimate_gas(admin, delay, {'from': admin}) * gas_price[gas_speed]
  ### Deployment ###
  timelock = Timelock.deploy(admin, delay, { 'from': admin, 'gas_limit': limit })
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
