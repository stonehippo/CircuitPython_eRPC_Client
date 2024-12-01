# CircuitPython support for WiFi and Bluetooth LE on Seeed WIO Terminal

## Context

The [Seeed WIO Terminal](https://www.seeedstudio.com/Wio-Terminal-p-4509.html) is generally supported by [CircuitPython](https://circuitpython.org/board/seeeduino_wio_terminal/), but there is no implementation for access to the WiFi or Bluetooth LE networking functions on the board. After taking a look at the Arduino support for these features, I can see that the RealTek RTL8720D is set up to be driven by a UART connection from the SAMD51 that acts as the main controller for the WIO Terminal. In other words, the RTL8720D is set up as a co-processor, similar to the ESP32 in Adafruit's [Airlift modules](https://www.adafruit.com/product/4201).

The UART driver is based on an [embedded remote procedure call (eRPC) library](https://github.com/Seeed-Studio/Seeed_Arduino_rpcUnified) on the Arduino side. This is good news, because it means that there is a chance that the driver can be implemented in CP! In theory, this can be built on [`busio.UART`](https://docs.circuitpython.org/en/latest/shared-bindings/busio/#busio.UART), though it's not a simple RX/TX protocol. There seems to be some framing around the data coming in and out of the RTL8720D.

There are some higher-level libraries, like [Seeed Arduino rpcWiFi](https://github.com/Seeed-Studio/Seeed_Arduino_rpcWiFi) and [Seeed Arduino rpcBLE](https://github.com/Seeed-Studio/Seeed_Arduino_rpcBLE) that provide the user-facing APIs. For details on their usage, see:

- [WIO Terminal WiFI documentation (Arduino)](https://wiki.seeedstudio.com/Wio-Terminal-Network-Overview/)
- [WIO Terminal BLE documentation (Arduino)](https://wiki.seeedstudio.com/Wio-Terminal-Bluetooth-Overview/)

Interestingly, if this can be made to work, it seems like simultaneous WiFi and BLE is possible, since the underlying RT8720D firmware suppports it, as does the Arduino eRPC driver.

## Notes

- CP already has [the pins for the connection from the WIO Terminal's SAMD51 to the RTL8729D](https://github.com/adafruit/circuitpython/blob/main/ports/atmel-samd/boards/seeeduino_wio_terminal/pins.c) defined
- The SAMD51 talks to the RTL8720D at 115200 bps
- [`busio.UART`](https://docs.circuitpython.org/en/latest/shared-bindings/busio/#busio.UART) is going to be the basis for the eRPC transport.
- The atmel-samd CP port does not yet support RTS/CTS in busio.UART. I'll probably have to fix that before I can get the RTL8720D to work correctly.

## Pins for RTL8720D on the WIO Terminal

Based on the WIO Terminal CircuitPython config, here are the pins/pads for talking to the RTL8720D:

```
    // RTL8720D
    { MP_OBJ_NEW_QSTR(MP_QSTR_RTL_PWR),  MP_ROM_PTR(&pin_PA18) },       // CHIP_PU
    { MP_OBJ_NEW_QSTR(MP_QSTR_RTL_RXD),  MP_ROM_PTR(&pin_PC22) },
    { MP_OBJ_NEW_QSTR(MP_QSTR_RTL_TXD),  MP_ROM_PTR(&pin_PC23) },
    { MP_OBJ_NEW_QSTR(MP_QSTR_RTL_MOSI),  MP_ROM_PTR(&pin_PB24) },
    { MP_OBJ_NEW_QSTR(MP_QSTR_RTL_CLK),  MP_ROM_PTR(&pin_PB25) },
    { MP_OBJ_NEW_QSTR(MP_QSTR_RTL_MISO),  MP_ROM_PTR(&pin_PC24) },
    { MP_OBJ_NEW_QSTR(MP_QSTR_RTL_CS),  MP_ROM_PTR(&pin_PC25) },
    { MP_OBJ_NEW_QSTR(MP_QSTR_RTL_READY),  MP_ROM_PTR(&pin_PC20) },     // IRQ0
    { MP_OBJ_NEW_QSTR(MP_QSTR_RTL_DIR),  MP_ROM_PTR(&pin_PA19) },       // SYNC
```

See https://github.com/adafruit/circuitpython/blob/main/ports/atmel-samd/boards/seeeduino_wio_terminal/pins.c for more.

### A TRAP?! (I have been trying to use the wrong pins)

Well, no, not a trap but an issue with my understanding of how to talk to the RTL chip. As noted above, the CircuitPython config for the WIO Terminal has two pins `RTL_TXD` and `RTL_RXD` that are *implied* to be the UART pins for comms with the module. The Seeed schematic doesn't make this clear at all (it refers to those pins as UART_LOG_TXD and UART_LOG_RXD in brief note on the schematic). However, I was looking at issues in the Seeed RPC Unified repo, and noticed this:

https://github.com/Seeed-Studio/Seeed_Arduino_rpcUnified/issues/6

Looking at the comments there, is looks PC24 (pad 2) is meant to be TX and PB24 (pad 0) is meant to be RX. In the CP config, that's `RTL_MISO` and `RTL_MOSI` pins! So it may be that I've been using the wrong pins (the ones that seem like they're the UART, rather than the repurposed SPI pins). Ugh.

Great news though is that this was the blocker that was keeping me from talking to the RTL chip. As noted at the bottom of this gist, once I realized this was the issue, I was able to send an eRPC request and get a valid reponse. Yay!

## Thoughts

The Adafruit PyPortal's CP networking implementation follows a couple of patterns. On the BLE side, it uses `adafruit_airlift` as an implementation to pass to `adafruit_ble` (and relies on `_bleio` at a low level) (see [CircuitPython BLE](https://learn.adafruit.com/adafruit-pyportal/circuitpython-ble)). On the Wifi side, there's a dedicated driver `adadfruit_esp32spi` that is compatible with `adafruit_requests` (see [Internet Connect](https://docs.circuitpython.org/en/latest/shared-bindings/busio/#busio.UART)). This feels a little messy, but it's the pattern that's currently followed by the CP-compatible device that's closest to the WIO Terminal. I need to take a look at these patterns and see how to best implement this for the WIO Terminal.

The reliance on UART may be an issue. CP doesn't support interrupts, and I think that's probably the most efficient way to handle checking to see if the RTL8720D has data. I'm going to have to dig into the Arduino eRPC implementation a bit more to see what's what.

## eRPC

The connectivity between the SAMD51 chip and the RealTek on the WIO is based on [eRPC](https://github.com/EmbeddedRPC/erpc), which is an open RPC implementation designed for chip-to-chip communication. And it turns out that the `erpcgen` tool can generate Python code! Still looking at this, but it might be good news, as it may enable me to get the basis for a CircuitPython implementation without having to rewrite the WIO's ePRC implementation from the ground up. 

For details on eRPC, a good place to start is [on the development wiki](https://github.com/EmbeddedRPC/erpc/wiki).

### Generating eRPC shims for Python

The `.erpc` files, which contain the IDL (interface definition language) descriptions are available in the [seeed-ambd-firmware repository](https://github.com/Seeed-Studio/seeed-ambd-firmware). To build the eRPC shims for Python, do this (need to install `erpcgen` first):

```
git clone https://github.com/Seeed-Studio/seeed-ambd-firmware.git
cd seeed-ambd-firmare/erpc_idl
erpcgen -g py -o [some path] rpc_system.erpc
```

This will generate all of the shims for an eRPC client and server for the firmware. This is a huge step, since it means we have the full client side API in Python! Of course, it relies on a CPython implementation of eRPC, so the next step is to get something that works on CircuitPython. Fortunately, this seems like it might be somewhat straigtforward.

## eRPC Client for CircuitPython

I've done a little porting of the CPython eRPC core and I think I've got a working version. It's at https://github.com/stonehippo/CircuitPython_eRPC_Client. ~~I've sort of confirmed that this works, using some modified shims for the RTL WiFi API, but I haven't really got the chip to talk me yet. It seems that the eRPC implementation is pretty big, and the chip is running into `MemoryError` issues when I try to import it. On to the next step…~~ I have got eRPC working, along with the first of the RPC shims. This means I can talk to the RTL and get it to give me a couple of basic acknowledgements. Next up is to get something that works for WiFi, BLE, or both. The IDL-generated code for those might be a bit on the hefty side, though…

## eRPC baseline is working!

After realizing that my assumption about which pins should be used for the UART to the RTL was wrong, I was able to get the most basic eRPC function working, which is a big step! This confirms that the basic transport and encoding seem to be correct.

Here's what I tried (and that worked!)

```
import board
import busio
from time import sleep
from digitalio import DigitalInOut

import erpc
from erpc_shim import rpc_system, rpc_wifi_api

# Reset RTL8720
def rtl_init():
    pwr = DigitalInOut(board.RTL_PWR)
    pwr.switch_to_output()
    pwr.value = False
    sleep(.125)
    pwr.value = True
    sleep(.125)

rdy = DigitalInOut(board.RTL_READY)

rtl_init()
log_uart = busio.UART(board.RTL_TXD, board.RTL_RXD, baudrate=614400)
uart = busio.UART(board.RTL_MOSI, board.RTL_MISO, baudrate=614400)
xport = erpc.transport.SerialTransport(uart)
manager = erpc.client.ClientManager(xport, erpc.basic_codec.BasicCodec)

try:
    test_byte = 0xF
    system_client = rpc_system.client.rpc_systemClient(manager)
    ver = system_client.rpc_system_version()
    ack = system_client.rpc_system_ack(test_byte)
    print(f"OH MY GAWD: version: {ver}, ack({test_byte}): {ack}")
except TypeError:
    print("Well damn")
    pass
    
# OH MY GAWD: version: 2.1.3, ack(15): 15
```

That `OH MY GAWD: 2.1.3` result confirms that I was able to enable the RTL from CircuitPython, then send it an eRPC message requesting the system version, and get back a clean response. Oh man, that feels good. And the ack means I can make a simple call to echo back a byte.

## The next challange: working within a limited memory footprint

I was able to use erpcgen to generate python code for the WiFi and BLE client apis that sit on top of ERPC. This is great, in theory, becuase it means that I should be able to use those APIs to talk to the server running on the RTL. The reality is less than awesome, though.

The auto-generated Python implemention is not exaclty svelte. It's a pretty chatty API, with a whole lot of methods that can be implemented. And the SAMD51 in the WIO Terminal is roomy, but not that roomy, especially when CircuitPython is already eating up some of the memory headroom. To resolve this, I am going to have to take a hard look at slimming down the API into something that will fit _and_ still leave enough space to do anything useful. Also, there's another, high level pair of APIs for WiFi and BLE support implemented on top of that in the Arduino version of this code. That's clearly going to need some slimming down.

## See Also

I've got a gist that covers other [usage of the WIO Terminal with CircuitPython](https://gist.github.com/stonehippo/03677c206bf68846328f151ee8322193). It's still a WIP.
