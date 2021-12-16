from yaml.tokens import TagToken
from brownie import veFLEX, DailyPayout
from brownie.network import accounts, Chain
from yaml import safe_load
from eth_account.account import Account, ValidationError

TERM_RED  = '\033[1;31m'
TERM_NFMT = '\033[0;0m'

def main():
  chain = Chain()
  print(f'Network Chain-ID: { chain }')
  chain_id = chain._chainid
  if chain_id != 10000:
    return print(f'{TERM_RED}network is not in smartbch-mainnet, exit!{TERM_NFMT}')

  addresses = ['0x513b1C3941656b9f8e797693039256c6fF828d22',
              '0x945e9704D2735b420363071bB935ACf2B9C4b814',
              '0xfd8E76520296bddb6e3657Af11700F10CC165A98',
              '0x81f056b3C93379dA0A22ed2De40909a333dF1164',
              '0x83206707Bb189b811c71cc0d1B3Aa445Da27E4ce',
              '0x72b3f018e1B9Db47d8C37Fd7549083395391a800',
              '0x4Ef9435598f078661edF182D0671E4d737F4fc27',
              '0xDDb3F8cD1303eF25a8dd8f2FA904a771a93DF1a5',
              '0xd4dee0ADAEf1E4070e8d96F0F6C181c9DaA7270E']

  payout_address = '0xe5B22d8240F479f34aBA4913A67964f3Df9dAFCc'
  payout = DailyPayout.at(payout_address)
  
  veFlex_address = '0x52aDbbB04572f61a9b48DD649719592C80750958'
  veflex = veFLEX.at(veFlex_address)

  privkey_file = 'wallet.smartbch-mainnet.yml'

  try:
    with open(privkey_file) as f:
      content = safe_load(f)
      privkey = content.get('privkey', None)
      acct = accounts.add(privkey)
  except FileNotFoundError:
    print(f'{TERM_RED}Cannot find wallet mnemonic file defined at `{privkey_file}`.{TERM_NFMT}')
    return
  except ValidationError:
    print(f'{TERM_RED}Invalid address found in wallet mnemonic file.{TERM_NFMT}')
    return
  balance = acct.balance()
  print(f'Account: {acct}')
  print(f'Balance: {balance}\n\n')


  epoch = min(payout.getCurrentEpoch({'from': acct}), payout.currentEpoch())
  print(f'Current epoch is {epoch}')

  for i in range(epoch + 1):
    print(f'{TERM_RED}== Epoch {i} =={TERM_NFMT}')
    
    # get epoch i start block height
    start_block_height = payout.getEpochStartBlockHeight(i, {'from': acct})
    print(f'start block height:   {start_block_height}')
    # rewards in the epoch
    reward = payout.payoutForEpoch(i)
    print(f'epoch total reward:   {reward}')

    # veFlex total balance at the block height
    total_veflex = veflex.totalSupplyAt(start_block_height)
    print(f'total veflex balance: {total_veflex}')

    sum = 0
    for addr in addresses:
      print(f'\taddress: {addr}')
      # addr veflex balance at the height
      addr_veflex = veflex.balanceOfAt(addr, start_block_height)
      
      print(f'\tveflex:  {addr_veflex}')
      # using integer divide to mimic solidity logic
      if total_veflex == 0:
        addr_reward = 0
      else:
        addr_reward = (reward * addr_veflex) // total_veflex
      print(f'\treward:  {addr_reward}')
      sum += addr_reward
    
    print(f'manually sum of addr reward: {sum}')
    print(f'contract reward:             {reward}')
    if sum == reward:
      print(f'EQUAL')
    elif sum < reward:
      print(f'SMALLER!')
    else:
      print(f'{TERM_RED}BIGGER!{TERM_NFMT}')
    print('\n')