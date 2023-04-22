=========================
CircuitPython eRPC Client
=========================

This is a CircuitPython port of the CPython UART-based `eRPC <https://github.com/EmbeddedRPC/erpc>`_ client. This implementation is largely adapted from the CPython eRPC client code, and is mainly altered where CircuitPython does not support a particular module or feature (e.g. threading). 

This port does not include a server-side eRPC implementation, and currently only supports UART for transport.