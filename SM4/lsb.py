import numpy as np
from PIL import Image
import cv2

def text_to_binary(text):
    # 将文本转换为二进制数据
    binary_data = ''.join(format(ord(char), '08b') for char in text)
    return binary_data

def binary_to_pixels(binary_data):
    # 将二进制数据转换为像素值列表
    pixels = []
    for bit in binary_data:
        pixels.append(int(bit))
    return pixels


def hide_data(image_path, text):
    # 打开图像文件
    img    = Image.open(image_path)
    pixels = img.getdata()
    width, height = img.size
    binary_text = text_to_binary(text)
    binary_pixels = binary_to_pixels(binary_text)

    # 将二进制数据隐藏到图像中的最低有效位
    new_pixels = []
    index = 0
    for pixel in pixels:
        # 如果已经隐藏完所有数据，则停止
        if index >= len(binary_pixels):
            new_pixels.append(pixel)
            continue
        # 使用最低有效位替换像素值
        new_pixel = list(pixel)
        new_pixel[-1] = binary_pixels[index]
        new_pixel = tuple(new_pixel)
        new_pixels.append(new_pixel)
        index += 1

    # 创建新图像
    new_img = Image.new("RGB", (width, height))
    new_img.putdata(new_pixels)
    new_img.save("hidden_image.png")

    # 转换为OpenCV格式图像
    opencv_img = np.array(new_img)
    opencv_img = cv2.cvtColor(opencv_img, cv2.COLOR_RGB2BGR)
    return opencv_img,new_img

def extract_data(image_path, text_length):
    # 打开图像文件
    img = Image.open(image_path)
    pixels = img.getdata()

    # 提取图像中的最低有效位
    binary_data = ''
    for pixel in pixels:
        binary_data += str(pixel[-1])

    # 将二进制数据分割成指定数量的字节，并转换为原始数据
    data_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    extracted_data = ''
    for byte in data_bytes[:text_length * 8]:
        extracted_data += chr(int(byte, 2))

    return extracted_data



def extract_data2(image_path, text_length):
    # 打开图像文件
    img = Image.open(image_path)
    pixels = img.getdata()

    # 提取图像中的最低有效位
    binary_data = ''
    for pixel in pixels:
        binary_data += str(pixel[-1])

    # 将二进制数据分割成指定数量的字节，并转换为原始数据
    data_bytes = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    extracted_data = ''
    for byte in data_bytes[:text_length]:
        extracted_data += chr(int(byte, 2))

    return extracted_data

if __name__ == '__main__':
    # 示例用法
    text_data = "Hello, World!"
    hide_data("original_image.png", text_data)
    extracted_text = extract_data("hidden_image.png", len(text_data))
    print("Extracted Text:", extracted_text)
