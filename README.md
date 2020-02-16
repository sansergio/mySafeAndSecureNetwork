# mySafeAndSecureNetwork

This repo contains the basic software required to implement a safe and security network layer on the Kinetis K64 microcontroller. The new layer includes AES128 encryption and CRC32 integrity checks.

The repo conponents are:

## McuXpresso base project
The project is based on the lwIp's tcp echo example project but includes the [tiny AES](https://github.com/kokke/tiny-AES-c) library by kokke; and also the NXP's CRC driver. 
The project also includes a task named *aescrc_test_task()* which can be used as an example of how to use AES128 (CRB mode) and CRC32 on the K64.

## Test Python Scripts
The scripts in the pythonScripts folder can be used to test the safe and security network layer. 

* myssn_server.py - Implenents a server side host which echoes all secured messages it receives. All messages are decrypted and crc checked before sendint them back.
* myssn_client.py - Implements a client side host with a small console-like app that allows sending messages to the server.
* myssn.py - Implements the safe and secure network layer in Python 3. It is used by myssn_server.py and myssn_client.h. It can be used as an example of how to implement the network layer in C for the k64.

## Instructions

1. Install Python 3
2. Clone this repo. If you haven't used GIT before then you can learn from the [GitHub's tutorials](https://github.com/NREL/SAM/wiki/Basic-git-tutorial). 
3. Test the python scripts comunicating the Client with the Server.
4. Run the McuXpresso example and learn how AES128 and CRC32 works in C.
5. Implement your own network layer in C. Use the one in myssn.py as example.
