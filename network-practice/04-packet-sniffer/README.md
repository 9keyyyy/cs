# 실습 4: 패킷 분석 - OSI 7계층 체감하기

## 면접 키워드
- OSI 7계층 vs TCP/IP 4계층
- 캡슐화(Encapsulation) / 역캡슐화(Decapsulation)
- Ethernet Frame → IP Packet → TCP Segment → Application Data

## 과제

scapy 없이 Python struct로 패킷을 직접 파싱하여 각 계층의 헤더를 출력합니다.
(macOS에서는 raw socket 권한이 필요하므로, pcap 파일을 파싱하는 방식으로 진행합니다.)

### 요구사항
1. `sample.pcap` 파일의 패킷을 읽어서 파싱
2. Ethernet 헤더: src MAC, dst MAC, EtherType
3. IP 헤더: src IP, dst IP, Protocol, TTL
4. TCP 헤더: src port, dst port, flags (SYN/ACK/FIN)

## 면접 예상 질문

### Q. OSI 7계층을 설명하세요.

OSI(Open Systems Interconnection) 모델은 네트워크 통신을 7개의 계층으로 분리한 참조 모델입니다.

| 계층 | 이름 | 역할 | 프로토콜/장비 예시 |
|------|------|------|-------------------|
| 7 | 응용(Application) | 사용자와 직접 상호작용하는 서비스 제공 | HTTP, FTP, DNS, SMTP |
| 6 | 표현(Presentation) | 데이터 형식 변환, 암호화, 압축 | SSL/TLS, JPEG, ASCII |
| 5 | 세션(Session) | 연결 수립·유지·종료 관리 | NetBIOS, RPC |
| 4 | 전송(Transport) | 종단 간 신뢰성 있는 데이터 전송 | TCP, UDP |
| 3 | 네트워크(Network) | 논리적 주소(IP) 기반 라우팅 | IP, ICMP, 라우터 |
| 2 | 데이터링크(Data Link) | 물리적 주소(MAC) 기반 프레임 전송 | Ethernet, Wi-Fi, 스위치 |
| 1 | 물리(Physical) | 전기 신호, 비트 전송 | 케이블, 허브, NIC |

계층을 나누는 이유는 **각 계층이 독립적으로 동작하여 한 계층의 변경이 다른 계층에 영향을 주지 않기 때문**입니다. 예를 들어, 이더넷에서 Wi-Fi로 바꿔도 상위 계층은 변경할 필요가 없습니다.

### Q. TCP/IP 4계층과 OSI 7계층의 차이는?

TCP/IP 모델은 실제 인터넷에서 사용되는 프로토콜 스택을 기반으로 한 **실용적인 모델**이고, OSI는 이론적인 **참조 모델**입니다.

| OSI 7계층 | TCP/IP 4계층 | 비고 |
|-----------|-------------|------|
| 응용·표현·세션 (5~7) | 응용(Application) | OSI 상위 3개를 하나로 통합 |
| 전송 (4) | 전송(Transport) | 동일 (TCP, UDP) |
| 네트워크 (3) | 인터넷(Internet) | 동일 (IP) |
| 데이터링크·물리 (1~2) | 네트워크 액세스(Network Access) | OSI 하위 2개를 하나로 통합 |

- OSI는 **프로토콜 독립적**인 범용 모델, TCP/IP는 **특정 프로토콜에 기반**한 모델
- 실무에서는 TCP/IP 4계층이 더 많이 사용되지만, 면접에서는 OSI 7계층으로 설명하는 것이 일반적

### Q. 캡슐화란 무엇인가요?

캡슐화(Encapsulation)는 **상위 계층의 데이터에 현재 계층의 헤더(와 트레일러)를 붙여 하위 계층으로 전달하는 과정**입니다. 역캡슐화(Decapsulation)는 수신 측에서 각 계층의 헤더를 제거하며 상위로 올리는 반대 과정입니다.

```
[Application Data]
         ↓ 캡슐화
[TCP Header | Application Data]              → 세그먼트(Segment)
         ↓ 캡슐화
[IP Header | TCP Header | App Data]          → 패킷(Packet)
         ↓ 캡슐화
[Eth Header | IP Header | TCP | App | Eth Trailer] → 프레임(Frame)
```

각 계층의 데이터 단위(PDU)가 다르게 불리는 이유가 바로 이 캡슐화 때문입니다:
- **4계층**: 세그먼트(TCP) / 데이터그램(UDP)
- **3계층**: 패킷
- **2계층**: 프레임

### Q. 패킷이 목적지까지 전달되는 과정을 계층별로 설명하세요.

클라이언트가 `http://example.com`에 요청을 보내는 경우를 예로 들면:

**송신 측 (캡슐화)**:
1. **응용 계층**: HTTP GET 요청 메시지 생성
2. **전송 계층**: TCP 헤더 추가 (출발지/목적지 포트, 시퀀스 번호) → 세그먼트
3. **네트워크 계층**: IP 헤더 추가 (출발지/목적지 IP, TTL) → 패킷
4. **데이터링크 계층**: Ethernet 헤더 추가 (출발지/목적지 MAC) → 프레임
5. **물리 계층**: 프레임을 전기 신호/광 신호로 변환하여 전송

**네트워크 경유**:
- **라우터(L3)**: IP 헤더를 확인하여 다음 홉(next hop) 결정, TTL 감소, MAC 주소 교체
- **스위치(L2)**: MAC 주소를 확인하여 해당 포트로 프레임 전달

**수신 측 (역캡슐화)**:
1. **물리 → 데이터링크**: 신호를 프레임으로 복원, MAC 확인 후 Ethernet 헤더 제거
2. **데이터링크 → 네트워크**: IP 헤더 확인, 목적지 IP 일치 확인 후 제거
3. **네트워크 → 전송**: TCP 헤더 확인, 포트 번호로 소켓 식별 후 제거
4. **전송 → 응용**: HTTP 데이터를 웹 서버 애플리케이션에 전달

### Q. TTL(Time To Live)의 역할은?

IP 헤더의 TTL 필드는 **패킷이 네트워크에서 무한히 순환하는 것을 방지하는 메커니즘**입니다.

- 패킷이 **라우터를 거칠 때마다(hop) TTL이 1씩 감소**합니다.
- TTL이 **0이 되면 라우터가 해당 패킷을 폐기**하고, 송신자에게 ICMP "Time Exceeded" 메시지를 보냅니다.
- 라우팅 설정 오류로 패킷이 루프를 돌더라도, TTL 덕분에 영원히 떠돌지 않습니다.

**활용 예시**:
- **traceroute**: TTL을 1부터 순차적으로 증가시키며 각 홉의 라우터에서 ICMP Time Exceeded 응답을 받아 경로를 추적
- 일반적인 초기 TTL 값: Linux=64, Windows=128, 일부 네트워크 장비=255

> DNS의 TTL(캐시 유효 시간)과 IP의 TTL(홉 제한)은 이름은 같지만 역할이 다릅니다.
