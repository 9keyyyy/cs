"""
실습 1B: UDP 에코 서버

TODO: 아래 빈칸을 채워 UDP 에코 서버를 완성하세요.

학습 포인트:
- TCP와 달리 listen(), accept()가 없는 이유
- recvfrom()과 recv()의 차이
- 비연결(connectionless)의 의미
"""

import socket


def run_udp_server(host="127.0.0.1", port=9001):
    # TODO 1: UDP 소켓을 생성하세요.
    # 힌트: TCP와 어떤 인자가 다른가요?
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # TODO 2: 소켓을 (host, port)에 바인딩하세요.
    server_sock.bind((host, port))

    # 질문: TCP 서버와 달리 listen()을 호출하지 않는 이유는?

    print(f"[UDP 서버] {host}:{port}에서 대기 중...")

    while True:
        # TODO 3: 데이터를 수신하세요.
        # recvfrom()은 (데이터, 송신자 주소) 튜플을 반환합니다.
        # 질문: recv() 대신 recvfrom()을 쓰는 이유는?
        data, client_addr = server_sock.recvfrom(1024)

        message = data.decode("utf-8")
        print(f"[UDP 서버] {client_addr}로부터 수신: {message}")

        # TODO 4: 받은 데이터를 송신자에게 돌려보내세요.
        # 힌트: UDP는 연결이 없으므로 주소를 명시해야 합니다.
        server_sock.sendto(data, client_addr)
        print(f"[UDP 서버] {client_addr}로 송신: {message}")


if __name__ == "__main__":
    run_udp_server()
