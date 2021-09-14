#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/daotoken.py
# VERSION: 	 1.0
# CREATED: 	 2021-09-12 09:51
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contracts ###
from brownie import Controller, Timelock
### Third-Party Packages ###
from brownie.network.gas.strategies import GasNowStrategy
from eth_account import Account
from pytest import fixture, mark
### Local Modules ###
from . import *
from .timelock import deploy_timelock

@mark.parametrize('gas_speed', ('standard', 'fast'))
def test_deploy_controller(admin: Account, \
  governance: Account, treasury: Account, \
    deploy_timelock: Timelock, gas_speed: str):
  '''
  TEST: Deploy Controller Contract
  '''
  timelock = deploy_timelock
  ### Deployment ###
  gas_strategy = GasNowStrategy(gas_speed)
  ctrl         = Controller.deploy(governance, timelock, treasury, { 'from': admin, 'gas_price': gas_strategy })
  print(f'Controller: { ctrl }')
