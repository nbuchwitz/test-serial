# Serial Device Test

This repository provides a tool `test-serial.py`, which can be used to test the serial connection between two devices. It can be used in plain serial or RS485 mode.

## Install Dependencies

```
sudo apt install python3-serial
```

## Usage

```
usage: test-serial.py [-h] -d DEVICE [-b BAUD] [--rs485] [--response-timeout RESPONSE_TIMEOUT] {server,client}

positional arguments:
  {server,client}

options:
  -h, --help            show this help message and exit
  -d DEVICE, --device DEVICE
  -b BAUD, --baud BAUD  Baudrate for interface
  --rs485               Use interface in RS485 mode
  --response-timeout RESPONSE_TIMEOUT
```
