import time
from pathlib import Path

import cv2
import numpy as np
import pyautogui


# ==================================================
# 配置：请修改为你自己的图片路径
# ==================================================

PLAY_BUTTON_PATH = r"D:\ljh\Script-for-Mental-Health-Courses\scripts\pic\play_button.png"
NEXT_BUTTON_PATH = r"D:\ljh\Script-for-Mental-Health-Courses\scripts\pic\next_button.png"
END_ICON_PATH = r"D:\ljh\Script-for-Mental-Health-Courses\scripts\pic\end_icon.png"

# 播放键、完成图标的优先搜索区域：
# 格式为 (左上角 X, 左上角 Y, 宽度, 高度)
# 如果不确定坐标，可以改成 None，表示搜索整个屏幕。
PLAY_REGION = None
# 只搜索视频上方的任务状态
# 格式：(左上角 X, 左上角 Y, 宽度, 高度)
END_REGION = (120, 300, 350, 100)

# 匹配阈值：越高越严格。
# 如果误识别，适当调高；如果总是识别不到，可以少量调低。
PLAY_THRESHOLD = 0.78
NEXT_THRESHOLD = 0.78
END_THRESHOLD = 0.82

# 模板缩放范围，用于适应按钮大小变化。
SCALES = (0.8, 0.9, 1.0, 1.1, 1.2)

# 查找下一节时，最多向下滚动多少次。
MAX_SCROLL_STEPS = 8
SCROLL_AMOUNT = -450

# 点击下一节后的加载等待时间。
PAGE_LOAD_WAIT = 5

# 鼠标移到屏幕左上角可触发 PyAutoGUI 紧急停止。
pyautogui.FAILSAFE = True


def print_with_timestamp(message):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{current_time}] {message}", flush=True)


def load_template(image_path):
    """读取模板图片，支持中文路径。"""
    path = Path(image_path)

    if not path.is_file():
        raise FileNotFoundError(f"图片不存在：{image_path}")

    data = np.fromfile(str(path), dtype=np.uint8)
    template = cv2.imdecode(data, cv2.IMREAD_COLOR)

    if template is None:
        raise ValueError(f"无法读取图片，请检查图片格式：{image_path}")

    return template


def normalize_region(region):
    """将搜索区域限制在屏幕范围内；None 表示整个屏幕。"""
    screen_width, screen_height = pyautogui.size()

    if region is None:
        return (0, 0, screen_width, screen_height)

    x, y, width, height = region

    left = max(0, x)
    top = max(0, y)
    right = min(screen_width, x + width)
    bottom = min(screen_height, y + height)

    if right <= left or bottom <= top:
        raise ValueError(f"搜索区域不在屏幕内：{region}")

    return (left, top, right - left, bottom - top)


def find_image(template, region=None, threshold=0.78):
    """
    多尺度模板匹配。

    返回：
        (屏幕绝对中心坐标, 最佳匹配分数)

    匹配分数不足时，坐标为 None。
    """
    x, y, width, height = normalize_region(region)

    screenshot = pyautogui.screenshot(region=(x, y, width, height))
    screenshot = cv2.cvtColor(np.asarray(screenshot), cv2.COLOR_RGB2BGR)
    screenshot_gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)

    template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    template_height, template_width = template_gray.shape

    best_score = -1.0
    best_position = None

    for scale in SCALES:
        scaled_width = max(1, round(template_width * scale))
        scaled_height = max(1, round(template_height * scale))

        # 模板不能大于搜索区域。
        if scaled_width > width or scaled_height > height:
            continue

        interpolation = cv2.INTER_AREA if scale < 1 else cv2.INTER_LINEAR
        scaled_template = cv2.resize(
            template_gray,
            (scaled_width, scaled_height),
            interpolation=interpolation,
        )

        result = cv2.matchTemplate(
            screenshot_gray,
            scaled_template,
            cv2.TM_CCOEFF_NORMED,
        )
        _, score, _, location = cv2.minMaxLoc(result)

        if np.isfinite(score) and score > best_score:
            best_score = score
            best_position = (
                x + location[0] + scaled_width // 2,
                y + location[1] + scaled_height // 2,
            )

    if best_position is not None and best_score >= threshold:
        return best_position, best_score

    return None, best_score


