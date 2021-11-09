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
from brownie import DailyPayoutV2, FLEXCoin, veFLEX, Distributor
### Third-Party Packages ###
from brownie.network import Chain
from brownie.network.gas.strategies import ExponentialScalingStrategy
from eth_account import Account
from pytest import mark, reverts
### Local Modules ###
from tests import admin, user_accounts
from tests.deployments.daily_payout import deploy_daily_payout_v2
from tests.deployments.flex import deploy_flex
from tests.deployments.ve_flex import deploy_ve_flex # Used by deploy_daily_payout
from tests.deployments.distributor import deploy_daily_distributor_for_v2

def test_dailyPayoutV2_integration_with_distributor(admin: Account, user_accounts: List[Account], deploy_flex: FLEXCoin, deploy_ve_flex: veFLEX, deploy_daily_payout_v2: DailyPayoutV2, deploy_daily_distributor_for_v2: Distributor):
  # 1: test set up
  epochs: int              = 50
  flex: FLEXCoin           = deploy_flex
  ve_flex: veFLEX            = deploy_ve_flex
  payout: DailyPayoutV2    = deploy_daily_payout_v2
  distributor: Distributor = deploy_daily_distributor_for_v2
  gas_strategy             = ExponentialScalingStrategy('10 gwei', '50 gwei')
  chain                    = Chain()
  EPOCH_BLOCKS: int        = 10;
  alice                    = user_accounts[1]
  bob                      = user_accounts[2]
  flex.transfer(alice, 10*1e18, {'from': admin, 'gas_price': gas_strategy})

  # 2: ownable test
  payout_admin = payout.owner()
  assert payout_admin == admin

  # 3: start block height set and test
  startBlockHeight: int   = chain.height
  print(f'epoch starts at block height: {startBlockHeight}')
  payout.setStartBlockHeight(startBlockHeight, {'from': admin, 'gas_price': gas_strategy})
  print(f'====> block height {chain.height}')
  assert payout.startBlockHeight() == startBlockHeight

  # 4: add/remove distributor test
  tx = payout.addDistributor(alice, {'from': admin, 'gas_price': gas_strategy})
  assert payout.isDistributor(alice) == True
  print(f'====> block height {chain.height}')
  tx = payout.removeDistributor(alice, {'from': admin, 'gas_price': gas_strategy})
  assert payout.isDistributor(alice) == False
  print(f'====> block height {chain.height}')

  # 5: distribute rewards until epoch 10
  rewards = 1e18
  epochs = 10
  # 5.1: add distributor into whitelist
  payout.addDistributor(distributor, {'from': admin, 'gas_price': gas_strategy})
  print(f'====> block height {chain.height}')
  for i in range(epochs):
    # 5.2: transfer reward to Distributor for each epoch
    flex.transfer(distributor, rewards, {'from': admin, 'gas_price': gas_strategy})
    distributor.distribute({'from': admin, 'gas_price': gas_strategy})
    print(f'distributed {rewards} for epoch {i}')
    print(f'====> block height {chain.height}')
    assert payout.payoutForEpoch(i) == rewards
  assert payout.currentEpoch() == epochs
  print(f'====> block height {chain.height}')

  # 6: fail to claim due to the chain haven't reached specific block height for epoch
  unlock_time  = chain.time() + (4 * 365 * 86400) # 4 years in seconds
  ve_flex.create_lock(flex.balanceOf(alice), unlock_time, { 'from': alice, 'gas_price': gas_strategy })
  print(f'alice stake at block height {chain.height}')

  chain.mine(4)
  print(f'====> block height {chain.height}')
  tx = payout.claim(alice, { 'from': alice, 'gas_price': gas_strategy })
  print(tx.events)
  print(f'block number: {chain.height}')

  tx = payout.claim(alice, { 'from': alice, 'gas_price': gas_strategy })
  print(tx.events)
  print(f'block number: {chain.height}')

  # 7: chain tranvel
  print(f'chain travelling: {10 * EPOCH_BLOCKS} blocks')
  chain.mine(10 * EPOCH_BLOCKS)
  print(f'current block height: {chain.height}')
  print(f'current epoch: {payout.currentEpoch()}')

  # 8: claim the first 
  alice_claimable = payout.getClaimable(alice)
  print(f'alice claimable reward: {alice_claimable}')
  tx = payout.claim(alice, { 'from': alice, 'gas_price': gas_strategy })
  print(tx.events)
  assert tx.events['Claim']['amount'] == alice_claimable

