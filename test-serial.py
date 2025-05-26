#!/usr/bin/env python3

"""Test serial connection between two devices."""

import argparse
import signal
import sys
from types import FrameType
from typing import Optional

import serial
import serial.rs485


class InvalidSerial5Reponse(Exception):
    """Missmatch between response and expected reponse."""

    def __init__(self, response: bytes, expected_response: bytes) -> None:
        super().__init__(
            f"Reponse does not match expected reponse: {response} != {expected_response}"
        )
        self.response = response
        self.expected_response = expected_response


class SerialInterface:
    """Serial interface class for testing RX and TX functionality."""

    def __init__(self, device: str, baudrate: int = 115200, timeout: int = 2) -> None:
        """Create serial interface which is used to run tests.

        Parameters
        ----------
        device : str
            Name of the serial device to use.
        baudrate : int, optional
            Baudrate. Defaults to 115200.
        timeout : int, optional
            Response timeout. Defaults to 2.
        """
        self.device = device

        self.port = serial.Serial(device, baudrate=baudrate, timeout=timeout)

        # drain RX buffer
        if self.port.in_waiting > 0:
            self.port.read(ser.in_waiting)

    def echo_client(self, num_runs: int = 10) -> None:
        """Send payload string on serial interface and wait for response.

        The payload string is formatted like 'TX_run_N' whereas 'N' represents the current index
        of the loop. The number of runs can be altered with the parameter 'num_runs'.

        Parameters
        ----------
        num_runs : int, optional
            Number of test runs. Defaults to 10.

        Raises
        ------
        InvalidSerialReponse
            Exception contains reponse and expected reponse
        """
        for run in range(num_runs + 1):
            payload = f"TX_run_{run}\n"
            expected_response = f"RX_run_{run}\n".encode()

            self.port.write(payload.encode())
            response = self.port.readline()

            if response != expected_response:
                raise InvalidSerial5Reponse(response, expected_response)

    def echo_server(self) -> None:
        """Run echo server on serial interface.

        The received payload is altered by replacing the string 'TX' with 'RX' and send back.
        """
        while True:
            try:
                payload = self.port.readline()
                payload = payload.decode()

                response = payload.replace("TX", "RX")
                self.port.write(response.encode())
            except UnicodeDecodeError:
                # This is an echo server and we really don't care about any errors.
                # So let's print the payload for the sake of easier debugging and go on.
                print(f"Failed to decode payload: {payload}", file=sys.stderr)


class RS485Interface(SerialInterface):
    """RS485 interface class for testing RX and TX functionality."""

    def __init__(self, device: str, baudrate: int = 115200, timeout: int = 2) -> None:
        self.device = device

        self.port = serial.rs485.RS485(device, baudrate=baudrate, timeout=timeout)
        self.port.rs485_mode = serial.rs485.RS485Settings()


def signal_handler(signal: int, frame: Optional[FrameType]) -> None:
    """Gracefully handle enforced program exit."""
    sys.exit()


def main() -> None:
    """Parse CLI args and run echo server."""
    signal.signal(signal.SIGINT, signal_handler)

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--device", required=True)
    parser.add_argument("-b", "--baud", default=115200, type=int, help="Baudrate for interface")
    parser.add_argument(
        "--rs485",
        action="store_true",
        default=False,
        required=False,
        help="Use interface in RS485 mode",
    )
    parser.add_argument("--response-timeout", default=3, type=int)
    parser.add_argument("mode", default="server", type=str, choices=["server", "client"])

    args = parser.parse_args()

    if args.rs485:
        interface = RS485Interface(args.device, args.baud, args.response_timeout)
    else:
        interface = SerialInterface(args.device, args.baud, args.response_timeout)

    if args.mode == "server":
        interface.echo_server()
    else:
        try:
            interface.echo_client()
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)

        print("TEST OK")


if __name__ == "__main__":
    main()
