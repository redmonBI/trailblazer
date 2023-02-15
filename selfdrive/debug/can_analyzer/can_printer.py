#!/usr/bin/env python3
import argparse
import binascii
from collections import defaultdict
from dataclasses import dataclass

def can_printer(fn:str, delay:bool, bus, max_msg, addr, ascii_decode):
  start = 0
  lp = 0
  msgs = defaultdict(list)
  with open(fn) as f:
    while 1:
      before_ts = 0
      line = f.readline()
      if not line:
        break
      fields = line.strip().split(' ')
      can_recv = CanMessage(float(fields[0]), int(fields[1]), int(fields[2]), binascii.unhexlify(fields[3]))

      if can_recv.bus == bus:
        msgs[can_recv.address].append(can_recv.dat)

      if can_recv.time - lp > 0.1:
        dd = chr(27) + "[2J"
        dd += f"{can_recv.time - start:5.2f}\n"
        for addr in sorted(msgs.keys()):
          a = f"\"{msgs[addr][-1].decode('ascii', 'backslashreplace')}\"" if ascii_decode else ""
          x = binascii.hexlify(msgs[addr][-1]).decode('ascii')
          freq = len(msgs[addr]) / (can_recv.time - start)
          if max_msg is None or addr < max_msg:
            dd += "%04X(%4d)(%6d)(%3dHz) %s %s\n" % (addr, addr, len(msgs[addr]), freq, x.ljust(20), a)
        print(dd)
        lp = can_recv.time

@dataclass
class CanMessage:
    time: float
    bus: int
    address: int
    dat: bytearray

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="simple CAN data viewer",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument("--delay", help="Apply replay delay", action='store_true')
  parser.add_argument("--file", type=str, help="CAN dump file to test")
  parser.add_argument("--bus", type=int, help="CAN bus to print out", default=0)
  parser.add_argument("--max_msg", type=int, help="max addr")
  parser.add_argument("--ascii", action='store_true', help="decode as ascii")
  parser.add_argument("--addr", default="127.0.0.1")

  args = parser.parse_args()
  can_printer(args.file,args.delay, args.bus, args.max_msg, args.addr, args.ascii)
