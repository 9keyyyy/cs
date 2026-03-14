"""
실습 1 정답 모음 - 빈칸을 채운 후 비교해보세요.

스스로 풀어본 뒤에 확인하세요!
"""

# ============================================================
# TCP 서버 정답
# ============================================================
# server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# server_sock.bind((host, port))
# server_sock.listen(5)
# client_sock, client_addr = server_sock.accept()
# data = client_sock.recv(1024)
# client_sock.sendall(data)

# ============================================================
# TCP 클라이언트 정답
# ============================================================
# sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# sock.connect((host, port))
# sock.sendall(message.encode("utf-8"))
# response = sock.recv(1024)

# ============================================================
# UDP 서버 정답
# ============================================================
# server_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# server_sock.bind((host, port))
# data, client_addr = server_sock.recvfrom(1024)
# server_sock.sendto(data, client_addr)

# ============================================================
# UDP 클라이언트 정답
# ============================================================
# sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# sock.sendto(message.encode("utf-8"), (host, port))
# data, server_addr = sock.recvfrom(1024)
