import PIL.Image as Image
import PIL.ImageDraw as ImageDraw
import PIL.ImageFont as ImageFont
import qrcode
# 源码来自：https://github.com/wuxianghou/postmaker

# 海报制作
class PostMaker(object):
    def __init__(self, backImg, font):
        self.backImg = backImg
        self.font = font
        self.post = None

    def create(self, userName, qrImg, textColor,file_name):
        """
        :param userName: 用户昵称
        :param qrImg: 二维码URL
        :param textColor: 文字颜色，{R，G，B}
        :param invation_code: 邀请码
        :return:
        """
        try:
            backImg = Image.open(self.backImg)
            font = ImageFont.truetype(self.font, 30)

            draw = ImageDraw.Draw(backImg)
            draw.ink = textColor.get('R', 0) + textColor.get('G', 0) * 256 + textColor.get('B', 0) * 256 * 256
            textWidth, textHeight = font.getsize(userName)
            draw.text([360 - textWidth / 2, 335], userName, font=font)

            qrImg = Image.open(qrImg)
            qrImg.thumbnail((142, 142))
            backImg.paste(qrImg, (191, 946))

            self.post = backImg
            backImg.save(file_name, "png")
        except Exception as e:
            print(repr(e))

# 生成二维码
def getQRcode(text,file_name):
    """
    :param text: 二维码的内容
    :param iamge_path: 存放二维码的路径
    :param file_name: 二维码图片的名称
    :return:
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=1,
    )
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save(file_name)