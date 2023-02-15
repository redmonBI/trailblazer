#!/usr/bin/env python3
import pandas as pd

def can_table(dat):
  rows = []
  for b in dat:
    r = list(bin(b).lstrip('0b').zfill(8))
    r += [hex(b)]
    rows.append(r)

  df = pd.DataFrame(data=rows)
  df.columns = [str(n) for n in range(7, -1, -1)] + [' ']
  table = df.to_markdown(tablefmt='grid')
  return table