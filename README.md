# SVD tool in gdb

## Introduction

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

## using in gdb

An example gdb file is written, including commands to load this python module and associated
SVD file.
This example gdb configuration also handle rdp manipulation (setting RDP1/RDP2, etc.). See this
file for more information.

WARNING: this file is working on STM32F4 Flash device (using the correct magic values and sequence).
If you have a different device, verify how the RDP lock mechanism works in the datasheet first and
create a new gdb config file for this device.

## Licensing

As the initial svd-dump.py file has been pasted by Devan Lai without any licensing, a BSD3 license has been
added, including him as initial author.
