import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog
from PyQt5.QtGui import QPixmap, QImage
import numpy as np
from PIL import Image
import pysm4
import cv2
import binascii
import base64
from lsb import * 
from lsb2 import * 
from PIL import Image
from io import BytesIO
from gmssl.sm4 import CryptSM4, SM4_ENCRYPT, SM4_DECRYPT
import base64
from sm4 import * 
import io
from PIL.ImageQt import ImageQt 
from blind_watermark import WaterMark
# from Cryptodomx.Cipher import SM4
# from Cryptodomex.Random import get_random_bytes
# from Cryptodomex.Util.Padding import pad, unpad


g_w_h = 0 
g_w_w = 0
g_sm4_key =  b"JeF38U9wT9wlMfs2"
g_sm4_len = 0
g_ecoded_image_path    = './encode_image.png'
g_sm4_water_file_path  = './encrypted_watermark.bin'
g_ori_image_path       = './1.jpg'
g_ori_watermark_path   = './water_small.png'

g_bw_len = 0

def img_to_bytes(img_path):

    img =  Image.open(img_path)
    img_bytes = io.BytesIO()
    img.save(img_bytes, format=img.format)
    img_bytes.seek(0)  # 将文件指针移到文件开头

    plant_text = img_bytes.read()
    return plant_text


def pil_to_cv2(pil_img):
    # 将PIL图像转换为OpenCV图像
    cv2_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return cv2_img


def embed_watermark():
    global g_ori_watermark_path ,g_sm4_water_file_path,g_w_w , g_w_h , g_sm4_key , g_sm4_len ,g_ecoded_image_path,g_ori_image_path,g_bw_len 
    # read ori and watermark image 
    original_image = cv2.imread(g_ori_image_path)
    watermark_image = Image.open(g_ori_watermark_path )
    width, height = watermark_image.size
    w_w = width
    w_h = height 
    
    # sm4 encrypt
    plant_text = img_to_bytes(g_ori_watermark_path )
    encrypted_watermark  = encryptData_ECB(g_sm4_key ,plant_text)
    print(' encrypted_watermark  ::  ', encrypted_watermark)
    
    # save encrypted watermark file
    with open(g_sm4_water_file_path , 'wb') as f:
        f.write(bytes(encrypted_watermark,encoding='utf8'))

    g_sm4_len = len( encrypted_watermark )

    # write encrypted watermark strings to ori image 
    bwm1 = WaterMark(password_img=1, password_wm=1)
    bwm1.read_img(g_ori_image_path)
    wm = encrypted_watermark 
    bwm1.read_wm(wm, mode='str')
    bwm1.embed(g_ecoded_image_path )
    g_bw_len  = len(bwm1.wm_bit)

    print('Put down the length of wm_bit {len_wm}'.format(len_wm=g_bw_len))
     

def extract_watermark():
    global g_ori_watermark_path ,g_sm4_water_file_path,g_w_w , g_w_h , g_sm4_key , g_sm4_len ,g_ecoded_image_path,g_ori_image_path,g_bw_len 

    # extract sm4 encrypted string
    bwm1 = WaterMark(password_img=1, password_wm=1)
    wm_extract = bwm1.extract(g_ecoded_image_path, wm_shape = g_bw_len , mode='str')
   

    print("lsb extra  encrypted_watermark ::  ",  wm_extract )

    # decrypt sm4 string
    decrypted_watermark = decryptData_ECB(g_sm4_key, wm_extract )


    # 将解密后的数据转换为灰度图像
    with open('./decrypted_watermark_.png', 'wb') as f:
        f.write(decrypted_watermark)


if __name__ == "__main__":
  embed_watermark()
  input("press any key Enter to decrypt procedure...")
  extract_watermark()

