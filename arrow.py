import cv2
import numpy as np
import math

# 创建一张白底图
img = np.ones((500, 500, 3), dtype=np.uint8) * 255

# 起点
x0, y0 = 250, 250

# 设定箭头长度和角度
length = 100
theta_deg = 45  # 角度 (度)
theta_rad = math.radians(theta_deg)  # 转为弧度

# 计算终点坐标
x1 = int(x0 + length * math.cos(theta_rad))
y1 = int(y0 - length * math.sin(theta_rad))  # 注意OpenCV y轴向下

# 画箭头
cv2.arrowedLine(img, (x0, y0), (x1, y1), color=(0, 0, 255), thickness=2, tipLength=0.1)

# 显示
cv2.imshow('Arrow Example', img)
cv2.waitKey(0)
cv2.destroyAllWindows()

