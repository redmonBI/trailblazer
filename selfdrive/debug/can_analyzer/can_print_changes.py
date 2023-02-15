#!/usr/bin/env python3
import sys
import argparse
import binascii
import time
from collections import defaultdict
from dataclasses import dataclass

#from tools.lib.logreader import logreader_from_route_or_segment

RED = '\033[91m'
CLEAR = '\033[0m'

def update(msgs, bus, dat, low_to_high, high_to_low, quiet=False):
  for msg in msgs:
    if msg.bus == bus:
      dat[msg.address] = msg.dat

      i = int.from_bytes(msg.dat, byteorder='big')
      l_h = low_to_high[msg.address]
      h_l = high_to_low[msg.address]

      change = None
      if (i | l_h) != l_h:
        low_to_high[msg.address] = i | l_h
        change = "+"

      if (~i | h_l) != h_l:
        high_to_low[msg.address] = ~i | h_l
        change = "-"

      if change and not quiet:
        print(f"{msg.time:.2f}\t{hex(msg.address)} ({msg.address})\t{change}{binascii.hexlify(msg.dat)}")


def can_printer(bus=0, init_msgs=None, new_msgs=None, table=False):
  dat = defaultdict(int)
  low_to_high = defaultdict(int)
  high_to_low = defaultdict(int)

  if init_msgs is not None:
    update(init_msgs, bus, dat, low_to_high, high_to_low, quiet=True)

  low_to_high_init = low_to_high.copy()
  high_to_low_init = high_to_low.copy()

  if new_msgs is not None:
    update(new_msgs, bus, dat, low_to_high, high_to_low)
  else:
    # Live mode
    print(f"Waiting for messages on bus {bus}")
    try:
      for line in sys.stdin:
        fields = line.strip().split(' ')
        can_recv = CanMessage(float(fields[0]), int(fields[1]), int(fields[2]), binascii.unhexlify(fields[3]))
        update([can_recv], bus, dat, low_to_high, high_to_low)
    except KeyboardInterrupt:
      pass

  print("\n\n")
  tables = ""
  for addr in sorted(dat.keys()):
    init = low_to_high_init[addr] & high_to_low_init[addr]
    now = low_to_high[addr] & high_to_low[addr]
    d = now & ~init
    if d == 0:
      continue
    b = d.to_bytes(len(dat[addr]), byteorder='big')

    byts = ''.join([(c if c == '0' else f'{RED}{c}{CLEAR}') for c in str(binascii.hexlify(b))[2:-1]])
    header = f"{hex(addr).ljust(6)}({str(addr).ljust(4)})"
    print(header, byts)
    if table:
      tables += f"{header}\n"
      tables += can_table(b) + "\n\n"

  if table:
    print(tables)

def can_table(dat):
  import pandas as pd
  rows = []
  for b in dat:
    r = list(bin(b).lstrip('0b').zfill(8))
    r += [hex(b)]
    rows.append(r)

  df = pd.DataFrame(data=rows)
  df.columns = [str(n) for n in range(7, -1, -1)] + [' ']
  table = df.to_markdown(tablefmt='grid')
  return table

@dataclass
class CanMessage:
    time: float
    bus: int
    address: int
    dat: bytearray

def load_from_file(fn: str):
  can_msgs = []
  with open(fn) as f:
    while 1:          
      line = f.readline()
      if not line:
        break
      fields = line.strip().split(' ')      
      can_recv = CanMessage(float(fields[0]), int(fields[1]), int(fields[2]), binascii.unhexlify(fields[3]))
      can_msgs.append(can_recv)
  return can_msgs

if __name__ == "__main__":
  desc = """Collects messages and prints when a new bit transition is observed.
  This is very useful to find signals based on user triggered actions, such as blinkers and seatbelt.
  Leave the script running until no new transitions are seen, then perform the action."""
  parser = argparse.ArgumentParser(description=desc,
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)
  parser.add_argument("--bus", type=int, help="CAN bus to print out", default=0)
  parser.add_argument("--table", action="store_true", help="Print a cabana-like table")
  parser.add_argument("init", type=str, nargs='?', help="Route or segment to initialize with. Use empty quotes to compare against all zeros.")
  parser.add_argument("comp", type=str, nargs='?', help="Route or segment to compare against init")

  args = parser.parse_args()

  init_lr, new_lr = None, None

  if args.init:
    if args.init == '':
      init_lr = []
    else:
      init_lr = load_from_file(args.init)
  if args.comp:
    new_lr = load_from_file(args.comp)

  can_printer(args.bus, init_msgs=init_lr, new_msgs=new_lr, table=args.table)
