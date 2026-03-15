"""
실습 5 정답 모음
"""

# on_ack_received:
#   self.cwnd += self.mss      # Slow Start
#   if self.cwnd >= self.ssthresh:
#       self.state = "congestion_avoidance"
#   self.cwnd += self.mss / self.cwnd  # Congestion Avoidance (선형 증가)

# on_duplicate_ack:
#   self.ssthresh = self.cwnd / 2
#   self.cwnd = self.ssthresh + 3

# on_timeout:
#   self.ssthresh = self.cwnd / 2
#   self.cwnd = self.mss  # 또는 1.0
