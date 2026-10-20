<div align="center">

# VNPAY Sandbox Demo

## Nhóm SOA.26-11

| MSSV | Họ và tên |
|------|-----------|
| 524H0036 | Lê Ngọc Bảo Trân |
| 524H0113 | Phan Thụy Mỹ Ngọc |
| 524H0076 | Hoàng Thái An |

---

## Mục lục

1. [Yêu cầu hệ thống](#-yêu-cầu-hệ-thống)
2. [Tạo môi trường ảo](#1-tạo-môi-trường-ảo)
3. [Tạo database MySQL](#2-tạo-database-mysql)
4. [Cấu hình file `.env`](#3-cấu-hình-file-env)
5. [Cấu hình ngrok](#4-cấu-hình-ngrok)
6. [Cấu hình IPN URL trên VNPAY Sandbox](#5-cấu-hình-ipn-url-trên-vnpay-sandbox)
7. [Chạy chương trình](#6-chạy-chương-trình)
8. [Thử thanh toán Sandbox](#7-thử-thanh-toán-sandbox)
9. [Kiểm tra dữ liệu](#8-kiểm-tra-dữ-liệu-trong-database)
10. [Xử lý lỗi thường gặp](#-xử-lý-lỗi-thường-gặp)
11. [Bảo mật](#-bảo-mật)

---

## Yêu cầu hệ thống

- **Python** 3.11
- **MySQL Server** hoặc **XAMPP** (có MySQL)
- **ngrok**
- Tài khoản **VNPAY Sandbox** và thông tin merchant

---

## 1. Tạo môi trường ảo

Mở Terminal tại thư mục dự án.

**Windows (PowerShell)**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

**macOS / Linux**

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

---

## 2. Tạo database MySQL

Chạy đoạn SQL sau trong MySQL hoặc phpMyAdmin:

```sql
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
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

---

## 3. Cấu hình file `.env`

Sao chép `.env.example` thành `.env`, sau đó điền thông tin của bạn:

```env
VNPAY_TMN_CODE=YOUR_TMN_CODE
VNPAY_HASH_SECRET=YOUR_HASH_SECRET
VNPAY_PAYMENT_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html

BASE_URL=https://YOUR-NGROK-URL

MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DATABASE=vnpay_demo
```

> Thay các giá trị mẫu bằng thông tin VNPAY Sandbox và MySQL thực tế của bạn.
>
> `BASE_URL` là URL **HTTPS** hiện tại do ngrok cung cấp, **không** thêm dấu `/` ở cuối.

---

## 4. Cấu hình ngrok

Nếu chưa cấu hình ngrok, thêm authtoken của tài khoản:

```bash
ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
```

Khởi động ứng dụng theo [bước 6](#6-chạy-chương-trình), sau đó mở **Terminal thứ hai** và chạy:

```bash
ngrok http 8000
```

Sao chép URL HTTPS do ngrok hiển thị và cập nhật `BASE_URL` trong `.env`.

> Mỗi khi thay đổi `.env`, hãy khởi động lại ứng dụng.

---

## 5. Cấu hình IPN URL trên VNPAY Sandbox

Trong trang cấu hình merchant của VNPAY Sandbox, đặt IPN URL thành:

```
https://YOUR-NGROK-URL/payment/ipn
```

> Hãy dùng đúng domain HTTPS ngrok hiện tại. Nếu URL ngrok thay đổi, cần cập nhật lại IPN URL trên VNPAY Sandbox.

---

## 6. Chạy chương trình

Sau khi kích hoạt môi trường ảo, chạy:

```bash
uvicorn main:app --reload --port 8000
```

Nếu `main.py` nằm trong thư mục package tên `app`, dùng lệnh sau thay thế:

```bash
uvicorn app.main:app --reload --port 8000
```

Mở trình duyệt tại: **http://localhost:8000**

---

## 7. Thử thanh toán Sandbox

1. Đảm bảo **MySQL**, **FastAPI** và **ngrok** đang chạy.
2. Mở ứng dụng bằng địa chỉ local hoặc URL HTTPS công khai của ngrok.
3. Nhập số tiền và thông tin đơn hàng, sau đó nhấn **Pay with VNPAY**.
4. Hoàn tất thanh toán bằng thông tin kiểm thử do VNPAY Sandbox cung cấp.

---

## 8. Kiểm tra dữ liệu trong database

Chạy câu lệnh sau trong MySQL:

```sql
USE vnpay_demo;
SELECT * FROM transactions ORDER BY id DESC;
```

---

## Xử lý lỗi thường gặp

| Lỗi | Cách khắc phục |
|-----|----------------|
| Thiếu thư viện MySQL | Kích hoạt môi trường ảo rồi chạy `python -m pip install mysql-connector-python` |
| Không kết nối được MySQL | Kiểm tra MySQL đang chạy và thông tin database trong `.env` chính xác |
| Không nhận được IPN callback | Kiểm tra FastAPI và ngrok đang chạy; IPN URL trên VNPAY phải kết thúc bằng `/payment/ipn` |
| URL ngrok thay đổi | Cập nhật `BASE_URL` trong `.env` và IPN URL trên VNPAY Sandbox |

---

## Bảo mật

- **Không** đưa file `.env`, VNPAY hash secret hoặc ngrok authtoken lên GitHub (hãy thêm `.env` vào `.gitignore`).
- Dự án chỉ dùng để **học tập và kiểm thử** trên môi trường **Sandbox**.
