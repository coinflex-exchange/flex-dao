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
from brownie import DailyPayout, FLEXCoin, veFLEX, Distributor
### Third-Party Packages ###
from brownie.network import Chain
from brownie.network.gas.strategies import ExponentialScalingStrategy
from eth_account import Account
from pytest import mark, reverts
### Local Modules ###
from tests import admin, user_accounts
from tests.deployments.daily_payout import deploy_daily_payout
from tests.deployments.flex import deploy_flex
from tests.deployments.ve_flex import deploy_ve_flex # Used by deploy_daily_payout
from tests.deployments.distributor import deploy_daily_distributor

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

  flex_balance      = flex.balanceOf(admin)
  payout_per_epoch  = flex_balance / (epochs * 2)
  
  ### Execute ###
  for i in range(epochs):
    payout.distribute(payout_per_epoch, { 'from': admin, 'gas_price': gas_strategy })
    print(f'Current Epoch: { payout.currentEpoch() }')
    print(f'Current Epoch payout: { payout.payoutForEpoch(i) }')

  ### Sets Payout StartTime ###
  payout.setStartBlockHeight(chain.height, { 'from': admin, 'gas_price': gas_strategy })
  ### Chain travel ###
  chain.mine(5)
  
  ### Claim ###
  
  #for _ in range(epochs):
  claimable: Decimal = payout.getClaimable(claimant)#, { 'from': claimant, 'gas_price': gas_strategy })
  print(f'Claimable Amount: { claimable }')
  claim_txn = payout.claim(claimant, { 'from': claimant })
  print(f'Claim Txn: { claim_txn.events }')
  #chain.sleep(86400) # 1 day in seconds

def test_dailyPayout_integration_with_distributor(admin: Account, user_accounts: List[Account], deploy_flex: FLEXCoin, deploy_ve_flex: veFLEX, deploy_daily_payout: DailyPayout, deploy_daily_distributor: Distributor):
  # 1: test set up
  epochs: int              = 50
  flex: FLEXCoin           = deploy_flex
  ve_flex: veFLEX          = deploy_ve_flex
  payout: DailyPayout      = deploy_daily_payout
  distributor: Distributor = deploy_daily_distributor
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
  # 3.1: set init epoch block length as 10
  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')
  assert payout.startBlockHeight() == startBlockHeight

  # 4: add/remove distributor test
  tx = payout.addDistributor(alice, {'from': admin, 'gas_price': gas_strategy})
  assert payout.isDistributor(alice) == True
  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')
  tx = payout.removeDistributor(alice, {'from': admin, 'gas_price': gas_strategy})
  assert payout.isDistributor(alice) == False
  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')

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
    print(f'***** epoch number {payout.getCurrentEpoch()}')
    assert payout.payoutForEpoch(i) == rewards
  assert payout.currentEpoch() == epochs

  # 6: fail to claim due to the chain haven't reached specific block height for epoch
  unlock_time  = chain.time() + (4 * 365 * 86400) # 4 years in seconds
  ve_flex.create_lock(flex.balanceOf(alice), unlock_time, { 'from': alice, 'gas_price': gas_strategy })
  print(f'alice stake at block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')

  chain.mine(4)
  tx = payout.claim(alice, { 'from': alice, 'gas_price': gas_strategy })
  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')
  print(tx.events)
  print(f'block number: {chain.height}')

  tx = payout.claim(alice, { 'from': alice, 'gas_price': gas_strategy })
  print(tx.events)
  print(f'block number: {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')

  # 7: chain tranvel
  print(f'chain travelling: {10 * EPOCH_BLOCKS} blocks')
  chain.mine(100)
  print(f'block number: {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')

  # 8: claim the rest 
  alice_claimable = payout.getClaimable(alice)
  print(f'alice claimable reward: {alice_claimable}')
  tx = payout.claim(alice, { 'from': alice, 'gas_price': gas_strategy })
  print(tx.events)

def test_epoch0_is_not_claimable(admin: Account, user_accounts: List[Account], deploy_flex: FLEXCoin, deploy_ve_flex: veFLEX, deploy_daily_payout: DailyPayout, deploy_daily_distributor: Distributor):
  # 1: test set up
  flex: FLEXCoin           = deploy_flex
  ve_flex: veFLEX          = deploy_ve_flex
  payout: DailyPayout      = deploy_daily_payout
  distributor: Distributor = deploy_daily_distributor
  gas_strategy             = ExponentialScalingStrategy('10 gwei', '50 gwei')
  chain                    = Chain()
  alice                    = user_accounts[1]
  flex.transfer(alice, 10*1e18, {'from': admin, 'gas_price': gas_strategy})

  # 2: start block height set and test
  startBlockHeight: int   = chain.height
  print(f'epoch starts at block height: {startBlockHeight}')
  payout.setStartBlockHeight(startBlockHeight, {'from': admin, 'gas_price': gas_strategy})
  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')

  # 3: stake some into veFlex from alice at epoch 0
  unlock_time  = chain.time() + (4 * 365 * 86400) # 4 years in seconds
  ve_flex.create_lock(flex.balanceOf(alice), unlock_time, { 'from': alice, 'gas_price': gas_strategy })
  print(f'alice stake at block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}') 

  # 4: distribute for epoch 0
  payout.addDistributor(distributor, {'from': admin, 'gas_price': gas_strategy})
  flex.transfer(distributor, 1e18, {'from': admin, 'gas_price': gas_strategy})
  distributor.distribute({'from': admin, 'gas_price': gas_strategy})

  # 4: claim at epoch 0, should get none
  alice_claimable = payout.getClaimable(alice)
  print(f'alice claimable reward: {alice_claimable}')
  tx = payout.claim(alice, { 'from': alice, 'gas_price': gas_strategy })
  print(tx.events)
  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}') 

  # 5: can claim at next epoch {epoch 1}
  payout.addDistributor(distributor, {'from': admin, 'gas_price': gas_strategy})
  flex.transfer(distributor, 1e18, {'from': admin, 'gas_price': gas_strategy})

  distributor.distribute({'from': admin, 'gas_price': gas_strategy})
  chain.mine(5)
  alice_claimable = payout.getClaimable(alice)
  print(f'alice claimable reward: {alice_claimable}')
  tx = payout.claim(alice, { 'from': alice, 'gas_price': gas_strategy })
  print(tx.events)
  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')

