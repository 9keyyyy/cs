"""
실습 5: TCP 혼잡 제어 시뮬레이션

Slow Start, Congestion Avoidance, Fast Recovery를 구현하고
cwnd 변화를 관찰합니다.

"""


class TCPCongestionControl:
    """TCP Reno 혼잡 제어 시뮬레이터"""

    def __init__(self, mss=1):
        """
        mss: Maximum Segment Size (단위: 세그먼트)
        cwnd: Congestion Window (초기값: 1 MSS)
        ssthresh: Slow Start Threshold (초기값: 크게 설정)
        """
        self.mss = mss
        self.cwnd = 1.0        # 혼잡 윈도우
        self.ssthresh = 64.0   # slow start 임계값
        self.state = "slow_start"
        self.dup_ack_count = 0

        # cwnd 변화 기록 (시각화용)
        self.history = []

    def on_ack_received(self):
        """
        정상 ACK를 수신했을 때의 동작

        Slow Start 단계:
          - cwnd를 1 MSS만큼 증가 (지수적 증가 효과)
          - cwnd가 ssthresh에 도달하면 Congestion Avoidance로 전환

        Congestion Avoidance 단계:
          - cwnd를 1/cwnd MSS만큼 증가 (선형 증가, AIMD의 AI)

        """
        self.dup_ack_count = 0

        if self.state == "slow_start":
            self.cwnd += self.mss

            if self.cwnd >= self.ssthresh:
                self.state = "congestion_avoidance"
                print(f"  → Congestion Avoidance로 전환 (cwnd={self.cwnd:.1f})")

        elif self.state == "congestion_avoidance":
            self.cwnd += 1/self.cwnd

        elif self.state == "fast_recovery":
            # Fast Recovery 중 ACK → Congestion Avoidance로
            self.state = "congestion_avoidance"
            self.cwnd = self.ssthresh
            print(f"  → Fast Recovery 종료, Congestion Avoidance로 (cwnd={self.cwnd:.1f})")

        self.history.append(("ack", self.cwnd, self.state))

    def on_duplicate_ack(self):
        """
        중복 ACK를 수신했을 때의 동작 (TCP Reno)

        3 Duplicate ACK 감지 시:
          1. ssthresh = cwnd / 2
          2. cwnd = ssthresh + 3 (Fast Recovery)
          3. Fast Recovery 상태로 전환

        """
        self.dup_ack_count += 1

        if self.dup_ack_count == 3:
            print(f"  *** 3 Duplicate ACK 감지! (cwnd={self.cwnd:.1f})")

            self.ssthresh = self.cwnd / 2

            self.cwnd = self.ssthresh + 3

            self.state = "fast_recovery"
            print(f"  → Fast Recovery (ssthresh={self.ssthresh:.1f}, cwnd={self.cwnd:.1f})")

        elif self.dup_ack_count > 3 and self.state == "fast_recovery":
            # Fast Recovery 중 추가 dup ACK → cwnd + 1
            self.cwnd += self.mss

        self.history.append(("dup_ack", self.cwnd, self.state))

    def on_timeout(self):
        """
        타임아웃 발생 시의 동작 (TCP Reno / Tahoe 공통)

        1. ssthresh = cwnd / 2
        2. cwnd = 1 MSS
        3. Slow Start로 복귀

        """
        print(f"  *** TIMEOUT! (cwnd={self.cwnd:.1f})")

        self.ssthresh = self.cwnd / 2

        self.cwnd = self.mss

        self.state = "slow_start"
        self.dup_ack_count = 0

        print(f"  → Slow Start 복귀 (ssthresh={self.ssthresh:.1f}, cwnd={self.cwnd:.1f})")
        self.history.append(("timeout", self.cwnd, self.state))


def simulate():
    """시뮬레이션 시나리오 실행"""
    tcp = TCPCongestionControl()

    print("=" * 60)
    print("TCP Reno 혼잡 제어 시뮬레이션")
    print("=" * 60)

    # Phase 1: Slow Start (RTT 1~6)
    print("\n[Phase 1] Slow Start")
    for rtt in range(1, 7):
        acks_this_rtt = int(tcp.cwnd)
        for _ in range(acks_this_rtt):
            tcp.on_ack_received()
        print(f"  RTT {rtt}: cwnd = {tcp.cwnd:.1f} (state: {tcp.state})")

    # Phase 2: Congestion Avoidance (RTT 7~15)
    print("\n[Phase 2] Congestion Avoidance")
    for rtt in range(7, 16):
        acks_this_rtt = int(tcp.cwnd)
        for _ in range(acks_this_rtt):
            tcp.on_ack_received()
        print(f"  RTT {rtt}: cwnd = {tcp.cwnd:.1f} (state: {tcp.state})")

    # Phase 3: 3 Duplicate ACK 발생!
    print("\n[Phase 3] 3 Duplicate ACK 감지")
    for _ in range(3):
        tcp.on_duplicate_ack()
    print(f"  cwnd = {tcp.cwnd:.1f}, ssthresh = {tcp.ssthresh:.1f}")

    # Phase 4: Fast Recovery → Congestion Avoidance
    print("\n[Phase 4] Fast Recovery → Congestion Avoidance")
    tcp.on_ack_received()
    for rtt in range(16, 22):
        acks_this_rtt = int(tcp.cwnd)
        for _ in range(acks_this_rtt):
            tcp.on_ack_received()
        print(f"  RTT {rtt}: cwnd = {tcp.cwnd:.1f} (state: {tcp.state})")

    # Phase 5: Timeout!
    print("\n[Phase 5] Timeout!")
    tcp.on_timeout()

    # Phase 6: 다시 Slow Start
    print("\n[Phase 6] Slow Start 재시작")
    for rtt in range(22, 28):
        acks_this_rtt = int(tcp.cwnd)
        for _ in range(acks_this_rtt):
            tcp.on_ack_received()
        print(f"  RTT {rtt}: cwnd = {tcp.cwnd:.1f} (state: {tcp.state})")

    # 결과 텍스트 그래프
    print("\n" + "=" * 60)
    print("cwnd 변화 그래프 (텍스트)")
    print("=" * 60)
    max_cwnd = max(c for _, c, _ in tcp.history)
    width = 60
    for i, (event, cwnd, state) in enumerate(tcp.history):
        bar_len = int(cwnd / max_cwnd * width)
        marker = "*" if event == "timeout" else ("!" if event == "dup_ack" else "#")
        print(f"{i:3d} |{marker * bar_len:<{width}}| {cwnd:.1f}")


if __name__ == "__main__":
    simulate()
