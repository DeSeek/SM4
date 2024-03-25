from PIL import Image

def lsb_encode_image(img_path, msg):
    img =  Image.open(img_path)
    # 获取图片的高和宽
    width, height = img.size
    # 计算图像的像素数量
    num_pixels = width * height
    # 存储字符串的二进制
    msg_bits = ''.join([format(ord(i), "08b") for i in msg])

    # 检查是否有足够的像素来隐藏消息
    if len(msg_bits) > num_pixels * 3:
        raise ValueError("消息太长，无法隐藏在图像中。")

    # 设置已编码字符数的计数器
    count = 0
    # 遍历每个像素的RGB通道
    for x in range(width):
        for y in range(height):
            r, g, b = img.getpixel((x, y))
            # 在每个通道的最后一位嵌入信息
            if count < len(msg_bits):
                # 将字符的二进制嵌入RGB通道的LSB
                img.putpixel((x, y), (r, g, b - b % 2 + int(msg_bits[count])))
                count += 1
    return img

def lsb_decode_image(img_path):
    # 获取图片的高和宽
    img = Image.open(img_path)
    width, height = img.size
    # 初始化计数器和存储消息的字符串
    count = 0
    msg = ""
    # 遍历每个像素RGB通道的LSB
    for x in range(width):
        for y in range(height):
            r, g, b = img.getpixel((x, y))
            msg += chr(b % 2 + 48)
            count += 1
    #解码二进制文本
    decoded_msg = ""
    for i in range(0, len(msg), 8):
        decoded_msg += chr(int(msg[i:i + 8], 2))
    return decoded_msg





def encode_lsb(image_path, message, key='1'):
    img = Image.open(image_path)
    width, height = img.size
    pixel_map = img.load()

    # Konversi pesan dan kunci ke dalam bentuk biner
    binary_message = ''.join(format(ord(char), '08b') for char in message)
    binary_message += '00000000'  # Tambahkan delimeter agar bisa menghentikan proses ekstraksi
    binary_key = ''.join(format(ord(char), '08b') for char in key)

    # Periksa apakah pesan dapat disembunyikan dalam citra
    max_message_length = width * height * 3
    if len(binary_message) + len(binary_key) > max_message_length:
        raise ValueError("Pesan terlalu panjang untuk diwatermarking dalam citra ini.")

    index = 0
    for y in range(height):
        for x in range(width):
            r, g, b = pixel_map[x, y]

            # Ubah bit terakhir menjadi bit pesan atau kunci
            if index < len(binary_message):
                r = (r & 0xFE) | int(binary_message[index])
                index += 1
            elif index < len(binary_message) + len(binary_key):
                r = (r & 0xFE) | int(binary_key[index - len(binary_message)])
                index += 1

            pixel_map[x, y] = (r, g, b)

    # Simpan citra yang telah diwatermarking
    encoded_image_path = 'encoded_image.png'
    img.save(encoded_image_path)
    print("Citra berhasil diwatermarking dan disimpan sebagai encoded_image.png")
  
    return img

def decode_lsb(encoded_image_path,  key='1'):
    img = Image.open(encoded_image_path)
    width, height = img.size
    pixel_map = img.load()

    binary_message = ""
    binary_key = ''.join(format(ord(char), '08b') for char in key)
    key_index = 0
    for y in range(height):
        for x in range(width):
            r, _, _ = pixel_map[x, y]

            # Ekstrak bit terakhir dari pesan atau kunci
            if key_index < len(binary_key):
                binary_message += bin(r)[-1]
                key_index += 1
            else:
                break

    # Pisahkan pesan dari delimeter
    binary_message = binary_message.rstrip('0')
    split_message = [binary_message[i:i+8] for i in range(0, len(binary_message), 8)]

    # Konversi biner ke karakter
    message = ""
    for binary in split_message:
        char = chr(int(binary, 2))
        message += char

    return message


if __name__ == '__main__':
    # Menggunakan fungsi encode_lsb untuk menerapkan watermarking pada citra
    image_path = 'gambar.jpg'
    message = "jul"
    key = "R"

    encode_lsb(image_path, message, key)

    print("Citra sebelum diwatermarking:")
    before_img = Image.open(image_path)
    before_img.show()

    # Tampilkan citra sebelum dan sesudah diwatermarking
    print("Citra setelah diwatermarking:")
    after_img = Image.open('encoded_image.png')
    after_img.show()

    # Menggunakan fungsi decode_lsb untuk mengekstraksi pesan dari citra yang telah diwatermarking
    print("Langkah-langkah dekripsi:")
    decode_lsb('encoded_image.png', key)

    # Menggunakan fungsi decode_lsb untuk mengekstraksi pesan dari citra yang telah diwatermarking
    decoded_message = decode_lsb('encoded_image.png', key)
    print("Pesan yang diekstraksi: ", decoded_message)