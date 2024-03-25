
import json

from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
import base64
# 加密方法
def encryptData_ECB(key,plain_text):
    # 创建 SM4对象
    crypt_sm4 = CryptSM4()
    # 定义key值
    secret_key = key
    # print("key: ", secret_key)

    # 设置key
    crypt_sm4.set_key(secret_key, SM4_ENCRYPT)

    # 调用加密方法加密(十六进制的bytes类型)
    encrypt_value = crypt_sm4.crypt_ecb(plain_text)
    # print("encrypt_value: ", encrypt_value)

    # 用base64.b64encode转码（编码后的bytes）
    cipher_text = base64.b64encode(encrypt_value)

    # print("加密后：", cipher_text)
    # print(cipher_text.decode('utf-8', 'ignore'))
    # 返回加密后的字符串
    return cipher_text.decode('utf-8', 'ignore') ,encrypt_value

def decryptData_ECB(key, cipher_text):
    crypt_sm4 = CryptSM4()
    secret_key = key
    print(secret_key)
    crypt_sm4.set_key(secret_key, SM4_DECRYPT)
    # 将转入参数base64.b64decode解码成十六进制的bytes类型
    byt_cipher_text = base64.b64decode(cipher_text)
    # 调用加密方法解密，解密后为bytes类型
    decrypt_value = crypt_sm4.crypt_ecb(byt_cipher_text)
    print(decrypt_value)
    print(decrypt_value.decode('utf-8', 'ignore'))
    print(json.dumps(decrypt_value.decode('utf-8', 'ignore')))

    # return decrypt_value.decode('utf-8', 'ignore'),
    return  decrypt_value

def decryptData_ECB_bytes(key, cipher_text):
    crypt_sm4 = CryptSM4()
    secret_key = key
    print(secret_key)
    crypt_sm4.set_key(secret_key, SM4_DECRYPT)
    # 将转入参数base64.b64decode解码成十六进制的bytes类型
    byt_cipher_text = cipher_text
    # 调用加密方法解密，解密后为bytes类型
    decrypt_bytes = crypt_sm4.crypt_ecb(byt_cipher_text)
    decrypt_value = decrypt_bytes.decode('utf-8', 'ignore')
    # print(json.dumps(decrypt_value.decode('utf-8', 'ignore')))

    # return decrypt_value.decode('utf-8', 'ignore'),
    return  decrypt_value, decrypt_bytes