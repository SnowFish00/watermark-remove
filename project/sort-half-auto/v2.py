import os
import subprocess
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import threading

# 定义水印参数的字典
watermark_params = {
    'A': {'x': 697, 'y': 14, 'w': 150, 'h': 32},
    'B': {'x': 943, 'y': 46, 'w': 291, 'h': 54},
    'C': {'x': 1023, 'y': 17, 'w': 205, 'h': 62}
}

# 创建一个全局锁，用于确保进度条更新的线程安全
progress_lock = threading.Lock()


def remove_watermark(video_path, output_dir, watermark_param):
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
    try:
        # 使用 subprocess.run 进行处理
        subprocess.run(ffmpeg_command, check=True)
        # 处理完成后重命名文件，去掉 -processing 后缀
        final_output_path = os.path.join(output_dir, video_name)
        os.rename(output_path, final_output_path)
    except subprocess.CalledProcessError as e:
        print(f"处理视频 {video_name} 时出错: {e}")
    return video_name


def process_videos_in_directory(video_dir, output_dir, total_progress_bar):
    video_files_paths = [os.path.join(video_dir, f) for f in os.listdir(
        video_dir) if f.lower().endswith('.mp4')]

    directory_name = os.path.basename(os.path.normpath(video_dir))
    watermark_param = watermark_params.get(directory_name, None)

    if watermark_param is None:
        print(f"未找到对应的水印参数: {directory_name}")
        return

    # 使用 ProcessPoolExecutor 替代 ThreadPoolExecutor
    with ProcessPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(
            remove_watermark, video, output_dir, watermark_param) for video in video_files_paths]

        # 使用 as_completed 逐步更新进度条
        for future in as_completed(futures):
            result = future.result()  # 获取处理结果
            with progress_lock:
                total_progress_bar.update(1)  # 更新总进度条
            if result:
                print(f"已处理视频: {result}")


if __name__ == '__main__':
    video_base_dir = '/Users/snowfish/Desktop/demo/resource/mp4-sort/'
    output_base_dir = '/Users/snowfish/Desktop/demo/resource/mp4-sort-out/'

    subdirectories = [os.path.join(video_base_dir, d) for d in os.listdir(
        video_base_dir) if os.path.isdir(os.path.join(video_base_dir, d))]

    # 计算所有子目录中视频文件的总数量
    total_video_files = sum(len([f for f in os.listdir(
        subdir) if f.lower().endswith('.mp4')]) for subdir in subdirectories)

    # 创建一个总的进度条
    total_progress_bar = tqdm(total=total_video_files,
                              desc="Total Processing Videos")

    # 处理每个子目录下的视频
    for subdir in subdirectories:
        output_subdir = os.path.join(output_base_dir, os.path.basename(subdir))
        os.makedirs(output_subdir, exist_ok=True)
        process_videos_in_directory(subdir, output_subdir, total_progress_bar)

    # 关闭总进度条
    total_progress_bar.close()
