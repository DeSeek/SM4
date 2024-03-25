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
#from PIL.ImageQt import ImageQt 
from blind_watermark import WaterMark
# from Cryptodomx.Cipher import SM4
# from Cryptodomex.Random import get_random_bytes
# from Cryptodomex.Util.Padding import pad, unpad

def img_to_bytes(img_path,):

    img =  Image.open('./water_small.png')
    img_bytes = io.BytesIO()
    img.save(img_bytes, format=img.format)
    img_bytes.seek(0)  # 将文件指针移到文件开头

    plant_text = img_bytes.read()
    return plant_text


def pil_to_cv2(pil_img):
    # 将PIL图像转换为OpenCV图像
    cv2_img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    return cv2_img

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # 创建主布局
        main_layout = QHBoxLayout()

        # 创建左侧布局
        left_layout = QVBoxLayout()
        self.image_label = QLabel()
        left_layout.addWidget(self.image_label)
        main_layout.addLayout(left_layout)

        # 创建右侧布局
        right_layout = QVBoxLayout()
        btn_b1 = QPushButton("选择图片")
        btn_b1.clicked.connect(self.select_image)
        right_layout.addWidget(btn_b1)
        btn_b2 = QPushButton("加密并嵌入水印")
        btn_b2.clicked.connect(self.embed_watermark)
        right_layout.addWidget(btn_b2)
        btn_b3 = QPushButton("解密水印")
        btn_b3.clicked.connect(self.extract_watermark)
        right_layout.addWidget(btn_b3)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
        self.setWindowTitle("LSB水印嵌入")

        self.image = None
        self.watermark_image  = None
        self.encode_sm4_image = None 
        self.decode_sm4_image = None 
        self.encoded_image    = None
        self.decrypted_watermark  = None

        self.image_path =None
        self.key = b"JeF38U9wT9wlMfs2"

    def select_image(self):

        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Image files (*.jpg *.png)")
        file_path, _ = file_dialog.getOpenFileName(self, "选择图片", "", "Image files (*.jpg *.png)")
        if file_path:
            pixmap = QPixmap(file_path)
            self.image_label.setPixmap(pixmap.scaledToWidth(640))
            self.image_path = file_path

        # self.sm4_encrypt(None)

    # def show_image(self, image):
    #     # 将图片转换为 QPixmap 并显示在界面上
    #     q_image = QImage(image.data, image.shape[1], image.shape[0], QImage.Format_RGB888)
    #     pixmap = QPixmap.fromImage(q_image)
    #     self.image_label.setPixmap(pixmap.scaledToWidth(640))


    def show_image(self, image):
        # 将 numpy 数组转换为 QImage 并显示在界面上
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_image = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)
        pixmap = QPixmap.fromImage(q_image)
        self.image_label.setPixmap(pixmap.scaledToWidth(640))


    def get_pixmap(self, img):
        height, width, channel = img.shape
        bytes_per_line = 3 * width
        q_img = QImage(img.data, width, height, bytes_per_line, QImage.Format_BGR888)
        pixmap = QPixmap.fromImage(q_img)
        return pixmap

    def update_image(self, processed_img):
        if self.image_label is not None:
            if processed_img is not None:
                height, width, _ = processed_img.shape
                target_width = 640
                target_height = 480

                # 计算缩放比例
                scale_factor_width = target_width / width
                scale_factor_height = target_height / height
                scale_factor = min(scale_factor_width, scale_factor_height)

                # 缩放图像
                scaled_image = cv2.resize(processed_img, None, fx=scale_factor, fy=scale_factor)

                pixmap = self.get_pixmap(scaled_image)
                self.image_label.setPixmap(pixmap)
            else:
                self.image_label.clear()
        else:
            print("Image or img_area is None.")


    def embed_watermark(self):
        if not hasattr(self, 'image_path'):
            return

        #读取原始图
        original_image = cv2.imread(self.image_path)
        #读取水印图
        watermark_image = Image.open('./water_small.png')
        width, height = watermark_image.size
        self.watermark_image =  watermark_image
        self.w_w = width
        self.w_h = height 
        
        # 水印图片转换成字节
        plant_text = img_to_bytes('./water_small.png')

        # 水印图片字节SM4加密
        encrypted_watermark  = encryptData_ECB(self.key ,plant_text)
        print(' encrypted_watermark  ::  ', encrypted_watermark)
        

        self.pass_length = len( encrypted_watermark )
        self.encode_sm4_image = encrypted_watermark
        # # 将加密后的水印图片嵌入原图
      
        self.encode_image_path = './encode_image.png'

        # 加密后的水印嵌入原图
        bwm1 = WaterMark(password_img=1, password_wm=1)
        bwm1.read_img(self.image_path)
        wm = encrypted_watermark 
        bwm1.read_wm(wm, mode='str')
        bwm1.embed(self.encode_image_path)
        self.len_wm = len(bwm1.wm_bit)
        print('Put down the length of wm_bit {len_wm}'.format(len_wm=self.len_wm))
         

        stego_image = Image.open(self.encode_image_path)
        # 显示嵌入水印后的图片
        self.update_image(pil_to_cv2(stego_image))
        self.encode_image = pil_to_cv2(stego_image)
        #save 
       
        # cv2.imwrite(self.encode_image_path, self.encode_image)
        # stego_image.save(  self.encode_image_path )
        

    def extract_watermark(self):
        if self.encode_image is None or len(self.encode_image) == 0:
            print('encode_image is empty')
            return

        # 提取出图片中的盲水印
        bwm1 = WaterMark(password_img=1, password_wm=1)
        wm_extract = bwm1.extract(self.encode_image_path, wm_shape= self.len_wm, mode='str')
        # print('wm_extract  ::   ',wm_extract)
        print("extra  encrypted_watermark ::  ",  wm_extract )

        # 将水印经过SM4解密
        decrypted_watermark = decryptData_ECB(self.key, wm_extract )
    
        # with open('./decrypted_watermark.png', "wb") as f:
        #     f.write( bytes(encrypted_watermark, 'utf-8'))

        # 将解密后的数据转换为灰度图像
        with open('./decrypted_watermark3333.png', 'wb') as f:
            f.write(decrypted_watermark)



        self.decrypted_watermark  =  decrypted_watermark
        # 显示解密后的水印图片
        self.update_image(pil_to_cv2(Image.open('./decrypted_watermark3333.png')))




if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