def test_multi_claim(admin: Account, user_accounts: List[Account], deploy_flex: FLEXCoin, deploy_ve_flex: veFLEX, deploy_daily_payout: DailyPayout, deploy_daily_distributor: Distributor):
  # 1: test set up
  flex: FLEXCoin           = deploy_flex
  ve_flex: veFLEX          = deploy_ve_flex
  payout: DailyPayout      = deploy_daily_payout
  distributor: Distributor = deploy_daily_distributor
  gas_strategy             = ExponentialScalingStrategy('10 gwei', '50 gwei')
  chain                    = Chain()
  alice                    = user_accounts[1]
  bob                      = user_accounts[2]
  eve                      = user_accounts[3]
  sam                      = user_accounts[4]
  flex.transfer(alice, 1000*1e18, {'from': admin, 'gas_price': gas_strategy})
  flex.transfer(bob, 1000*1e18, {'from': admin, 'gas_price': gas_strategy})
  flex.transfer(eve, 1000*1e18, {'from': admin, 'gas_price': gas_strategy})

  # 2: start block height set and test
  startBlockHeight: int   = chain.height
  print(f'epoch starts at block height: {startBlockHeight}')
  payout.setStartBlockHeight(startBlockHeight, {'from': admin, 'gas_price': gas_strategy})
  print('set DAO start block height')
  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')

  # 3: stake some into veFlex from alice at epoch 0
  _4_years  = chain.time() + (4 * 365 * 86400)
  _1_years  = chain.time() + (365 * 86400)
  _1_month  = chain.time() + (30 * 86400)
  ve_flex.create_lock(flex.balanceOf(alice), _4_years, { 'from': alice, 'gas_price': gas_strategy })
  print(f'alice stake 4 years at block height {chain.height}')
  print(f'veFLEX Balance: { ve_flex.balanceOf(alice) }')
  print(f'***** epoch number {payout.getCurrentEpoch()}') 
  ve_flex.create_lock(flex.balanceOf(bob), _1_years, { 'from': bob, 'gas_price': gas_strategy })
  print(f'bob stake 1 year at block height {chain.height}')
  print(f'veFLEX Balance: { ve_flex.balanceOf(bob) }')
  print(f'***** epoch number {payout.getCurrentEpoch()}') 
  ve_flex.create_lock(flex.balanceOf(eve), _1_month, { 'from': eve, 'gas_price': gas_strategy })
  print(f'eve stake 1 month at block height {chain.height}')
  print(f'veFLEX Balance: { ve_flex.balanceOf(eve) }')
  print(f'***** epoch number {payout.getCurrentEpoch()}') 
  print('sam stake nothing')
  print(f'veFLEX Balance: { ve_flex.balanceOf(sam) }')
  print(f'***** epoch number {payout.getCurrentEpoch()}') 
  # 4: distribute for 50 epochs
  ### Execute ###
  payout.addDistributor(distributor, {'from': admin, 'gas_price': gas_strategy})
  print('activate 10 epochs for rewarding')
  for i in range(10):
    payout.distribute(3000 * 1e18, { 'from': admin, 'gas_price': gas_strategy })
    print(f'Epoch { payout.currentEpoch() - 1 } payout: { payout.payoutForEpoch(i) }')
  print(f'====> block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')

  # 5: claim
  tx = payout.claim(alice, { 'from': alice, 'gas_price': gas_strategy })
  print(tx.events)
  print(f'====> alice claimed at block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}') 
  
  tx = payout.claim(bob, { 'from': bob, 'gas_price': gas_strategy })
  print(tx.events)
  print(f'====> bob claimed at block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')   
  
  tx = payout.claim(eve, { 'from': eve, 'gas_price': gas_strategy })
  print(tx.events)
  print(f'====> eve claimed block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}') 

  tx = payout.claim(sam, { 'from': sam, 'gas_price': gas_strategy })
  print(tx.events)
  print(f'====> sam claimed block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}') 

  # 6: chain is moving and claim again

  chain.mine(100)
  tx = payout.claim(alice, { 'from': alice, 'gas_price': gas_strategy })
  print(tx.events)
  print(f'====> alice claimed at block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}') 
  
  tx = payout.claim(bob, { 'from': bob, 'gas_price': gas_strategy })
  print(tx.events)
  print(f'====> bob claimed at block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}')   
  
  tx = payout.claim(eve, { 'from': eve, 'gas_price': gas_strategy })
  print(tx.events)
  print(f'====> eve claimed block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}') 

  tx = payout.claim(sam, { 'from': sam, 'gas_price': gas_strategy })
  print(tx.events)
  print(f'====> sam claimed block height {chain.height}')
  print(f'***** epoch number {payout.getCurrentEpoch()}') 