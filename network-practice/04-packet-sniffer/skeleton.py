"""
실습 4: 패킷 파서 - OSI 계층별 헤더 분석

pcap 파일을 직접 파싱하여 각 계층의 헤더 구조를 이해합니다.
외부 라이브러리 없이 struct만 사용합니다.

먼저 generate_pcap.py를 실행하여 sample.pcap을 생성하세요.

"""

import struct


# ============================================================
# Ethernet 헤더 파싱 (14 bytes)
# ============================================================
def parse_ethernet(data: bytes) -> dict:
    """
    Ethernet Frame Header:
    +-------------------+-------------------+-----------+
    |  Dst MAC (6bytes) |  Src MAC (6bytes) | Type (2)  |
    +-------------------+-------------------+-----------+

    EtherType: 0x0800 = IPv4, 0x0806 = ARP, 0x86DD = IPv6

    """
    # 힌트: struct.unpack("!6s6sH", data[:14])
    # 6s = 6바이트 문자열 (MAC 주소)
    # H = unsigned short (EtherType)
    dst_mac, src_mac, ethertype = struct.unpack("!6s6sH", data[:14])

    return {
        "dst_mac": ":".join(f"{b:02x}" for b in dst_mac),
        "src_mac": ":".join(f"{b:02x}" for b in src_mac),
        "ethertype": ethertype,
        "ethertype_name": {0x0800: "IPv4", 0x0806: "ARP", 0x86DD: "IPv6"}.get(ethertype, "Unknown"),
        "payload": data[14:],
    }


# ============================================================
# IP 헤더 파싱 (최소 20 bytes)
# ============================================================
def parse_ip(data: bytes) -> dict:
    """
    IPv4 Header (20 bytes, 옵션 없을 때):
    +------+------+------------+-------------------+
    |VER+IHL| TOS | Total Len  |   Identification  |
    +------+------+-----+------+-------------------+
    | Flags+Frag Offset |  TTL | Protocol| Checksum|
    +-------------------+------+---------+---------+
    |            Source IP Address                  |
    +-----------------------------------------------+
    |         Destination IP Address                |
    +-----------------------------------------------+

    Protocol: 6 = TCP, 17 = UDP, 1 = ICMP

    """
    # 첫 바이트에서 version(상위 4비트)과 IHL(하위 4비트) 추출
    version_ihl = data[0]
    version = version_ihl >> 4
    ihl = (version_ihl & 0x0F) * 4  # IHL은 4바이트 단위

    # TTL은 offset 8, Protocol은 offset 9
    ttl = data[8]
    protocol = data[9]

    # Source IP: offset 12~15, Dest IP: offset 16~19
    # struct.unpack("!4s4s", data[12:20])으로 4바이트씩 추출
    src_ip_bytes, dst_ip_bytes = struct.unpack("!4s4s", data[12:20])
    src_ip = ".".join(str(b) for b in src_ip_bytes)
    dst_ip = ".".join(str(b) for b in dst_ip_bytes)

    protocol_names = {1: "ICMP", 6: "TCP", 17: "UDP"}

    return {
        "version": version,
        "header_length": ihl,
        "ttl": ttl,
        "protocol": protocol,
        "protocol_name": protocol_names.get(protocol, "Unknown"),
        "src_ip": src_ip,
        "dst_ip": dst_ip,
        "payload": data[ihl:],
    }


