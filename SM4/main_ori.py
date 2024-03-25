import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap, QImage, QBrush, QPalette
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
#from blind_watermark import WaterMark
# from Cryptodomx.Cipher import SM4
# from Cryptodomex.Random import get_random_bytes
# from Cryptodomex.Util.Padding import pad, unpad


def img_to_bytes(img_path,):

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
        btn_b2 = QPushButton("加密图片")
        btn_b2.clicked.connect(self.embed_watermark)
        right_layout.addWidget(btn_b2)
        btn_b3 = QPushButton("解密图片")
        btn_b3.clicked.connect(self.extract_watermark)
        right_layout.addWidget(btn_b3)
        main_layout.addLayout(right_layout)

        self.setLayout(main_layout)
        self.setWindowTitle("图片SM4加密，电信202夏雨昕毕业设计")
        self.setGeometry(300,300,1920,1080)
        pixmap =QPixmap('thegirl.jpg') #调用爷准备好的图片 也是让这个程序变的花里胡哨的关键
        brush = QBrush(pixmap)
        palette = self.palette()
        palette.setBrush(self.backgroundRole(),brush)
        self.setPalette(palette)
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
 
        
        # 图片转换成字节
        plant_text = img_to_bytes(self.image_path)
        # 水印图片字节SM4加密
        encrypted_base64, encrypted_bytes = encryptData_ECB(self.key ,plant_text)
        print(' encrypted_watermark  ::  ', encrypted_base64)
        

        self.pass_length = len( encrypted_base64 )
        self.encode_sm4_image = encrypted_base64
        # 将加密后的数据写入文件
        self.encrypted_image_path = "encrypted_image.sm4"
        with open(self.encrypted_image_path, "wb") as f:
            f.write(encrypted_bytes )

        self.encode_image =  encrypted_base64

        # 显示加密成功对话框
        self.show_encryption_success_dialog()

    def extract_watermark(self):
        if self.encrypted_image_path  is None or len(self.encrypted_image_path ) == 0:
            print('encode_image is empty')
            return

        ct_bytes = None
        with open(self.encrypted_image_path , "rb") as f:
            ct_bytes = f.read()
        # 将水印经过SM4解密
        decrypted_str, decrypted_bytes = decryptData_ECB_bytes(self.key,  ct_bytes )
    
        # with open('./decrypted_watermark.png', "wb") as f:
        #     f.write( bytes(encrypted_watermark, 'utf-8'))

        # 将解密后的数据转换为灰度图像
        decrypted_img_path = './decrypted.png'
        with open( decrypted_img_path , 'wb') as f:
            f.write(decrypted_bytes)



        # self.decrypted_watermark  =  decrypted_str
        # 显示解密后的水印图片
        self.update_image(pil_to_cv2(Image.open(decrypted_img_path )))
         # 显示加密成功对话框
        self.show_decryption_success_dialog()

    # 在加密成功后弹出消息框
    def show_encryption_success_dialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("加密成功，xyx毕设")
        msg.setText("加密成功！66666666")
        msg.exec_()

    # 在解密成功后弹出消息框
    def show_decryption_success_dialog(self):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle("解密成功,xyx毕设")
        msg.setText("解密成功！6666666")
        msg.exec_()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

