# Sử dụng base image đã build sẵn (hoặc fallback về python:3.10-slim nếu chưa build)
# Build base image trước: docker build -f Dockerfile.base -t tele-base:latest .
FROM tele-base:latest

# Thiết lập thư mục làm việc
WORKDIR /app

# Sao chép mã nguồn ứng dụng vào thư mục làm việc
COPY . .

# Lệnh để chạy ứng dụng

CMD ["python", "app.py"]