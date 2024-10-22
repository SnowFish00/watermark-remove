import cv2
import numpy as np
import subprocess
import os
from concurrent.futures import ThreadPoolExecutor


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
    # 判断是否视频重复
    video_name = os.path.basename(video_path)
    logo_name = os.path.basename(watermark_image_path)
    output_path = f'/Users/snowfish/Desktop/demo/resource/outList/{video_name}'

    if os.path.exists(output_path):
        print(f"输出文件已存在，跳过处理: {video_name}")
        return

    # 打开视频和水印图片
    cap = cv2.VideoCapture(video_path)
    ret, frame = cap.read()
    watermark_image = cv2.imread(watermark_image_path)

    if not ret:
        print(f"无法读取视频帧: {video_name}")
        return

    best_scale = None
    best_val = 0.6
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

        # 使用ffmpeg delogo滤镜实时预览去除水印
        ffmpeg_command = [
            'ffmpeg',
            '-i', video_path,  # 指定输入视频文件路径
            '-vf', f'delogo=x={x}:y={y}:w={w}:h={h}',  # 应用delogo滤镜
            '-c:v', 'libx264',  # 指定视频编码器
            '-c:a', 'aac',  # 指定音频编码器
            output_path  # 指定输出
        ]

        # 执行命令
        print(f"当前视频 {video_name} 匹配水印 {logo_name}")
        subprocess.run(ffmpeg_command)
    else:
        print(f"当前视频 {video_name} 未找到水印 {logo_name}")


def process_video_with_logos(video, logos):
    for logo in logos:
        preview_remove_watermark(video, logo)


# 并发处理
output_path_base = '/Users/snowfish/Desktop/demo/resource/outList/'

# 获取logo文件列表
directory_logo_path = '/Users/snowfish/Desktop/demo/resource/logo'
logo_files_paths = [os.path.join(directory_logo_path, f) for f in os.listdir(
    directory_logo_path) if f.lower().endswith('.png')]
print(logo_files_paths)

# 获取视频文件列表
directory_video_path = '/Users/snowfish/Desktop/demo/resource/mp4List'
video_files_paths = [os.path.join(directory_video_path, f) for f in os.listdir(
    directory_video_path) if f.lower().endswith('.mp4')]
print(video_files_paths)

# 使用ThreadPoolExecutor并发处理
with ThreadPoolExecutor() as executor:
    # 将视频与水印文件传入线程池进行并发处理
    futures = [executor.submit(
        process_video_with_logos, video, logo_files_paths) for video in video_files_paths]

    # 等待所有任务完成
    for future in futures:
        future.result()
