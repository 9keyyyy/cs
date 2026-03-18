"""
실습 7: Reliable UDP - Stop-and-Wait ARQ

UDP 위에 ACK, Timeout, 재전송을 구현하여 신뢰성 있는 전송을 만듭니다.
인위적으로 패킷 손실을 시뮬레이션합니다.

"""

import socket
import struct
import random
import threading
import time

# 패킷 형식: [seq_num(4 bytes)][type(1 byte)][data]
# type: 0=DATA, 1=ACK
PACKET_DATA = 0
PACKET_ACK = 1

# 인위적 패킷 손실률 (0.0~1.0)
LOSS_RATE = 0.3
TIMEOUT = 2.0  # 초


def make_packet(seq_num: int, pkt_type: int, data: bytes = b"") -> bytes:
    """패킷을 구성합니다."""
    header = struct.pack("!IB", seq_num, pkt_type)
    return header + data


def parse_packet(packet: bytes) -> tuple:
    """패킷을 파싱합니다."""
    seq_num, pkt_type = struct.unpack("!IB", packet[:5])
    data = packet[5:]
    return seq_num, pkt_type, data


def simulate_loss() -> bool:
    """패킷 손실을 시뮬레이션합니다."""
    return random.random() < LOSS_RATE


# ============================================================
# Sender (Stop-and-Wait)
# ============================================================
def reliable_send(sock: socket.socket, addr: tuple, messages: list[str]):
    """
    Stop-and-Wait ARQ로 메시지를 전송합니다.

    알고리즘:
    1. 패킷 전송 (seq_num 포함)
    2. ACK 대기 (timeout 설정)
    3. ACK 수신 시 → 다음 패킷 전송
    4. Timeout 시 → 같은 패킷 재전송

    TODO: Stop-and-Wait 알고리즘을 완성하세요.
    """
    seq_num = 0

    for msg in messages:
        data = msg.encode("utf-8")
        packet = make_packet(seq_num, PACKET_DATA, data)
        acked = False
        retries = 0

        while not acked:
            # TODO 1: 패킷을 전송하세요. (손실 시뮬레이션 포함)
            if simulate_loss():
                print(f"  [Sender] 패킷 #{seq_num} 전송 → [손실됨!]")
            else:
                print(f"  [Sender] 패킷 #{seq_num} 전송: '{msg}'")
                sock.sendto(packet, addr)

            # TODO 2: ACK를 기다리세요. (timeout 설정)
            sock.settimeout(TIMEOUT)

            try:
                # TODO 3: ACK를 수신하고 파싱하세요.
                ack_packet, _ = sock.recvfrom(1024)
                ack_seq, ack_type, _ = parse_packet(ack_packet)

                # TODO 4: 올바른 ACK인지 확인하세요.
                # (type이 ACK이고, seq_num이 현재 전송한 것과 일치)
                if ack_type == PACKET_ACK and ack_seq == seq_num:
                    print(f"  [Sender] ACK #{ack_seq} 수신 ✓")
                    acked = True
                    # TODO 5: 다음 패킷을 위해 seq_num을 증가시키세요.
                    seq_num += 1
                else:
                    print(f"  [Sender] 잘못된 ACK (expected={seq_num}, got={ack_seq})")

            except socket.timeout:
                retries += 1
                print(f"  [Sender] Timeout! 재전송 (시도 #{retries})")

    # 종료 신호
    fin = make_packet(seq_num, PACKET_DATA, b"__FIN__")
    sock.sendto(fin, addr)
    print(f"\n  [Sender] 전송 완료! (총 {seq_num}개 메시지)")


# ============================================================
# Receiver (Stop-and-Wait)
# ============================================================
def reliable_receive(sock: socket.socket) -> list[str]:
    """
    Stop-and-Wait ARQ 수신자

    알고리즘:
    1. 패킷 수신
    2. seq_num 확인 → 기대하는 번호면 ACK 전송, 아니면 이전 ACK 재전송
    3. 중복 패킷은 무시

    TODO: 수신 로직을 완성하세요.
    """
    expected_seq = 0
    received = []

    while True:
        data, sender_addr = sock.recvfrom(1024)
        seq_num, pkt_type, payload = parse_packet(data)

        # FIN은 손실 시뮬레이션 없이 즉시 처리
        if payload == b"__FIN__":
            print(f"  [Receiver] FIN 수신, 종료")
            break

        # 패킷 손실 시뮬레이션 (수신 측)
        if simulate_loss():
            print(f"  [Receiver] 패킷 수신 → [손실됨!]")
            continue

        print(f"  [Receiver] 패킷 #{seq_num} 수신 (expected={expected_seq})")

        # TODO 6: 기대하는 seq_num인지 확인하세요.
        if seq_num == expected_seq:
            msg = payload.decode("utf-8")
            received.append(msg)
            print(f"  [Receiver] 데이터 수락: '{msg}'")

            # TODO 7: ACK를 전송하세요.
            ack = make_packet(seq_num, PACKET_ACK)
            if not simulate_loss():
                sock.sendto(ack, sender_addr)
                print(f"  [Receiver] ACK #{seq_num} 전송")
            else:
                print(f"  [Receiver] ACK #{seq_num} → [손실됨!]")

            # TODO 8: 다음 기대 seq_num을 증가
            expected_seq += 1
        else:
            # 중복 패킷 → 이전 ACK 재전송
            print(f"  [Receiver] 중복 패킷! 이전 ACK 재전송")
            ack = make_packet(expected_seq - 1, PACKET_ACK)
            sock.sendto(ack, sender_addr)

    return received


# ============================================================
# 메인: 테스트
# ============================================================
if __name__ == "__main__":
    HOST = "127.0.0.1"
    SENDER_PORT = 10000
    RECEIVER_PORT = 10001

    messages = [
        "Hello",
        "Network",
        "is",
        "fun!",
        "TCP는 이런 걸 자동으로 해줍니다",
    ]

    print("=" * 60)
    print(f"Stop-and-Wait ARQ 시뮬레이션 (손실률: {LOSS_RATE*100}%)")
    print("=" * 60)

    sender_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sender_sock.bind((HOST, SENDER_PORT))

    receiver_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    receiver_sock.bind((HOST, RECEIVER_PORT))

    # Receiver를 별도 스레드에서 실행
    result = []

    def receiver_thread():
        r = reliable_receive(receiver_sock)
        result.extend(r)

    t = threading.Thread(target=receiver_thread)
    t.start()

    time.sleep(0.1)
    reliable_send(sender_sock, (HOST, RECEIVER_PORT), messages)

    t.join(timeout=30)

    print(f"\n{'='*60}")
    print(f"전송한 메시지: {messages}")
    print(f"수신한 메시지: {result}")
    print(f"일치 여부: {messages == result}")

    sender_sock.close()
    receiver_sock.close()