def test_dailyPayoutV2_different_epoch_length(admin: Account, user_accounts: List[Account], deploy_flex: FLEXCoin, deploy_ve_flex: veFLEX, deploy_daily_payout_v2: DailyPayoutV2, deploy_daily_distributor_for_v2: Distributor):
  # 1: test set up
  epochs: int              = 50
  flex: FLEXCoin           = deploy_flex
  ve_flex: veFLEX            = deploy_ve_flex
  payout: DailyPayoutV2    = deploy_daily_payout_v2
  distributor: Distributor = deploy_daily_distributor_for_v2
  gas_strategy             = ExponentialScalingStrategy('10 gwei', '50 gwei')
  chain                    = Chain();
  alice                    = user_accounts[1]
  bob                      = user_accounts[2]
  flex.transfer(alice, 10*1e18, {'from': admin, 'gas_price': gas_strategy})

  # 2: start block height set and test
  startBlockHeight: int   = chain.height
  print(f'epoch starts at block height: {startBlockHeight}')
  payout.setStartBlockHeight(startBlockHeight, {'from': admin, 'gas_price': gas_strategy})
  print(f'====> block height {chain.height}')
  
  # 3: distribute rewards
  rewards = 1e18
  EPOCH_BLOCKS = 10
  # 3.1: add distributor into whitelist
  payout.addDistributor(distributor, {'from': admin, 'gas_price': gas_strategy})
  print(f'====> block height {chain.height}')
  for i in range(2):
    # 3.2: transfer reward to Distributor for each epoch
    flex.transfer(distributor, rewards, {'from': admin, 'gas_price': gas_strategy})
    distributor.distribute({'from': admin, 'gas_price': gas_strategy})
    print(f'distributed {rewards} for epoch {i} with block length: {EPOCH_BLOCKS}')
    print(f'====> block height {chain.height}')
  assert payout.getEpochBlockHeight(2) == startBlockHeight + EPOCH_BLOCKS*2
  print(f'current epoch start height: {payout.getEpochBlockHeight(2)}')

  # 3.3: change epoch length from 10 to 5
  EPOCH_BLOCKS = 5
  payout.setEpochLength(0 + 2, EPOCH_BLOCKS)
  print(f'====> block height {chain.height}')
  print(payout.epochLengthHistory(0, 0))
  print(payout.epochLengthHistory(1, 0))
  for i in range(2,5):
    # 5.2: transfer reward to Distributor for each epoch
    flex.transfer(distributor, rewards, {'from': admin, 'gas_price': gas_strategy})
    distributor.distribute({'from': admin, 'gas_price': gas_strategy})
    print(f'distributed {rewards} for epoch {i} with block length: {EPOCH_BLOCKS}')
    print(f'====> block height {chain.height}')
  print(f'current epoch start height: {payout.getEpochBlockHeight(5)}')
  assert payout.getEpochBlockHeight(5) == payout.getEpochBlockHeight(2) + EPOCH_BLOCKS*3

  # 6: fail to claim due to the chain haven't reached specific block height for epoch
  unlock_time  = chain.time() + (4 * 365 * 86400) # 4 years in seconds
  ve_flex.create_lock(flex.balanceOf(alice), unlock_time, { 'from': alice, 'gas_price': gas_strategy })
  print(f'alice stake at block height {chain.height}')

  chain.mine(30)
  print(f'====> block height {chain.height}')
  tx = payout.claim(alice, { 'from': alice, 'gas_price': gas_strategy })
  print(tx.events)
  print(f'block number: {chain.height}')