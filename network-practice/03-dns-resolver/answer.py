"""
실습 3 정답 모음
"""

# cache_lookup:
#   if elapsed < entry["ttl"]:
#   del dns_cache[domain]

# build_dns_query:
#   transaction_id = random.randint(0, 65535)
#   header = struct.pack("!HHHHHH", transaction_id, 0x0100, 1, 0, 0, 0)

# resolve:
#   sock.sendto(query, (dns_server, 53))
#   response, _ = sock.recvfrom(512)
