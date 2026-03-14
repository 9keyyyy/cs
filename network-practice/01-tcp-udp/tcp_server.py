"""
실습 1A: TCP 에코 서버

TODO: 아래 빈칸을 채워 TCP 에코 서버를 완성하세요.

학습 포인트:
- socket(), bind(), listen(), accept()의 역할
- 3-way handshake가 어느 시점에 일어나는지
- connect()와 accept()의 관계
"""

import socket


def run_tcp_server(host="127.0.0.1", port=9000):
    # TODO 1: TCP 소켓을 생성하세요.
    # 힌트: socket.socket(family, type)
    # family: socket.AF_INET (IPv4)
    # type: socket.SOCK_STREAM (TCP) vs socket.SOCK_DGRAM (UDP)
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # SO_REUSEADDR: 서버 재시작 시 "Address already in use" 방지
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    # TODO 2: 소켓을 (host, port)에 바인딩하세요.
    server_sock.bind((host, port))

    # TODO 3: 연결 대기 상태로 전환하세요. (backlog=5)
    # 질문: listen()은 3-way handshake의 어느 단계와 관련있나요?
    server_sock.listen(5)

    print(f"[TCP 서버] {host}:{port}에서 대기 중...")

    while True:
        # TODO 4: 클라이언트 연결을 수락하세요.
        # accept()는 (새 소켓, 클라이언트 주소) 튜플을 반환합니다.
        # 질문: 이 시점에서 3-way handshake는 완료되었나요?
        client_sock, client_addr = server_sock.accept()
        print(f"[TCP 서버] 연결됨: {client_addr}")

        try:
            while True:
                # TODO 5: 클라이언트로부터 데이터를 수신하세요. (최대 1024바이트)
                data = client_sock.recv(1024)

                if not data:
                    print(f"[TCP 서버] {client_addr} 연결 종료")
                    break

                message = data.decode("utf-8")
                print(f"[TCP 서버] 수신: {message}")

                # TODO 6: 받은 데이터를 그대로 돌려보내세요. (에코)
                client_sock.sendall(data)
                print(f"[TCP 서버] 송신: {message}")
        finally:
            client_sock.close()


if __name__ == "__main__":
    run_tcp_server()
