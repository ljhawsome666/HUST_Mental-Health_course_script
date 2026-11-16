## 华科心理健康教育电脑端刷课脚本
免责声明：
仅供学习使用，禁止用于其他用途,
本脚本参考 https://github.com/sorryqin/Script-for-Mental-Health-Courses 的思路，做了一些优化的脚本改进


使用方法：

1.建议将项目克隆到非中文路径下，不然可能报错

2.环境配置：

# 创建环境；建议将 3.11 换成当前环境的 Python 版本
conda create -n scripts python=3.11 -y

# 激活环境
conda activate scripts

# 安装pip
conda install pip

# 安装当前环境导出的依赖
pip install -r requirements.txt

如果没有安装conda可以用以下指令
# 创建虚拟环境，目录名为 .venv
python -m venv .venv

# 激活虚拟环境
.\.venv\Scripts\Activate.ps1

# 安装依赖
python -m pip install -r requirements.txt

3.用浏览器打开我们的课程平台，![alt text](image-1.png)

4.修改路径，换成你当前的路径![alt text](image.png)

5.由于我们的心理健康教育课程有章节测验，本脚本仅支持播放视频（各位大佬后续可以优化自动完成章节测验的功能），因此在使用脚本刷课前需要各位人工将右边每一章中含有2的那一小节的章节测验做完，章节测验是可以无数次的重复提交的各位不要有心理压力。![alt text](image-1.png)

6.运行mian.py,然后将页面切回浏览器课程页面脚本即会自动刷课。

7.刷课结束记得将创建的虚拟环境删除以免占用空间