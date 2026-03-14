"""
실험: TCP vs UDP로 10KB 데이터 전송 비교

서버/클라이언트를 하나의 스크립트에서 자동으로 실행합니다.
"""

import socket
import threading
import time

DATA_SIZE = 10 * 1024  # 10KB
HOST = "127.0.0.1"
TCP_PORT = 9100
UDP_PORT = 9101


# ============================================================
# TCP 10KB 전송 테스트
# ============================================================
def test_tcp():
    print("=" * 60)
    print("[TCP] 10KB 전송 테스트")
    print("=" * 60)

    original = b"A" * DATA_SIZE
    received_chunks = []

    def tcp_server():
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, TCP_PORT))
        server.listen(1)

        client_sock, addr = server.accept()
        while True:
            chunk = client_sock.recv(1024)
            if not chunk:
                break
            received_chunks.append(chunk)

        client_sock.close()
        server.close()

    # 서버 시작
    t = threading.Thread(target=tcp_server)
    t.start()
    time.sleep(0.1)

    # 클라이언트: 10KB 전송
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, TCP_PORT))
    sock.sendall(original)
    sock.close()

    t.join()

    # 결과
    received = b"".join(received_chunks)
    print(f"  전송 크기:       {len(original):,} bytes")
    print(f"  수신 크기:       {len(received):,} bytes")
    print(f"  recv() 호출 횟수: {len(received_chunks)}번")
    print(f"  각 chunk 크기:   {[len(c) for c in received_chunks]}")
    print(f"  데이터 일치:     {original == received}")
    print()


# ============================================================
# UDP 10KB 전송 테스트
# ============================================================
def test_udp():
    print("=" * 60)
    print("[UDP] 10KB 전송 테스트")
    print("=" * 60)

    original = b"B" * DATA_SIZE
    received_data = [None]

    def udp_server():
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, UDP_PORT))
        server.settimeout(3.0)

        try:
            data, addr = server.recvfrom(65535)  # 최대 크기로 수신
            received_data[0] = data
        except socket.timeout:
            received_data[0] = b""

        server.close()

    # 서버 시작
    t = threading.Thread(target=udp_server)
    t.start()
    time.sleep(0.1)

    # 클라이언트: 10KB를 한 번에 전송 시도
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.sendto(original, (HOST, UDP_PORT))
        sock.close()
        t.join()

        received = received_data[0]
        print(f"  전송 크기: {len(original):,} bytes")
        print(f"  수신 크기: {len(received):,} bytes")
        print(f"  데이터 일치: {original == received}")
    except OSError as e:
        print(f"  sendto() 에러: {e}")
        print(f"  → UDP는 한 데이터그램이 너무 크면 전송 자체가 거부됩니다!")
        print(f"  → macOS/Linux 루프백 MTU 초과 시 'Message too long' 발생")
        sock.close()
        # 서버 타임아웃 대기
        t.join()
    print()

    # 실험 2: 작은 크기(1KB)로 보내고, recvfrom(512)로 받으면?
    print("-" * 40)
    print("[UDP] 1KB 전송 → recvfrom(512)로 수신하면?")
    print("-" * 40)

    small_original = b"C" * 1024  # 1KB
    truncated_data = [None]

    def udp_server_small_buf():
        server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((HOST, UDP_PORT + 1))
        server.settimeout(3.0)

        try:
            data, addr = server.recvfrom(512)  # 작은 버퍼!
            truncated_data[0] = data
        except socket.timeout:
            truncated_data[0] = b""

        server.close()

    t = threading.Thread(target=udp_server_small_buf)
    t.start()
    time.sleep(0.1)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(small_original, (HOST, UDP_PORT + 1))
    sock.close()

    t.join()

    truncated = truncated_data[0]
    print(f"  전송 크기: {len(small_original):,} bytes")
    print(f"  수신 크기: {len(truncated):,} bytes")
    print(f"  잘린 크기: {len(small_original) - len(truncated):,} bytes 유실!")
    print(f"  데이터 일치: {small_original == truncated}")
    print(f"  → UDP는 버퍼보다 큰 데이터그램은 잘리고, 나머지는 영구 유실!")
    print()


# ============================================================
# 실행
# ============================================================
if __name__ == "__main__":
    test_tcp()
    test_udp()

    print("=" * 60)
    print("결론:")
    print("  TCP: 10KB 전부 도착. 여러 번 recv()해서 이어붙이면 됨 (바이트 스트림).")
    print("  UDP: 10KB 한 번에 전송 시도 → 'Message too long' 에러.")
    print("       작은 데이터도 recvfrom 버퍼보다 크면 잘려서 유실.")
    print("=" * 60)
