# Network Practice - CS 면접 대비 실습

네트워크 핵심 개념을 직접 코드로 구현하며 체감하는 실습 과제 모음입니다.

## 실습 구조

| # | 주제 | 디렉토리 | 핵심 면접 키워드 |
|---|------|----------|-----------------|
| 1 | TCP vs UDP | `01-tcp-udp/` | 3-way handshake, 신뢰성, 순서 보장 |
| 2 | HTTP/1.1 직접 구현 | `02-http-server/` | Request/Response, Status Code, Header |
| 3 | DNS Resolver | `03-dns-resolver/` | 재귀/반복 질의, 캐싱, TTL |
| 4 | 패킷 분석 (Raw Socket) | `04-packet-sniffer/` | OSI 7계층, 캡슐화/역캡슐화 |
| 5 | TCP 혼잡 제어 시뮬레이션 | `05-congestion-control/` | Slow Start, AIMD, cwnd |
| 6 | ARP 테이블 & 서브넷 계산기 | `06-arp-subnet/` | ARP, 서브넷 마스크, CIDR |
| 7 | Reliable UDP (Stop-and-Wait) | `07-reliable-udp/` | ARQ, ACK, Timeout, 재전송 |
| 8 | 프록시 서버 | `08-proxy-server/` | Forward/Reverse Proxy, 캐싱 |
| 9 | 멀티플렉싱 채팅 (select/epoll) | `09-multiplexing-chat/` | I/O 멀티플렉싱, Blocking vs Non-blocking |
| 10 | TLS Handshake 시뮬레이션 | `10-tls-handshake/` | 대칭키/비대칭키, 인증서, HTTPS |

## 사용법

```bash
# 각 디렉토리로 이동 후 README를 먼저 읽고, 코드를 완성하세요.
cd 01-tcp-udp/
cat README.md
python3 skeleton.py  # 스켈레톤 코드 실행
```

## 난이도

- 1~3: 기초 (필수)
- 4~6: 중급 (면접 빈출)
- 7~10: 심화 (깊이 있는 이해)
