# Copyright (c) 2015-2016 Freescale Semiconductor, Inc.
# Copyright 2016-2021 NXP
# Copyright 2022 ACRIOS Systems s.r.o.
# All rights reserved.
#
# Modified to work with CircuitPython 7.3.x by George White <stonehippo@gmail.com>
# Copyright 2022 George White
#
# SPDX-License-Identifier: BSD-3-Clause

import board
import busio
import struct
from .crc16 import Crc16
from .client import RequestError

class Transport(object):
    def __init__(self):
        pass

    def send(self, message):
        raise NotImplementedError()

    def receive(self):
        raise NotImplementedError()

class FramedTransport(Transport):
    HEADER_LEN = 4

    def __init__(self):
        super(FramedTransport, self).__init__()
        self._Crc16 = Crc16()

    @property
    def crc_16(self):
        return self._Crc16

    @crc_16.setter
    def crc_16(self, crcStart):
        if type(crcStart) is not int:
            raise RequestError("invalid CRC, not a number")
        self._Crc16 = Crc16(crcStart)

    def send(self, message):
        crc = self._Crc16.computeCRC16(message)

        header = bytearray(struct.pack('<HH', len(message), crc))
        assert len(header) == self.HEADER_LEN
        self._base_send(header + message)

    def receive(self):
        # Read fixed size header containing the message length.
        headerData = self._base_receive(self.HEADER_LEN)
        messageLength, crc = struct.unpack('<HH', headerData)

        # Now we know the length, read the rest of the message.
        data = self._base_receive(messageLength)
        computedCrc = self._Crc16.computeCRC16(data)

        if computedCrc != crc:
            raise RequestError("invalid message CRC")
        return data

    def _base_send(self, data):
        raise NotImplementedError()

    def _base_receive(self):
        raise NotImplementedError()

class SerialTransport(FramedTransport):
    def __init__(self, uart):
        super(SerialTransport, self).__init__()
        self._serial = uart # 8N1 by default

    def close(self):
        self._serial.deinit()

    def _base_send(self, data):
        self._serial.write(data)

    def _base_receive(self, count):
        return self._serial.read(count)
