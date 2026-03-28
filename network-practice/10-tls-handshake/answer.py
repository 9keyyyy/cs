"""
실습 10 정답 모음
"""

# step1_client_hello:
#   self.client_random = os.urandom(32).hex()

# step3_verify_cert_and_send_premaster:
#   self.premaster_secret = os.urandom(48).hex()
#   encrypted_premaster = self.rsa.encrypt_with_public_key(
#       self.premaster_secret, certificate.public_key
#   )
#   self.session_key = hashlib.sha256(
#       (self.premaster_secret + self.client_random + self.server_random).encode()
#   ).hexdigest()[:32]

# step2_server_hello:
#   self.server_random = os.urandom(32).hex()
