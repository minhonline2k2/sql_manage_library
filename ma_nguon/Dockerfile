# Giao diện Streamlit (cùng phiên bản đã kiểm thử: Python 3.10 + requirements.txt)
FROM python:3.10-slim
# PYTHONDONTWRITEBYTECODE: không ghi __pycache__ (quyền root) vào thư mục app/ được mount từ máy
ENV TZ=Asia/Ho_Chi_Minh PIP_NO_CACHE_DIR=1 PIP_DISABLE_PIP_VERSION_CHECK=1 PYTHONDONTWRITEBYTECODE=1
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY app/ .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.headless", "true", "--server.address", "0.0.0.0", "--server.port", "8501", "--browser.gatherUsageStats", "false"]
