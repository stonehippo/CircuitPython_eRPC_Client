# Copyright (c) 2015-2016 Freescale Semiconductor, Inc.
# Copyright 2016-2017 NXP
# All rights reserved.
#
# Modified to work with CircuitPython 7.3.x by George White <stonehippo@gmail.com>
# Copyright 2022 George White
#
# SPDX-License-Identifier: BSD-3-Clause

from collections import namedtuple

# A dumb hack until we get enum.Enum in CP
# This should be switched out for enum ASAP
# and also fix the lookuip in basic_codec.py when that happens!
MessageTypes = namedtuple('MessageTypes', ['kInvocationMessage', 'kOnewayMessage', 'kReplyMessage', 'kNotificationMessage'])

class MessageType(object):
    (kInvocationMessage, kOnewayMessage, kReplyMessage, kNotificationMessage) = range(0,4)
    types = MessageTypes(kInvocationMessage, kOnewayMessage, kReplyMessage, kNotificationMessage)

MessageInfo = namedtuple('MessageInfo', ['type', 'service', 'request', 'sequence'])

class CodecError(RuntimeError):
    pass

class Codec(object):
    def __init__(self):
        self.reset()

    @property
    def buffer(self):
        return self._buffer

    @buffer.setter
    def buffer(self, buf):
        self._buffer = buf
        self._cursor = 0

    def reset(self):
        self._buffer = bytearray()
        self._cursor = 0

    def start_write_message(self, msgInfo):
        raise NotImplementedError()

    def write_bool(self, value):
        raise NotImplementedError()

    def write_int8(self, value):
        raise NotImplementedError()

    def write_int16(self, value):
        raise NotImplementedError()

    def write_int32(self, value):
        raise NotImplementedError()

    def write_int64(self, value):
        raise NotImplementedError()

    def write_uint8(self, value):
        raise NotImplementedError()

    def write_uint16(self, value):
        raise NotImplementedError()

    def write_uint32(self, value):
        raise NotImplementedError()

    def write_uint64(self, value):
        raise NotImplementedError()

    def write_float(self, value):
        raise NotImplementedError()

    def write_double(self, value):
        raise NotImplementedError()

    def write_string(self, value):
        raise NotImplementedError()

    def write_binary(self, value):
        raise NotImplementedError()

    def start_write_list(self, length):
        raise NotImplementedError()

    def start_write_union(self, discriminator):
        raise NotImplementedError()

    def write_null_flag(self, flag):
        raise NotImplementedError()

    ##
    # @return MessageInfo object.
    def start_read_message(self):
        raise NotImplementedError()

    def read_bool(self):
        raise NotImplementedError()

    def read_int8(self):
        raise NotImplementedError()

    def read_int16(self):
        raise NotImplementedError()

    def read_int32(self):
        raise NotImplementedError()

    def read_int64(self):
        raise NotImplementedError()

    def read_uint8(self):
        raise NotImplementedError()

    def read_uint16(self):
        raise NotImplementedError()

    def read_uint32(self):
        raise NotImplementedError()

    def read_uint64(self):
        raise NotImplementedError()

    def read_float(self):
        raise NotImplementedError()

    def read_double(self):
        raise NotImplementedError()

    def read_string(self):
        raise NotImplementedError()

    def read_binary(self):
        raise NotImplementedError()

    ##
    # @return Int of list length.
    def start_read_list(self):
        raise NotImplementedError()

    ##
    # @return Int of union discriminator.
    def start_read_union(self):
        raise NotImplementedError()

    def read_null_flag(self):
        raise NotImplementedError()




