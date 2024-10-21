import cv2
import subprocess

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


def play_video_with_delogo(video_path, x, y, w, h):
    # 构建FFmpeg命令
    command = [
        'ffplay',
        '-f', 'lavfi',
        '-i', f'movie={video_path},delogo=x={x}:y={y}:w={w}:h={h}:show=1'
    ]
    # 调用FFmpeg命令
    subprocess.run(command)


# 主流程
video_file = '/Users/snowfish/Desktop/demo/resource/mp4List/test.mp4'  # 视频文件路径
img = get_10th_frame(video_file)

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
            break

    cv2.destroyAllWindows()

    if rect_params:
        logo_position_x, logo_position_y, logo_width, logo_height = rect_params
        # 调用delogo函数
        play_video_with_delogo(video_file, logo_position_x,
                               logo_position_y, logo_width, logo_height)
