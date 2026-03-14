"""
실습 3: DNS Resolver 직접 구현

DNS 프로토콜 메시지를 직접 구성하고 UDP로 DNS 서버에 질의합니다.
외부 라이브러리 없이 struct + socket만 사용합니다.

TODO: 아래 빈칸을 채워주세요.
"""

import socket
import struct
import time
import random


# ============================================================
# DNS 캐시
# ============================================================
dns_cache = {}  # { "example.com": {"ip": "93.184.216.34", "ttl": 300, "cached_at": time.time()} }


def cache_lookup(domain: str) -> str | None:
    """
    캐시에서 도메인을 조회합니다.
    TTL이 만료되었으면 캐시에서 제거하고 None을 반환합니다.

    TODO: TTL 기반 캐시 조회를 구현하세요.
    """
    if domain in dns_cache:
        entry = dns_cache[domain]
        elapsed = time.time() - entry["cached_at"]

        # TODO 1: TTL이 아직 유효한지 확인하세요.
        if elapsed < entry["ttl"]:
            print(f"  [캐시 HIT] {domain} → {entry['ip']} (남은 TTL: {int(entry['ttl'] - elapsed)}초)")
            return entry["ip"]
        else:
            # TODO 2: 만료된 엔트리를 삭제하세요.
            print(f"  [캐시 EXPIRED] {domain}")
            del dns_cache[domain]

    print(f"  [캐시 MISS] {domain}")
    return None


def cache_store(domain: str, ip: str, ttl: int):
    """캐시에 DNS 레코드를 저장합니다."""
    dns_cache[domain] = {
        "ip": ip,
        "ttl": ttl,
        "cached_at": time.time(),
    }
    print(f"  [캐시 STORE] {domain} → {ip} (TTL: {ttl}초)")


# ============================================================
# DNS 메시지 구성
# ============================================================
def build_dns_query(domain: str) -> bytes:
    """
    DNS 질의 메시지를 직접 구성합니다.

    DNS 메시지 구조:
    +---------------------+
    |       Header        |  12 bytes
    +---------------------+
    |      Question       |  가변 길이
    +---------------------+

    Header (12 bytes):
    - Transaction ID (2 bytes): 임의의 식별자
    - Flags (2 bytes): 표준 질의 = 0x0100
    - Questions (2 bytes): 질의 수 = 1
    - Answer RRs (2 bytes): 0
    - Authority RRs (2 bytes): 0
    - Additional RRs (2 bytes): 0
    """
    # TODO 3: Transaction ID를 랜덤으로 생성하세요. (0~65535)
    transaction_id = random.randint(0, 65535)

    # TODO 4: DNS Header를 struct.pack으로 구성하세요.
    # 형식: !HHHHHH (네트워크 바이트 오더, unsigned short 6개)
    # 값: transaction_id, 0x0100(표준질의), 1(질문1개), 0, 0, 0
    header = struct.pack("!HHHHHH", transaction_id, 0x0100, 1, 0, 0, 0)

    # TODO 5: Question 섹션을 구성하세요.
    # 도메인 "www.example.com"을 DNS 형식으로 인코딩:
    # → \x03www\x07example\x03com\x00
    # 각 레이블 앞에 길이 바이트를 붙이고, 마지막에 \x00
    question = b""
    for label in domain.split("."):
        question += bytes([len(label)]) + label.encode("ascii")
    question += b"\x00"

    # QTYPE=A(1), QCLASS=IN(1)
    question += struct.pack("!HH", 1, 1)

    return header + question


def parse_dns_response(response: bytes) -> tuple[str, int]:
    """
    DNS 응답에서 IP 주소와 TTL을 추출합니다.

    TODO 6: 응답을 파싱하세요. (간략화된 버전)
    실제 DNS 파싱은 더 복잡하지만, 기본 구조를 이해하는 것이 목표입니다.
    """
    # Header에서 Answer 수 확인 (offset 6-7)
    answer_count = struct.unpack("!H", response[6:8])[0]

    if answer_count == 0:
        return ("", 0)

    # Question 섹션 건너뛰기
    offset = 12
    while response[offset] != 0:
        offset += response[offset] + 1
    offset += 5  # null byte + QTYPE(2) + QCLASS(2)

    # Answer 섹션 파싱
    # Name (보통 포인터 0xC0XX로 2바이트)
    if response[offset] & 0xC0 == 0xC0:
        offset += 2
    else:
        while response[offset] != 0:
            offset += response[offset] + 1
        offset += 1

    # TYPE(2) + CLASS(2) + TTL(4) + RDLENGTH(2)
    rtype, rclass, ttl, rdlength = struct.unpack("!HHIH", response[offset:offset + 10])
    offset += 10

    # A 레코드(TYPE=1)이면 IPv4 주소 추출
    if rtype == 1 and rdlength == 4:
        ip = ".".join(str(b) for b in response[offset:offset + 4])
        return (ip, ttl)

    return ("", 0)


# ============================================================
# DNS 질의 실행
# ============================================================
def resolve(domain: str, dns_server: str = "8.8.8.8") -> str:
    """
    도메인을 IP 주소로 변환합니다.
    1. 캐시 확인
    2. 캐시 미스 시 DNS 서버에 질의
    3. 결과를 캐시에 저장
    """
    print(f"\n[DNS 질의] {domain}")

    # 캐시 확인
    cached = cache_lookup(domain)
    if cached:
        return cached

    # TODO 7: DNS 질의를 UDP로 보내고 응답을 받으세요.
    query = build_dns_query(domain)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(5.0)

    # DNS는 포트 53을 사용합니다.
    sock.sendto(query, (dns_server, 53))
    response, _ = sock.recvfrom(512)
    sock.close()

    # 응답 파싱
    ip, ttl = parse_dns_response(response)

    if ip:
        cache_store(domain, ip, ttl)
        return ip
    else:
        print(f"  [ERROR] {domain} 질의 실패")
        return ""


# ============================================================
# 메인
# ============================================================
if __name__ == "__main__":
    domains = [
        "www.google.com",
        "www.naver.com",
        "www.github.com",
        "www.google.com",   # 두 번째 질의 → 캐시 HIT 예상
        "www.naver.com",    # 두 번째 질의 → 캐시 HIT 예상
    ]

    for domain in domains:
        ip = resolve(domain)
        if ip:
            print(f"  → {domain} = {ip}")

    print(f"\n[캐시 상태] {len(dns_cache)}개 엔트리")
    for domain, entry in dns_cache.items():
        remaining = int(entry["ttl"] - (time.time() - entry["cached_at"]))
        print(f"  {domain}: {entry['ip']} (남은 TTL: {remaining}초)")
