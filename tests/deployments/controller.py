#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/deployments/controller.py
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
from brownie.network.gas.strategies import ExponentialScalingStrategy
from eth_account import Account
from pytest import fixture, mark
### Local Modules ###
from tests import *
from .timelock import deploy_timelock

@fixture
def deploy_controller(admin: Account, \
  governance: Account, treasury: Account, deploy_timelock: Timelock) -> Controller:
  '''
  FIXTURE: Returns deployed Controller contract to be used by other contract testing.
  '''
  timelock     = deploy_timelock
  gas_strategy = ExponentialScalingStrategy('10 gwei', '50 gwei')
  return Controller.deploy(governance, timelock, treasury, { 'from': admin, 'gas_price': gas_strategy })

def test_deploy_controller(admin: Account, governance: Account, treasury: Account, deploy_timelock: Timelock):
  '''
  TEST: Deploy Controller Contract
  '''
  timelock = deploy_timelock
  ### Deployment ###
  gas_strategy = ExponentialScalingStrategy('10 gwei', '50 gwei')
  ctrl         = Controller.deploy(governance, timelock, treasury, { 'from': admin, 'gas_price': gas_strategy })
  print(f'Controller: { ctrl }')
