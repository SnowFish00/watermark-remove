import os
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import threading
from queue import Queue, Empty
import sys
import select

# 定义水印参数的字典
watermark_params = {
    'A': {'x': 697, 'y': 14, 'w': 150, 'h': 32},
    'B': {'x': 943, 'y': 46, 'w': 291, 'h': 54},
    'C': {'x': 1023, 'y': 17, 'w': 205, 'h': 62}
}

# 创建一个全局锁，用于确保进度条更新的线程安全
progress_lock = threading.Lock()


def remove_watermark(video_path, output_dir, watermark_param, processing_set):
    video_name = os.path.basename(video_path)
    # 添加 -processing 后缀到输出文件名
    output_path = os.path.join(
        output_dir, video_name.replace('.mp4', '-processing.mp4'))

    # 检查输出目录中是否存在同名文件或以 -processing 结尾的文件
    existing_files = os.listdir(output_dir)
    if video_name in existing_files or video_name.replace('.mp4', '-processing.mp4') in existing_files:
        print(f"输出文件已存在，跳过处理: {video_name}")
        return

    ffmpeg_command = [
        'ffmpeg',
        '-i', video_path,
        '-vf', f'delogo=x={watermark_param["x"]}:y={watermark_param["y"]}:w={
            watermark_param["w"]}:h={watermark_param["h"]}',
        '-c:v', 'libx264',
        '-c:a', 'aac',
        output_path
    ]

    print(f"正在处理视频: {video_name}")
    processing_set.add(video_name)
    try:
        # 使用 subprocess.run 进行处理
        subprocess.run(ffmpeg_command, check=True)
        # 处理完成后重命名文件，去掉 -processing 后缀
        final_output_path = os.path.join(output_dir, video_name)
        os.rename(output_path, final_output_path)
    except subprocess.CalledProcessError as e:
        print(f"处理视频 {video_name} 时出错: {e}")
    finally:
        processing_set.remove(video_name)


def is_file_completed(filepath, check_interval=0.1):
    """检查文件是否传输完成，通过循环检测文件大小是否稳定"""
    current_size = os.path.getsize(filepath)

    time.sleep(check_interval)

    current_size_now = os.path.getsize(filepath)

    return current_size == current_size_now and current_size_now != 0  # 如果文件大小不变且不为0，认为传输完成


def monitor_directory(video_dir, output_dir, processing_set, queue):
    """监控输入目录以添加新视频文件到处理队列"""
    processed_files = set()
    total_files = 0  # 总文件数
    while True:
        new_files_count = 0  # 新文件计数
        for folder_name in os.listdir(video_dir):
            folder_path = os.path.join(video_dir, folder_name)
            if os.path.isdir(folder_path):
                for video_file in os.listdir(folder_path):
                    if video_file.lower().endswith('.mp4') and video_file not in processed_files:
                        video_file_path = os.path.join(folder_path, video_file)

                        # 检查文件是否传输完成（循环检测）
                        if is_file_completed(video_file_path):
                            processed_files.add(video_file)
                            # 通过目录名称获取对应的水印参数
                            # 获取视频文件所在的目录路径
                            directory_path = os.path.dirname(video_file_path)
                            # 获取目录的最后一部分，即目录名
                            directory_name = os.path.basename(directory_path)
                            watermark_param = watermark_params.get(
                                directory_name, None)
                            if watermark_param:
                                queue.put(
                                    (video_file_path, os.path.join(output_dir, folder_name), watermark_param))
                                new_files_count += 1
                                total_files += 1  # 更新总文件数
                            else:
                                print(f"未找到对应的水印参数: {directory_name}")
        if new_files_count > 0:
            print(f"检测到 {new_files_count} 个新文件，当前总文件数: {total_files}")
        time.sleep(1)  # 每隔1秒检查一次目录


def worker(queue, processing_set, stop_event):
    """处理队列中的视频文件"""
    while not stop_event.is_set():
        try:
            video_info = queue.get(timeout=3)  # 设置超时防止卡住
            remove_watermark(*video_info, processing_set)
            queue.task_done()
        except Empty:
            break


def main_concurrent(video_dir, output_dir):
    queue = Queue()
    processing_set = set()
    stop_event = threading.Event()  # 新增一个事件用于停止工作线程

    # 启动监控线程
    monitor_thread = threading.Thread(target=monitor_directory, args=(
        video_dir, output_dir, processing_set, queue), daemon=True)
    monitor_thread.start()

    with ThreadPoolExecutor(max_workers=10) as executor:
        while True:
            for _ in range(min(10, queue.qsize())):
                executor.submit(worker, queue, processing_set, stop_event)

             # 检查是否有键盘输入
            i, o, e = select.select([sys.stdin], [], [], 0.1)
            if i:
                key = sys.stdin.readline().strip()
                if key == 'q':
                    print("检测到退出信号，准备退出...")
                    # 等待队列处理完所有任务
                    queue.join()

                    # 设置信号停止所有工作线程
                    stop_event.set()

                    # 等待所有任务完成并停止
                    print("等待线程池关闭...")
                    executor.shutdown(wait=True)

                    print("所有任务完成，程序退出")
                    break
            time.sleep(1)  # 短暂休眠，避免CPU空转


if __name__ == '__main__':
    video_base_dir = '/Users/snowfish/Desktop/demo/resource/mp4-sort/'
    output_base_dir = '/Users/snowfish/Desktop/demo/resource/mp4-sort-out/'

    # 创建输出目录
    os.makedirs(output_base_dir, exist_ok=True)

    main_concurrent(video_base_dir, output_base_dir)
