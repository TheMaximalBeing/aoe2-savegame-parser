import struct

def to_int(bytes):

  return int.from_bytes(bytes[::-1], byteorder='big', signed=True)

def to_float(bytess):

  return struct.unpack('!f', bytess[::-1])[0]
