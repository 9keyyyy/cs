"""
sample.pcap 생성기

TCP 3-way handshake를 시뮬레이션하는 pcap 파일을 생성합니다.
이 파일을 실행한 후 skeleton.py로 분석하세요.
"""

import struct
import time


def mac_to_bytes(mac: str) -> bytes:
    return bytes(int(b, 16) for b in mac.split(":"))


def ip_to_bytes(ip: str) -> bytes:
    return bytes(int(b) for b in ip.split("."))


def checksum(data: bytes) -> int:
    if len(data) % 2:
        data += b"\x00"
    s = sum(struct.unpack("!%dH" % (len(data) // 2), data))
    while s >> 16:
        s = (s & 0xFFFF) + (s >> 16)
    return ~s & 0xFFFF


def build_tcp_packet(src_mac, dst_mac, src_ip, dst_ip, src_port, dst_port,
                     seq, ack, flags, payload=b""):
    """Ethernet + IP + TCP 패킷을 구성합니다."""
    # TCP Header
    tcp_offset = 5  # 20 bytes, no options
    tcp_flags = 0
    if "SYN" in flags: tcp_flags |= 0x02
    if "ACK" in flags: tcp_flags |= 0x10
    if "FIN" in flags: tcp_flags |= 0x01
    if "PSH" in flags: tcp_flags |= 0x08

    tcp_header = struct.pack("!HHIIBBHHH",
        src_port, dst_port,
        seq, ack,
        (tcp_offset << 4), tcp_flags,
        65535,  # window
        0,      # checksum (simplified)
        0       # urgent pointer
    )
    tcp_segment = tcp_header + payload

    # IP Header
    ip_total_len = 20 + len(tcp_segment)
    ip_header = struct.pack("!BBHHHBBH4s4s",
        0x45,       # version=4, IHL=5
        0,          # TOS
        ip_total_len,
        1234,       # identification
        0,          # flags + fragment offset
        64,         # TTL
        6,          # protocol = TCP
        0,          # checksum (simplified)
        ip_to_bytes(src_ip),
        ip_to_bytes(dst_ip),
    )

    # Ethernet Header
    eth_header = struct.pack("!6s6sH",
        mac_to_bytes(dst_mac),
        mac_to_bytes(src_mac),
        0x0800,  # IPv4
    )

    return eth_header + ip_header + tcp_segment


def write_pcap(filename, packets):
    """pcap 파일을 작성합니다."""
    with open(filename, "wb") as f:
        # Global Header
        f.write(struct.pack("<IHHiIII",
            0xA1B2C3D4,  # magic
            2, 4,         # version
            0,            # timezone
            0,            # sigfigs
            65535,        # snaplen
            1,            # link type (Ethernet)
        ))

        ts = int(time.time())
        for i, pkt in enumerate(packets):
            # Packet Header
            f.write(struct.pack("<IIII",
                ts, i * 100000,  # timestamp
                len(pkt),        # captured length
                len(pkt),        # original length
            ))
            f.write(pkt)


if __name__ == "__main__":
    src_mac = "aa:bb:cc:dd:ee:01"
    dst_mac = "aa:bb:cc:dd:ee:02"
    client_ip = "192.168.1.100"
    server_ip = "93.184.216.34"
    client_port = 54321
    server_port = 80

    packets = [
        # 1. SYN (Client → Server): 3-way handshake 시작
        build_tcp_packet(src_mac, dst_mac, client_ip, server_ip,
                         client_port, server_port, seq=1000, ack=0, flags=["SYN"]),

        # 2. SYN-ACK (Server → Client)
        build_tcp_packet(dst_mac, src_mac, server_ip, client_ip,
                         server_port, client_port, seq=5000, ack=1001, flags=["SYN", "ACK"]),

        # 3. ACK (Client → Server): 3-way handshake 완료
        build_tcp_packet(src_mac, dst_mac, client_ip, server_ip,
                         client_port, server_port, seq=1001, ack=5001, flags=["ACK"]),

        # 4. HTTP GET (Client → Server)
        build_tcp_packet(src_mac, dst_mac, client_ip, server_ip,
                         client_port, server_port, seq=1001, ack=5001,
                         flags=["ACK", "PSH"],
                         payload=b"GET /index.html HTTP/1.1\r\nHost: example.com\r\n\r\n"),

        # 5. HTTP Response (Server → Client)
        build_tcp_packet(dst_mac, src_mac, server_ip, client_ip,
                         server_port, client_port, seq=5001, ack=1060,
                         flags=["ACK", "PSH"],
                         payload=b"HTTP/1.1 200 OK\r\nContent-Length: 5\r\n\r\nHello"),

        # 6. FIN (Client → Server): 연결 종료 시작
        build_tcp_packet(src_mac, dst_mac, client_ip, server_ip,
                         client_port, server_port, seq=1060, ack=5050, flags=["FIN", "ACK"]),
    ]

    write_pcap("sample.pcap", packets)
    print("sample.pcap 생성 완료! (6개 패킷: SYN → SYN-ACK → ACK → HTTP GET → HTTP 200 → FIN)")
    print("이제 skeleton.py를 실행하세요: python3 skeleton.py")
