# @version ^0.2.16

'''
@title Delegated distribution of payout tokens by an admin
@notice To minimise attack surfaces, addresses are not changeable by the admin;
        they can only trigger a call of distribute() on the revenue share contract
'''
### Interfaces ###
from vyper.interfaces import ERC20
interface PayoutContract:
  def distribute(_amount: uint256): nonpayable

### Member Variables ###
admin: public(address)  # Account which can trigger the distribution of FLEX tokens from this contract
payout: public(address) # The receiving Payout Contract (Daily/Quarterly) to receive the FLEX tokens
flex: public(address)   # Address of the FLEX token, replaced by constant at production
name: public(String[64])    # The name of the distributor
isDistributor: public(HashMap[address, bool]) # Delegatees

### Constants ###
# FLEX: constant(address) = 0x98Dd7eC28FB43b3C4c770AE532417015fa939Dd3

### Events ###
event OwnershipTransferred:
  prevAdmin: address
  currAdmin: address

event CallDistribute:
  distributor: indexed(address)
  amount: uint256

event IsDistributor:
  distributor: address
  status: bool

@external
def __init__(_payout: address, _flex: address, _name: String[64]):
  '''
  @notice Contract may be published by an address that will not be the admin
  @dev It is safe to approve with maxuint256 because all the FLEX is going to payout contract anyway
  @param _payout address to the Payout contract (DailyPayout) which implements `distribute(_amount: uint256)
  @param _flex address to the FLEX Token; Pending removal during production as it can be defined as a constant
  '''
  assert _payout != ZERO_ADDRESS, 'Payout contract cannot be null address' # dev: payout null
  assert _flex   != ZERO_ADDRESS, 'FLEX contract cannot be null address'   # dev: flex null
  self.admin      = msg.sender
  self.payout     = _payout
  self.flex       = _flex
  self.name       = _name
  assert ERC20(_flex).approve(_payout, MAX_UINT256), 'Unable to max approve FLEX tokens for transfers' # dev: approval failed

@external
@nonreentrant('lock')
def distribute():
  '''
  @notice Ensures non-zero balance before executing distribute(_amount) on a payout contract with entire balance.
  '''
  assert msg.sender == self.admin or self.isDistributor[msg.sender], 'You are not the admin or valid delegatee'         # dev: admin only
  flex_balance: uint256 = ERC20(self.flex).balanceOf(self)
  assert flex_balance > 0, 'You must transfer more than zero FLEX' # dev: insufficient balance
  PayoutContract(self.payout).distribute(flex_balance)
  log CallDistribute(msg.sender, flex_balance)

@external
def transferOwnership(_addr: address):
  '''
  @notice Transfer ownership of Distributor contract to `_addr`
  @param _addr Address to have ownership transferred to
  '''
  assert msg.sender == self.admin,   'You are not the admin'            # dev: admin only
  assert _addr      != ZERO_ADDRESS, 'New admin address cannot be null' # dev: admin not set
  _prev: address     = self.admin
  self.admin         = _addr
  log OwnershipTransferred(_prev, _addr)

@external
def addDistributor(_addr: address):
  '''
  @notice Add delegatee to call distribute function
  @param _addr Address to have permission to call distribute function
  '''
  assert msg.sender == self.admin,   'You are not the admin'            # dev: admin only
  assert _addr      != ZERO_ADDRESS, 'Delegatee address cannot be null' # dev: admin not set
  self.isDistributor[_addr] = True
  log IsDistributor(_addr, True)

@external
def removeDistributor(_addr: address):
  '''
  @notice Remove delegatee to call distribute function
  @param _addr Address to remove permission to call distribute function
  '''
  assert msg.sender == self.admin,   'You are not the admin'            # dev: admin only
  assert _addr      != ZERO_ADDRESS, 'Delegatee address cannot be null' # dev: admin not set
  self.isDistributor[_addr] = False
  log IsDistributor(_addr, False)