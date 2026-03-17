"""
실습 2: CPU 스케줄링 알고리즘

FCFS, SJF, Round Robin, Priority 스케줄링을 구현하고
평균 대기 시간 및 반환 시간을 비교합니다.

"""

from dataclasses import dataclass, field


@dataclass
class Process:
    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0  # 낮을수록 높은 우선순위
    remaining_time: int = 0
    start_time: int = -1
    completion_time: int = 0
    waiting_time: int = 0
    turnaround_time: int = 0

    def __post_init__(self):
        self.remaining_time = self.burst_time


def print_results(name: str, processes: list[Process]):
    """스케줄링 결과를 출력합니다."""
    print(f"\n{'='*50}")
    print(f"  {name} 스케줄링 결과")
    print(f"{'='*50}")
    print(f"  {'PID':<5} {'도착':<5} {'실행':<5} {'완료':<5} {'반환':<5} {'대기':<5}")
    print(f"  {'-'*30}")

    for p in sorted(processes, key=lambda x: x.pid):
        print(f"  {p.pid:<5} {p.arrival_time:<5} {p.burst_time:<5} "
              f"{p.completion_time:<5} {p.turnaround_time:<5} {p.waiting_time:<5}")

    avg_wt = sum(p.waiting_time for p in processes) / len(processes)
    avg_tat = sum(p.turnaround_time for p in processes) / len(processes)
    print(f"\n  평균 대기 시간: {avg_wt:.2f}")
    print(f"  평균 반환 시간: {avg_tat:.2f}")


def get_test_processes() -> list[Process]:
    """테스트용 프로세스 목록을 반환합니다."""
    return [
        Process("P1", arrival_time=0, burst_time=8, priority=3),
        Process("P2", arrival_time=1, burst_time=4, priority=1),
        Process("P3", arrival_time=2, burst_time=9, priority=4),
        Process("P4", arrival_time=3, burst_time=5, priority=2),
    ]


# ============================================================
# FCFS (First Come First Served)
# ============================================================
def schedule_fcfs(processes: list[Process]) -> list[Process]:
    """
    FCFS: 도착 순서대로 실행합니다. (Non-preemptive)

    알고리즘:
    1. 도착 시간 순으로 정렬
    2. 순서대로 실행, 완료 시간 = 이전 완료 시간 + burst_time
    3. 반환 시간 = 완료 시간 - 도착 시간
    4. 대기 시간 = 반환 시간 - 실행 시간
    """
    procs = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]

    # 도착 시간 기준으로 정렬하세요.
    procs.sort(key=lambda p: p.arrival_time)

    current_time = 0
    gantt = []

    for p in procs:
        if current_time < p.arrival_time:
            current_time = p.arrival_time

        p.start_time = current_time
        # 완료 시간을 계산하세요.
        p.completion_time = current_time + p.burst_time
        # 반환 시간을 계산하세요. (반환 시간 = 완료 시간 - 도착 시간)
        p.turnaround_time = p.completion_time - p.arrival_time
        # 대기 시간을 계산하세요. (대기 시간 = 반환 시간 - 실행 시간)
        p.waiting_time = p.turnaround_time - p.burst_time

        gantt.append((p.pid, p.start_time, p.completion_time))
        current_time = p.completion_time

    print(f"  Gantt: {' → '.join(f'{pid}[{s}-{e}]' for pid, s, e in gantt)}")
    return procs


# ============================================================
# SJF (Shortest Job First, Non-preemptive)
# ============================================================
def schedule_sjf(processes: list[Process]) -> list[Process]:
    """
    SJF: CPU burst가 가장 짧은 프로세스를 먼저 실행합니다.

    알고리즘:
    1. 현재 시간까지 도착한 프로세스 중 burst_time이 가장 짧은 프로세스 선택
    2. 해당 프로세스를 완료까지 실행 (Non-preemptive)
    3. 반복
    """
    procs = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    completed = []
    current_time = 0
    gantt = []

    while len(completed) < len(procs):
        # 현재 시간까지 도착하고 아직 완료되지 않은 프로세스들
        available = [p for p in procs if p.arrival_time <= current_time and p not in completed]

        if not available:
            current_time += 1
            continue

        # burst_time이 가장 짧은 프로세스를 선택하세요.
        selected = min(available, key=lambda p: p.burst_time)

        selected.start_time = current_time
        selected.completion_time = current_time + selected.burst_time
        selected.turnaround_time = selected.completion_time - selected.arrival_time
        selected.waiting_time = selected.turnaround_time - selected.burst_time

        gantt.append((selected.pid, selected.start_time, selected.completion_time))
        current_time = selected.completion_time
        completed.append(selected)

    print(f"  Gantt: {' → '.join(f'{pid}[{s}-{e}]' for pid, s, e in gantt)}")
    return procs


