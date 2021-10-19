#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/vesting/users.py
# VERSION: 	 1.0
# CREATED: 	 2021-09-22 19:33
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Standard Packages ###
from decimal import Decimal
from typing import List, NoReturn
### Project Contracts ###
from brownie import FLEXCoin, veFLEX
### Third-Party Packages ###
from brownie.convert import Wei
from brownie.network import Chain
from brownie.network.gas.strategies import ExponentialScalingStrategy
from eth_account import Account
from pytest import mark
### Local Modules ###
from tests import *
from tests.deployments.flex import deploy_flex
from tests.deployments.ve_flex import deploy_ve_flex

@mark.parametrize('amount', (
  Wei('1 ether').to('wei'),
  Wei('10 ether').to('wei'),
  Wei('100 ether').to('wei')
))
def test_users_vesting(admin: Account, user_accounts: List[Account], amount: Decimal, deploy_flex: FLEXCoin, deploy_ve_flex: veFLEX):
  '''
  TEST: Test vesting different amounts from all users.
  '''
  chain: Chain   = Chain() # get chain instance
  gas_strategy   = ExponentialScalingStrategy('10 gwei', '50 gwei')
  ### Distribute FLEXCoin to users ###
  print(f'{ BLUE }Distribute FLEXCoin to users.{ NFMT }')
  flex: FLEXCoin = deploy_flex
  print(f'Admin: { admin }')
  print(f'FLEXCoin Balance (admin): { Wei(flex.balanceOf(admin)).to("ether") }')
  assert flex.totalSupply() > 0
  amt: Decimal   = Wei('100 ether').to('wei')
  for acct in user_accounts:
    txn = flex.transfer(acct, amt, { 'from': admin, 'gas_price': gas_strategy })
  ### Current-day ###
  print(f'{ BLUE }Blocktime: { chain.time() }{ NFMT }')

  ### Creat Locks ###
  print(f'{ BLUE }Create locks.{ NFMT }')
  ve_flex: veFLEX = deploy_ve_flex
  print(f'Block timestamp: { len(chain) }')
  print(f'Total Voting Supply: { ve_flex.totalSupply() }')
  unlock_time     = chain.time() + 4 * 365 * 86400 # 1 week in seconds
  print(f'Unlock Time: { unlock_time }')
  for i, acct in enumerate(user_accounts):
    locked = ve_flex.create_lock(amount, unlock_time, { 'from': acct, 'gas_price': gas_strategy })
    print(f'veFLEX Balance (acct #{i}): { ve_flex.balanceOf(acct) }')
  
  ### Time-machine ###
  chain.sleep(7 * 86400) # 1 weeks in seconds

  ### Calls Checkooint to update Stakes ###
  ve_flex.checkpoint()

  print(f'{ BLUE }Blocktime: { chain.time() }{ NFMT }')
  print(f'Total Voting Supply: { ve_flex.totalSupply() }')
  accum_voting_power: float = 0

  ### Checks stakes 
  for i, acct in enumerate(user_accounts):
    print(f'veFLEX Balance (acct #{i}): { ve_flex.balanceOf(acct) }')
    accum_voting_power += ve_flex.balanceOf(acct)
  assert ve_flex.totalSupply() == accum_voting_power
  print(f'Accumulated Voting Power: { accum_voting_power }')
