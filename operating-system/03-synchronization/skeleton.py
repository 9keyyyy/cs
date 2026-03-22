"""
실습 3: 프로세스 동기화

Race Condition을 재현하고 Mutex/Semaphore로 해결합니다.
Producer-Consumer 문제를 구현합니다.

TODO: 아래 빈칸을 채워주세요.
"""

import threading
import time
import random

# ============================================================
# Part A: Race Condition 재현
# ============================================================

counter = 0


def increment_without_lock(n: int):
    """동기화 없이 공유 변수를 증가 → Race Condition 발생."""
    global counter
    for _ in range(n):
        # 읽기 → 증가 → 쓰기가 원자적이지 않음!
        temp = counter
        temp += 1
        counter = temp


def demonstrate_race_condition():
    """Race Condition을 재현합니다."""
    global counter
    counter = 0
    threads = []

    for _ in range(5):
        t = threading.Thread(target=increment_without_lock, args=(100000,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"  기대값: 500000")
    print(f"  실제값: {counter}")
    print(f"  차이: {500000 - counter} (Race Condition!)")


# ============================================================
# Part B: Mutex로 해결
# ============================================================

counter_safe = 0
# TODO 1: threading 모듈의 Lock 객체를 생성하세요.
mutex = threading.Lock()


def increment_with_lock(n: int):
    """Mutex를 사용하여 안전하게 공유 변수를 증가합니다."""
    global counter_safe
    for _ in range(n):
        # TODO 2: Lock을 획득하세요.
        mutex.acquire()
        try:
            counter_safe += 1
        finally:
            # TODO 3: Lock을 해제하세요.
            mutex.release()


def demonstrate_mutex():
    """Mutex로 Race Condition을 해결합니다."""
    global counter_safe
    counter_safe = 0
    threads = []

    for _ in range(5):
        t = threading.Thread(target=increment_with_lock, args=(100000,))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    print(f"  기대값: 500000")
    print(f"  실제값: {counter_safe}")
    print(f"  정확한가? {counter_safe == 500000}")


# ============================================================
# Part C: Producer-Consumer (Semaphore)
# ============================================================

BUFFER_SIZE = 5


class BoundedBuffer:
    """유한 버퍼: Semaphore로 동기화합니다."""

    def __init__(self, size: int):
        self.buffer = []
        self.size = size
        self.mutex = threading.Lock()
        # TODO 4: Semaphore를 생성하세요.
        # empty: 빈 슬롯 수 (초기값 = 버퍼 크기)
        # full: 채워진 슬롯 수 (초기값 = 0)
        self.empty = threading.Semaphore(BUFFER_SIZE)
        self.full = threading.Semaphore(0)

    def produce(self, item):
        """생산자: 아이템을 버퍼에 넣습니다."""
        # TODO 5: empty 세마포어를 대기(acquire)하세요.
        # (빈 슬롯이 생길 때까지 대기)

        self.empty.acquire()
        self.mutex.acquire()

        self.buffer.append(item)
        print(f"  [Producer] 생산: {item} | 버퍼: {self.buffer}")

        self.mutex.release()
        # TODO 6: full 세마포어를 시그널(release)하세요.
        # (채워진 슬롯이 하나 증가했음을 알림)
        self.full.release()


    def consume(self) -> object:
        """소비자: 아이템을 버퍼에서 꺼냅니다."""
        # TODO 7: full 세마포어를 대기하세요.
        # (채워진 슬롯이 있을 때까지 대기)
        self.full.acquire()
        self.mutex.acquire()

        item = self.buffer.pop(0)
        print(f"  [Consumer] 소비: {item} | 버퍼: {self.buffer}")

        self.mutex.release()
        # TODO 8: empty 세마포어를 시그널하세요.
        self.empty.release()

        return item


def producer(buffer: BoundedBuffer, items: int):
    """생산자 스레드."""
    for i in range(items):
        buffer.produce(f"item-{i}")
        time.sleep(random.uniform(0.01, 0.05))


def consumer(buffer: BoundedBuffer, items: int):
    """소비자 스레드."""
    for _ in range(items):
        buffer.consume()
        time.sleep(random.uniform(0.02, 0.08))


def demonstrate_producer_consumer():
    """Producer-Consumer 문제를 시연합니다."""
    buf = BoundedBuffer(BUFFER_SIZE)
    num_items = 10

    prod = threading.Thread(target=producer, args=(buf, num_items))
    cons = threading.Thread(target=consumer, args=(buf, num_items))

    prod.start()
    cons.start()

    prod.join()
    cons.join()

    print(f"\n  버퍼 최종 상태: {buf.buffer} (비어있어야 정상)")


# ============================================================
# Part D: Reader-Writer 문제
# ============================================================

class ReadWriteLock:
    """
    Reader-Writer Lock:
    - 여러 Reader가 동시에 읽기 가능
    - Writer는 단독으로만 쓰기 가능
    - Writer가 있으면 Reader도 대기
    """

    def __init__(self):
        self.readers = 0
        self.mutex = threading.Lock()       # readers 카운터 보호
        self.write_lock = threading.Lock()  # writer 상호배제

    def read_acquire(self):
        """Reader가 읽기를 시작합니다."""
        self.mutex.acquire()
        self.readers += 1
        # TODO 9: 첫 번째 Reader가 진입하면 write_lock을 획득하세요.
        # (Writer가 쓰지 못하도록)
        if self.readers == ______:
            self.write_lock.acquire()
        self.mutex.release()

    def read_release(self):
        """Reader가 읽기를 종료합니다."""
        self.mutex.acquire()
        self.readers -= 1
        # TODO 10: 마지막 Reader가 나가면 write_lock을 해제하세요.
        if self.readers == ______:
            self.write_lock.release()
        self.mutex.release()

    def write_acquire(self):
        """Writer가 쓰기를 시작합니다."""
        self.write_lock.acquire()

    def write_release(self):
        """Writer가 쓰기를 종료합니다."""
        self.write_lock.release()


shared_resource = {"data": "초기값"}


def reader(rw_lock: ReadWriteLock, reader_id: int):
    """Reader 스레드."""
    for _ in range(3):
        rw_lock.read_acquire()
        print(f"  [Reader-{reader_id}] 읽기: {shared_resource['data']} (현재 readers={rw_lock.readers})")
        time.sleep(random.uniform(0.01, 0.03))
        rw_lock.read_release()
        time.sleep(random.uniform(0.01, 0.02))


def writer(rw_lock: ReadWriteLock, writer_id: int):
    """Writer 스레드."""
    for i in range(2):
        rw_lock.write_acquire()
        shared_resource["data"] = f"Writer-{writer_id}이(가) 쓴 데이터 #{i}"
        print(f"  [Writer-{writer_id}] 쓰기: {shared_resource['data']}")
        time.sleep(random.uniform(0.02, 0.05))
        rw_lock.write_release()
        time.sleep(random.uniform(0.01, 0.03))


def demonstrate_reader_writer():
    """Reader-Writer 문제를 시연합니다."""
    rw_lock = ReadWriteLock()
    threads = []

    for i in range(3):
        threads.append(threading.Thread(target=reader, args=(rw_lock, i)))
    for i in range(2):
        threads.append(threading.Thread(target=writer, args=(rw_lock, i)))

    for t in threads:
        t.start()
    for t in threads:
        t.join()


# ============================================================
# 메인
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Part A: Race Condition 재현")
    print("=" * 60)
    demonstrate_race_condition()

    print("\n" + "=" * 60)
    print("Part B: Mutex로 해결")
    print("=" * 60)
    demonstrate_mutex()

    print("\n" + "=" * 60)
    print("Part C: Producer-Consumer (Semaphore)")
    print("=" * 60)
    demonstrate_producer_consumer()

    print("\n" + "=" * 60)
    print("Part D: Reader-Writer")
    print("=" * 60)
    demonstrate_reader_writer()
