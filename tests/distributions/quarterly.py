#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/distributions/quarterly.py
# VERSION: 	 1.0
# CREATED: 	 2021-10-14 16:39
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Standard Packages ###
from decimal import Decimal
from typing import List
### Project Contracts ###
from brownie import FLEXCoin, QuarterlyPayout, veFLEX
### Third-Party Packages ###
from brownie.network import Chain
from brownie.network.gas.strategies import GasNowStrategy
from eth_account import Account
from pytest import mark
### Local Modules ###
from tests import admin, user_accounts
from tests.deployments.quarterly_payout import deploy_quarterly_payout
from tests.deployments.flex import deploy_flex
from tests.deployments.ve_flex import deploy_ve_flex # Used by deploy_quarterly_payout

@mark.parametrize('gas_speed', ('standard', 'fast'))
def test_distribute_calls(admin: Account, deploy_flex: FLEXCoin, deploy_quarterly_payout: QuarterlyPayout, gas_speed: str):
  epochs: int             = 1
  flex: FLEXCoin          = deploy_flex
  payout: QuarterlyPayout = deploy_quarterly_payout
  flex_balance: Decimal   = flex.balanceOf(admin)
  payout_per_epoch        = flex_balance / epochs
  gas_strategy            = GasNowStrategy(gas_speed)
  ### Execute ###
  for _ in range(epochs):
    txn = payout.distribute(payout_per_epoch, { 'from': admin, 'gas_speed': gas_strategy })
    print(f'Current Epoch: { payout.currentEpoch() }')

@mark.parametrize('gas_speed', ('standard', 'fast'))
def test_claim_calls(admin: Account, user_accounts: List[Account], deploy_flex: FLEXCoin, deploy_ve_flex: veFLEX, deploy_quarterly_payout: QuarterlyPayout, gas_speed: str):
  epochs: int             = 5
  flex: FLEXCoin          = deploy_flex
  payout: QuarterlyPayout = deploy_quarterly_payout
  ve_flex: veFLEX         = deploy_ve_flex
  flex_balance: Decimal   = flex.balanceOf(admin)
  payout_per_epoch        = flex_balance / 2 / epochs
  gas_strategy            = GasNowStrategy(gas_speed)
  ### Execute ###
  for _ in range(epochs):
    payout.distribute(payout_per_epoch, { 'from': admin, 'gas_speed': gas_strategy })
    print(f'Current Epoch: { payout.currentEpoch() }')
  ### Vest ###
  claimant     = user_accounts[0]
  flex.transfer(claimant, flex.balanceOf(admin), { 'from': admin, 'gas_speed': gas_strategy })
  chain: Chain = Chain() # get chain instance
  unlock_time  = chain.time() + 4 * 365 * 86400 # 1 week in seconds
  ve_flex.create_lock(flex.balanceOf(claimant), unlock_time, { 'from': claimant, 'gas_price': gas_strategy })
  print(f'veFLEX Balance: { ve_flex.balanceOf(claimant) }')
  ### Claim ###
  for _ in range(epochs):
    claimable: Decimal = payout.getClaimable(claimant)#, { 'from': claimant, 'gas_price': gas_strategy })
    print(claimable)
