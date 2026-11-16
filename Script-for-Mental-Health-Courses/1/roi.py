import time
import cv2
import numpy as np
import pyautogui
import os

def print_with_timestamp(message):
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{current_time}] {message}")

# 调试函数：看看截到的区域里到底是什么，匹配度是多少
def debug_find_image(image_path, region, name, threshold=0.8):
    try:
        # 1. 截取指定区域
        screenshot = pyautogui.screenshot(region=region)
        screenshot_np = np.asarray(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # 保存截到的区域图片，看看框对没有
        cv2.imencode('.png', screenshot_bgr)[1].tofile(f"debug_{name}_region.png")

        # 2. 读取模板图片
        button_image = cv2.imdecode(np.fromfile(image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if button_image is None:
            print_with_timestamp(f"[{name}] ❌ 严重错误: 根本读不到图片 {image_path}")
            return None
            
        # 3. 模板匹配
        result = cv2.matchTemplate(screenshot_bgr, button_image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # 打印匹配度，看看差多少
        print_with_timestamp(f"[{name}] 匹配度: {max_val:.4f} (阈值要求: {threshold})")

        # 如果匹配度高，计算坐标
        if max_val > threshold:
            h, w, _ = button_image.shape
            actual_x = region[0] + max_loc[0] + w // 2
            actual_y = region[1] + max_loc[1] + h // 2
            return (actual_x, actual_y)
    except Exception as e:
        print_with_timestamp(f"[{name}] 查找出错: {e}")
    return None

def main():
    play_button_path = r"D:\ljh\Script-for-Mental-Health-Courses\1\play_button.png" 
    next_button_path = r"D:\ljh\Script-for-Mental-Health-Courses\1\next_button.png" 
    end_icon_image_path = r"D:\ljh\Script-for-Mental-Health-Courses\1\end_icon.png" 

    # 你之前设定的区域
    play_region = (500, 200, 800, 500)  
    end_region = (100, 250, 300, 150)   
    next_region = (700, 700, 500, 300) 

    print("调试模式启动，请观察终端输出，并查看文件夹生成的 debug_xxx.png 图片...")
    
    # 只运行 3 次，看看结果就行
    for i in range(3):
        print(f"\n--- 第 {i+1} 次扫描 ---")
        debug_find_image(play_button_path, play_region, "play")
        debug_find_image(end_icon_image_path, end_region, "end")
        debug_find_image(next_button_path, next_region, "next")
        time.sleep(2)

if __name__ == "__main__":
    main()