# ============================================================
# TCP 헤더 파싱 (최소 20 bytes)
# ============================================================
def parse_tcp(data: bytes) -> dict:
    """
    TCP Header (20 bytes, 옵션 없을 때):
    +------------------+------------------+
    |  Src Port (2)    |  Dst Port (2)    |
    +------------------+------------------+
    |         Sequence Number (4)         |
    +-------------------------------------+
    |      Acknowledgment Number (4)      |
    +------+--------+----+----------------+
    |Offset|Reserved|Flags|  Window (2)   |
    +------+--------+----+----------------+

    Flags: FIN=0x01, SYN=0x02, RST=0x04, PSH=0x08, ACK=0x10

    """
    # 각각 2바이트, unsigned short
    src_port, dst_port = struct.unpack("!HH", data[:4])

    # 각각 4바이트, unsigned int)
    seq_num, ack_num = struct.unpack("!II", data[4:12])

    # Data offset(상위 4비트)과 Flags
    data_offset = (data[12] >> 4) * 4
    flags = data[13]

    flag_names = []
    if flags & 0x02:  # SYN
        flag_names.append("SYN")
    if flags & 0x10:  # ACK
        flag_names.append("ACK")
    if flags & 0x01:  # FIN
        flag_names.append("FIN")
    if flags & 0x04:  # RST
        flag_names.append("RST")
    if flags & 0x08:  # PSH
        flag_names.append("PSH")

    return {
        "src_port": src_port,
        "dst_port": dst_port,
        "seq_num": seq_num,
        "ack_num": ack_num,
        "flags": flag_names,
        "payload": data[data_offset:],
    }


# ============================================================
# PCAP 파일 파서
# ============================================================
def read_pcap(filename: str):
    """
    pcap 파일 구조:
    - Global Header (24 bytes)
    - [Packet Header (16 bytes) + Packet Data] × N

    """
    packets = []

    with open(filename, "rb") as f:
        # Global Header (24 bytes) 건너뛰기
        global_header = f.read(24)
        magic = struct.unpack("<I", global_header[:4])[0]
        if magic != 0xA1B2C3D4:
            print("유효하지 않은 pcap 파일입니다.")
            return packets

        while True:
            # Packet Header (16 bytes)
            pkt_header = f.read(16)
            if len(pkt_header) < 16:
                break

            ts_sec, ts_usec, incl_len, orig_len = struct.unpack("<IIII", pkt_header)

            # Packet Data
            pkt_data = f.read(incl_len)
            if len(pkt_data) < incl_len:
                break

            packets.append(pkt_data)

    return packets


# ============================================================
# 메인: 패킷 분석
# ============================================================
def analyze_packet(pkt_data: bytes, pkt_num: int):
    """패킷을 계층별로 파싱하여 출력합니다."""
    print(f"\n{'='*60}")
    print(f"패킷 #{pkt_num} ({len(pkt_data)} bytes)")
    print(f"{'='*60}")

    # Layer 2: Ethernet
    eth = parse_ethernet(pkt_data)
    print(f"[L2 Ethernet] {eth['src_mac']} → {eth['dst_mac']} | Type: {eth['ethertype_name']}")

    if eth["ethertype"] != 0x0800:
        print("  (IPv4가 아니므로 이후 파싱 생략)")
        return

    # Layer 3: IP
    ip = parse_ip(eth["payload"])
    print(f"[L3 IP]       {ip['src_ip']} → {ip['dst_ip']} | Proto: {ip['protocol_name']} | TTL: {ip['ttl']}")

    if ip["protocol"] != 6:
        print("  (TCP가 아니므로 이후 파싱 생략)")
        return

    # Layer 4: TCP
    tcp = parse_tcp(ip["payload"])
    print(f"[L4 TCP]      :{tcp['src_port']} → :{tcp['dst_port']} | Seq: {tcp['seq_num']} | Ack: {tcp['ack_num']} | Flags: {tcp['flags']}")

    # Layer 7: Application Data
    if tcp["payload"]:
        try:
            app_data = tcp["payload"].decode("utf-8", errors="replace")[:100]
            print(f"[L7 App Data] {app_data}")
        except Exception:
            print(f"[L7 App Data] ({len(tcp['payload'])} bytes, binary)")


if __name__ == "__main__":
    import os

    pcap_file = os.path.join(os.path.dirname(__file__), "sample.pcap")

    if not os.path.exists(pcap_file):
        print("sample.pcap이 없습니다. 먼저 generate_pcap.py를 실행하세요.")
        print("  python3 generate_pcap.py")
    else:
        packets = read_pcap(pcap_file)
        print(f"총 {len(packets)}개 패킷 로드됨")

        for i, pkt in enumerate(packets, 1):
            analyze_packet(pkt, i)
