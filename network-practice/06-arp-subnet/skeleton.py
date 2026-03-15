"""
실습 6: ARP 테이블 시뮬레이션 & 서브넷 계산기

TODO: 아래 빈칸을 채워주세요.
"""


# ============================================================
# Part A: 서브넷 계산기
# ============================================================
def ip_to_int(ip: str) -> int:
    """IP 주소 문자열을 32비트 정수로 변환합니다."""
    # 예: "192.168.1.0" → 3232235776
    parts = ip.split(".")
    return (int(parts[0]) << 24) | (int(parts[1]) << 16) | (int(parts[2]) << 8) | int(parts[3])


def int_to_ip(num: int) -> str:
    """32비트 정수를 IP 주소 문자열로 변환합니다."""
    return f"{(num >> 24) & 0xFF}.{(num >> 16) & 0xFF}.{(num >> 8) & 0xFF}.{num & 0xFF}"


def calc_subnet(cidr: str) -> dict:
    """
    CIDR 표기법으로 서브넷 정보를 계산합니다.

    예: "192.168.1.0/24"

    """
    ip_str, prefix_len = cidr.split("/")
    prefix_len = int(prefix_len)
    ip_int = ip_to_int(ip_str)

    # /24 → 11111111.11111111.11111111.00000000 → 0xFFFFFF00
    # 힌트: 상위 prefix_len 비트가 1, 나머지가 0
    subnet_mask = 0xFFFFFFFF << (32 - prefix_len) & 0xFFFFFFFF

    network_addr = ip_int & subnet_mask

    # 브로드캐스트 주소 = 네트워크 주소 OR (NOT 서브넷 마스크)
    broadcast_addr = network_addr | (~subnet_mask & 0xFFFFFFFF)

    # 사용 가능한 호스트 수 = 2^(32-prefix) - 2
    host_count = 2 ** (32-prefix_len) - 2

    # 첫 번째 호스트 = 네트워크 주소 + 1
    first_host = network_addr + 1
    # 마지막 호스트 = 브로드캐스트 주소 - 1
    last_host = broadcast_addr - 1

    return {
        "cidr": cidr,
        "subnet_mask": int_to_ip(subnet_mask),
        "network_addr": int_to_ip(network_addr),
        "broadcast_addr": int_to_ip(broadcast_addr),
        "first_host": int_to_ip(first_host),
        "last_host": int_to_ip(last_host),
        "host_count": host_count,
    }


def is_same_subnet(ip1: str, ip2: str, prefix_len: int) -> bool:
    """
    두 IP가 같은 서브넷에 있는지 판별합니다.

    """
    mask = (0xFFFFFFFF << (32 - prefix_len)) & 0xFFFFFFFF
    # TODO: 두 IP에 마스크를 적용하여 네트워크 주소가 같은지 비교
    return (ip_to_int(ip1) & mask) == (ip_to_int(ip2) & mask)


