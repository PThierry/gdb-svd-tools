"""
Utilities for dumping STM32 peripheral registers with tab-completion
Based on a script by vampi-the-frog

Dependencies:
    pip install -U cmsis-svd

Usage (inside gdb):

    (gdb) source /path/to/svd-dump.py
    (gdb) svd_load STMicro STM32F103xx.svd
    (gdb) svd_show USB
    USB @ 0x40005c00
    EP0R   0x0000 0000000000000000 EA=0 STAT_TX=0 DTOG_TX=0 CTR_TX=0 EP_KIND=0 EP_TYPE=0 SETUP=0 STAT_RX=0 DTOG_RX=0 CTR_RX=0
    EP1R   0x0004 0000000000000000 EA=0 STAT_TX=0 DTOG_TX=0 CTR_TX=0 EP_KIND=0 EP_TYPE=0 SETUP=0 STAT_RX=0 DTOG_RX=0 CTR_RX=0
    EP2R   0x0008 0000000000000000 EA=0 STAT_TX=0 DTOG_TX=0 CTR_TX=0 EP_KIND=0 EP_TYPE=0 SETUP=0 STAT_RX=0 DTOG_RX=0 CTR_RX=0
    EP3R   0x000c 0000000000000000 EA=0 STAT_TX=0 DTOG_TX=0 CTR_TX=0 EP_KIND=0 EP_TYPE=0 SETUP=0 STAT_RX=0 DTOG_RX=0 CTR_RX=0
    EP4R   0x0010 0000000000000000 EA=0 STAT_TX=0 DTOG_TX=0 CTR_TX=0 EP_KIND=0 EP_TYPE=0 SETUP=0 STAT_RX=0 DTOG_RX=0 CTR_RX=0
    EP5R   0x0014 0000000000000000 EA=0 STAT_TX=0 DTOG_TX=0 CTR_TX=0 EP_KIND=0 EP_TYPE=0 SETUP=0 STAT_RX=0 DTOG_RX=0 CTR_RX=0
    EP6R   0x0018 0000000000000000 EA=0 STAT_TX=0 DTOG_TX=0 CTR_TX=0 EP_KIND=0 EP_TYPE=0 SETUP=0 STAT_RX=0 DTOG_RX=0 CTR_RX=0
    EP7R   0x001c 0000000000000000 EA=0 STAT_TX=0 DTOG_TX=0 CTR_TX=0 EP_KIND=0 EP_TYPE=0 SETUP=0 STAT_RX=0 DTOG_RX=0 CTR_RX=0
    CNTR   0x0040 0000000000000011 FRES=1 PDWN=1 LPMODE=0 FSUSP=0 RESUME=0 ESOFM=0 SOFM=0 RESETM=0 SUSPM=0 WKUPM=0 ERRM=0 PMAOVRM=0 CTRM=0
    ISTR   0x0044 0000000000000000 EP_ID=0 DIR=0 ESOF=0 SOF=0 RESET=0 SUSP=0 WKUP=0 ERR=0 PMAOVR=0 CTR=0
    FNR    0x0048 0000000000000000 FN=0 LSOF=0 LCK=0 RXDM=0 RXDP=0
    DADDR  0x004c 0000000000000000 ADD=0 EF=0
    BTABLE 0x0050 0000000000000000 BTABLE=0
    (gdb) svd_show USB ISTR
    ISTR 0x0044 0000000000000000 EP_ID=0 DIR=0 ESOF=0 SOF=0 RESET=0 SUSP=0 WKUP=0 ERR=0 PMAOVR=0 CTR=0

Customization:
To turn on colorizing non-zero values, set colorize = True
(doesn't work in TUI mode)
"""

import gdb
import struct
from cmsis_svd.parser import SVDParser
import pkg_resources

