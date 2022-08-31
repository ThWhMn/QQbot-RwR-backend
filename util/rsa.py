from Crypto.PublicKey import RSA as rsa
from Crypto.Cipher import PKCS1_v1_5
class MyRSA():
    def __init__(self, key) -> None:
        if len(key) == 1:
            self.create_cipher(key[0])
        elif isinstance(key, str):
            self.create_cipher(key)
        else:
            raise ValueError("Pubkey length is not 1")

    def create_cipher(self, key):
        k = rsa.importKey(key)
        self.cipher = PKCS1_v1_5.new(k)

    def encrypt(self, msg:str):
        return self.cipher.encrypt(msg.encode())
    
    def decrypt(self, e:bytes):
        return self.cipher.decrypt(e, None)

    # 存在多个公钥时使用的函数
    def read_pub_all(self, pubkeys):
        pubs = []
        for s in pubkeys:
            pub = rsa.importKey(s)
            cipher = PKCS1_v1_5.new(pub)
            pubs.append(cipher)
        self.ciphers = pubs
    
    
    def encrypt_all(self, msg:str):
        es = []
        for cipher in self.ciphers:
            es.append(cipher.encrypt(msg.encode()))
        return es
