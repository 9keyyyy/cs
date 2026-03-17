# 실습 2: CPU 스케줄링 알고리즘

## 면접 키워드
- FCFS (First Come First Served)
- SJF (Shortest Job First)
- RR (Round Robin)
- Priority Scheduling
- Preemptive vs Non-preemptive
- Convoy Effect, Starvation, Aging

## 과제
4가지 CPU 스케줄링 알고리즘을 구현하고, 같은 프로세스 집합에 대해
평균 대기 시간과 평균 반환 시간을 비교합니다.

## 면접 예상 질문

### Q. FCFS 스케줄링의 장단점은?

FCFS(First Come First Served)는 **먼저 도착한 프로세스를 먼저 실행**하는 가장 단순한 스케줄링입니다.

| 항목 | 내용 |
|------|------|
| 장점 | 구현 간단 (FIFO 큐), 공정함 (도착 순서 보장) |
| 단점 | **Convoy Effect** 발생 |
| 방식 | Non-preemptive |

**Convoy Effect**: CPU burst가 긴 프로세스가 먼저 도착하면, 뒤에 오는 짧은 프로세스들이 모두 오래 기다리게 됩니다.

```
예: P1(burst=24), P2(burst=3), P3(burst=3) 순서로 도착
Gantt: |    P1 (24)    | P2(3) | P3(3) |
P1 대기=0, P2 대기=24, P3 대기=27
평균 대기시간 = (0+24+27)/3 = 17

만약 P2, P3, P1 순서였다면?
Gantt: |P2(3)|P3(3)|    P1 (24)    |
평균 대기시간 = (0+3+6)/3 = 3
```

### Q. SJF가 최적인 이유와 한계는?

SJF(Shortest Job First)는 **CPU burst가 가장 짧은 프로세스를 먼저 실행**합니다.

**최적인 이유**: 짧은 작업을 먼저 처리하면, 뒤에 대기하는 프로세스 수가 빠르게 줄어들어 **평균 대기 시간이 수학적으로 최소**가 됩니다.

**한계**:
1. **CPU burst 예측 불가**: 다음 burst 길이를 사전에 알 수 없음. **지수 평균(Exponential Averaging)**으로 추정: `τ(n+1) = α × t(n) + (1-α) × τ(n)` (α: 가중치, t(n): 실제 값, τ(n): 예측 값)
2. **Starvation**: burst가 긴 프로세스가 짧은 프로세스에게 계속 밀려 **무한 대기** 가능
3. Preemptive SJF (= SRTF, Shortest Remaining Time First)는 더 짧은 프로세스 도착 시 현재 실행 중단

### Q. Round Robin에서 Time Quantum 크기의 영향은?

Round Robin은 **각 프로세스에 고정된 시간(Time Quantum, TQ)만큼 CPU를 할당**하고, 시간이 만료되면 Ready 큐 끝으로 보내는 Preemptive 스케줄링입니다.

| TQ 크기 | 효과 |
|---------|------|
| **너무 큼** | 각 프로세스가 burst를 다 수행 → FCFS와 동일해짐 |
| **너무 작음** | Context Switch가 잦아 오버헤드 증가 → CPU가 실제 작업보다 전환에 시간 소비 |
| **적절** | 보통 10~100ms. burst의 80%가 TQ 이내에 끝나도록 설정 |

```
TQ=4일 때: P1(burst=10), P2(burst=4), P3(burst=6)
Gantt: |P1(4)|P2(4)|P3(4)|P1(4)|P3(2)|P1(2)|
→ 모든 프로세스가 비교적 빨리 응답 시작
```

RR의 핵심 장점은 **응답 시간(Response Time)**이 짧다는 것입니다. 인터랙티브 시스템에 적합합니다.

### Q. Starvation과 Aging을 설명하세요.

**Starvation(기아)**은 우선순위가 낮은 프로세스가 높은 우선순위 프로세스에게 계속 밀려 **CPU를 영원히 할당받지 못하는 상태**입니다. SJF, Priority Scheduling에서 발생합니다.

**Aging**은 Starvation을 해결하는 기법으로, **대기 시간이 길어질수록 우선순위를 점진적으로 높여**줍니다.

```
예: 매 1초마다 우선순위를 1씩 증가
시각 0: P1(priority=100), P2(priority=1)  → P1 실행
시각 1: P1(priority=100), P2(priority=2)  → P1 실행
...
시각 99: P1(priority=100), P2(priority=100) → P2도 실행 기회!
```

### Q. Preemptive vs Non-preemptive 차이는?

| 구분 | Preemptive (선점) | Non-preemptive (비선점) |
|------|-------------------|----------------------|
| 정의 | 실행 중인 프로세스를 **강제로 중단** 가능 | 프로세스가 **자발적으로 CPU 양보** (I/O, 종료) |
| 중단 시점 | Timer interrupt, 높은 우선순위 도착 | 프로세스 스스로 종료 또는 I/O 요청 시만 |
| 응답 시간 | 짧음 (높은 우선순위 즉시 실행) | 길 수 있음 (현재 프로세스 끝날 때까지 대기) |
| 오버헤드 | Context Switch 빈번 | 적음 |
| 예시 | RR, SRTF, Preemptive Priority | FCFS, Non-preemptive SJF |
| 적합 환경 | 인터랙티브 시스템, 실시간 시스템 | 배치 시스템 |

현대 OS는 대부분 **Preemptive 스케줄링**을 사용합니다. Timer interrupt를 통해 하나의 프로세스가 CPU를 독점하지 못하게 합니다.
