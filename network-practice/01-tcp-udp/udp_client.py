"""
실습 1B: UDP 에코 클라이언트

TODO: 아래 빈칸을 채워 UDP 에코 클라이언트를 완성하세요.

실험:
1. 서버를 켜지 않은 상태에서 이 클라이언트를 실행해보세요.
   TCP 클라이언트와 동작이 어떻게 다른가요?
2. 10KB 데이터를 보내보세요. 전부 도착하나요?
"""

import socket


def run_udp_client(host="127.0.0.1", port=9001):
    # TODO 1: UDP 소켓 생성
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 질문: TCP 클라이언트와 달리 connect()를 호출하지 않는 이유는?

    try:
        while True:
            message = input("보낼 메시지 (quit으로 종료): ")
            if message.lower() == "quit":
                break

            # TODO 2: 서버로 메시지를 전송하세요.
            # 힌트: UDP는 sendto()로 매번 주소를 지정합니다.
            sock.sendto(message.encode("utf-8"), (host, port))

            # TODO 3: 응답을 수신하세요.
            # 타임아웃을 설정하여 무한 대기를 방지합니다.
            sock.settimeout(3.0)
            try:
                data, server_addr = sock.recvfrom(1024)
                print(f"[UDP 클라이언트] 에코 응답: {data.decode('utf-8')}")
            except socket.timeout:
                print("[UDP 클라이언트] 응답 타임아웃! (서버가 꺼져있거나 패킷 손실)")
    finally:
        sock.close()


if __name__ == "__main__":
    run_udp_client()
