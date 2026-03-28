"""
실습 10: TLS Handshake 시뮬레이션

TLS 1.2 Handshake의 각 단계를 시뮬레이션합니다.
실제 RSA/AES 대신 간략화된 암호화로 개념을 이해합니다.

"""

import hashlib
import os
import time


# ============================================================
# 간략화된 암호화 유틸 (개념 이해용)
# ============================================================
class SimpleRSA:
    """비대칭키 암호화 시뮬레이션 (실제 RSA가 아님)"""

    def __init__(self, name: str):
        self.name = name
        self.private_key = os.urandom(16).hex()
        self.public_key = hashlib.sha256(self.private_key.encode()).hexdigest()[:32]

    def encrypt_with_public_key(self, data: str, recipient_public_key: str) -> str:
        """공개키로 암호화 (수신자만 복호화 가능)"""
        return hashlib.sha256((data + recipient_public_key).encode()).hexdigest()

    def sign(self, data: str) -> str:
        """개인키로 서명 (발신자 인증)"""
        return hashlib.sha256((data + self.private_key).encode()).hexdigest()[:16]

    def verify_signature(self, data: str, signature: str, signer_public_key: str) -> bool:
        """서명 검증 (간략화: 항상 True)"""
        return len(signature) > 0


class SimpleAES:
    """대칭키 암호화 시뮬레이션"""

    def __init__(self, key: str):
        self.key = key

    def encrypt(self, plaintext: str) -> str:
        """대칭키로 암호화"""
        encrypted = hashlib.sha256((plaintext + self.key).encode()).hexdigest()[:len(plaintext)]
        return f"[ENC:{encrypted}]"

    def decrypt(self, ciphertext: str) -> str:
        """대칭키로 복호화 (시뮬레이션: 원문 반환)"""
        return ciphertext.replace("[ENC:", "").replace("]", "")


class Certificate:
    """X.509 인증서 시뮬레이션"""

    def __init__(self, domain: str, public_key: str, ca_name: str):
        self.domain = domain
        self.public_key = public_key
        self.ca_name = ca_name
        self.valid_from = "2024-01-01"
        self.valid_to = "2025-12-31"
        self.signature = hashlib.sha256(
            f"{domain}{public_key}{ca_name}".encode()
        ).hexdigest()[:16]

    def __str__(self):
        return (f"Certificate(domain={self.domain}, CA={self.ca_name}, "
                f"pubkey={self.public_key[:16]}...)")


# ============================================================
# TLS Handshake 시뮬레이션
# ============================================================
class TLSClient:
    def __init__(self):
        self.rsa = SimpleRSA("Client")
        self.client_random = None
        self.server_random = None
        self.premaster_secret = None
        self.session_key = None
        self.aes = None

    def step1_client_hello(self) -> dict:
        """
        Step 1: Client Hello

        클라이언트가 서버에게 보내는 첫 메시지:
        - 지원하는 TLS 버전
        - 지원하는 암호 스위트 목록
        - Client Random (난수)

        TODO 1: Client Hello 메시지를 구성하세요.
        """
        # TODO: 32바이트 랜덤 값 생성
        self.client_random = os.urandom(32).hex()

        message = {
            "type": "ClientHello",
            "tls_version": "TLS 1.2",
            "cipher_suites": [
                "TLS_RSA_WITH_AES_256_CBC_SHA",
                "TLS_RSA_WITH_AES_128_CBC_SHA",
            ],
            "client_random": self.client_random,
        }

        print(f"\n[Step 1] Client Hello")
        print(f"  TLS Version: {message['tls_version']}")
        print(f"  Cipher Suites: {message['cipher_suites']}")
        print(f"  Client Random: {self.client_random[:16]}...")
        return message

    def step3_verify_cert_and_send_premaster(self, server_hello: dict,
                                              certificate: Certificate) -> dict:
        """
        Step 3: 인증서 검증 + Pre-Master Secret 전송

        1. 서버 인증서 검증 (CA 서명 확인)
        2. Pre-Master Secret 생성
        3. 서버의 공개키로 Pre-Master Secret 암호화하여 전송
        4. Master Secret 계산 (= PRF(pre_master, client_random, server_random))

        TODO 2: Pre-Master Secret을 생성하고, 세션 키를 도출하세요.
        """
        self.server_random = server_hello["server_random"]

        # 인증서 검증 (시뮬레이션)
        print(f"\n[Step 3] 인증서 검증")
        print(f"  인증서: {certificate}")
        print(f"  CA 서명 확인: OK")

        # Pre-Master Secret 생성 (48바이트 랜덤)
        self.premaster_secret = os.urandom(48).hex()
        print(f"  Pre-Master Secret 생성: {self.premaster_secret[:16]}...")

        # 서버의 공개키로 Pre-Master Secret 암호화
        encrypted_premaster = self.rsa.encrypt_with_public_key(
            self.premaster_secret, certificate.public_key
        )
        print(f"  서버 공개키로 암호화: {encrypted_premaster[:16]}...")

        # 세션 키(대칭키) 도출
        self.session_key = hashlib.sha256(
            (self.premaster_secret + self.client_random + self.server_random).encode()
        ).hexdigest()[:32]

        print(f"  세션 키 도출: {self.session_key[:16]}...")
        self.aes = SimpleAES(self.session_key)

        return {
            "type": "ClientKeyExchange",
            "encrypted_premaster": encrypted_premaster,
        }

    def step5_finished(self) -> dict:
        """Step 5: Client Finished - 핸드셰이크 완료 확인"""
        verify = self.aes.encrypt("client_finished")
        print(f"\n[Step 5] Client Finished")
        print(f"  검증 데이터: {verify}")
        return {"type": "Finished", "verify_data": verify}

    def send_encrypted(self, message: str) -> str:
        """핸드셰이크 완료 후: 대칭키로 암호화하여 데이터 전송"""
        return self.aes.encrypt(message)


