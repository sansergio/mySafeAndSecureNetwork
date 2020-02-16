#Implementation of a Safe and Secure layer over TCP IP
#It applies AES128 and CRC32
import socket     # The TCP/IP Sockets module 
import binascii   # For CRC32 
from Crypto.Cipher import AES # For AES128


###############################################################################
#                                   CONFIG
###############################################################################
SERVER_PORT    = 10000 # Port to accept client connections
SOCKET_TIMEOUT = 20 #seconds
# AES 128 Encryption Key and Initialization Vector
# See this Wikipedia's wiki on Block Cipher for details
# https://en.wikipedia.org/wiki/Block_cipher_mode_of_operation
# 
key = b'\x01\x02\x03\x04\x05\x06\x07\x08\x09\x00\x01\x02\x03\x04\x05\x06'
iv = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

verbose = True # True -> Enables debug messages

###############################################################################
#                              INTERNAL METHODS
###############################################################################
# AES128 Encryption function
def enc(message):
    # To encrypt an array its lenght must be a multiple of 16 so we add zeros
    ptxt = message + (b'\x00' * (16 - len(message) % 16))
    # Encrypt in EBC mode
    encryptor = AES.new(key, AES.MODE_CBC, IV=iv)
    ciphed_msg = encryptor.encrypt(ptxt)
    return ciphed_msg

# AES128 Decryption function
def dec(message):
    # Decrypt in EBC mode
    decryptor =  AES.new(key, AES.MODE_CBC, IV=iv)
    deciphed_msg = decryptor.decrypt(message)
    # Remove the Padding
    deciphed_msg = deciphed_msg.rstrip(b'\x00')
    return deciphed_msg

###############################################################################
#                                    API
###############################################################################
###############################################################################
# Creates a myssn server socket
# Returns the Socket handle
###############################################################################
def server_create(server_ip_address):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # set the socket timeout for accept operations
    sock.settimeout(SOCKET_TIMEOUT)
    # Bind the socket to the port
    server_address = (server_ip_address, SERVER_PORT)
    if verbose: print('myssn INFO: Create server on {} port {}'.format(*server_address))
    sock.bind(server_address)
    return sock

###############################################################################
# Accept a new connection on the myssn server socket
###############################################################################
def server_accept(sock):
    # Wait for a client's connection
    if verbose: print('myssn INFO: waiting {} seconds for client connections'.format(sock.gettimeout()))
    try:        
        # Listen for incoming connections
        sock.listen(1)
        # Accept a client connection, this is a blocking call it times out 
        # after SOCKET_TIMEOUT seconds
        connection, client_address = sock.accept()    
    except socket.timeout as e:
        if verbose: print('myssn INFO: No client connected')
        connection = None
    finally: 
        if connection is not None:
            if verbose: print('myssn INFO: connection from', client_address)
            # Once connected, disable the sockets timeout
            connection.settimeout(None)
    return connection

###############################################################################
# Connect to server
###############################################################################
def client_connect(server_addr):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Connect the socket to the port where the server is listening
    server_address = (server_addr, SERVER_PORT)
    if verbose: print('myssn INFO: connecting to {} port {}'.format(*server_address))    
    try:
        # Connect the socket
        sock.connect(server_address)
    except ConnectionRefusedError:
        if verbose: print('myssn INFO: The server is not available')
        # if the server is not available then close the socket
        sock.close()
        sock = None
    finally:
        return sock

###############################################################################
# Receive data from socket
###############################################################################
def recv(sock):
    try:
        # Receive up to 1024 bytes
        bytes_msg = sock.recv(1024)
        if bytes_msg:
            # Get the message body 
            msg_body_bytes = bytes_msg[:-4]
            # Get the 4 bytes of the CRC 32
            msg_crc_bytes = bytes_msg[-4:]
            # Calculate the CRC from the body
            crc = binascii.crc32(msg_body_bytes)
            # Convert the CRC bytes from the message to integer
            rx_crc = int.from_bytes(msg_crc_bytes, byteorder = 'little')
            # Compare the message's CRC vs. the one we just Calc.
            if crc != rx_crc:
                if verbose: print('myssn INFO: CRC error!  calc: {} vs.  recv: {}'.format(crc, rx_crc))
                data = None
            else:
                # If the CRC is fine then decrypt the message
                data = dec(msg_body_bytes)            
                if verbose: print('myssn DATA: {!r}'.format(data))
        else:
            # No data was received, this may be because of a closed coennection
            if verbose: print('myssn INFO: no data myssn connection')
            data = None
    except:
        if verbose: print('myssn INFO: recv error')
        data = None
    return data

###############################################################################
# Transmit data on socket
###############################################################################
def send(sock, data):
    if verbose: print('myssn INFO: sending data: {}'.format(data))
    # First encrypt the message
    bytes_msg = enc(data)
    if verbose: print('myssn INFO: encrypted message: {}'.format(bytes_msg))
    # Second, calculate the CRC over the encrypted message
    crc = binascii.crc32(bytes_msg)
    # crc is a python's integer, we have to convert it into a 4 bytes array to transmit it
    crc_bytes = crc.to_bytes(4, byteorder = 'little')
    if verbose: print('myssn INFO: tx crc32 = {}, crc bytes = {}'.format(crc, crc_bytes))
    # Concatenate the crc at the end of the encrypted message
    bytes_msg = bytes_msg + crc_bytes
    # Send the message over TCP
    sock.send(bytes_msg)

###############################################################################
# Close myssn data on socket
###############################################################################
def close(sock):
    if verbose: print('myssn INFO: Closing myssn socket')
    # Close the TCP socket
    sock.close()
