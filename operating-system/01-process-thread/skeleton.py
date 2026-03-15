"""
실습 1: 프로세스와 스레드 시뮬레이터

프로세스 상태 전이, PCB, Context Switch를 시뮬레이션합니다.
스레드와 프로세스의 메모리 공유 차이를 실험합니다.

"""

import threading
import multiprocessing
import time

# ============================================================
# Part A: PCB와 프로세스 상태 전이
# ============================================================

# 프로세스 상태 정의
NEW = "NEW"
READY = "READY"
RUNNING = "RUNNING"
WAITING = "WAITING"
TERMINATED = "TERMINATED"

# 유효한 상태 전이 정의
VALID_TRANSITIONS = {
    NEW: [READY],
    READY: [RUNNING],
    RUNNING: [READY, WAITING, TERMINATED],
    WAITING: [READY],
    TERMINATED: [],
}


class PCB:
    """Process Control Block - 프로세스의 모든 정보를 담는 자료구조"""

    _next_pid = 1

    def __init__(self, name: str, priority: int = 0):
        # TODO 1: PCB 필드를 초기화하세요.
        self.pid = PCB._next_pid
        PCB._next_pid += 1
        self.name = name
        self.state = NEW
        self.priority = priority
        self.program_counter = 0
        self.registers = {"AX": 0, "BX": 0, "CX": 0, "SP": 0}
        self.memory_usage = 0
        self.cpu_time_used = 0

    def __repr__(self):
        return f"PCB(pid={self.pid}, name={self.name}, state={self.state})"


class ProcessManager:
    """프로세스 상태 전이를 관리합니다."""

    def __init__(self):
        self.processes: dict[int, PCB] = {}
        self.ready_queue: list[PCB] = []
        self.running_process: PCB | None = None
        self.context_switch_count = 0

    def create_process(self, name: str, priority: int = 0) -> PCB:
        """새 프로세스를 생성합니다 (New 상태)."""
        pcb = PCB(name, priority)
        self.processes[pcb.pid] = pcb
        print(f"  [생성] {pcb}")
        return pcb

    def _transition(self, pcb: PCB, new_state: str):
        """상태 전이를 수행합니다. 유효하지 않은 전이는 거부합니다."""
        # TODO 2: 유효한 전이인지 검증하세요.
        # VALID_TRANSITIONS 딕셔너리를 참조합니다.
        if new_state not in VALID_TRANSITIONS[pcb.state]:
            print(f"  [오류] {pcb.state} → {new_state} 전이 불가!")
            return False

        old_state = pcb.state
        pcb.state = new_state
        print(f"  [{pcb.name}] {old_state} → {new_state}")
        return True

    def admit(self, pcb: PCB):
        """New → Ready: 프로세스를 Ready 큐에 추가합니다."""
        if self._transition(pcb, READY):
            self.ready_queue.append(pcb)

    def dispatch(self):
        """Ready → Running: Ready 큐에서 프로세스를 선택하여 실행합니다."""
        if not self.ready_queue:
            print("  [스케줄러] Ready 큐가 비었습니다.")
            return

        if self.running_process:
            print("  [스케줄러] 이미 실행 중인 프로세스가 있습니다. 먼저 interrupt하세요.")
            return

        # Ready 큐에서 프로세스를 꺼내 실행 상태로 전이하세요.
        pcb = self.ready_queue.pop(0)
        if self._transition(pcb, RUNNING):
            self.running_process = pcb

    def interrupt(self):
        """Running → Ready: 실행 중인 프로세스를 Ready로 되돌립니다 (Preemption)."""
        if not self.running_process:
            return

        pcb = self.running_process
        # Context Switch를 수행하세요.
        # 현재 프로세스의 상태를 저장하고 Ready 큐로 되돌립니다.
        self._save_context(pcb)
        if self._transition(pcb, READY):
            self.ready_queue.append(pcb)
            self.running_process = None
            self.context_switch_count += 1

    def io_wait(self):
        """Running → Waiting: I/O 요청으로 대기 상태로 전환합니다."""
        if not self.running_process:
            return

        pcb = self.running_process
        self._save_context(pcb)
        if self._transition(pcb, WAITING):
            self.running_process = None
            self.context_switch_count += 1

    def io_complete(self, pcb: PCB):
        """Waiting → Ready: I/O 완료 후 Ready 큐로 복귀합니다."""
        # Waiting 상태의 프로세스를 Ready로 전이하세요.
        if self._transition(pcb, READY):
            self.ready_queue.append(pcb)

    def terminate(self):
        """Running → Terminated: 프로세스를 종료합니다."""
        if not self.running_process:
            return

        pcb = self.running_process
        self._save_context(pcb)
        if self._transition(pcb, TERMINATED):
            self.running_process = None
            self.context_switch_count += 1

    def _save_context(self, pcb: PCB):
        """현재 실행 상태를 PCB에 저장합니다 (Context Switch의 일부)."""
        pcb.program_counter += 10
        pcb.registers["AX"] += 1
        print(f"  [Context Save] PID={pcb.pid}: PC={pcb.program_counter}, AX={pcb.registers['AX']}")

    def _restore_context(self, pcb: PCB):
        """PCB에서 상태를 복원합니다 (Context Switch의 일부)."""
        print(f"  [Context Restore] PID={pcb.pid}: PC={pcb.program_counter}, AX={pcb.registers['AX']}")

    def show_status(self):
        """현재 시스템 상태를 출력합니다."""
        print(f"\n  Running: {self.running_process}")
        print(f"  Ready Queue: {self.ready_queue}")
        print(f"  Context Switches: {self.context_switch_count}")


