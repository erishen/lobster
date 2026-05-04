# Lobster Dockerfile
# OpenClaw Assistant CLI Tool
# 使用华为云镜像加速

FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12-slim as builder

WORKDIR /app

# 使用阿里云镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 使用阿里云 PyPI 镜像（国内稳定）
RUN pip config set global.index-url https://mirrors.aliyun.com/pypi/simple/ && \
    pip config set global.trusted-host mirrors.aliyun.com && \
    pip config set global.timeout 120 && \
    pip install --no-cache-dir --upgrade pip wheel setuptools

# 复制 investkit_utils 并安装
COPY investkit_utils /tmp/investkit_utils
RUN pip install --no-cache-dir --timeout 120 /tmp/investkit_utils && rm -rf /tmp/investkit_utils

# 复制 lobster 项目文件
COPY lobster /app

# 移除 pyproject.toml 中的 investkit-utils 本地依赖（已单独安装）
RUN sed -i '/investkit-utils @ file:/d' pyproject.toml

# 使用 pip 安装依赖（避免 poetry hash 验证问题）
RUN pip install --no-cache-dir --timeout 120 -e .

FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12-slim

WORKDIR /app

# 使用阿里云镜像源
RUN sed -i 's/deb.debian.org/mirrors.aliyun.com/g' /etc/apt/sources.list.d/debian.sources && \
    apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 从构建阶段复制安装的包
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# 复制项目文件
COPY lobster /app

RUN mkdir -p /app/.cache

ENV PYTHONUNBUFFERED=1
ENV LOBSTER_ENV=production

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -m lobster --help || exit 1

CMD ["python", "-m", "lobster", "--help"]

LABEL maintainer="InvestKit Team"
LABEL version="1.0.0"
LABEL description="Lobster - OpenClaw Assistant CLI Tool"
