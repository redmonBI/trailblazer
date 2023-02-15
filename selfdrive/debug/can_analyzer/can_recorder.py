#!/usr/bin/env python3
import argparse
import binascii

import cereal.messaging as messaging
from common.realtime import sec_since_boot

def handle_message(ts, bus,addr,msg):
  msg_hs = binascii.hexlify(msg).decode('ascii')
  print(f"{ts:5.2f} {bus} {addr} {msg_hs}")

def can_recorder(addr):
  start = sec_since_boot()
  logcan = messaging.sub_sock('can', addr=addr)

  while 1:
    can_recv = messaging.drain_sock(logcan, wait_for_one=True)
    diff_ts = sec_since_boot() - start
    for x in can_recv:
      for y in x.can:
        handle_message(diff_ts, y.src,y.address,y.dat)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="simple CAN recorder",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument("--addr", default="127.0.0.1")

  args = parser.parse_args()
  can_recorder(args.addr)