def move_mouse_to_page():
    """将鼠标移到屏幕中间，方便滚动页面。"""
    screen_width, screen_height = pyautogui.size()
    pyautogui.moveTo(screen_width // 2, screen_height // 2)


def find_next_with_scrolling(next_template):
    """
    先搜索当前屏幕；如果没找到，逐步向下滚动并搜索。
    返回找到的位置及匹配分数。
    """
    for step in range(MAX_SCROLL_STEPS + 1):
        position, score = find_image(
            next_template,
            region=None,
            threshold=NEXT_THRESHOLD,
        )

        if position:
            return position, score

        if step < MAX_SCROLL_STEPS:
            print_with_timestamp(
                f"未找到下一节，继续向下滚动"
                f"（{step + 1}/{MAX_SCROLL_STEPS}，"
                f"当前最佳匹配度 {score:.2f}）"
            )
            move_mouse_to_page()
            pyautogui.scroll(SCROLL_AMOUNT)
            time.sleep(1)

    return None, score


def scroll_back_to_top():
    """
    尝试将页面滚回顶部。
    滚轮作用于鼠标所在位置，请确保鼠标所在区域可以滚动网页。
    """
    move_mouse_to_page()
    for _ in range(MAX_SCROLL_STEPS):
        pyautogui.scroll(abs(SCROLL_AMOUNT))
        time.sleep(0.1)
    time.sleep(1)

def main():
    play_template = load_template(PLAY_BUTTON_PATH)
    end_template = load_template(END_ICON_PATH)
    next_template = load_template(NEXT_BUTTON_PATH)

    print_with_timestamp("脚本已启动，将持续检测任务完成状态。")
    print_with_timestamp("将鼠标移到屏幕左上角可紧急停止。")

    while True:
        # 每一轮都先检测“任务点已完成”
        end_pos, end_score = find_image(
            end_template,
            region=END_REGION,
            threshold=END_THRESHOLD,
        )

        if end_pos is not None:
            print_with_timestamp(
                f"✅ 识别到任务点已完成：{end_pos}，"
                f"匹配度：{end_score:.2f}"
            )

            # 先搜索当前屏幕，找不到就逐步向下滚动搜索
            next_pos, next_score = find_next_with_scrolling(next_template)

            if next_pos is None:
                print_with_timestamp(
                    f"⚠️ 滚动后仍未找到下一节，"
                    f"最后一次匹配度：{next_score:.2f}。"
                    "请检查页面或确认是否已到最后一节。脚本停止。"
                )
                break

            print_with_timestamp(
                f"🎯 找到下一节：{next_pos}，"
                f"匹配度：{next_score:.2f}，准备点击。"
            )
            pyautogui.click(*next_pos)
            pyautogui.moveTo(10, 10)

            print_with_timestamp("等待新课时加载……")
            time.sleep(PAGE_LOAD_WAIT)

            # 滚回顶部，让下一课的视频和完成标志进入视野
            scroll_back_to_top()
            print_with_timestamp("继续检测新课时。")
            continue

        # 没有检测到完成标志时，检查是否需要点击播放
        play_pos, play_score = find_image(
            play_template,
            region=PLAY_REGION,
            threshold=PLAY_THRESHOLD,
        )

        if play_pos is not None:
            print_with_timestamp(
                f"▶️ 找到播放键：{play_pos}，"
                f"匹配度：{play_score:.2f}，准备点击。"
            )
            pyautogui.click(*play_pos)
            pyautogui.moveTo(10, 10)
            time.sleep(3)
        else:
            print_with_timestamp(
                f"等待任务完成……完成标志匹配度：{end_score:.2f}"
            )
            time.sleep(1)


if __name__ == "__main__":
    try:
        main()
    except pyautogui.FailSafeException:
        print_with_timestamp("检测到紧急停止，脚本已退出。")
    except KeyboardInterrupt:
        print_with_timestamp("收到停止指令，脚本已退出。")
    except Exception as exc:
        print_with_timestamp(f"脚本出错：{exc}")