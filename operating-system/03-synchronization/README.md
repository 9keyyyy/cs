# 실습 3: 프로세스 동기화

## 면접 키워드
- Race Condition
- Critical Section (임계 영역)
- Mutex (Mutual Exclusion)
- Semaphore (Counting / Binary)
- Monitor, Condition Variable
- Spinlock
- Producer-Consumer Problem
- Reader-Writer Problem

## 과제
Race condition을 직접 재현하고, Mutex와 Semaphore로 해결합니다.
Producer-Consumer 문제를 Semaphore로 구현합니다.

## 면접 예상 질문

### Q. Race Condition이란 무엇이고 어떻게 해결하나요?

Race Condition은 **여러 프로세스/스레드가 공유 자원에 동시에 접근할 때, 실행 순서에 따라 결과가 달라지는 상황**입니다.

```
스레드 A: counter 읽기 (counter = 5)
스레드 B: counter 읽기 (counter = 5)
스레드 A: counter = 5 + 1 = 6 저장
스레드 B: counter = 5 + 1 = 6 저장
→ 2번 증가했지만 결과는 6 (기대값: 7)
```

**해결: Critical Section 보호**

공유 자원에 접근하는 코드 영역(Critical Section)을 동기화 메커니즘으로 보호합니다.

**Critical Section 문제의 3가지 해결 조건**:
1. **Mutual Exclusion (상호 배제)**: 한 프로세스가 임계 영역에 있으면 다른 프로세스는 진입 불가
2. **Progress (진행)**: 임계 영역이 비어있으면 진입을 원하는 프로세스가 진입 가능해야 함
3. **Bounded Waiting (한정 대기)**: 임계 영역 진입 요청 후 무한히 대기하지 않아야 함

### Q. Mutex와 Semaphore의 차이는?

| 구분 | Mutex | Semaphore |
|------|-------|-----------|
| 값 | 0 또는 1 (이진) | 0 이상의 정수 (카운팅) |
| 소유권 | **있음** (lock한 스레드만 unlock 가능) | **없음** (다른 스레드가 signal 가능) |
| 용도 | **하나의 자원** 보호 (locking) | **N개의 자원** 관리 (signaling) |
| 메커니즘 | Locking mechanism | Signaling mechanism |
| 예시 | 화장실 열쇠 (한 명만 사용) | 주차장 (N대까지 입장) |

```python
# Mutex: 한 번에 한 스레드만
mutex.acquire()    # lock
# critical section
mutex.release()    # unlock (acquire한 스레드만 가능)

# Semaphore(N): 최대 N개 스레드 동시 접근
semaphore = Semaphore(3)  # 3개 슬롯
semaphore.acquire()  # wait (P 연산): count -= 1, count < 0이면 대기
# resource 사용
semaphore.release()  # signal (V 연산): count += 1, 대기 중인 스레드 깨움
```

> **Binary Semaphore ≠ Mutex**: Binary Semaphore는 값이 0/1이지만 소유권이 없습니다. Mutex는 소유권이 있어 **priority inheritance** 등 추가 기능을 제공합니다.

### Q. Spinlock이란?

Spinlock은 lock을 획득할 때까지 **Busy Waiting(바쁜 대기)**하는 동기화 메커니즘입니다.

```python
# Spinlock의 원리
while not lock.try_acquire():  # 계속 시도
    pass  # CPU를 사용하며 대기 (spin)
# critical section
lock.release()
```

| 상황 | Spinlock | Mutex (Sleep) |
|------|----------|---------------|
| **짧은 대기** | 유리 (context switch 없이 바로 진입) | 불리 (sleep/wakeup 오버헤드) |
| **긴 대기** | 불리 (CPU 낭비) | 유리 (sleep 상태에서 CPU 양보) |
| **싱글코어** | **비효율적** (spin 중 lock 해제 불가) | 적합 |
| **멀티코어** | **효과적** (다른 코어에서 lock 해제) | 적합 |

Linux 커널에서는 **짧은 임계 영역에 Spinlock**, **긴 임계 영역에 Mutex**를 사용합니다.

### Q. Producer-Consumer 문제를 설명하세요.

**유한 크기의 버퍼**를 사이에 두고, 생산자(Producer)는 데이터를 넣고, 소비자(Consumer)는 데이터를 꺼내는 문제입니다.

**문제 상황**:
- 버퍼가 **가득 참** → 생산자 대기
- 버퍼가 **비어 있음** → 소비자 대기
- **동시 접근** → 데이터 손상

**해결: Mutex + Semaphore 2개**

```
mutex = Mutex()         # 버퍼 접근 보호
empty = Semaphore(N)    # 빈 슬롯 수 (초기값 = 버퍼 크기)
full  = Semaphore(0)    # 채워진 슬롯 수 (초기값 = 0)

Producer:                Consumer:
  empty.wait()             full.wait()
  mutex.lock()             mutex.lock()
  buffer.put(item)         item = buffer.get()
  mutex.unlock()           mutex.unlock()
  full.signal()            empty.signal()
```

> `wait()`와 `lock()`의 순서가 중요합니다. `mutex.lock()` 후 `empty.wait()`을 하면 **데드락** 발생 가능 (mutex를 잡은 채로 대기).

### Q. Monitor란 무엇인가요?

Monitor는 **상호배제를 언어/컴파일러 수준에서 자동으로 보장**하는 고수준 동기화 구조입니다. Semaphore는 프로그래머가 직접 `wait()`/`signal()` 순서를 관리해야 해서 실수하기 쉬운 반면, Monitor는 **구조 자체가 상호배제를 강제**합니다.

#### Monitor의 내부 구조