# ============================================================
# Part B: ARP 테이블 시뮬레이터
# ============================================================
class ARPSimulator:
    """가상 LAN의 ARP 과정을 시뮬레이션합니다."""

    def __init__(self):
        # 가상 호스트 목록: {IP: MAC}
        self.hosts = {
            "192.168.1.1":   "aa:bb:cc:00:00:01",  # 게이트웨이
            "192.168.1.100": "aa:bb:cc:00:00:64",  # Host A
            "192.168.1.101": "aa:bb:cc:00:00:65",  # Host B
            "192.168.1.102": "aa:bb:cc:00:00:66",  # Host C
        }
        # 각 호스트의 ARP 캐시
        self.arp_tables = {ip: {} for ip in self.hosts}

    def arp_request(self, sender_ip: str, target_ip: str):
        """
        ARP 요청/응답 시뮬레이션

        과정:
        1. sender가 브로드캐스트로 ARP Request 전송
           "Who has {target_ip}? Tell {sender_ip}"
        2. target이 유니캐스트로 ARP Reply 전송
           "{target_ip} is at {target_mac}"
        3. 양쪽 ARP 테이블 업데이트

        TODO 3: ARP 과정을 완성하세요.
        """
        print(f"\n[ARP Request] Who has {target_ip}? Tell {sender_ip}")
        print(f"  (브로드캐스트: FF:FF:FF:FF:FF:FF)")

        # 타겟이 존재하는지 확인
        if target_ip not in self.hosts:
            print(f"  [응답 없음] {target_ip}는 네트워크에 없습니다.")
            return

        sender_mac = self.hosts[sender_ip]
        target_mac = self.hosts[target_ip]

        print(f"[ARP Reply] {target_ip} is at {target_mac}")
        print(f"  (유니캐스트: {sender_mac})")

        # TODO: sender의 ARP 테이블에 target 정보 추가
        self.arp_tables[sender_ip][target_ip] = target_mac

        # TODO: target의 ARP 테이블에도 sender 정보 추가 (gratuitous)
        self.arp_tables[target_ip][sender_ip] = sender_mac

    def send_packet(self, src_ip: str, dst_ip: str, gateway_ip: str = "192.168.1.1"):
        """
        패킷 전송 시뮬레이션

        """
        print(f"\n{'='*50}")
        print(f"[패킷 전송] {src_ip} → {dst_ip}")

        # 같은 서브넷인지 확인
        same_net = is_same_subnet(src_ip, dst_ip, 24)

        if same_net:
            print(f"  → 같은 서브넷! 직접 전송")
            next_hop = dst_ip
        else:
            print(f"  → 다른 서브넷! 게이트웨이({gateway_ip})를 통해 전송")
            next_hop = gateway_ip

        # ARP 테이블에 next_hop의 MAC이 있는지 확인
        if next_hop in self.arp_tables.get(src_ip, {}):
            mac = self.arp_tables[src_ip][next_hop]
            print(f"  [ARP 캐시 HIT] {next_hop} → {mac}")
        else:
            print(f"  [ARP 캐시 MISS] ARP 요청 필요!")
            self.arp_request(src_ip, next_hop)

        # ARP 테이블 출력
        self.print_arp_table(src_ip)

    def print_arp_table(self, host_ip: str):
        """호스트의 ARP 테이블을 출력합니다."""
        print(f"\n  [{host_ip}의 ARP 테이블]")
        table = self.arp_tables.get(host_ip, {})
        if not table:
            print("    (비어있음)")
        for ip, mac in table.items():
            print(f"    {ip:20s} → {mac}")


# ============================================================
# 메인
# ============================================================
if __name__ == "__main__":
    # Part A: 서브넷 계산
    print("=" * 60)
    print("Part A: 서브넷 계산기")
    print("=" * 60)

    test_cidrs = ["192.168.1.0/24", "10.0.0.0/8", "172.16.0.0/20", "192.168.1.128/25"]

    for cidr in test_cidrs:
        info = calc_subnet(cidr)
        print(f"\n{cidr}:")
        print(f"  서브넷 마스크:     {info['subnet_mask']}")
        print(f"  네트워크 주소:     {info['network_addr']}")
        print(f"  브로드캐스트 주소: {info['broadcast_addr']}")
        print(f"  첫 번째 호스트:    {info['first_host']}")
        print(f"  마지막 호스트:     {info['last_host']}")
        print(f"  호스트 수:         {info['host_count']}")

    # 같은 서브넷 판별 테스트
    print(f"\n{'='*60}")
    tests = [
        ("192.168.1.100", "192.168.1.200", 24),
        ("192.168.1.100", "192.168.2.100", 24),
        ("192.168.1.100", "192.168.1.200", 25),
    ]
    for ip1, ip2, prefix in tests:
        result = is_same_subnet(ip1, ip2, prefix)
        print(f"  {ip1} & {ip2} (/{prefix}): {'같은 서브넷' if result else '다른 서브넷'}")

    # Part B: ARP 시뮬레이션
    print(f"\n{'='*60}")
    print("Part B: ARP 시뮬레이션")
    print("=" * 60)

    sim = ARPSimulator()

    # 같은 서브넷 내 통신
    sim.send_packet("192.168.1.100", "192.168.1.101")

    # 같은 호스트에게 다시 → 캐시 HIT
    sim.send_packet("192.168.1.100", "192.168.1.101")

    # 다른 서브넷으로 전송 → 게이트웨이 필요
    sim.send_packet("192.168.1.100", "8.8.8.8")
