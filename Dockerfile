# 使用Python 3.10作为基础镜像
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

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 创建texts目录
RUN mkdir -p /app/texts

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV DISPLAY=:0

# 暴露端口（如果需要）
# EXPOSE 8000

# 运行应用
CMD ["python", "test.py"] 