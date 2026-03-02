import os
import logging

# Lưu log vào /app/bot-logs/ thay vì folder hiện tại
# Điều này cho phép mount ./bot-logs:/app/bot-logs mà không mất file logs.py
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.realpath(__file__))), 'bot-logs')
os.makedirs(log_dir, exist_ok=True)  # Tạo folder nếu chưa có

formatter = logging.Formatter('%(asctime)s %(filename)s:%(lineno)d\t %(levelname)s: %(message)s')


def setup_logger(name, level=logging.INFO):
    log_file = os.path.join(log_dir, name)
    handler = logging.FileHandler(log_file, mode="a")
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger