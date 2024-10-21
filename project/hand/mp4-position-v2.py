import cv2
import subprocess
import os
# 鼠标事件处理函数


def draw_rectangle(event, x, y, flags, param):
    global x_init, y_init, drawing, img, img_copy, top_left, bottom_right, rect_params

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
        left, top = top_left
        width = abs(bottom_right[0] - top_left[0])
        height = abs(bottom_right[1] - top_left[1])
        rect_params = (left, top, width, height)
        print(
            f"Selected region - Left: {left}, Top: {top}, Width: {width}, Height: {height}")


# 提取视频的第10帧
def get_10th_frame(video_path):
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    target_frame = 10
    ret, frame = None, None

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret or frame_count > target_frame:
            break
        if frame_count == target_frame:
            break
        frame_count += 1

    cap.release()
    return frame

# 播放视频并调用delogo


def deal_video_with_delogo(video_path, x, y, w, h):
    # 构建FFmpeg命令
    command = [
        'ffmpeg',
        '-i', video_path,  # 指定输入视频文件路径
        '-vf', f'delogo=x={x}:y={y}:w={w}:h={h}',  # 应用delogo滤镜
        '-c:v', 'libx264',  # 指定视频编码器
        '-c:a', 'aac',  # 指定音频编码器
        output_path  # 指定输出
    ]
    # 调用FFmpeg命令
    subprocess.run(command)


# 示例用法
output_path_base = '/Users/snowfish/Desktop/demo/resource/outList/'

directory_video_path = '/Users/snowfish/Desktop/demo/resource/mp4List'
# 存储video文件绝对路径的列表
video_files_paths = []
# 遍历目录中的所有文件
for filename in os.listdir(directory_video_path):
    # 检查文件是否为video图片
    if filename.lower().endswith('.mp4'):
        # 构造绝对路径并添加到列表中
        absolute_video_path = os.path.join(directory_video_path, filename)
        video_files_paths.append(absolute_video_path)

# 打印获取到的PNG文件路径列表
print(video_files_paths)

for video in video_files_paths:
    video_name = video.split("/")[-1]
    output_path = '/Users/snowfish/Desktop/demo/resource/outList/'+video_name
    img = get_10th_frame(video)
    if img is None:
        print("Error: Could not extract the 10th frame.")
    else:
        img_copy = img.copy()
        drawing = False
        rect_params = None
        x_init, y_init = -1, -1  # 初始化起始点

        # 创建窗口并设置鼠标回调函数
        cv2.namedWindow("Frame")
        cv2.setMouseCallback("Frame", draw_rectangle)

        while True:
            cv2.imshow("Frame", img)
            # 按下 'Enter' 键退出框选模式
            if cv2.waitKey(1) & 0xFF == 13:  # 13 是 Enter 键的 ASCII
                cv2.destroyAllWindows()
                cv2.waitKey(1)
                break

        if rect_params:
            logo_position_x, logo_position_y, logo_width, logo_height = rect_params
            # 调用delogo函数
            deal_video_with_delogo(video, logo_position_x,
                                   logo_position_y, logo_width, logo_height)
