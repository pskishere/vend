FROM python:3.12 AS build

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends build-essential libpq-dev gcc default-libmysqlclient-dev  \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn uvicorn[standard]

# 第二阶段：运行阶段
FROM python:3.12-slim AS final

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 仅复制必要的文件
COPY --from=build /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=build /usr/local/bin /usr/local/bin
COPY . .

EXPOSE 8081

CMD ["sh", "-c", "gunicorn -k uvicorn.workers.UvicornWorker vend.asgi:application --bind 0.0.0.0:8081 --workers $((2 * $(nproc) + 1))"]