# 실습 7: Reliable UDP (Stop-and-Wait ARQ)

## 면접 키워드
- ARQ (Automatic Repeat reQuest)
- Stop-and-Wait, Go-Back-N, Selective Repeat
- ACK, Timeout, 재전송
- Sequence Number의 역할

## 과제
UDP 위에 신뢰성을 직접 구현합니다.
Stop-and-Wait ARQ 프로토콜로 패킷 손실에도 데이터를 안전하게 전달합니다.

## 면접 예상 질문

### Stop-and-Wait ARQ를 설명하세요.
가장 단순한 ARQ 방식입니다. 송신자가 패킷 하나를 보내고, 수신자의 ACK가 올 때까지 기다립니다. ACK가 오면 다음 패킷을 보내고, Timeout 내에 ACK가 안 오면 같은 패킷을 재전송합니다. 구현이 간단하지만 ACK를 기다리는 동안 회선이 놀기 때문에 **채널 이용률이 낮다**는 단점이 있습니다. 특히 RTT가 긴 네트워크에서는 대부분의 시간을 대기에 소비하게 됩니다.

### Go-Back-N과 Selective Repeat의 차이는?
둘 다 Stop-and-Wait의 낮은 효율을 개선하기 위해 **윈도우 기반으로 여러 패킷을 동시에 전송**하는 파이프라이닝 방식입니다.

- **Go-Back-N**: 수신자는 순서대로만 받습니다. 중간에 패킷이 유실되면 그 이후 패킷을 전부 버리고, 송신자는 유실된 패킷부터 **윈도우 전체를 재전송**합니다. 수신자 버퍼가 필요 없어 구현이 단순하지만, 불필요한 재전송이 많습니다.
- **Selective Repeat**: 수신자는 순서와 무관하게 올바른 패킷을 **개별적으로 버퍼에 저장**합니다. 유실된 패킷만 선택적으로 재전송하므로 효율적이지만, 수신자에 버퍼와 개별 타이머 관리가 필요해 구현이 복잡합니다.

| 비교 | Go-Back-N | Selective Repeat |
|------|-----------|------------------|
| 수신자 버퍼 | 불필요 | 필요 |
| 재전송 범위 | 윈도우 전체 | 유실된 패킷만 |
| 구현 복잡도 | 낮음 | 높음 |
| 네트워크 효율 | 낮음 | 높음 |

### Sequence Number가 왜 필요한가요?
패킷의 **순서 보장**과 **중복 감지**를 위해 필요합니다. 네트워크에서는 패킷이 유실, 지연, 중복되어 도착할 수 있습니다. 예를 들어 송신자가 ACK를 못 받아 같은 패킷을 재전송하면 수신자는 동일한 데이터를 두 번 받게 됩니다. Sequence Number가 있으면 "이미 받은 패킷인지" 판별해서 중복을 버릴 수 있고, 도착 순서가 뒤바뀌어도 원래 순서대로 재조립할 수 있습니다.

### Timeout 값은 어떻게 정하나요? (RTT 측정)
Timeout은 **RTT(Round Trip Time)를 기반으로 동적으로 설정**합니다. TCP의 경우 다음과 같이 계산합니다.

1. **SampleRTT**: 패킷을 보내고 ACK가 돌아올 때까지의 실측 시간
2. **EstimatedRTT**: 지수 가중 이동 평균(EWMA)으로 평활화
   - `EstimatedRTT = (1-α) × EstimatedRTT + α × SampleRTT` (보통 α=0.125)
3. **DevRTT**: RTT의 변동폭 추적
   - `DevRTT = (1-β) × DevRTT + β × |SampleRTT - EstimatedRTT|` (보통 β=0.25)
4. **Timeout = EstimatedRTT + 4 × DevRTT**

너무 짧으면 불필요한 재전송이 발생하고, 너무 길면 유실 감지가 느려집니다. 그래서 RTT의 평균뿐 아니라 **편차(DevRTT)**까지 반영하여 네트워크 상태에 적응적으로 조절합니다.
