# FLEXStakingStrategy

Inherits `BaseStakingStrategy` contract; Implements `getName()` and `harvest()` differently form base

## Parameters

* rewards: `address`  the StakingRewards contract implementing IStakingRewards interface that handles the reward ratio and handouts.
* want: `address` the token where this strategy wants and will reward for staking
* governance: `address` (Can be Gnosis MultiSig on Mainnet)
* controller: `address` the address to the DAO Controller  
* timelock: `address` pointing at deployed `Timelock` contract
