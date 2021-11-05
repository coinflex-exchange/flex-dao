#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/distributions/daily.py
# VERSION: 	 1.0
# CREATED: 	 2021-10-19 16:39
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Standard Packages ###
from decimal import Decimal
from typing import List
### Project Contracts ###
from brownie import DailyPayout, DailyPayoutV1, FLEXCoin, veFLEX, Distributor
### Third-Party Packages ###
from brownie.network import Chain
from brownie.network.gas.strategies import ExponentialScalingStrategy
from eth_account import Account
from pytest import mark
### Local Modules ###
from tests import admin, user_accounts
from tests.deployments.daily_payout import deploy_daily_payout, deploy_daily_payout_v1
from tests.deployments.flex import deploy_flex
from tests.deployments.ve_flex import deploy_ve_flex # Used by deploy_daily_payout
from tests.deployments.distributor import deploy_daily_distributor_for_v1

def test_distribute_calls(admin: Account, deploy_flex: FLEXCoin, deploy_daily_payout: DailyPayout):
  epochs: int           = 10
  flex: FLEXCoin        = deploy_flex
  payout: DailyPayout   = deploy_daily_payout
  flex_balance: Decimal = flex.balanceOf(admin)
  payout_per_epoch      = flex_balance / epochs
  gas_strategy          = ExponentialScalingStrategy('10 gwei', '50 gwei')
  ### Execute ###
  for i in range(epochs):
    txn = payout.distribute(payout_per_epoch, { 'from': admin, 'gas_price': gas_strategy })
    print(f'Current Epoch: { payout.currentEpoch() }')
    print(f'Current Epoch payout: { payout.payoutForEpoch(i) }')

def test_claim_calls(admin: Account, user_accounts: List[Account], deploy_flex: FLEXCoin, deploy_ve_flex: veFLEX, deploy_daily_payout: DailyPayout):
  epochs: int           = 50
  flex: FLEXCoin        = deploy_flex
  payout: DailyPayout   = deploy_daily_payout
  ve_flex: veFLEX       = deploy_ve_flex
  flex_balance: Decimal = flex.balanceOf(admin)
  payout_per_epoch      = flex_balance / (epochs * 2)
  gas_strategy          = ExponentialScalingStrategy('10 gwei', '50 gwei')

  ### Vest ###
  chain: Chain = Chain() # get chain instance  
  claimant     = user_accounts[0]
  flex.transfer(claimant, flex.balanceOf(admin)-500000*1e18, { 'from': admin, 'gas_price': gas_strategy })
  unlock_time  = chain.time() + (4 * 365 * 86400) # 4 years in seconds
  ve_flex.create_lock(flex.balanceOf(claimant), unlock_time, { 'from': claimant, 'gas_price': gas_strategy })
  print(f'veFLEX Balance claimant: { ve_flex.balanceOf(claimant) }')

  flex_balance= flex.balanceOf(admin)
  payout_per_epoch      = flex_balance / (epochs * 2)
  
  ### Execute ###
  for i in range(epochs):
    payout.distribute(payout_per_epoch, { 'from': admin, 'gas_price': gas_strategy })
    print(f'Current Epoch: { payout.currentEpoch() }')
    print(f'Current Epoch payout: { payout.payoutForEpoch(i) }')
    print(f'blocknumberForEpoch: { payout.blocknumberForEpoch(i) }')

  ### Sets Payout StartTime ###
  payout.setStartTime(chain.time(), { 'from': admin, 'gas_price': gas_strategy })
  ### Sleep ###
  chain.sleep(86400) # 1 day in seconds
  
  ### Claim ###
  
  #for _ in range(epochs):
  claimable: Decimal = payout.getClaimable(claimant)#, { 'from': claimant, 'gas_price': gas_strategy })
  print(f'Claimable Amount: { claimable }')
  claim_txn = payout.claim(claimant, { 'from': admin })
  print(f'Claim Txn: { claim_txn }')
  #chain.sleep(86400) # 1 day in seconds

def test_dailyPayoutV1_integration_test_with_distributor(admin: Account, user_accounts: List[Account], deploy_flex: FLEXCoin, deploy_daily_payout_v1: DailyPayoutV1, deploy_daily_distributor_for_v1: Distributor):
  # 1: test set up
  epochs: int             = 50
  flex: FLEXCoin          = deploy_flex
  payout: DailyPayoutV1   = deploy_daily_payout_v1
  gas_strategy            = ExponentialScalingStrategy('10 gwei', '50 gwei')
  chain                   = Chain()
  EPOCH_BLOCKS: int       = 17280;
  alice                   = user_accounts[1]
  bob                     = user_accounts[2]

  # 2: ownable test
  payout_admin = payout.owner()
  assert payout_admin == admin

  # 3: start block height set and test
  startBlockHeight: int   = chain.height
  print(f'current block height: {startBlockHeight}')
  payout.setStartBlockHeight(startBlockHeight, {'from': admin, 'gas_price': gas_strategy})
  assert payout.startBlockHeight() == startBlockHeight

  # 4: add/remove distributor test
  tx = payout.addDistributor(alice, {'from': admin, 'gas_price': gas_strategy})
  assert payout.isDistributor(alice) == True
  print(tx.events)
  tx = payout.removeDistributor(alice, {'from': admin, 'gas_price': gas_strategy})
  assert payout.isDistributor(alice) == False
  print(tx.events)
