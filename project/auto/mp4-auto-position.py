import cv2
import numpy as np
import subprocess


def find_watermark_position(video_frame, watermark_image, scale_factor):
    # 调整水印图片大小
    watermark_resized = cv2.resize(watermark_image,
                                   (0, 0),
                                   fx=scale_factor,
                                   fy=scale_factor)

    # 转换为灰度图像
    frame_gray = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
    watermark_gray = cv2.cvtColor(watermark_resized, cv2.COLOR_BGR2GRAY)

    # 使用模板匹配找到水印位置
    result = cv2.matchTemplate(
        frame_gray, watermark_gray, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 返回匹配度和水印尺寸
    return max_val, max_loc, watermark_resized.shape[1], watermark_resized.shape[0]


def preview_remove_watermark(video_path, watermark_image_path):
    # 打开视频和水印图片
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    watermark_image = cv2.imread(watermark_image_path)

    if not ret:
        print("无法读取视频帧")
        return

    best_scale = None
    best_val = -1
    best_position = None
    best_size = (0, 0)

    # 枚举缩放比例
    scale_factors = np.arange(0.05, 1.0, 0.01)  # 从0.05到1.0，步长为0.01
    for scale_factor in scale_factors:
        max_val, position, w, h = find_watermark_position(
            frame, watermark_image, scale_factor)

        if max_val > best_val:  # 寻找最大匹配度
            best_val = max_val
            best_scale = scale_factor
            best_position = position
            best_size = (w, h)

    # 提取最佳位置
    if best_position is not None:
        x, y = best_position
        w, h = best_size

        # 使用ffplay delogo滤镜实时预览去除水印
        ffplay_command = [
            'ffplay',
            '-f', 'lavfi',
            '-i', f'movie={video_path},delogo=x={x}:y={y}:w={w}:h={h}:show=1'
        ]

        # 执行命令
        subprocess.run(ffplay_command)
    else:
        print("未找到水印")


# 示例用法
video_path = '/Users/snowfish/Desktop/demo/resource/mp4List/test.mp4'
watermark_image_path = '/Users/snowfish/Desktop/demo/resource/logo/bilibili.png'

preview_remove_watermark(video_path, watermark_image_path)
