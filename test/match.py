import cv2
import numpy as np
import threading
from queue import Queue
from tqdm import tqdm

# 假设的find_watermark_position函数


def find_watermark_position(video_frame, watermark_image, scale_factor):
    # 调整水印图片大小
    watermark_resized = cv2.resize(
        watermark_image, None, fx=scale_factor, fy=scale_factor, interpolation=cv2.INTER_AREA)

    # 转换为灰度图像
    frame_gray = cv2.cvtColor(video_frame, cv2.COLOR_BGR2GRAY)
    watermark_gray = cv2.cvtColor(watermark_resized, cv2.COLOR_BGR2GRAY)

    # 搜索水印位置
    res = cv2.matchTemplate(frame_gray, watermark_gray, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)

    return max_val, max_loc, watermark_resized.shape[1], watermark_resized.shape[0]

# 线程工作函数


def worker(video_frames, watermark_image, scale_factors, results_queue):
    for frame in video_frames:
        for scale_factor in scale_factors:
            max_val, max_loc, w, h = find_watermark_position(
                frame, watermark_image, scale_factor)
            results_queue.put((max_val, max_loc, w, h))

# 主函数


def preview_remove_watermark(video_path, watermark_image_path):
    cap = cv2.VideoCapture(video_path)
    watermark_image = cv2.imread(watermark_image_path, cv2.IMREAD_UNCHANGED)

    if watermark_image is None:
        print("无法读取水印图片")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    scale_factors = np.arange(0.03, 0.5, 0.01)  # 假设水印大小变化范围

    # 创建队列用于存储结果
    results_queue = Queue()

    # 读取视频帧并分配给线程
    threads = []
    frames_per_thread = frame_count // 20
    print(f"一共{frame_count}帧")
    for i in range(20):
        start_frame = i * frames_per_thread
        cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
        video_frames = []
        for j in range(frames_per_thread):
            ret, frame = cap.read()
            if not ret:
                break
            video_frames.append(frame)
        thread = threading.Thread(target=worker, args=(
            video_frames, watermark_image, scale_factors, results_queue))
        threads.append(thread)
        thread.start()

    # 显示进度条
    with tqdm(total=frame_count) as pbar:
        while any(thread.is_alive() for thread in threads):
            pbar.update(results_queue.qsize())
            while not results_queue.empty():
                max_val, max_loc, w, h = results_queue.get()
                # 这里可以添加逻辑来更新最佳匹配结果
                pass
            pbar.refresh()

    # 等待所有线程完成
    for thread in threads:
        thread.join()

    # 处理结果
    best_match = None
    while not results_queue.empty():
        match = results_queue.get()
        if best_match is None or match[0] > best_match[0]:
            best_match = match

    if best_match:
        print(f"最佳匹配度: {best_match[0]}, 位置: {
              best_match[1]}, 大小: ({best_match[2]}, {best_match[3]})")
    else:
        print("没有找到水印位置")


# 示例用法
video_path = '/Users/snowfish/Desktop/demo/resource/mp4List/smart.mp4'
watermark_image_path = '/Users/snowfish/Desktop/demo/resource/logo/songshu.png'

preview_remove_watermark(video_path, watermark_image_path)
