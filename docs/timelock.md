# Timelock

Simple implementation of a time-locked approval process with immutable duration at point of deployment. Used by Controller contract to adjust convenience fee in a transparent manner.

## Parameters

* admin: address of the contract deployer or someone with the administrative right to queue, cancel and execute transactions from the timelock contract (to set convenience fee on the controller)
* delay: integer  duration in blockheight between minimum (2 days) and maximum (30 days) to time-lock the transaction queue
