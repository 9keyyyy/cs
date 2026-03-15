# Operating System Practice - CS 면접 대비 실습

운영체제 핵심 개념을 직접 코드로 구현하며 체감하는 실습 과제 모음입니다.

## 실습 구조

| # | 주제 | 디렉토리 | 핵심 면접 키워드 |
|---|------|----------|-----------------|
| 1 | 프로세스와 스레드 | `01-process-thread/` | PCB, Context Switch, 프로세스 상태 |
| 2 | CPU 스케줄링 | `02-cpu-scheduling/` | FCFS, SJF, RR, Priority, Starvation |
| 3 | 프로세스 동기화 | `03-synchronization/` | Race Condition, Mutex, Semaphore |
| 4 | 데드락 | `04-deadlock/` | 4가지 조건, Banker's Algorithm |
| 5 | 페이징 & 주소 변환 | `05-paging/` | Page Table, TLB, 내부/외부 단편화 |
| 6 | 페이지 교체 알고리즘 | `06-page-replacement/` | FIFO, LRU, Optimal, Belady's Anomaly |
| 7 | 파일 시스템 | `07-file-system/` | inode, FAT, Hard/Symbolic Link |
| 8 | 프로세스 간 통신 (IPC) | `08-ipc/` | Pipe, Shared Memory, Message Queue |
| 9 | 디스크 스케줄링 | `09-disk-scheduling/` | FCFS, SSTF, SCAN, C-SCAN |
| 10 | 메모리 할당 | `10-memory-allocator/` | First/Best/Worst Fit, Buddy System |

## 사용법

```bash
# 각 디렉토리로 이동 후 README를 먼저 읽고, 코드를 완성하세요.
cd 01-process-thread/
cat README.md
python3 skeleton.py  # 스켈레톤 코드 실행
```

## 난이도

- 1~3: 기초 (필수)
- 4~6: 중급 (면접 빈출)
- 7~10: 심화 (깊이 있는 이해)