class SVDSelector(gdb.Command):
    def __init__(self):
        super(SVDSelector, self).__init__("svd_load", gdb.COMMAND_USER)
        vendor_names = pkg_resources.resource_listdir("cmsis_svd", "data")
        self.vendors = {}
        for vendor in vendor_names:
            fnames = pkg_resources.resource_listdir("cmsis_svd", "data/%s" % vendor)
            self.vendors[vendor] = [fname for fname in fnames if fname.lower().endswith(".svd")]

    def complete(self, text, word):
        args = gdb.string_to_argv(text)
        num_args = len(args)
        if text.endswith(" "):
            num_args += 1
        if not text:
            num_args = 1

        # "svd_load <tab>" or "svd_load ST<tab>"
        if num_args == 1:
            prefix = word.lower()
            return [vendor for vendor in self.vendors if vendor.lower().startswith(prefix)]
        # "svd_load STMicro<tab>" or "svd_load STMicro STM32F1<tab>"
        elif num_args == 2 and args[0] in self.vendors:
            prefix = word.lower()
            filenames = self.vendors[args[0]]
            return [fname for fname in filenames if fname.lower().startswith(prefix)]
        return gdb.COMPLETE_NONE

    def invoke(self, arg, from_tty):
        args = gdb.string_to_argv(arg)
        if len(args) >= 1:
            if args[0] not in self.vendors:
                print("Invalid vendor name")
                return
            vendor_name = args[0]
            vendor_filenames = self.vendors[vendor_name]
            if len(args) == 1:
                print("Usage: svd_load <vendor-name> <filename.svd>")
            elif len(args) >= 2:
                filename = args[1]
                parser = SVDParser.for_packaged_svd(vendor_name, filename)
                _svd_printer.set_device(parser.get_device())
        else:
            print("Usage: svd_load <vendor-name> <filename.svd>")

class SVDPrinter(gdb.Command):
    colorize = False
    def __init__ (self, device=None):
        super (SVDPrinter, self).__init__ ("svd_show", gdb.COMMAND_USER)
        self.device = device
        if device:
            self.peripherals = dict((peripheral.name,peripheral) for peripheral in self.device.peripherals)
        else:
            self.periphrals = {}

    def set_device(self, device):
        self.device = device
        self.peripherals = dict((peripheral.name,peripheral) for peripheral in self.device.peripherals)
        
    def complete(self, text, word):
        if not self.device:
            return gdb.COMPLETE_NONE
        
        args = gdb.string_to_argv(text)
        num_args = len(args)
        if text.endswith(" "):
            num_args += 1
        if not text:
            num_args = 1

        if num_args == 1:
            peripheral_names = [peripheral.name.upper() for peripheral in self.device.peripherals]
            if word:
                prefix = word.upper()
                return [name for name in peripheral_names if name.startswith(prefix)]
            else:
                return peripheral_names
        elif num_args == 2 and args[0].upper() in self.peripherals:
            periph_name = args[0].upper()
            periph = self.peripherals[periph_name]
            register_names = [register.name for register in periph.registers]
            if word:
                prefix = word.upper()
                return [name for name in register_names if name.upper().startswith(prefix)]
            return register_names
        return gdb.COMPLETE_NONE

    def dump_register(self, peripheral, register, name_width=0):
        val = struct.unpack("<L", gdb.inferiors()[0].read_memory(peripheral.base_address + register.address_offset, 4))[0];
        print("%-*s 0x%04x %s" % (name_width, register.name, register.address_offset, '{0:016b}'.format(val))),
        for field in register.fields:
            fieldval = (val >> field.bit_offset) & ((1 << field.bit_width) - 1)
            if self.colorize and fieldval > 0:
                print("\033[32m%s=%02x(%d)\033[0m" % (field.name, fieldval, fieldval)),
            else:
                print("%s=%d" % (field.name, fieldval)),
        print
    def invoke (self, arg, from_tty):
        if not self.device:
            print("Use svd_load to load an SVD file first")
            return

        args = gdb.string_to_argv(arg)
        if len(args) >= 1:
            if args[0] not in self.peripherals:
                print("Invalid peripheral name")
                return
            peripheral = self.peripherals[args[0]]
            if len(args) == 1:
                print("%s @ 0x%08x" % (peripheral.name, peripheral.base_address))
                if peripheral.registers:
                    width = max(len(reg.name) for reg in peripheral.registers) 
                    for register in peripheral.registers:
                        self.dump_register(peripheral, register, width)
            elif len(args) == 2:
                for register in peripheral.registers:
                    if register.name == args[1]:
                        self.dump_register(peripheral, register)
                        break
                else:
                    print("Invalid register name")
        else:
            print("Usage: svd_show peripheral-name [register-name]")

SVDSelector()
_svd_printer = SVDPrinter()