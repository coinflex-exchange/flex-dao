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
from brownie import DailyPayout, FLEXCoin, veFLEX, Distributor, reverts
### Third-Party Packages ###
from brownie.network import Chain
from brownie.network.gas.strategies import ExponentialScalingStrategy
from eth_account import Account
### Local Modules ###
from tests import admin, user_accounts
from tests.deployments.daily_payout import deploy_daily_payout
from tests.deployments.flex import deploy_flex
from tests.deployments.ve_flex import deploy_ve_flex # Used by deploy_daily_payout
from tests.deployments.distributor import deploy_daily_distributor

def test_dailyPayout_different_epoch_length(admin: Account, user_accounts: List[Account], deploy_flex: FLEXCoin, deploy_ve_flex: veFLEX, deploy_daily_payout: DailyPayout, deploy_daily_distributor: Distributor):
  # 1: test set up
  epochs: int              = 50
  flex: FLEXCoin           = deploy_flex
  ve_flex: veFLEX          = deploy_ve_flex
  payout: DailyPayout      = deploy_daily_payout
  distributor: Distributor = deploy_daily_distributor
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

  payout.setInitEpochBlockLength(10, { 'from': admin, 'gas_price': gas_strategy })
  
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

  # 3.3: change epoch length from 10 to 5
  EPOCH_BLOCKS = 5
  payout.setNextEpochLength(EPOCH_BLOCKS)
  print(f'====> block height {chain.height}')
  print(f'epoch block length history index 0 starting epoch: {payout.epochLengthHistory(0, 0)}')
  print(f'epoch block length history index 1 starting epoch: {payout.epochLengthHistory(1, 0)}')
  for i in range(2,5):
    # 5.2: transfer reward to Distributor for each epoch
    flex.transfer(distributor, rewards, {'from': admin, 'gas_price': gas_strategy})
    distributor.distribute({'from': admin, 'gas_price': gas_strategy})
    print(f'distributed {rewards} for epoch {i} with block length: {EPOCH_BLOCKS}')
    print(f'====> block height {chain.height}')

  # 6: fail to claim due to the chain haven't reached specific block height for epoch
  unlock_time  = chain.time() + (4 * 365 * 86400) # 4 years in seconds
  ve_flex.create_lock(flex.balanceOf(alice), unlock_time, { 'from': alice, 'gas_price': gas_strategy })
  print(f'alice stake at block height {chain.height}')

  chain.mine(30)
  print(f'====> block height {chain.height}')
  tx = payout.claim(alice, { 'from': alice, 'gas_price': gas_strategy })
  print(tx.events)
  print(f'block number: {chain.height}')

def test_dailyPayout_next_epoch_length_related(admin: Account, user_accounts: List[Account], deploy_flex: FLEXCoin, deploy_ve_flex: veFLEX, deploy_daily_payout: DailyPayout, deploy_daily_distributor: Distributor):
  # 1: test set up
  epochs: int              = 50
  flex: FLEXCoin           = deploy_flex
  ve_flex: veFLEX          = deploy_ve_flex
  payout: DailyPayout      = deploy_daily_payout
  distributor: Distributor = deploy_daily_distributor
  gas_strategy             = ExponentialScalingStrategy('10 gwei', '50 gwei')
  chain                    = Chain();
  alice                    = user_accounts[1]
  bob                      = user_accounts[2]
  flex.transfer(alice, 10*1e18, {'from': admin, 'gas_price': gas_strategy})

  # 2: start block height set
  startBlockHeight: int   = chain.height
  print(f'epoch starts at block height: {startBlockHeight}')
  payout.setStartBlockHeight(startBlockHeight, {'from': admin, 'gas_price': gas_strategy})
  payout.setInitEpochBlockLength(10, { 'from': admin, 'gas_price': gas_strategy })
  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')

  # 3: test set next epoch length func
  # 3.1: a epoch period = [startEpochHeight, endEpochHeight)
  # meaning for example, for epoch 1 with lenght 10 blocks.
  # block height 10,11,12,13,14,15,16,17,18,19 belongs to epoch 1, and 20 belongs to epoch 2.
  # set current block.number to the edge case of epoch 1.
  chain.mine(10 - 2)
  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')
  # set epoch 2 block length to 5
  payout.setNextEpochLength(5)
  print(f'from epoch2, the epoch block length change from 10 to 5')
  assert payout.epochLengthHistory(1,0) == 2

  # 3.2: test revert when set the seme epoch length for the next epoch
  chain.mine(12)
  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')
  with reverts('epoch length is the same with last epoch length'):
    payout.setNextEpochLength(5)
  
  # 3.3: test only can update epoch block length on the same epoch
  chain.mine(2)
  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')
  payout.setNextEpochLength(8)
  assert payout.epochLengthHistory(2,0) == 4
  assert payout.epochLengthHistory(2,1) == 8
  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')
  payout.updateLastEpochLength(10)
  assert payout.epochLengthHistory(2,0) == 4
  assert payout.epochLengthHistory(2,1) == 10

  # 3.4: revert if chain goes to next epoch while update epoch lenght
  chain.mine(10)
  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')
  with reverts('can only update next epoch length'):
    payout.updateLastEpochLength(10)

  # 4: test set init epoch block length
  # 4.1: revert while try to set twice
  with reverts('init block length already set!'):
    payout.setInitEpochBlockLength(20)

  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')

  # 5: test edge case for get current epoch and get epoch start block height
  assert payout.getCurrentEpoch() == 5
  assert payout.getEpochStartBlockHeight(5) == chain.height

  chain.mine(1)
  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')
  assert payout.getCurrentEpoch() == 5
  assert payout.getEpochStartBlockHeight(5) == chain.height - 1