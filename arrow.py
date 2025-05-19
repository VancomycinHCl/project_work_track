import cv2
import numpy as np
import math
from typing import Tuple



def get_dest(length: int = 100, theta_deg: float=45.0) -> Tuple[int, int]:
    x0: int = 0
    y0: int = 0
    # theta_rad = math.radians(theta_deg)  # 转为弧度
    theta_rad = theta_deg  # 转为弧度
    x1 = int(x0 + length * math.cos(theta_rad))
    y1 = int(y0 - length * math.sin(theta_rad)) # Attention! In openCV lib, the y axis is downward
    return (x1,-y1)


if __name__ == "__main__":
    

    img = np.ones((500, 500, 3), dtype=np.uint8) * 255

    x0, y0 = 250, 250
    x1, y1 = 0, 0

    length = 100
    theta_deg = 45  # degree 


    (x1, y1) = get_dest(length, theta_deg)
    x1 = x0 + x1
    y1 = y0 + y1
    cv2.arrowedLine(img, (x0, y0), (x1, y1), color=(0, 0, 255), thickness=2, tipLength=0.1)

    cv2.imshow('Arrow Example', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

