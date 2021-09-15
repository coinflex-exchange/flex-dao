#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/ve_flex.py
# VERSION: 	 1.0
# CREATED: 	 2021-09-03 14:07
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contracts ###
from brownie import Controller, FLEXCoin, fVault, Timelock
### Third-Party Packages ###
from brownie.network.gas.strategies import GasNowStrategy
from eth_account import Account
from pytest import mark
### Local Modules ###
from . import *
from .controller import deploy_controller
from .flex import deploy_flex
from .timelock import deploy_timelock

@fixture
def deploy_ve_flex(admin: Account, governance: Account, \
  deploy_controller: Controller, deploy_flex: FLEXCoin, deploy_timelock: Timelock) -> fVault:
  '''
  FIXTURE: Returns deployed fVault contract to be used by other contract testing

  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: governance  `Account`  the wallet address defined as DAO Controller governance  
  :param: deploy_controller  `Controller`  the main contract of the DAO  
  :param: deploy_flex  `FLEXCoin`  generic ERC-20 to serve as the Staking Token; Preferably FLEX  
  :param: deploy_timelock  `Timelock`  
  :returns: `fVault`
  '''
  controller: Controller = deploy_controller
  flex: FLEXCoin         = deploy_flex
  timelock: Timelock     = deploy_timelock
  gas_strategy           = GasNowStrategy('fast')
  ### Deployment ###
  return fVault.deploy(flex, governance, timelock, controller, { 'from': admin, 'gas_price': gas_strategy })

@mark.parametrize('gas_speed', ('fast', 'standard'))
def test_deploy_ve_flex(admin: Account, governance: Account, \
  deploy_controller: Controller, deploy_flex: FLEXCoin, deploy_timelock: Timelock, gas_speed: str):
  '''
  TEST: Deploy fVault Contract
  
  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: governance  `Account`  the wallet address defined as DAO Controller governance  
  :param: deploy_controller  `Controller`  the main contract of the DAO  
  :param: deploy_flex  `FLEXCoin`  generic ERC-20 to serve as the Staking Token; Preferably FLEX  
  :param: deploy_timelock  `Timelock`  
  :param: gas_speed  `str`  the mock speed key to be used with gas_price object; either `fast` or `standard`  
  '''
  controller: Controller = deploy_controller
  flex: FLEXCoin         = deploy_flex
  timelock: Timelock     = deploy_timelock
  gas_strategy           = GasNowStrategy(gas_speed)
  ### Deployment ###
  ve_flex        = fVault.deploy(flex, governance, timelock, controller, { 'from': admin, 'gas_price': gas_strategy })
  assert ve_flex.name()   == f'flex { flex.name() }'
  assert ve_flex.symbol() == f'f{ flex.symbol() }'
  print(f'veFLEX: { ve_flex }')
