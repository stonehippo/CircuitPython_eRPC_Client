#
# Generated by erpcgen 1.10.0 on Sat Apr 22 14:59:30 2023.
#
# AUTOGENERATED - DO NOT EDIT
#

# Abstract base class for rpc_system
class Irpc_system(object):
    SERVICE_ID = 1
    RPC_SYSTEM_VERSION_ID = 1
    RPC_SYSTEM_ACK_ID = 2

    def rpc_system_version(self):
        raise NotImplementedError()

    def rpc_system_ack(self, c):
        raise NotImplementedError()


