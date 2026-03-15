"""
실습 6 정답 모음
"""

# calc_subnet:
#   subnet_mask = (0xFFFFFFFF << (32 - prefix_len)) & 0xFFFFFFFF
#   network_addr = ip_int & subnet_mask
#   broadcast_addr = network_addr | (~subnet_mask & 0xFFFFFFFF)
#   host_count = 2 ** (32 - prefix_len) - 2

# is_same_subnet:
#   return (ip_to_int(ip1) & mask) == (ip_to_int(ip2) & mask)

# arp_request:
#   self.arp_tables[sender_ip][target_ip] = target_mac
#   self.arp_tables[target_ip][sender_ip] = sender_mac
