# Demo thanh toan VNPAY Sandbox voi FastAPI

Project nay dung de thuyet trinh theo huong don gian, de hieu cho sinh vien:

- **WHAT:** Tich hop cong thanh toan VNPAY Sandbox vao ung dung FastAPI.
- **WHY:** Website khong tu xu ly the/ngan hang, ma chuyen nguoi dung sang cong thanh toan de giao dich an toan hon.
- **HOW:** Tao don hang, ky du lieu bang HMAC-SHA512, redirect sang VNPAY, sau do nhan return/IPN de cap nhat trang thai.

## 1. Cong nghe su dung

- Python FastAPI: tao web server va route.
- MySQL: luu giao dich thanh toan.
- VNPAY Sandbox: moi truong thanh toan thu nghiem.
- HMAC-SHA512: tao va kiem tra chu ky bao mat.

## 2. Kien truc don gian

```text
User
  -> FastAPI /payment/create
  -> MySQL: tao giao dich PENDING
  -> VNPAY Sandbox
  -> /payment/return: hien thi ket qua cho user
  -> /payment/ipn: xac thuc va cap nhat database
```

## 3. Vai tro cac file chinh

- `app/main.py`: khoi tao FastAPI, mount static file, include router.
- `app/routers/pages.py`: hien thi trang demo, success, failed.
- `app/routers/payment.py`: route tao thanh toan, return, IPN.
- `app/services/vnpay.py`: tao URL thanh toan va kiem tra chu ky VNPAY.
- `app/services/transactions.py`: tao giao dich PENDING, kiem tra order, amount, status.
- `app/services/callback.py`: nhan IPN callback va chuyen sang buoc verify.
- `database.sql`: tao database/table mau cho demo.

## 4. Cai dat va chay demo

### Buoc 1: Cai thu vien

```bash
pip install -r requirements.txt
```

### Buoc 2: Tao database

Mo MySQL va chay file:

```bash
mysql -u root -p < database.sql
```

### Buoc 3: Cau hinh `.env`

```env
VNPAY_TMN_CODE=YOUR_SANDBOX_TMN_CODE
VNPAY_HASH_SECRET=YOUR_SANDBOX_HASH_SECRET
VNPAY_PAYMENT_URL=https://sandbox.vnpayment.vn/paymentv2/vpcpay.html
BASE_URL=http://127.0.0.1:8000

MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DATABASE=vnpay_demo
```

### Buoc 4: Chay server

```bash
uvicorn app.main:app --reload
```

Mo trinh duyet:

```text
http://127.0.0.1:8000
```

## 5. Luong demo khi thuyet trinh

1. Mo trang chu, nhap noi dung don hang va so tien.
2. Bam **Thanh toan voi VNPAY**.
3. Giai thich app tao `order_id`, luu `PENDING`, nhan so tien voi 100.
4. Giai thich `build_payment_url()` sap xep tham so va tao `vnp_SecureHash`.
5. Thanh toan tren VNPAY Sandbox.
6. Quay ve trang success/failed.
7. Mo console/server log de xem IPN verify:
   - SecureHash hop le hay khong.
   - Order ID co ton tai khong.
   - Amount co dung khong.
   - Trang thai database co con PENDING khong.
   - Cap nhat sang PAID hoac FAILED.

## 6. Noi dung nen trinh bay theo rubric

### WHAT

De tai trinh bay cach tich hop VNPAY Sandbox vao web app FastAPI. Thanh phan chinh gom form thanh toan, route tao thanh toan, service ky du lieu, database giao dich va callback/IPN.

### WHY

Tich hop cong thanh toan giup website nhan tien online ma khong phai tu xu ly thong tin ngan hang. VNPAY phu hop de demo vi co sandbox, tai lieu ro, va mo hinh callback/IPN giong cac cong thanh toan thuc te.

### HOW

Ung dung tao giao dich local truoc, sau do gui user sang VNPAY bang URL da ky. Khi VNPAY tra ket qua, ung dung kiem tra chu ky, order id, so tien va trang thai giao dich truoc khi cap nhat database.

### Demo hands-on

Sinh vien co the chay MySQL, import `database.sql`, cau hinh `.env`, chay `uvicorn`, sau do thanh toan tren sandbox va quan sat log.

### Reusability

Code chia thanh router va service nen co the tai su dung:

- Doi UI ma khong sua logic VNPAY.
- Doi database ma giu lai cach ky/verify.
- Them API tra lich su giao dich neu can.

### Best practices va han che

- Luon verify `vnp_SecureHash`, khong tin query string tu browser.
- Luon so sanh amount voi database.
- IPN moi la noi xac nhan thanh toan dang tin cay.
- Demo chua xu ly day du timeout, retry IPN, log nang cao va bao mat production.

## 7. Cau hoi Q&A goi y

- Vi sao phai nhan amount voi 100?
- Return URL va IPN khac nhau nhu the nao?
- Neu user sua query string thi he thong phat hien bang cach nao?
- Tai sao phai luu don hang PENDING truoc khi redirect?
- Vi sao khong cap nhat PAID chi dua vao trang success?
