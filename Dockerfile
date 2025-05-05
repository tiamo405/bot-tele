FROM python:3.9-slim

# # Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép file requirements.txt vào thư mục làm việc
COPY requirements.txt .

#update pip
RUN pip install --upgrade pip

# # # Cài đặt các phụ thuộc từ tệp requirements.txt
RUN pip install -r requirements.txt

CMD ["python", "app.py"]