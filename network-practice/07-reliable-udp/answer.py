"""
실습 7 정답 모음
"""

# reliable_send:
#   sock.sendto(packet, addr)
#   sock.settimeout(TIMEOUT)
#   ack_packet, _ = sock.recvfrom(1024)
#   if ack_type == PACKET_ACK and ack_seq == seq_num:
#   seq_num += 1

# reliable_receive:
#   if seq_num == expected_seq:
#   ack = make_packet(seq_num, PACKET_ACK)
#   expected_seq += 1
