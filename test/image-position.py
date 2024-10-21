import cv2
import numpy as np

# 鼠标事件处理函数


def draw_rectangle(event, x, y, flags, param):
    global x_init, y_init, drawing, img, img_copy, top_left, bottom_right

    # 当左键按下时，记录起点
    if event == cv2.EVENT_LBUTTONDOWN:
        drawing = True
        x_init, y_init = x, y
        top_left = (x, y)

    # 当移动鼠标时，如果正在画，更新图像显示
    elif event == cv2.EVENT_MOUSEMOVE:
        if drawing:
            img = img_copy.copy()  # 每次移动时重置图像
            cv2.rectangle(img, (x_init, y_init), (x, y), (0, 255, 0), 2)

    # 当左键抬起时，完成矩形
    elif event == cv2.EVENT_LBUTTONUP:
        drawing = False
        bottom_right = (x, y)
        cv2.rectangle(img, top_left, bottom_right, (0, 255, 0), 2)
        print(f"Top left: {top_left}")
        print(f"Bottom right: {bottom_right}")
        left, top = top_left
        width = abs(bottom_right[0] - top_left[0])
        height = abs(bottom_right[1] - top_left[1])
        print(f"Left: {left}, Top: {top}, Width: {width}, Height: {height}")
        return left, top, width, height


# 读取图像
img = cv2.imread('/Users/snowfish/Desktop/demo/resource/images/base.jpg')
img_copy = img.copy()
drawing = False  # 是否在画框
x_init, y_init = -1, -1  # 初始点

# 创建窗口并设置鼠标回调函数
cv2.namedWindow("Image")
cv2.setMouseCallback("Image", draw_rectangle)

while True:
    cv2.imshow("Image", img)
    # 按下 'q' 键退出
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
