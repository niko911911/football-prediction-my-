# 后端 + 前端静态托管 一体镜像
FROM python:3.12-slim

WORKDIR /app

# 先装依赖，利用构建缓存
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# 复制源码与前端
COPY backend/ ./backend
COPY frontend/ ./frontend

WORKDIR /app/backend
ENV USE_MOCK_DATA=true
ENV DATABASE_URL=sqlite:///./app.db
ENV PORT=8000

EXPOSE 8000
CMD ["python", "-m", "app.main"]
