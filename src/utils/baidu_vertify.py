import numpy as np
from aip import AipFace
from urllib import request
import base64
import cv2




#百度云API
APP_ID = '25884575'
API_KEY = 'g3IGO5CNXzmC0UAGCO8BKCz4'
SECRET_KEY = 'GF3KHgTtH9HjmEuGVGoxGGrgnuaKMRGP'
BaiduClient = AipFace(APP_ID, API_KEY, SECRET_KEY)  # 百度人脸识别API账号信息
IMAGE_TYPE = 'BASE64'  # 图像编码方式
GROUP = 'Class1'  # 用户组信息
url = "https://wallpaperm.cmcm.com/fedea52c7f796c3eeeb8598d4a09a3e7.jpg"  # 从推流地址取截图用于opencv处理


# 如果摄像头无法使用，则可通过网络请求获取图片
def downloadImg(url):  # 从推流地址取截图用于opencv处理
    with request.urlopen(url) as f:
        data = f.read()
        img1 = np.frombuffer(data, np.uint8)
        img_cv = cv2.imdecode(img1, cv2.IMREAD_COLOR)
        return img_cv

def transimage(image_path):  # 对图片的格式进行转换
    f = open(image_path, 'rb')
    img = base64.b64encode(f.read())
    return img

def go_api(image):  # 上传到百度api进行人脸检测
    result = BaiduClient.search(str(image, 'utf-8'), IMAGE_TYPE, GROUP)
    if result['error_msg'] == 'SUCCESS':
        name = result['result']['user_list'][0]['user_id']
        score = result['result']['user_list'][0]['score']
        if score < 85:  # 相似度
            if name == '1913001008':
                StudentID = 1913001008
            return StudentID
        else:
            name = 'Unknow'
            return 0
    if result['error_msg'] == 'pic not has face':
        return 0
