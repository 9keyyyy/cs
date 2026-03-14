"""
실습 4 정답 모음
"""

# parse_ethernet:
#   dst_mac, src_mac, ethertype = struct.unpack("!6s6sH", data[:14])

# parse_ip:
#   ttl = data[8]
#   protocol = data[9]

# parse_tcp:
#   src_port, dst_port = struct.unpack("!HH", data[:4])
#   seq_num, ack_num = struct.unpack("!II", data[4:12])
#   if flags & 0x10:  # ACK
#   if flags & 0x01:  # FIN