class TLSServer:
    def __init__(self, domain: str):
        self.rsa = SimpleRSA("Server")
        self.domain = domain
        self.certificate = Certificate(domain, self.rsa.public_key, "Let's Encrypt")
        self.client_random = None
        self.server_random = None
        self.premaster_secret = None
        self.session_key = None
        self.aes = None

    def step2_server_hello(self, client_hello: dict) -> tuple[dict, Certificate]:
        """
        Step 2: Server Hello + Certificate

        1. 암호 스위트 선택
        2. Server Random 생성
        3. 서버 인증서 전송

        Server Hello 메시지를 구성하세요.
        """
        self.client_random = client_hello["client_random"]

        # Server Random 생성 (32바이트)
        self.server_random = os.urandom(32).hex()

        # 암호 스위트 선택 (클라이언트 목록에서 첫 번째)
        selected_cipher = client_hello["cipher_suites"][0]

        message = {
            "type": "ServerHello",
            "tls_version": "TLS 1.2",
            "selected_cipher": selected_cipher,
            "server_random": self.server_random,
        }

        print(f"\n[Step 2] Server Hello + Certificate")
        print(f"  Selected Cipher: {selected_cipher}")
        print(f"  Server Random: {self.server_random[:16]}...")
        print(f"  Certificate: {self.certificate}")

        return message, self.certificate

    def step4_derive_session_key(self, client_key_exchange: dict) -> dict:
        """
        Step 4: 세션 키 도출

        서버도 같은 방식으로 Master Secret → Session Key를 도출합니다.
        (실제로는 Pre-Master Secret을 개인키로 복호화)

        서버 측에서도 동일한 세션 키를 도출하세요.
        """
        print(f"\n[Step 4] 서버 세션 키 도출")
        print(f"  개인키로 Pre-Master Secret 복호화 (시뮬레이션)")

        # 서버는 개인키로 Pre-Master Secret을 복호화
        # (시뮬레이션에서는 클라이언트와 동일 과정)
        # 실제로는: premaster = RSA_decrypt(encrypted_premaster, private_key)

        # 여기서는 클라이언트와 같은 세션 키가 나와야 하므로
        # 시뮬레이션용으로 직접 설정
        # 세션 키 도출 (클라이언트와 동일한 공식)
        self.session_key = hashlib.sha256(
            (self.premaster_secret + self.client_random + self.server_random).encode()
        ).hexdigest()[:32]

        print(f"  세션 키: {self.session_key[:16]}...")
        self.aes = SimpleAES(self.session_key)

        return {"type": "ServerFinished", "verify_data": self.aes.encrypt("server_finished")}


# ============================================================
# 전체 TLS Handshake 시뮬레이션
# ============================================================
def simulate_tls_handshake():
    print("=" * 60)
    print("TLS 1.2 Handshake 시뮬레이션")
    print("=" * 60)

    client = TLSClient()
    server = TLSServer("www.example.com")

    # Step 1: Client → Server: ClientHello
    client_hello = client.step1_client_hello()

    # Step 2: Server → Client: ServerHello + Certificate
    server_hello, cert = server.step2_server_hello(client_hello)

    # Step 3: Client → Server: ClientKeyExchange (Pre-Master Secret)
    key_exchange = client.step3_verify_cert_and_send_premaster(server_hello, cert)

    # 시뮬레이션: 서버에 premaster_secret을 공유 (실제로는 RSA 복호화)
    server.premaster_secret = client.premaster_secret

    # Step 4: 양쪽 모두 세션 키 도출
    server_finished = server.step4_derive_session_key(key_exchange)

    # Step 5: Client Finished
    client_finished = client.step5_finished()

    # 검증: 양쪽 세션 키가 동일한지 확인
    print(f"\n{'='*60}")
    print("[핸드셰이크 완료 검증]")
    print(f"  Client 세션 키: {client.session_key[:16]}...")
    print(f"  Server 세션 키: {server.session_key[:16]}...")
    print(f"  키 일치: {client.session_key == server.session_key}")

    # 이후: 대칭키(세션 키)로 암호화 통신
    print(f"\n{'='*60}")
    print("[암호화 통신 시작 - 대칭키 사용]")

    messages = [
        "GET /index.html HTTP/1.1",
        "HTTP/1.1 200 OK",
        "Hello, Secure World!",
    ]

    for msg in messages:
        encrypted = client.send_encrypted(msg)
        print(f"  평문:   {msg}")
        print(f"  암호문: {encrypted}")

    print(f"\n{'='*60}")
    print("핵심 정리:")
    print("  1. 비대칭키(RSA): 핸드셰이크에서 Pre-Master Secret 교환에만 사용 (느림)")
    print("  2. 대칭키(AES): 실제 데이터 통신에 사용 (빠름)")
    print("  3. 인증서: 서버의 공개키가 진짜인지 CA가 보증")
    print("  4. Client/Server Random + Pre-Master → 세션 키 도출")


if __name__ == "__main__":
    simulate_tls_handshake()