# ============================================================
# Round Robin
# ============================================================
def schedule_rr(processes: list[Process], time_quantum: int = 3) -> list[Process]:
    """
    Round Robin: 각 프로세스에 time_quantum만큼 CPU를 할당합니다.

    알고리즘:
    1. Ready 큐에서 프로세스를 꺼냄
    2. min(remaining_time, time_quantum)만큼 실행
    3. 남은 시간이 있으면 Ready 큐 끝에 추가
    4. 없으면 완료 처리
    """
    procs = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    ready_queue = []
    current_time = 0
    completed_count = 0
    gantt = []

    # 도착 시간 순으로 정렬
    procs.sort(key=lambda p: p.arrival_time)
    arrived = set()

    while completed_count < len(procs):
        # 현재 시간까지 도착한 프로세스를 Ready 큐에 추가
        for p in procs:
            if p.arrival_time <= current_time and p.pid not in arrived and p.remaining_time > 0:
                ready_queue.append(p)
                arrived.add(p.pid)

        if not ready_queue:
            current_time += 1
            continue

        p = ready_queue.pop(0)

        if p.start_time == -1:
            p.start_time = current_time

        # 실행 시간을 결정하세요. (remaining_time과 time_quantum 중 작은 값)
        exec_time = min(p.remaining_time, time_quantum)

        current_time += exec_time
        # 남은 실행 시간을 갱신하세요.
        p.remaining_time -= exec_time

        gantt.append((p.pid, current_time - exec_time, current_time))

        # 새로 도착한 프로세스를 먼저 큐에 추가
        for q in procs:
            if q.arrival_time <= current_time and q.pid not in arrived and q.remaining_time > 0:
                ready_queue.append(q)
                arrived.add(q.pid)

        # 남은 시간이 있으면 큐에 다시 추가, 없으면 완료 처리
        if p.remaining_time > 0:
            ready_queue.append(p)
        else:
            p.completion_time = current_time
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            completed_count += 1

    print(f"  Gantt: {' → '.join(f'{pid}[{s}-{e}]' for pid, s, e in gantt)}")
    return procs


# ============================================================
# Priority Scheduling (with Aging)
# ============================================================
def schedule_priority(processes: list[Process], aging_interval: int = 5) -> list[Process]:
    """
    Priority Scheduling: 우선순위가 높은(값이 낮은) 프로세스를 먼저 실행합니다.
    Aging: aging_interval마다 대기 중인 프로세스의 우선순위를 1씩 높입니다.

    """
    procs = [Process(p.pid, p.arrival_time, p.burst_time, p.priority) for p in processes]
    effective_priority = {p.pid: p.priority for p in procs}
    completed = []
    current_time = 0
    gantt = []

    while len(completed) < len(procs):
        available = [p for p in procs if p.arrival_time <= current_time and p not in completed]

        if not available:
            current_time += 1
            continue

        # Aging: 대기 시간이 aging_interval 이상인 프로세스의 우선순위를 높임
        for p in available:
            wait = current_time - p.arrival_time
            # Aging 적용 - 대기 시간에 따라 우선순위를 낮추세요 (값이 작을수록 높은 우선순위).
            effective_priority[p.pid] = p.priority - (wait // aging_interval)

        # effective_priority가 가장 낮은(= 우선순위가 가장 높은) 프로세스를 선택하세요.
        selected = min(available, key=lambda p: effective_priority[p.pid])

        selected.start_time = current_time
        selected.completion_time = current_time + selected.burst_time
        selected.turnaround_time = selected.completion_time - selected.arrival_time
        selected.waiting_time = selected.turnaround_time - selected.burst_time

        gantt.append((selected.pid, selected.start_time, selected.completion_time))
        current_time = selected.completion_time
        completed.append(selected)

    print(f"  Gantt: {' → '.join(f'{pid}[{s}-{e}]' for pid, s, e in gantt)}")
    return procs


# ============================================================
# 메인: 비교 실행
# ============================================================
if __name__ == "__main__":
    print("=" * 60)
    print("CPU 스케줄링 알고리즘 비교")
    print("=" * 60)

    test_procs = get_test_processes()
    print(f"\n  프로세스 목록:")
    print(f"  {'PID':<5} {'도착':<5} {'실행':<5} {'우선순위':<8}")
    for p in test_procs:
        print(f"  {p.pid:<5} {p.arrival_time:<5} {p.burst_time:<5} {p.priority:<8}")

    print("\n[1] FCFS")
    result_fcfs = schedule_fcfs(test_procs)
    print_results("FCFS", result_fcfs)

    print("\n[2] SJF (Non-preemptive)")
    result_sjf = schedule_sjf(test_procs)
    print_results("SJF", result_sjf)

    print("\n[3] Round Robin (TQ=3)")
    result_rr = schedule_rr(test_procs, time_quantum=3)
    print_results("Round Robin", result_rr)

    print("\n[4] Priority (with Aging)")
    result_pri = schedule_priority(test_procs, aging_interval=5)
    print_results("Priority", result_pri)
