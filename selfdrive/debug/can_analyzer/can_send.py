#!/usr/bin/env python3
import argparse
import binascii

panda = None
def can_send_panda(bus: int,addr: int,msg: bytes):
  global panda
  if panda == None:
    from panda import Panda
    panda = Panda()
  panda.can_send(addr, msg, bus)

def can_send_cereal(bus: int,addr: int,msg: bytes):
  from selfdrive.boardd.boardd import can_list_to_can_capnp
  from selfdrive.car import make_can_msg
  import cereal.messaging as messaging

  sendcan = messaging.pub_sock('sendcan')

  to_send = []
  to_send.append(make_can_msg(addr, msg, bus))
  sendcan.send(can_list_to_can_capnp(to_send, msgtype='sendcan'))  

def can_send_dummy(bus: int,addr: int,msg: bytes):
  print(f"send to can with bus({bus}) addr({addr}) msg({msg})")

def send_method(bus: int, addr_id: int, msg, method:str = None):
  b_msg =  binascii.unhexlify(msg)
  can_send_dummy(bus,addr_id,b_msg)
  if method == "cereal":
    can_send_cereal(bus,addr_id, b_msg)
  elif method == "panda":
    can_send_panda(bus,addr_id, b_msg)

if __name__ == "__main__":
  parser = argparse.ArgumentParser(description="simple CAN sender",
                                   formatter_class=argparse.ArgumentDefaultsHelpFormatter)

  parser.add_argument("--send", type=str, help="send one line command (bus, addr, msg)")
  parser.add_argument("--file", type=str, help="send from dump file")
  parser.add_argument("--cereal", action="store_true", help="Send via cereal")
  parser.add_argument("--panda", action="store_true", help="Send via panda")

  args = parser.parse_args()

  method = None
  if args.cereal == True:
    method = "cereal"
  elif args.panda == True:
    method = "panda"

  if args.file != None:
    with open(args.file) as f:
      while 1:          
        line = f.readline()
        if not line:
          break
        fields = line.strip().split(' ')
        send_method(int(fields[1]), int(fields[2]), fields[3], method)
  elif args.send != None:
    fields = args.send.strip().split(' ')
    send_method(int(fields[0]), int(fields[1]), fields[2], method)
