FROM python:3.9-slim

# # Thiết lập thư mục làm việc
WORKDIR /app

# Cài tzdata và set timezone
RUN apt-get update && \
    apt-get install -y tzdata && \
    ln -sf /usr/share/zoneinfo/Asia/Ho_Chi_Minh /etc/localtime && \
    echo "Asia/Ho_Chi_Minh" > /etc/timezone && \
    dpkg-reconfigure -f noninteractive tzdata && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
    
# Sao chép file requirements.txt vào thư mục làm việc
COPY requirements.txt .

#update pip
RUN pip install --upgrade pip

# # # Cài đặt các phụ thuộc từ tệp requirements.txt
RUN pip install -r requirements.txt

CMD ["python", "app.py"]