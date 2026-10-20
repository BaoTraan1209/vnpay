VNPAY Sandbox — Hướng dẫn cài đặt và chạy chương trình
Nhóm SOA.26-11. Thành viên nhóm: 524H0036-Lê Ngọc Bảo Trân, 524H0113-Phan Thụy Mỹ Ngọc, 524H0076-Hoàng Thái An

Yêu cầu
- Python 3.11
- MySQL Server hoặc XAMPP có MySQL
- ngrok
- Tài khoản VNPAY Sandbox và thông tin merchant
  
1. Tạo môi trường ảo
Mở Terminal tại thư mục dự án.

Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
macOS / Linux
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt

2. Tạo database MySQL
Chạy câu lệnh SQL sau trong MySQL hoặc phpMyAdmin:
CREATE DATABASE vnpay_demo;
USE vnpay_demo;

CREATE TABLE transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id VARCHAR(100) UNIQUE NOT NULL,
    amount INT NOT NULL,
    status VARCHAR(20) DEFAULT 'PENDING',
    vnp_transaction_no VARCHAR(100),
    response_code VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP
);

3. Cấu hình file .env
Sao chép file .env.example thành .env, sau đó điền thông tin của bạn:
VNPAY_TMN_CODE=YOUR_TMN_CODE
VNPAY_HASH_SECRET=YOUR_HASH_SECRET
VNPAY_PAYMENT_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html

BASE_URL=https://YOUR-NGROK-URL

MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=vnpay_demo
Thay các giá trị mẫu bằng thông tin VNPAY Sandbox và MySQL thực tế của bạn. BASE_URL là URL HTTPS hiện tại do ngrok cung cấp, không thêm dấu / ở cuối.

4. Cấu hình ngrok
Nếu chưa cấu hình ngrok, thêm authtoken của tài khoản:
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
Khởi động ứng dụng theo bước 6, sau đó mở Terminal thứ hai và chạy:
ngrok http 8000
Sao chép URL HTTPS được ngrok hiển thị và cập nhật giá trị BASE_URL trong .env. Nếu thay đổi .env, hãy khởi động lại ứng dụng.

5. Cấu hình IPN URL trên VNPAY Sandbox
Trong trang cấu hình merchant của VNPAY Sandbox, đặt IPN URL thành:
https://YOUR-NGROK-URL/payment/ipn
Hãy sử dụng đúng domain HTTPS ngrok hiện tại. Nếu URL ngrok thay đổi, cần cập nhật lại IPN URL trên VNPAY Sandbox.

6. Chạy chương trình
Sau khi kích hoạt môi trường ảo, chạy:
uvicorn main:app --reload --port 8000
Nếu file main.py nằm trong thư mục package tên app, sử dụng lệnh sau thay thế:
uvicorn app.main:app --reload --port 8000
Mở trình duyệt tại:
http://localhost:8000

7. Thử thanh toán Sandbox
  1. Đảm bảo MySQL, FastAPI và ngrok đang chạy.
  2. Mở ứng dụng bằng địa chỉ local hoặc URL HTTPS công khai của ngrok.
  3. Nhập số tiền và thông tin đơn hàng, sau đó nhấn Pay with VNPAY.
  4. Hoàn tất thanh toán bằng thông tin kiểm thử được cung cấp cho tài khoản VNPAY Sandbox.
     
8. Kiểm tra dữ liệu trong database
Chạy câu lệnh sau trong MySQL:
USE vnpay_demo;
SELECT * FROM transactions ORDER BY id DESC;
Xử lý lỗi thường gặp
- Thiếu thư viện MySQL: kích hoạt môi trường ảo rồi chạy python -m pip install mysql-connector-python.
- Không kết nối được MySQL: kiểm tra MySQL đang chạy và thông tin database trong .env chính xác.
- Không nhận được IPN callback: kiểm tra FastAPI và ngrok đang chạy, đồng thời IPN URL trên VNPAY phải kết thúc bằng /payment/ipn.
- URL ngrok thay đổi: cập nhật BASE_URL trong .env và IPN URL trên VNPAY Sandbox.
Bảo mật
Không đưa file .env, VNPAY hash secret hoặc ngrok authtoken lên GitHub. Dự án này chỉ dùng để học tập và kiểm thử trên môi trường Sandbox.
