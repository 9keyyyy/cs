"""
실습 2 정답 모음
"""

# TODO 1: procs.sort(key=lambda p: p.arrival_time)

# TODO 2: p.completion_time = current_time + p.burst_time

# TODO 3: p.turnaround_time = p.completion_time - p.arrival_time

# TODO 4: p.waiting_time = p.turnaround_time - p.burst_time

# TODO 5: selected = min(available, key=lambda p: p.burst_time)

# TODO 6: exec_time = min(p.remaining_time, time_quantum)

# TODO 7: p.remaining_time -= exec_time

# TODO 8: if p.remaining_time > 0:

# TODO 9: effective_priority[p.pid] = p.priority - (wait // aging_interval)

# TODO 10: selected = min(available, key=lambda p: effective_priority[p.pid])
