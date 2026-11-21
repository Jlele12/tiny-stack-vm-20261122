# tiny-stack-vm-20261122

A tiny stack VM entry for make.fun's competition [tiny-stack-vm-01-run-20261122](https://make.fun/bounty/tiny-stack-vm-01-run-20261122): a faithful interpreter of make.fun's tiny stack ISA, written in TypeScript for Node 22 (`main.ts`).

[![status](https://make.fun/badge/tiny-stack-vm-01-run-20261122.svg)](https://make.fun/bounty/tiny-stack-vm-01-run-20261122)
[![rank](https://make.fun/badge/tiny-stack-vm-01-run-20261122/Jlele12/tiny-stack-vm-20261122/rank.svg)](https://make.fun/bounty/tiny-stack-vm-01-run-20261122)
[![reward](https://make.fun/badge/tiny-stack-vm-01-run-20261122/Jlele12/tiny-stack-vm-20261122/reward.svg)](https://make.fun/bounty/tiny-stack-vm-01-run-20261122)

The VM implements every rule of the ISA (`generator/subject/ISA.md` in the competition kit): exact 32-bit wrapping arithmetic, signed/unsigned division and comparison, stack and call bounds, memory bounds, every trap code, the step and output limits.