```
                  ┌─ Entry Queue ──────────────────────────────────────────┐
                  │  (Monitor 진입을 기다리는 스레드들이 대기)                  │
                  │  [스레드 D] → [스레드 E] → [스레드 F]                    │
                  └──────────────────────┬─────────────────────────────────┘
                                         ▼
                  ┌─ Monitor ─────────────────────────────────────────────┐
                  │                                                       │
                  │  공유 데이터 (예: buffer[], count)                      │
                  │                                                       │
                  │  프로시저 put() ──┐                                    │
                  │  프로시저 get() ──┤ 한 번에 하나의 스레드만 실행           │
                  │                   └──────────────────────────────────  │
                  │                                                       │
                  │  Condition Variables:                                  │
                  │  ┌─ not_full (Waiting Queue) ───────────────────────┐  │
                  │  │  버퍼가 가득 차서 대기 중인 Producer들               │  │
                  │  │  [스레드 A] → [스레드 B]                           │  │
                  │  └─────────────────────────────────────────────────┘  │
                  │  ┌─ not_empty (Waiting Queue) ──────────────────────┐  │
                  │  │  버퍼가 비어서 대기 중인 Consumer들                  │  │
                  │  │  [스레드 C]                                       │  │
                  │  └─────────────────────────────────────────────────┘  │
                  └───────────────────────────────────────────────────────┘
```

#### 핵심 개념

**1. Entry Queue (진입 큐)**

Monitor에 진입하려는 스레드들이 대기하는 큐입니다. Monitor 내부에는 **한 번에 하나의 스레드만** 존재할 수 있으므로, 이미 다른 스레드가 실행 중이면 Entry Queue에서 대기합니다.

```
스레드 A: put() 호출 → Monitor 진입 (실행 중)
스레드 B: put() 호출 → Entry Queue에서 대기
스레드 C: get() 호출 → Entry Queue에서 대기
→ 스레드 A가 끝나면, Entry Queue에서 다음 스레드가 진입
```

**2. Waiting Queue (조건 대기 큐)**

Monitor 내부에서 실행 중인 스레드가 **특정 조건이 충족되지 않아** `wait()`을 호출하면 Waiting Queue로 이동합니다. 이때 Monitor의 lock을 **반납**하므로, Entry Queue의 다른 스레드가 진입할 수 있습니다.

- `condition.wait()`: Waiting Queue로 이동 + Monitor lock 반납
- `condition.notify()`: Waiting Queue에서 스레드 하나를 깨움

> Waiting Queue는 Condition Variable마다 별도로 존재합니다. 위 그림에서 `not_full`과 `not_empty`는 각각 독립적인 Waiting Queue를 가집니다.

**3. signal() 후 누가 실행되는가? (Signal semantics)**

| 방식 | 설명 | 사용 예 |
|------|------|---------|
| **Signal and Wait** (Hoare) | signal을 보낸 스레드가 **양보**, 깨어난 스레드가 즉시 실행 | 이론적 모델 |
| **Signal and Continue** (Mesa) | signal을 보낸 스레드가 **계속 실행**, 깨어난 스레드는 Entry Queue로 이동 | Java, Python, POSIX |

Mesa 방식에서는 깨어난 스레드가 실행될 때 조건이 다시 거짓일 수 있으므로 **`while` 루프로 조건을 재확인**해야 합니다.

#### Bounded Buffer 예시 (Monitor 동작 흐름)

```
초기 상태: buffer 크기 = 3, buffer = []

[시간 1] Producer P1: put(A) 호출
  → Monitor 진입 (아무도 없음)
  → buffer가 안 가득 참 → buffer = [A]
  → not_empty.notify() → (대기 중인 Consumer 없으므로 아무 일도 안 일어남)
  → Monitor 퇴장

[시간 2] Producer P2: put(B) 호출, Consumer C1: get() 호출 (동시)
  → P2가 먼저 Monitor 진입, C1은 Entry Queue에서 대기
  → buffer = [A, B]
  → not_empty.notify()
  → P2 퇴장 → C1이 Entry Queue에서 Monitor 진입
  → buffer가 안 비어 있음 → item = A, buffer = [B]
  → not_full.notify()
  → C1 퇴장

[시간 3] Producer P3, P4, P5가 동시에 put() 호출
  → P3 진입: buffer = [B, C, D] (가득 참), 퇴장
  → P4 진입: buffer 가득 참 → not_full.wait() → Waiting Queue로 이동, lock 반납
  → P5 진입: buffer 가득 참 → not_full.wait() → Waiting Queue로 이동, lock 반납
  ※ P4, P5는 Monitor 안의 not_full Waiting Queue에서 대기 중

[시간 4] Consumer C2: get() 호출
  → Monitor 진입 → item = B, buffer = [C, D]
  → not_full.notify() → P4가 Waiting Queue에서 깨어남
  → (Mesa 방식) C2가 계속 실행, C2 퇴장
  → P4가 Monitor 재진입 → while not full 재확인 → buffer = [C, D, E]
  → not_empty.notify()
  → P4 퇴장
```

- Python의 `with condition` → Monitor의 Entry Queue + 자동 상호배제
- `condition.wait()` → Condition Variable의 Waiting Queue로 이동
- `condition.notify_all()` → Waiting Queue의 모든 스레드를 깨워 Entry Queue로 이동시킴

#### Semaphore vs Monitor 비교

| 구분 | Semaphore | Monitor |
|------|-----------|---------|
| 상호배제 | 프로그래머가 직접 구현 | 자동 보장 |
| 조건 대기 | 별도 Semaphore로 구현 | Condition Variable 내장 |
| 실수 가능성 | 높음 (wait/signal 순서 실수 → 데드락) | 낮음 (구조가 강제) |
| 추상화 수준 | 저수준 | 고수준 |
| 언어 지원 | OS 수준 | Java `synchronized`, Python `threading.Condition` |
