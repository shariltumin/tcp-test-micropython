
import esp32
import socket as soc
import gc, select, time, network
network.WLAN(network.AP_IF).active(False)
wlan = network.WLAN(network.STA_IF)
wlan.active(True)
wlan.config(pm=0) # disable power management
wlan.config(txpower=20)
wlan.connect("YOUR_SSID", "YOUR_PWD")
time.sleep(5)
print(wlan.ifconfig())

pkn = 1
# msg = bytearray(46000)
msg = bytearray(12000)
# S = 40 # KBytes # message size
S = 10 # KBytes

def get_request(cs):
   global msg, S
   bl = 256
   ql = 1024
   q = b''
   ok = True
   cs.setblocking(False)
   ready = select.poll()
   ready.register(cs)
   while(True):
      req = ready.poll(100) # milliseconds
      # [(<_socket 4>, 5)]
      if req: # req[0][1] = 4 or 5, req[0][0] is socket number
             # In case of timeout, an empty list is returned.
         try:
            w = cs.read(bl) # read at most 256 cha
         except Exception as e:
            print('Read Error:', e)
            print('Sleep for 3 sec')
            time.sleep(3)
            ok = False
            break
         if w:
            q += w
            if len(q) >= ql: # abort service request too large!
               cs.write(b'Ok\r\n')
               print('Bad client')
               ok = False
               break
         else: # no more data to read
            break
   ready.unregister(cs)
   print('req:', q) 
   if ok:
      send_reply(cs)
   else:
      cs.close()
      del cs

def send_reply(cs):
   global pkn, S
   cs.setblocking(True)

   hx = str(esp32.idf_heap_info(1))
   hd = str(esp32.idf_heap_info(4))
   sbn = len(hx)+len(hd)+12
   try:
      cs.write(b'EXEC:' + hx.encode() + b'\n')
      cs.write(b'DATA:' + hd.encode() + b'\n')
      cs.write(msg[0:S*1024]); sbn += S*1024
      # send a block at a time (we can use worker to run other task in between)
#      inx = 0
#      blksz = 1024 # 512, 1024
#      while inx < S*1024:
#        cs.send(msg[inx:inx+blksz])
#        sbn += blksz
#        inx += blksz
      pkn += 1
      print('Number of bytes sent:', sbn)
   except Exception as e:
      print('Send Error:', e)
   cs.close()
   del cs
   return

def server(cln):
   global msg, S
   port = 8080
   ready = select.poll()

   addr = soc.getaddrinfo('0.0.0.0', port)[0][-1]
   s = soc.socket(soc.AF_INET, soc.SOCK_STREAM)
   s.setsockopt(soc.SOL_SOCKET, soc.SO_BINDTODEVICE, 'st1')
   s.setsockopt(soc.SOL_SOCKET, soc.SO_REUSEADDR, 1)
   s.bind(addr)
   s.listen(cln)
   s.setblocking(False) # this set socket to non_blocking

   while(True):
      # prepare next msg here
      inx = 0
      hh = f' HelloWorld@{time.time_ns()}'.encode()
      while inx < S*1024:
         msg[inx:inx+len(hh)] = hh
         inx += len(hh)

      # check new connection
      ready.register(s)
      ok = ready.poll(10) # milliseconds timeout
      if ok:
         # print(ok)
         try:
            cs, ca = s.accept()   # get client connection socket and address
         except Exception as e:
            print('Accept Error:', e)
            print('Sleep 3 sec')
            time.sleep(3)
         else:
            print('Service:', ca)
            get_request(cs)
            gc.collect()
      ready.unregister(s)

#server(5) # up to 5 clients backlog
server(1) # one client only - since runing synchronously


