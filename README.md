# SVD tool in gdb

## Introduction

This tool handle SVD device canonical manipulation in gdb, simplyfying debugging of drivers.

SVD files are not hosted here, as they are hosted in the cmsis-svd python module

## Install dependencies

```
pip install -U cmsis-svd
```

or inside a virtualenv:
```
python -m venv venv
venv/bin/pip install -r requirements.txt
```

**NOTE**: in order to use the virtualenv append the following snippet to your `.gdbinit`
to update the GDB's Python paths [[ref](https://interrupt.memfault.com/blog/using-pypi-packages-with-gdb#setting-syspath-within-gdbinit)]:
```python
python
import os,subprocess,sys
paths = subprocess.check_output('python -c "import os,sys;print(os.linesep.join(sys.path).strip())"',shell=True).decode("utf-8").split()
sys.path.extend(paths)
end
```

then activate the virtualenv before launching gdb:
```
source /path/to/gdb-svd-tools/venv/bin/activate
```

## Usage

Source the python script and load the target SVD file:
```
(gdb) source /path/to/svd-dump.py
(gdb) svd_load STMicro STM32F103xx.svd
```

Run `svd_show` or `svd_set` to read or write registers:
```
(gdb) svd_show 
+svd_show 
Usage: svd_show[/[x|b]fi] peripheral-name [register-name]
(gdb) svd_set
+svd_set
Usage: svd_set peripheral-name register-name fieldname value
```

### Examples

Show an entire peripheral:
```
(gdb) svd_show USART2
USART2 @ 0x40004400
SR   CTS=0 LBD=0 TXE=1 TC=1 RXNE=0 IDLE=0 ORE=0 NE=0 FE=0 PE=0
DR   DR=0
BRR  DIV_Mantissa=19 DIV_Fraction=8
CR1  UE=1 M=0 WAKE=0 PCE=0 PS=0 PEIE=0 TXEIE=0 TCIE=0 RXNEIE=0 IDLEIE=0 TE=1 RE=1 RWU=0 SBK=0
CR2  LINEN=0 STOP=0 CLKEN=0 CPOL=0 CPHA=0 LBCL=0 LBDIE=0 LBDL=0 ADD=0
CR3  CTSIE=0 CTSE=0 RTSE=0 DMAT=0 DMAR=0 SCEN=0 NACK=0 HDSEL=0 IRLP=0 IREN=0 EIE=0
GTPR GT=0 PSC=0
```

Show just one register:
```
(gdb) svd_show USART2 BRR
BRR DIV_Mantissa=19 DIV_Fraction=8
```

Show field values in hex:
```
(gdb) svd_show/x USART2 BRR
BRR DIV_Mantissa=013 DIV_Fraction=8
```

Show field values in binary:
```
(gdb) svd_show/b USART2 BRR
BRR DIV_Mantissa=000000010011 DIV_Fraction=1000
```

Show whole register value in binary:
```
(gdb) svd_show/i USART2 BRR
BRR 00000000000000000000000100111000 DIV_Mantissa=19 DIV_Fraction=8
```

Show register offsets:
```
(gdb) svd_show/f USART2
USART2 @ 0x40004400
SR   0x0000 CTS=0 LBD=0 TXE=1 TC=1 RXNE=0 IDLE=0 ORE=0 NE=0 FE=0 PE=0
DR   0x0004 DR=0
BRR  0x0008 DIV_Mantissa=19 DIV_Fraction=8
CR1  0x000c UE=1 M=0 WAKE=0 PCE=0 PS=0 PEIE=0 TXEIE=0 TCIE=0 RXNEIE=0 IDLEIE=0 TE=1 RE=1 RWU=0 SBK=0
CR2  0x0010 LINEN=0 STOP=0 CLKEN=0 CPOL=0 CPHA=0 LBCL=0 LBDIE=0 LBDL=0 ADD=0
CR3  0x0014 CTSIE=0 CTSE=0 RTSE=0 DMAT=0 DMAR=0 SCEN=0 NACK=0 HDSEL=0 IRLP=0 IREN=0 EIE=0
GTPR 0x0018 GT=0 PSC=0
```

Loading from an external SVD file:
```
(gdb) svd_load_file /path/to/your_file.svd
```

See also the [gdb example file](gdb-stm32.cf) including commands to load this python module and associated
SVD file.
This example gdb configuration also handle rdp manipulation (setting RDP1/RDP2, etc.). See this
file for more information.

WARNING: this file is working on STM32F4 Flash device (using the correct magic values and sequence).
If you have a different device, verify how the RDP lock mechanism works in the datasheet first and
create a new gdb config file for this device.

## Licensing

As the initial svd-dump.py file has been pasted by Devan Lai without any licensing, a BSD3 license has been
added, including him as initial author.
