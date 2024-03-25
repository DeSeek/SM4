from PIL import Image
import numpy as np
import pyaes
import base64

def pad(data):
    # 计算需要填充的字节数
    padding = 16 - (len(data) % 16)
    # 对数据进行填充，并返回填充后的结果
    return data + bytes([padding] * padding)

def unpad(data):
    # 去除数据末尾的填充
    padding = data[-1]
    return data[:-padding]

def embed_watermark(original_image_path, watermark_image_path):
    # 读取原图和水印图
    original_image = Image.open(original_image_path)
    watermark_image = Image.open(watermark_image_path)

    # 调整水印图大小以适应原图
    watermark_image = watermark_image.resize(original_image.size)

    # 将水印图加密
    key = b"1234567890123456"
    aes = pyaes.AESModeOfOperationECB(key)
    encrypted_watermark = aes.encrypt(pad(watermark_image.tobytes()))

    # 将加密后的数据转换为字符串
    encrypted_watermark_str = base64.b64encode(encrypted_watermark).decode('utf-8')

    # 将加密后的数据LSB隐写到原图
    original_array = np.array(original_image)
    watermark_array = np.array(watermark_image)
    for i in range(len(original_array)):
        for j in range(len(original_array[0])):
            for k in range(3):  # 3 channels: RGB
                if i * len(original_array[0]) + j * 3 + k < len(encrypted_watermark_str):
                    # 将水印信息嵌入到最低有效位 (Least Significant Bit, LSB)
                    original_array[i][j][k] = (original_array[i][j][k] & 0xFE) | int(encrypted_watermark_str[i * len(original_array[0]) + j * 3 + k], 2)
    # 保存修改后的图像
    embedded_image = Image.fromarray(original_array)
    embedded_image.save('embedded_image.png')

def extract_watermark(embedded_image_path):
    # 读取包含水印的图像
    embedded_image = Image.open(embedded_image_path)
    embedded_array = np.array(embedded_image)

    # 提取LSB中的加密水印信息
    extracted_watermark = ''
    for i in range(len(embedded_array)):
        for j in range(len(embedded_array[0])):
            for k in range(3):  # 3 channels: RGB
                extracted_watermark += bin(embedded_array[i][j][k])[-1]  # 提取LSB

    # 将二进制字符串转换为字节，并解密
    extracted_watermark_bytes = bytearray([int(extracted_watermark[i:i+8], 2) for i in range(0, len(extracted_watermark), 8)])
    decrypted_watermark = unpad(aes.decrypt(extracted_watermark_bytes))

    # 解码为图像
    watermark_image = Image.frombytes('RGB', embedded_image.size, decrypted_watermark)

    # 保存解密的水印图像
    watermark_image.save('extracted_watermark.png')

# 测试方法
original_image_path = 'original_image.png'
watermark_image_path = 'water_small.png'
embedded_image_path = 'embedded_image.png'

# 测试加入水印
embed_watermark(original_image_path, watermark_image_path)

# 测试提取水印
extract_watermark(embedded_image_path)
