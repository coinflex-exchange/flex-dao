#!/usr/bin/env python3.7
# coding:utf-8
# Copyright (C) 2019-2021 All rights reserved.
# FILENAME:  tests/daotoken.py
# VERSION: 	 1.0
# CREATED: 	 2021-09-03 14:07
# AUTHOR: 	 Aekasitt Guruvanich <sitt@coinflex.com>
# DESCRIPTION:
#
# HISTORY:
#*************************************************************
### Project Contracts ###
from brownie import DAOToken
### Third-Party Packages ###
from eth_account import Account
from pytest import fixture, mark
### Local Modules ###
from . import *

@fixture
def deploy_daotoken(admin: Account) -> DAOToken:
  '''
  FIXTURE: Deploy a DAOToken contract to be used by other contracts' testing.  

  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :returns:  `DAOToken`  
  '''
  return DAOToken.deploy({ 'from': admin })

@mark.parametrize('gas_speed', ('fast', 'standard'))
def test_deploy_daotoken(admin: Account, gas_price: dict, gas_speed: str):
  '''
  TEST: Deploy DAOToken Contract
  
  ---
  :param: admin  `Account`  the wallet address to deploy the contract from  
  :param: gas_price  `dict`  the mock gas_price object as it would be like to receive from Gas Station API  
  :param: gas_speed  `str`  the mock speed key to be used with gas_price object; either `fast` or `standard`  
  '''
  ### Deployment ###
  limit: int         = DAOToken.deploy.estimate_gas({ 'from': admin }) * gas_price[gas_speed]
  daotoken: DAOToken = DAOToken.deploy({ 'from': admin, 'gas_limit': limit })
  print(f'DAOToken: { daotoken }')
