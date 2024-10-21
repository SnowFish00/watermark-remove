import subprocess


def play_video_with_delogo(video_path, x, y, w, h):
    # 构建FFmpeg命令
    command = [
        'ffplay',
        '-f', 'lavfi',
        '-i', f'movie={video_path},delogo=x={x}:y={y}:w={w}:h={h}:show=1'
    ]

    # 调用FFmpeg命令
    subprocess.run(command)


# 使用示例
video_file = '/Users/snowfish/Desktop/demo/resource/mp4List/test.mp4'  # 视频文件路径
logo_position_x = 700    # logo位置的x坐标
logo_position_y = 10     # logo位置的y坐标
logo_width = 150         # logo的宽度
logo_height = 50         # logo的高度

play_video_with_delogo(video_file, logo_position_x,
                       logo_position_y, logo_width, logo_height)