# ============================================================
# Part B: fork() 시뮬레이션
# ============================================================
def simulate_fork(parent: PCB) -> PCB:
    """
    fork()를 시뮬레이션합니다.
    부모 프로세스의 PCB를 복사하여 자식 프로세스를 만듭니다.

    """
    child = PCB(f"{parent.name}_child", parent.priority)

    # 부모의 레지스터와 PC를 자식에게 복사하세요.
    child.program_counter = parent.program_counter
    child.registers = parent.registers.copy()

    print(f"  [fork] 부모 PID={parent.pid} → 자식 PID={child.pid}")
    print(f"  [fork] 자식이 부모의 PC={child.program_counter}, 레지스터={child.registers}를 복사함")

    return child


# ============================================================
# Part C: 스레드 vs 프로세스 메모리 공유 비교
# ============================================================
shared_data = {"counter": 0}


def thread_worker(name: str, iterations: int):
    """스레드는 같은 프로세스의 메모리(shared_data)를 공유합니다."""
    for _ in range(iterations):
        # 명시적 read → modify → write (race condition 재현을 위해)
        # Python GIL 때문에 += 1로는 race가 거의 안 생기므로,
        # 읽기와 쓰기 사이에 time.sleep(0)으로 GIL을 양보시킵니다.
        temp = shared_data["counter"]   # 읽기
        time.sleep(0)                    # GIL 양보 → 다른 스레드가 끼어들 수 있음!
        shared_data["counter"] = temp + 1  # 쓰기


process_local_counter = 0  # 일반 전역 변수 (프로세스 간 공유 안 됨)


def process_worker_no_share(name: str, iterations: int):
    """프로세스는 독립된 메모리 → 일반 전역 변수를 바꿔도 다른 프로세스에 반영 안 됨."""
    global process_local_counter
    for _ in range(iterations):
        process_local_counter += 1
    print(f"  [Process-{name}] 내 메모리의 counter = {process_local_counter}")


def process_worker_shared(name: str, iterations: int, shared_value, lock):
    """공유 메모리 + Lock을 사용해야 프로세스 간 데이터 공유 가능."""
    for _ in range(iterations):
        with lock:
            shared_value.value += 1


def compare_thread_vs_process():
    """스레드와 프로세스의 메모리 공유 차이를 비교합니다."""
    print("\n--- 스레드 테스트 (메모리 공유) ---")
    shared_data["counter"] = 0
    threads = []

    for i in range(3):
        t = threading.Thread(target=thread_worker, args=(f"T{i}", 1000))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    expected = 3000
    actual = shared_data["counter"]
    print(f"  기대값: {expected}")
    print(f"  실제값: {actual}")
    print(f"  차이: {expected - actual}  ({'Race Condition 발생!' if actual != expected else '운 좋게 일치'})")

    print("\n--- 프로세스 테스트 1: 일반 변수 (공유 안 됨) ---")
    global process_local_counter
    process_local_counter = 0
    processes = []

    for i in range(3):
        p = multiprocessing.Process(target=process_worker_no_share, args=(f"P{i}", 1000))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print(f"  부모 프로세스의 counter = {process_local_counter}  (0! 자식이 바꿔도 부모에 반영 안 됨)")

    print("\n--- 프로세스 테스트 2: 공유 메모리 + Lock (명시적 공유) ---")
    shared_value = multiprocessing.Value("i", 0)
    lock = multiprocessing.Lock()
    processes = []

    for i in range(3):
        p = multiprocessing.Process(
            target=process_worker_shared, args=(f"P{i}", 1000, shared_value, lock)
        )
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    print(f"  최종 shared_value = {shared_value.value}  (Lock 사용 → 정확히 3000)")


# ============================================================
# 메인: 시뮬레이션 실행
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("Part A: 프로세스 상태 전이 시뮬레이션")
    print("=" * 60)

    pm = ProcessManager()

    # 프로세스 생성
    p1 = pm.create_process("웹서버", priority=2)
    p2 = pm.create_process("DB쿼리", priority=1)
    p3 = pm.create_process("로깅", priority=3)

    # 상태 전이 시뮬레이션
    pm.admit(p1)
    pm.admit(p2)
    pm.admit(p3)

    pm.dispatch()       # p1 실행
    pm.show_status()

    pm.interrupt()      # p1 → Ready (Context Switch!)
    pm.dispatch()       # p2 실행
    pm.show_status()

    pm.io_wait()        # p2 → Waiting (I/O 요청)
    pm.dispatch()       # p3 실행

    pm.io_complete(p2)  # p2 → Ready (I/O 완료)
    pm.terminate()      # p3 → Terminated
    pm.dispatch()       # p1 실행 (Ready 큐에서)

    pm.show_status()

    print(f"\n  총 Context Switch 횟수: {pm.context_switch_count}")

    print("\n" + "=" * 60)
    print("Part B: fork() 시뮬레이션")
    print("=" * 60)

    parent = PCB("bash", priority=5)
    parent.program_counter = 100
    parent.registers = {"AX": 42, "BX": 7, "CX": 0, "SP": 8000}
    child = simulate_fork(parent)

    print("\n" + "=" * 60)
    print("Part C: 스레드 vs 프로세스 메모리 공유")
    print("=" * 60)

    compare_thread_vs_process()
