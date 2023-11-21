
Since the migration of MicroPython to ESPIDFV5.0.x, I have had stability and throughput issues with WiFi and TCP/IP sockets.

Two test scripts and two ESP32 firmwares are provided here for those interested in testing their home private network.

The script:
1. http_rw_cln.py - The client test script executed on a Linux PC using Unix MicroPython port 
2. http_rw_srv.py - The server test script run on ESP32

The firmwares:
1. GENERIC_STD - Generic ESP32 with debug logging enabled
2. GENERIC_EXPR - Generic ESP32 with debugging and some LWIP flags changed from default values

You will need to build your own MicroPython for Unix as the programme requires dynamic libraries to work. My LinuxMint PC may have different libraries to your Linux PC.

However, you can run a test setup on two ESP32 boards, you just need to make some modifications to 'http_rw_cln.py' to include the WiFi part in the script.

For the EXPR variant, the GENERIC_EXPR contains this 'sdkconfig.expr'
```
# enable debug
CONFIG_LOG_DEFAULT_LEVEL_DEBUG=y

# LWIP setting
CONFIG_LWIP_TCPIP_TASK_PRIO=23
CONFIG_LWIP_SO_LINGER=y

CONFIG_LWIP_PPP_ENABLE_IPV6=n

CONFIG_LWIP_TCP_TMR_INTERVAL=100
CONFIG_LWIP_TCPIP_TASK_AFFINITY_CPU0=y

CONFIG_LWIP_TCP_MSL=6000
CONFIG_LWIP_TCP_FIN_WAIT_TIMEOUT=2000

```

These settings are experimental. These values are different from the default values found in "components/lwip/Kconfig". You can change, include or exclude them for your own firmware build.

These firmwares were built with esp-idf-5.0.4, which contains some fixes from esp-idf-5.0.2.

I am having good results with the GENERIC_EXPR firmware, testing within my private home network. My home network is quite busy with 4K YouTube steaming and online TV going on all the time.

These are the results of the 2023.11.20 tests:

```
STD server
>>> 
MPY: soft reboot
MicroPython v1.22.0-preview.67.g64c79a542 on 2023-10-30; Generic ESP32 module with ESP32
Type "help()" for more information.
...
>>> import http_rw_srv
('192.168.4.91', '255.255.252.0', '192.168.4.1', '192.168.4.1')
Service: ('192.168.4.27', 45410)
...

Client 

Connected after 5ms min:2ms max:304ms avg:5.071ms timeouts:708
PKT# 5000 Bytes read: 10438 w-err: 0 r-err: 155
EXEC:[(15072, 4, 0, 4), (113840, 38540, 8704, 4648), (1176, 844, 832, 828)]
DATA:[(240, 4, 0, 4), (7288, 4, 0, 4), (16648, 4, 0, 4), (87384, 4, 0, 4), (15072, 4, 0, 4), (113840, 38540, 8704, 4648)]
 HelloWorld@2606537269000 HelloWorld@26065
d@2606537269000 HelloWorld@2606537269000 HelloWorld@2606537269000 HelloWorld@260
 144ms min:38 max:2017 avg:154.199, Rate:67698.993Bytes/s Total:52195450/770.993

real	42m10,562s
user	0m5,604s
sys	0m4,629s

----------------------------------------------------------------------------

EXPR Server
>>> 
MPY: soft reboot
MicroPython v1.22.0-preview.164.gfce8d9fd5.dirty on 2023-11-20; Generic ESP32 module with ESP32-EXPR
Type "help()" for more information.
>>> import http_rw_srv
('192.168.4.92', '255.255.252.0', '192.168.4.1', '192.168.4.1')
...
Service: ('192.168.4.27', 35816)

Client

Connected after 9ms min:5ms max:61ms avg:12.007ms timeouts:5
PKT# 5000 Bytes read: 10442 w-err: 0 r-err: 0
EXEC:[(15072, 4, 0, 4), (113840, 74944, 69632, 50084), (1176, 844, 832, 828)]
DATA:[(240, 4, 0, 4), (7288, 4, 0, 4), (16648, 4, 0, 4), (87416, 4, 0, 4), (15072, 4, 0, 4), (113840, 74944, 69632, 50084)]
 HelloWorld@977193263000 HelloWorld@97
rld@977193263000 HelloWorld@977193263000 HelloWorld@977193263000 HelloWorld@9771
 184ms min:83 max:360 avg:167.593, Rate:62305.980Bytes/s Total:52210106/837.963

real	14m9,872s
user	0m5,537s
sys	0m4,357s

```

Debug log messages were omitted from the above report. You can see how the wifi and lwip behave by looking at the debug log.

I hope this will be of some help in making your network connection more stable if you are using MicroPython v1.22.x and the upcoming v2.0.

However, I am confident that the MicroPython Core Developer Team will resolve this issue soon so that we no longer have to worry about it.


