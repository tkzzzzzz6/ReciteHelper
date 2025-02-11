FROM python:3.10-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && \
    apt-get install -y \
    portaudio19-dev \
    python3-tk \
    --no-install-recommends && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY . /app/

# 设置pip镜像源为阿里云，然后安装依赖
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set install.trusted-host mirrors.aliyun.com && \
    pip install --no-cache-dir -r requirements.txt

# 创建texts目录
RUN mkdir -p /app/texts

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:0

# 运行应用
CMD ["python", "test.py"]