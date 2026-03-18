# 실습 2: HTTP/1.1 서버 직접 구현

## 면접 키워드
- HTTP 메서드 (GET, POST, PUT, DELETE)
- 상태 코드 (200, 301, 404, 500)
- Request/Response 구조 (Start Line, Header, Body)
- Content-Type, Content-Length
- Persistent Connection (Keep-Alive)

## 과제

TCP 소켓 위에 HTTP 프로토콜을 직접 파싱하여 웹 서버를 만드세요.
라이브러리(Flask, Django 등)를 사용하지 않고 **raw socket**으로 구현합니다.

### 요구사항
1. GET 요청을 파싱하여 정적 파일을 응답
2. 404 Not Found 처리
3. Content-Type 헤더 올바르게 설정 (html, css, jpg 등)
4. POST 요청의 Body 파싱

### 테스트
```bash
# 서버 실행 후 브라우저에서 접속
python3 skeleton.py
# http://127.0.0.1:8080/index.html
# http://127.0.0.1:8080/not-exist  → 404

# curl로 테스트
curl -v http://127.0.0.1:8080/index.html
curl -X POST -d "name=hello" http://127.0.0.1:8080/submit
```

## 면접 예상 질문

### Q. HTTP 요청 메시지의 구조를 설명하세요.

HTTP 요청 메시지는 크게 세 부분으로 구성됩니다.

1. **Start Line (요청 라인)**: `메서드 URI HTTP버전` 형식입니다.
   ```
   GET /index.html HTTP/1.1
   ```
2. **Headers**: 요청에 대한 메타데이터를 `Key: Value` 형태로 전달합니다.
   ```
   Host: example.com
   Content-Type: application/json
   ```
3. **Body (본문)**: POST, PUT 등의 메서드에서 서버로 전송할 데이터를 담습니다. GET 요청에는 일반적으로 Body가 없습니다.

Start Line과 Headers 사이, Headers와 Body 사이는 각각 CRLF(`\r\n`)로 구분되며, Headers와 Body 사이에는 빈 줄(`\r\n\r\n`)이 들어갑니다.

### Q. GET과 POST의 차이는?

| 구분 | GET | POST |
|------|-----|------|
| 목적 | 리소스 조회 | 리소스 생성/처리 |
| 데이터 전달 | URL 쿼리스트링 (`?key=value`) | 요청 Body |
| 멱등성 | O (같은 요청을 여러 번 보내도 결과 동일) | X |
| 캐싱 | 가능 | 일반적으로 불가 |
| 데이터 길이 | URL 길이 제한 있음 | 제한 없음 |
| 브라우저 히스토리 | URL에 파라미터가 남음 | 남지 않음 |

핵심은 **GET은 서버의 상태를 변경하지 않는 안전한(Safe) 메서드**이고, **POST는 서버의 상태를 변경할 수 있는 메서드**라는 점입니다.

### Q. HTTP는 Stateless하다는 것이 무슨 의미인가요?

HTTP 프로토콜은 각 요청을 독립적으로 처리하며, **서버가 이전 요청의 상태를 기억하지 않는다**는 의미입니다. 즉, 클라이언트가 첫 번째 요청에서 로그인했더라도 두 번째 요청에서 서버는 해당 클라이언트가 로그인한 사실을 알지 못합니다.

이러한 Stateless 특성 덕분에 서버는 요청 간 상태를 관리할 필요가 없어 **확장성(Scalability)이 높아집니다**. 여러 서버에 요청을 분산시키기 쉽기 때문입니다.

실제로 상태 유지가 필요한 경우(로그인 유지 등)에는 HTTP 자체가 아닌 별도 메커니즘을 사용합니다:
- **쿠키(Cookie)**: 서버가 응답 헤더에 `Set-Cookie`를 보내고, 클라이언트가 이후 요청마다 `Cookie` 헤더에 포함
- **세션(Session)**: 서버 측에 상태를 저장하고 세션 ID를 쿠키로 전달
- **토큰(JWT 등)**: 클라이언트가 인증 정보를 토큰에 담아 매 요청 시 전달

### Q. HTTP/1.1의 Keep-Alive는 무엇이고 왜 필요한가요?

HTTP/1.0에서는 요청-응답마다 TCP 연결을 새로 맺고 끊었습니다(Short-lived Connection). 웹 페이지 하나를 로드할 때 HTML, CSS, JS, 이미지 등 수십 개의 리소스를 요청하므로, 매번 3-way handshake를 수행하면 큰 오버헤드가 발생합니다.

**Keep-Alive(Persistent Connection)** 는 하나의 TCP 연결을 재사용하여 여러 HTTP 요청/응답을 처리하는 방식입니다. HTTP/1.1에서는 기본 동작이며, `Connection: keep-alive` 헤더로 명시합니다.

**장점**:
- TCP 연결 수립/해제 비용 감소
- TCP 슬로우 스타트로 인한 지연 감소 (이미 워밍업된 연결 재사용)
- 서버의 소켓 리소스 절약

**한계**: HTTP/1.1의 Keep-Alive에서도 하나의 연결에서 요청-응답이 순차적으로 처리되므로 **Head-of-Line Blocking** 문제가 있으며, 이를 근본적으로 해결한 것이 HTTP/2의 멀티플렉싱입니다.

https://inpa.tistory.com/entry/WEB-%F0%9F%8C%90-HTTP-20-%ED%86%B5%EC%8B%A0-%EA%B8%B0%EC%88%A0-%EC%9D%B4%EC%A0%9C%EB%8A%94-%ED%99%95%EC%8B%A4%ED%9E%88-%EC%9D%B4%ED%95%B4%ED%95%98%EC%9E%90

### Q. 상태 코드 2xx, 3xx, 4xx, 5xx의 의미는?

| 분류 | 의미 | 주요 코드 |
|------|------|-----------|
| **2xx** | **성공** - 요청이 정상적으로 처리됨 | `200 OK`, `201 Created`, `204 No Content` |
| **3xx** | **리다이렉션** - 요청 완료를 위해 추가 동작 필요 | `301 Moved Permanently`, `302 Found`, `304 Not Modified` |
| **4xx** | **클라이언트 에러** - 요청 자체에 문제가 있음 | `400 Bad Request`, `401 Unauthorized`, `403 Forbidden`, `404 Not Found` |
| **5xx** | **서버 에러** - 서버가 요청을 처리하지 못함 | `500 Internal Server Error`, `502 Bad Gateway`, `503 Service Unavailable` |

면접에서 자주 묻는 구분:
- **401 vs 403**: 401은 인증(Authentication) 실패 (누구인지 모름), 403은 인가(Authorization) 실패 (누구인지 알지만 권한 없음)
- **301 vs 302**: 301은 영구 이동 (브라우저가 캐싱), 302는 임시 이동 (매번 원래 URL로 요청)
- **502 vs 504**: 502는 게이트웨이가 잘못된 응답을 받음, 504는 게이트웨이가 응답을 시간 내에 받지 못함

