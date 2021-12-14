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
from brownie import FLEXCoin, DailyPayout, QuarterlyPayout, Distributor, reverts
### Third-Party Packages ###
from brownie.network.gas.strategies import ExponentialScalingStrategy
from eth_account import Account
from pytest import fixture, mark
### Local Modules ###
from tests import *
from .daily_payout import deploy_daily_payout, deploy_quarterly_payout
from .flex import deploy_flex
from .ve_flex import deploy_ve_flex # used by `deploy_daily_payout` and `deploy_quarterly_payout`
from typing import List

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
  return Distributor.deploy(payout, flex, 'Daily Payout Distributor', { 'from': admin, 'gas_price': gas_strategy })

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
  distributor: Distributor = Distributor.deploy(payout, flex, 'Daily Payout Distributor', { 'from': admin, 'gas_price': gas_strategy })
  print(f'Distributor: { distributor }')
  assert distributor.name() == 'Daily Payout Distributor'

def test_distributor(deploy_daily_distributor: Distributor, admin: Account, user_accounts: List[Account], deploy_flex: FLEXCoin, deploy_daily_payout: DailyPayout, deploy_quarterly_payout: QuarterlyPayout):
  distributor: Distributor   = deploy_daily_distributor
  flex: FLEXCoin             = deploy_flex
  payout: DailyPayout        = deploy_daily_payout
  newPayout: QuarterlyPayout = deploy_quarterly_payout
  alice: Account             = user_accounts[0]
  bob: Account               = user_accounts[1]
  
  # 1: basic add and remove test of delegator
  tx = distributor.addDistributor(alice)
  assert distributor.isDistributor(alice) == True
  assert distributor.isDistributor(bob) == False
  assert tx.events['AddDistributor']['distributor'] == alice

  tx= distributor.removeDistributor(alice)
  assert distributor.isDistributor(alice) == False
  assert tx.events['RemoveDistributor']['distributor'] == alice

  # 2: admin and delegator can distribute while others cannot
  with reverts('You must transfer more than zero FLEX'):
    distributor.distribute({'from': admin})
  
  distributor.addDistributor(alice)
  with reverts('You must transfer more than zero FLEX'):
    distributor.distribute({'from': alice})  

  with reverts('You are not the admin or valid delegatee'):
    distributor.distribute({'from': bob})

  # 3: distribute event test
  amount = 1e18
  flex.transfer(distributor, amount, {'from': admin})
  payout.addDistributor(distributor, {'from': admin})
  tx = distributor.distribute({'from': admin})
  assert tx.events['CallDistribute']['distributor'] == admin
  assert tx.events['CallDistribute']['amount'] == amount

  # 4: update payout contract addr
  newPayout.addDistributor(distributor, {'from': admin})
  tx = distributor.updatePayoutAddr(newPayout, {'from': admin})
  assert tx.events['UpdatePayoutAddr']['prevPayoutAddr'] == payout
  assert tx.events['UpdatePayoutAddr']['currPayoutAddr'] == newPayout
  flex.transfer(distributor, amount, {'from': admin})
  distributor.distribute({'from': admin})
  assert newPayout.currentEpoch() == 1
  assert newPayout.payoutForEpoch(0) == amount
