# Directory Structure
The directory structure is as follows:

```
.
├── device_1
│   ├── firmware
│   ├── inputs
│   ├── plogs
│   └── record
└── device_2
    ├── firmware
    ├── inputs
    ├── plogs
    └── record
```

## `firmware`
This directory contains the firmware that is flashed on the device. It is exported from the [Mbed Online Compiler](https://ide.mbed.com/compiler/).

## `inputs`
This is where TDES saves input files for future fuzz runs. You must supply the first input file, which should be named `initial`.

## `plogs`
This is where TDES saves `.plog` files from fuzz runs. The first `.plog` file is created during the first run of TDES, it is named `initial`.

## `record`
This is where TDES looks for the Avatar2/PANDA recording script. This script is device/program specific, and must be supplied by you.
