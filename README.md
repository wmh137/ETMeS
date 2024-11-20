# ETMeS (Electrical Transportation Measurement System)

*-- Build your own PPMS with few code !*

## What is ETMeS ?

ETMeS is a python package. It helps you control your digital source-meter, temperature controller, magnet and other instruments.

## What you need to learn ?

Basic usage of python is enough !

## Requirement

- Windows >= 10 (Powershell on Windows 7 does not support ANSI escape codes)
- python >= 3.8, pyvisa, pythonnet (optional), matplotlib (optional)
- .NET

## Basic usage

You need to write code as follow steps:

1. instantiate all the classes of your instruments
`k = etmes.Keithley2400("GPIB:xxxx")`
1. instantiate a experiment with your instruments and path of data file
`exp = etmes.etmes([k], "data")`
1. control instruments as you want
1. experiment standby (recommend) `exp.standby()` or stop `exp.stop()`

Following principles should be followed:

- some instruments cannot reach the targets immediately, wait for them is necessary
`exp.wait(time, [ins1 ins2 ...], [waitFlag1, waitFlag2, ...])`
- refresh the status manually unless you are waiting
`exp.refresh()`
- record the status manually as well
`exp.record()`
- if the class of your instrument is not applied, please write it by yourself: inherit `class ins`, override necessary functions and define specific functions of your instrument
`class myins(ins)`

Some measurements are applied in `etmes.meas`. Instantiate a measurement `m = etmes.meas(exp)` and call its functions.

## Future plan

- add more classes of different instruments
- compatible with modbus
- compatible with Windows 7
- test on Linux

## Acknowledge

We are inspired by [labdrivers](https://github.com/masonlab/labdrivers), and grateful to its contributors.

## Contributors

[Minghao Wang](wmh137@mail.ustc.edu.cn) (Founder)

[Ming Huang](hm2018@mail.ustc.edu.cn)

## Final

**Looking forward to your contribution !**
