"""
실습 2: HTTP/1.1 서버 직접 구현

TCP 소켓 위에서 HTTP 프로토콜을 직접 파싱합니다.
Flask/Django 같은 프레임워크 없이 raw socket만 사용합니다.
"""

import socket
import os

WEBROOT = os.path.join(os.path.dirname(__file__), "www")

# MIME 타입 매핑
MIME_TYPES = {
    ".html": "text/html",
    ".css": "text/css",
    ".js": "application/javascript",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".json": "application/json",
}


def parse_request(raw_request: str) -> dict:
    """
    HTTP 요청 문자열을 파싱합니다.

    예시 입력:
        GET /index.html HTTP/1.1\r\n
        Host: 127.0.0.1:8080\r\n
        Connection: keep-alive\r\n
        \r\n

    반환값:
        {
            "method": "GET",
            "path": "/index.html",
            "version": "HTTP/1.1",
            "headers": {"Host": "127.0.0.1:8080", "Connection": "keep-alive"},
            "body": ""
        }
    """
    result = {"method": "", "path": "", "version": "", "headers": {}, "body": ""}

    parts = raw_request.split("\r\n\r\n")

    header_section = parts[0]
    result["body"] = parts[1] if len(parts) > 1 else ""

    lines = header_section.split("\r\n")
    request_line = lines[0].split(" ")
    result["method"] = request_line[0]
    result["path"] = request_line[1]
    result["version"] = request_line[2]

    for line in lines[1:]:
        if ": " in line:
            key, value = line.split(": ")
            result["headers"][key] = value

    return result


def build_response(status_code: int, status_text: str, body: bytes,
                   content_type: str = "text/html") -> bytes:
    """
    HTTP 응답 메시지를 생성합니다.

    TODO: HTTP 응답 형식에 맞게 완성하세요.

    HTTP 응답 구조:
        HTTP/1.1 200 OK\r\n
        Content-Type: text/html\r\n
        Content-Length: 13\r\n
        Connection: close\r\n
        \r\n
        <h1>Hello</h1>
    """
    status_line = f"HTTP/1.1 {status_code} {status_text}\r\n"

    headers = ""
    headers += f"Content-Type: {content_type}\r\n"
    headers += f"Content-Length: {len(body)}\r\n"  # 힌트: body의 길이
    headers += "Connection: close\r\n"

    response = (status_line + headers + "\r\n").encode("utf-8") + body

    return response


def handle_get(path: str) -> bytes:
    """GET 요청을 처리하여 정적 파일을 반환합니다."""
    if path == "/":
        path = "/index.html"

    file_path = os.path.join(WEBROOT, path.lstrip("/"))

    if os.path.isfile(file_path):
        ext = os.path.splitext(file_path)[1]
        content_type = MIME_TYPES.get(ext, "application/octet-stream")

        with open(file_path, "rb") as f:
            body = f.read()

        return build_response(200, "OK", body, content_type)
    else:
        body = b"<h1>404 Not Found</h1>"
        return build_response(404, "Not Found", body)


def handle_post(path: str, body: str) -> bytes:
    """POST 요청을 처리합니다."""
    print(f"[POST] path={path}, body={body}")
    response_body = f"<h1>Received POST</h1><p>Data: {body}</p>".encode("utf-8")
    return build_response(200, "OK", response_body)


def run_server(host="127.0.0.1", port=8080):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server_sock.bind((host, port))
    server_sock.listen(5)

    print(f"[HTTP 서버] http://{host}:{port} 에서 대기 중...")

    while True:
        client_sock, client_addr = server_sock.accept()
        print(f"[HTTP 서버] 연결: {client_addr}")

        try:
            raw = client_sock.recv(4096).decode("utf-8", errors="replace")
            if not raw:
                continue

            request = parse_request(raw)
            print(f"[HTTP 서버] {request['method']} {request['path']}")

            if request["method"] == "GET":
                response = handle_get(request['path'])
            elif request["method"] == "POST":
                response = handle_post(request['path'], request['body'])
            else:
                response = build_response(405, "Method Not Allowed",
                                          b"<h1>405 Method Not Allowed</h1>")

            client_sock.sendall(response)
        except Exception as e:
            print(f"[HTTP 서버] 에러: {e}")
            error_resp = build_response(500, "Internal Server Error",
                                        b"<h1>500 Internal Server Error</h1>")
            client_sock.sendall(error_resp)
        finally:
            client_sock.close()


if __name__ == "__main__":
    run_server()
