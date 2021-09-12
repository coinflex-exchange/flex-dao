# Distributor

Formerly known as MasterChef;
Handles the distribution of reward tokens deployed. Holds tremendous power and therefore has its ownership
transferred to a governance smart contract once tokens is sufficiently distributed and the community can 
show to govern itself.

## Distributor: Parameters

reward_token: address pointing to deployed `RewardToken`
devfund: address (Can be Gnosis MultiSig on Mainnet)
token_per_block: integer  the rate of reward distribution per block
start_block: integer the blockheight where the distribution begins
end_block: integer the blockheight where the distribution ends

## Distributor: TODO - rename and deploy
