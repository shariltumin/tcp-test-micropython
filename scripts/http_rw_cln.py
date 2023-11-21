
import time, socket, gc
srv = '192.168.4.91' # ESP32 MicroPython standard
#srv = '192.168.4.92' # ESP32 MicroPython compile with DEBUG and CONFIG_LWIP_*
#srv = '192.168.4.82' # ESP32-S2
#srv = '192.168.4.90' # ESP32-S2
#srv = '192.168.4.86' # ESP32-S3
port = 8080
mn, mx, tt, avg, pkg, we, re = 10000, 0, 0, 0, 0, 0, 0
cn, cx, ct, cc, ca, cs = 10000, 0, 0, 0, 0, 0
pkn = 1
addr = socket.getaddrinfo(srv, port)[0][-1]
now = 0

def connect():
   global now, addr, cn, cx, ct, cc, ca, cs
   s = socket.socket()
   s.settimeout(1) # 1 sec timeout - as short as possible
   now = time.ticks_ms()
   cs += 1
   try:
      s.connect(addr)
   except Exception as e:
      print('========================')
      print('Connect exception:', e)
      print('========================')
      w_delta = time.ticks_diff(time.ticks_ms(), now)
      ct += 1
      print(f'Waited for {w_delta}ms timeouts:{ct}')
      s.close()
      time.sleep(1) # as short as possible
      del s
      return False
   else:
      c_delta = time.ticks_diff(time.ticks_ms(), now)
      if c_delta<cn: cn = c_delta
      if c_delta>cx: cx = c_delta
      cc += c_delta
      print('------------------------------------') 
      print(f'Connected after {c_delta}ms min:{cn}ms max:{cx}ms avg:{cc/cs:.3f}ms timeouts:{ct}')
      return request(s)

def request(s):
    global we
    try:
       s.write(b'GET / HTTP/1.1\r\nHost: 192.168.4.85\r\n\r\n')
    except Exception as e:
       print('------------------------')
       print('Send exception:', e)
       print('------------------------')
       we += 1
       s.close()
       time.sleep(1) # as short as possible
       del s
       return False
    else:
       return get_reply(s)

def get_reply(s):
    global now, re, mn, mx, tt, avg, pkg
    rep = b''
    blksz = 1024 # 512, 1024, 2048, 4096
    s.setblocking(True) # block until data
    while True:
       try:
          data = s.read(blksz) # blocking op
       except Exception as e: # read until server close connection
          print('READ error:', e)
          re += 1
          s.close()
          time.sleep(1) # as short as possible
          del s
          return False
       if data:
          rep += data
          print('Data:', len(data), len(rep))
       else: # no more data
          delta = time.ticks_diff(time.ticks_ms(), now)
          if delta<mn: mn = delta
          if delta>mx: mx = delta
          tt += (delta/1000) # second
          pkg += len(rep)
          avg = pkg/tt
          print('PKT#', pkn, 'Bytes read:', len(rep), 'w-err:', we, 'r-err:', re)
          print(rep[:240].decode())
          print(rep[-80:].decode())
          print(f' {delta}ms min:{mn} max:{mx} avg:{(tt/pkn)*1000:.3f}, Rate:{avg:.3f}Bytes/s Total:{pkg}/{tt:.3f}')
          s.close()
          del s
          return True

while True:
   ok = connect()
   if ok:
      pkn += 1
   gc.collect()
   if pkn>5000: break

