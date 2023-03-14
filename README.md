# ChatVITS

这是一个基于 ChatGPT、Whisper、VITS 和 Live2D 的语音聊天网页。

## 使用方法
- 安装 Python3.6 以上版本
- 安装 CMake
- 安装依赖 `pip install -r requirements.txt`
- 下载 VITS 模型文件，命名为 model.pth 和 config.json 放入 model 文件夹。
- 下载 Live2D 模型文件，放入 static 文件夹。
- 复制 config_sample.py 为 config.py ,并填写设置。
- 运行服务器 `python main.py`
