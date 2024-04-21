import numpy as np

from .create_infoBar import *
from .connect_mysql import *
from .baidu_vertify import *
from .opencv_vertify import *

def readQss(style):
            with open(style, 'r', encoding='UTF-8') as f:
                return f.read()


def qimage_to_cvimage(qimage):
    buf = qimage.constBits()  # 获取图像数据的指针
    width, height = qimage.width(), qimage.height()  # 获取图像的宽度和高度
    buf.setsize(qimage.byteCount())  # 设置缓冲区的大小为图像的字节数
    return np.array(buf).reshape(height, width, 4).copy()  # 将缓冲区转换为 NumPy 数组，并重新形状为图像尺寸
