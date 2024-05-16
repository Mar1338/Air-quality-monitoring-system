# Используйте официальный образ Ubuntu как базовый
FROM ubuntu:latest
# Working directory
WORKDIR /app

# Установите необходимые пакеты
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    protobuf-compiler
#    git \
#    build-essential
RUN mkdir generated
# Создайте виртуальное окружение
RUN python3 -m venv /opt/venv
# Активируйте виртуальное окружение
ENV PATH="/opt/venv/bin:$PATH"

RUN python3 -m pip install google protobuf influxdb-client

# Копируйте ваш проект или файлы .proto внутрь образа
COPY . .
RUN protoc -I. --python_out=./generated *.proto
CMD ["python3", "server.py"]

#need network