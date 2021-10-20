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
from brownie import Controller, FLEXCoin, veFLEX, Timelock
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
  :param: governance  `Account`  the wallet address defined as DAO Controller governance  
  :param: deploy_flex  `FLEXCoin`  generic ERC-20 to serve as the Staking Token; Preferably FLEX  
  :returns: `veFLEX`
  '''
  flex: FLEXCoin = deploy_flex
  gas_strategy   = ExponentialScalingStrategy('10 gwei', '50 gwei')
  version: str   = 'v1'
  ### Deployment ###
  return veFLEX.deploy(flex, f'vested {flex.name()}', f've{flex.symbol()}', version, { 'from': admin, 'gas_price': gas_strategy })

@mark.parametrize('version', ['v0', 'v1'])
def test_deploy_ve_flex(admin: Account, governance: Account, deploy_flex: FLEXCoin, version: str):
  '''
  TEST: Deploy veFLEX Contract
  
  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: governance  `Account`  the wallet address defined as DAO Controller governance  
  :param: deploy_flex  `FLEXCoin`  generic ERC-20 to serve as the Staking Token; Preferably FLEX  
  '''
  flex: FLEXCoin  = deploy_flex
  gas_strategy    = ExponentialScalingStrategy('10 gwei', '50 gwei')
  ### Deployment ###
  ve_flex: veFLEX = veFLEX.deploy(flex, f'vested {flex.name()}', f've{flex.symbol()}', version, { 'from': admin, 'gas_price': gas_strategy })
  assert ve_flex.name()   == f'vested { flex.name() }'
  assert ve_flex.symbol() == f've{ flex.symbol() }'
  print(f'veFLEX: { ve_flex }')
