#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/deployments/distributor.py
# VERSION: 	 1.0
# CREATED: 	 2021-10-14 10:21
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contracts ###
from brownie import FLEXCoin, DailyPayout, Distributor, QuarterlyPayout
### Third-Party Packages ###
from brownie.network.gas.strategies import ExponentialScalingStrategy
from eth_account import Account
from pytest import fixture, mark
### Local Modules ###
from tests import *
from .daily_payout import deploy_daily_payout
from .flex import deploy_flex
from .quarterly_payout import deploy_quarterly_payout
from .ve_flex import deploy_ve_flex # used by `deploy_daily_payout` and `deploy_quarterly_payout`

@fixture
def deploy_daily_distributor(admin: Account, deploy_flex: FLEXCoin, deploy_daily_payout: DailyPayout) -> Distributor:
  '''
  FIXTURE: Deploy DailyPayout Contract with its payout set to DailyPayout contract deployed

  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: deploy_flex  `FLEXCoin`  generic ERC-20 to serve as the Staking Token  
  :param: deploy_daily_payout  `DailyPayout`  Payout contract with daily epoch  
  :returns: `Distributor`
  '''
  flex: FLEXCoin      = deploy_flex
  payout: DailyPayout = deploy_daily_payout
  gas_strategy        = ExponentialScalingStrategy('10 gwei', '50 gwei')
  ### Deployment ###
  return Distributor.deploy(payout, flex, { 'from': admin, 'gas_price': gas_strategy })

@fixture
def deploy_quarterly_distributor(admin: Account, deploy_flex: FLEXCoin, deploy_quarterly_payout: QuarterlyPayout) -> Distributor:
  '''
  FIXTURE: Deploy Distributor Contract with its payout set to QuarterlyPayout contract deployed

  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: deploy_flex  `FLEXCoin`  generic ERC-20 to serve as the Staking Token  
  :param: deploy_quarterly_payout  `QuarterlyPayout`  Payout contract with 13 week epoch  
  :returns: `QuarterlyPayout`
  '''
  flex: FLEXCoin          = deploy_flex
  payout: QuarterlyPayout = deploy_quarterly_payout
  gas_strategy            = ExponentialScalingStrategy('10 gwei', '50 gwei')
  ### Deployment ###
  return Distributor.deploy(payout, flex, { 'from': admin, 'gas_price': gas_strategy })

def test_deploy_daily_distributor(admin: Account, deploy_flex: FLEXCoin, deploy_daily_payout: DailyPayout):
  '''
  TEST: Deploy DailyPayout Contract with its payout set to DailyPayout contract deployed
  
  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: deploy_flex  `FLEXCoin`  generic ERC-20 to serve as the Staking Token  
  :param: deploy_daily_payout  `DailyPayout`  Payout contract with daily epoch
  '''
  flex: FLEXCoin           = deploy_flex
  payout: DailyPayout      = deploy_daily_payout
  gas_strategy             = ExponentialScalingStrategy('10 gwei', '50 gwei')
  ### Deployment ###
  distributor: Distributor = Distributor.deploy(payout, flex, { 'from': admin, 'gas_price': gas_strategy })
  print(f'Distributor: { distributor }')

def test_deploy_quarterly_distributor(admin: Account, deploy_flex: FLEXCoin, deploy_quarterly_payout: QuarterlyPayout):
  '''
  TEST: Deploy Distributor Contract with its payout set to QuarterlyPayout contract deployed
  
  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: deploy_flex  `FLEXCoin`  generic ERC-20 to serve as the Staking Token  
  :param: deploy_quarterly_payout  `QuarterlyPayout`  Payout contract with 13 week epoch
  '''
  flex: FLEXCoin           = deploy_flex
  payout: QuarterlyPayout  = deploy_quarterly_payout
  gas_strategy             = ExponentialScalingStrategy('10 gwei', '50 gwei')
  ### Deployment ###
  distributor: Distributor = Distributor.deploy(payout, flex, { 'from': admin, 'gas_price': gas_strategy })
  print(f'Distributor: { distributor }')
