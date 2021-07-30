# Documentation on FLEX DAO contracts

---

## RewardToken

Formerly known as PICKLE or YFI;
The RewardToken is a tool for coordination between contributors, community and associated protocols.
It was created to decentralize the management and development of yearn products while providing an environment for fast paced innovation.

### RewardToken Parameters - n/a

### RewardToken: TODO - rename and deploy

---

## Distributor

Formerly known as MasterChef;
Handles the distribution of reward tokens deployed. Holds tremendous power and therefore has its ownership
transferred to a governance smart contract once tokens is sufficiently distributed and the community can 
show to govern itself.

### Distributor: Parameters

reward_token: address pointing to deployed `RewardToken`
devfund: address (Can be Gnosis MultiSig on Mainnet)
token_per_block: integer  the rate of reward distribution per block
start_block: integer the blockheight where the distribution begins
end_block: integer the blockheight where the distribution ends

### Distributor: TODO - rename and deploy

---

## Controller

Primary contract for Decentralized Autonomous Organization Contract Infrastructure;

### Controller: Parameters

* governance: address (Can be Gnosis MultiSig on Mainnet)
* strategist: address (Can be Gnosis MultiSig on Mainnet)
* timelock: address pointing at deployed `Timelock` contract
* devfund: address (Can be Gnosis MultiSig on Mainnet)
* treasury: address (Can be Gnosis MultiSig on Mainnet)
* onesplit: address pointing at deployed `OneSplitAudit` or `MockOneSplitAudit`

---

## MockOneSplitAudit

This is a deployment that mocks basic functionality of 1Inch's OneSplitAudit contract deployed on Ethereum Mainnet. It serves only one function when deployed which is informing the price pre-swapped and facilitating swap for the GaugeProxy. In this demo/mock contract, it assumes that only StableSwapFLEX is available.

### MockOneSplitAudit: Parameters - n/a

### MockOneSplitAudit: TODO - depending on chain selected, adopt 1Inch’s equivalent contracts or implement Oracle

---

## GaugeProxy

Proxy contract pointing to `LiquidityGauge` implementation.

### GaugeProxy: Parameters

* distributor: address pointing to deployed `Distributor`
* escrow: address pointing to deployed `veFLEX`
* reward_token: address pointing to deployed `RewardToken`
* treasury: address (Can be Gnosis MultiSig on Mainnet)

### GaugeProxy: TODO - Deploy

---

## LiquidityGauge

The Store and Implementation side of GaugeProxy. This contract handles the reward duration of the staking process.

### LiquidityGauge: Parameters - n/a

### See GaugeProxy for LiquidityGauge’s chained deployment

---

## DAOToken

Internal tally for the voting rights of the token holders.

### DAOToken: Parameters - n/a

### See GaugeProxy for DAOToken’s chained deployment

---

## ProtocolGovernance

Modifies GaugeProxy to allow for the transfer of governance power with two processes in mind, setting and accepting.

### ProtocolGovernance: Parameters - n/a

### ProtocolGovernance: TODO - n/a

---

## Timelock

Simple implementation of a time-locked approval process with immutable duration at point of deployment. Used by Controller contract to adjust convenience fee in a transparent manner.

### Timelock: Parameters

* admin: address of the contract deployer or someone with the administrative right to queue, cancel and execute transactions from the timelock contract (to set convenience fee on the controller)
* delay: integer  duration in blockheight between minimum (2 days) and maximum (30 days) to time-lock the transaction queue

---

## Strategies and Vaults

Accompanying contracts to be listed on the GaugeProxy and assigned ownership and fund movement powers to the Controller contract. These two, coupled as one, represent a Proposal made to the DAO and can be selected and voted upon by DAOToken holders, contributors and community

### Strategies and Vaults: Parameters

varies among contracts. Can be LiquidityPool focused like Yearn and Pickle or Token Listing focused like ShapeShift

* [See: Strategy Risks](https://docs.yearn.finance/resources/risks/strategy-risks)
* [See: Vault Risks](https://docs.yearn.finance/resources/risks/vault-risks)
* [See: Proposal Process](https://docs.yearn.finance/governance/proposal-process)
