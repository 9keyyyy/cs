# 실습 5: TCP 혼잡 제어 시뮬레이션

## 면접 키워드
- Slow Start: cwnd를 지수적으로 증가
- Congestion Avoidance (AIMD): 선형 증가, 반감 감소
- ssthresh (Slow Start Threshold)
- 패킷 손실 감지: Timeout vs 3 Duplicate ACK
- TCP Tahoe vs TCP Reno

## 과제
네트워크 시뮬레이션 환경에서 TCP 혼잡 제어 알고리즘을 구현하고
cwnd(Congestion Window) 변화를 시각화합니다.

## 면접 예상 질문

### Q. TCP 혼잡 제어의 4가지 단계를 설명하세요.

TCP 혼잡 제어는 네트워크 혼잡을 방지하기 위해 **전송 속도(cwnd)를 동적으로 조절**하는 메커니즘으로, 4단계로 구성됩니다.

1. **Slow Start**: 연결 초기에 cwnd를 **1 MSS에서 시작하여 ACK를 받을 때마다 2배씩 지수적으로 증가**시킵니다. cwnd가 ssthresh에 도달하면 Congestion Avoidance로 전환됩니다.

2. **Congestion Avoidance**: cwnd가 ssthresh 이상일 때, **RTT마다 cwnd를 1 MSS씩 선형적으로 증가**시킵니다. 네트워크 용량에 천천히 접근하며 혼잡을 피합니다.

3. **Fast Retransmit**: **3개의 중복 ACK(Duplicate ACK)** 을 수신하면 Timeout을 기다리지 않고 즉시 해당 세그먼트를 재전송합니다.

4. **Fast Recovery** (Reno): Fast Retransmit 후 cwnd를 1로 떨어뜨리지 않고 **ssthresh(= cwnd/2)로 설정**하여 Congestion Avoidance 단계부터 다시 시작합니다.

### Q. Slow Start와 Congestion Avoidance의 차이는?

| 구분 | Slow Start | Congestion Avoidance |
|------|-----------|---------------------|
| 증가 방식 | **지수적 증가** (매 ACK마다 cwnd +1 MSS → RTT당 2배) | **선형 증가** (RTT당 cwnd +1 MSS) |
| 시작 조건 | 연결 초기 또는 Timeout 발생 후 | cwnd ≥ ssthresh일 때 |
| 목적 | 가용 대역폭을 빠르게 탐색 | 혼잡 지점에 천천히 접근 |
| 전환 시점 | cwnd가 ssthresh에 도달하면 CA로 전환 | 패킷 손실이 감지될 때까지 유지 |

Slow Start라는 이름이지만 실제로는 **지수적으로 빠르게 증가**합니다. "Slow"라는 이름은 이전 방식(연결 시작부터 최대 속도로 전송)에 비해 느리다는 의미입니다.

### Q. AIMD란 무엇인가요?

AIMD(Additive Increase / Multiplicative Decrease)는 TCP 혼잡 제어의 핵심 원리입니다.

- **Additive Increase (가산 증가)**: 혼잡이 없으면 RTT마다 cwnd를 **1 MSS씩 선형 증가**시킵니다.
- **Multiplicative Decrease (승산 감소)**: 혼잡(패킷 손실)이 감지되면 cwnd를 **절반으로 감소**시킵니다.

이 비대칭적 조절이 중요한 이유:
- 증가는 천천히(선형) → 네트워크에 부담을 주지 않으면서 탐색
- 감소는 급격히(절반) → 혼잡 상황에 빠르게 대응
- 이 방식이 반복되면 네트워크의 **공정한 대역폭 분배**에 수렴하는 것이 수학적으로 증명되어 있습니다.

### Q. TCP Tahoe와 Reno의 차이는?

| 구분 | TCP Tahoe | TCP Reno |
|------|----------|---------|
| Timeout 발생 시 | cwnd = 1, ssthresh = cwnd/2 → Slow Start | 동일 |
| 3 Dup ACK 발생 시 | cwnd = 1, ssthresh = cwnd/2 → **Slow Start** | cwnd = cwnd/2, ssthresh = cwnd/2 → **Fast Recovery** |
| Fast Recovery | 없음 | 있음 |
| 성능 | 손실 시 항상 처음부터 시작 → 느림 | 3 Dup ACK 시 절반에서 재시작 → 빠른 회복 |

핵심 차이는 **3 Duplicate ACK 발생 시 대응**입니다:
- **Tahoe**: 모든 손실을 동일하게 취급 → cwnd를 1로 리셋
- **Reno**: 3 Dup ACK는 "경미한 혼잡"으로 판단 → cwnd를 절반으로만 줄이고 Fast Recovery 진입

### Q. 3 Duplicate ACK과 Timeout의 차이는?

둘 다 패킷 손실을 감지하는 방법이지만, **혼잡의 심각도를 다르게 해석**합니다.

| 구분 | 3 Duplicate ACK | Timeout |
|------|----------------|---------|
| 의미 | 특정 세그먼트만 손실, 이후 세그먼트는 도착 | 응답 자체가 없음, 심각한 혼잡 |
| 혼잡 정도 | 경미한 혼잡 | 심각한 혼잡 |
| 감지 속도 | 빠름 (중복 ACK 즉시 수신) | 느림 (RTO 타이머 만료까지 대기) |
| Reno 대응 | cwnd = cwnd/2 → Fast Recovery | cwnd = 1 → Slow Start |
| Tahoe 대응 | cwnd = 1 → Slow Start | cwnd = 1 → Slow Start |

3 Duplicate ACK은 "일부 패킷이 손실되었지만 네트워크는 살아있다"는 신호이므로, Reno는 이를 활용해 **cwnd를 완전히 리셋하지 않고 절반에서 빠르게 회복**합니다.
