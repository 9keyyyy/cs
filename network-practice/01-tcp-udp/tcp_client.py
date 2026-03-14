"""
실습 1A: TCP 에코 클라이언트

TODO: 아래 빈칸을 채워 TCP 에코 클라이언트를 완성하세요.
"""

import socket


def run_tcp_client(host="127.0.0.1", port=9000):
    # TODO 1: TCP 소켓 생성
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # TODO 2: 서버에 연결하세요.
    # 질문: 이 호출이 반환되면 3-way handshake는 어떤 상태인가요?
    sock.connect(( host, port))
    print(f"[TCP 클라이언트] {host}:{port}에 연결됨")

    try:
        while True:
            message = input("보낼 메시지 (quit으로 종료): ")
            if message.lower() == "quit":
                break

            # TODO 3: 메시지를 서버로 전송하세요.
            sock.sendall(message.encode("utf-8"))

            # TODO 4: 서버 응답을 수신하세요.
            response = sock.recv(1024)
            print(f"[TCP 클라이언트] 에코 응답: {response.decode('utf-8')}")
    finally:
        sock.close()


if __name__ == "__main__":
    run_tcp_client()
