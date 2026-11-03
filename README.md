# Zoo Visitors API — ปีงบประมาณ 2569

โปรเจกต์ FastAPI ข้อ 5: แสดงข้อมูลจริงของผู้เข้าชมสวนสัตว์จาก [Data.go.th](https://data.go.th/dataset/zoo-visitors2569) ออกเป็น JSON

- Dataset: `zoo-visitors2569`
- Fiscal Year: `2569`
- Resource ID **ตามภาพโจทย์**: `0ecc96cf-d914-42a1-b184-dbbd013c3c9c`
- Endpoint ที่ต้องส่ง: `GET /api/zoo-visitors`, `GET /docs`

## ก่อนเริ่ม: สำคัญเกี่ยวกับข้อมูล

ภายใน `data/zoo_visitors.csv` มี **ตัวอย่างข้อมูลจริงบางแถวที่ถอดจากตารางที่เผยแพร่บน Data.go.th** เพื่อให้เริ่มทดลอง API ได้ ไม่ใช่ข้อมูลจำลอง แต่มัน **ยังไม่ใช่ไฟล์เต็มฉบับของ Resource ID ที่อาจารย์กำหนด** เพราะยังยืนยันไฟล์จาก UUID นั้นไม่ได้

**ก่อนส่งอาจารย์** ต้องเปิดหน้า Data.go.th เลือก Resource ID ที่ระบุในโจทย์ ดาวน์โหลดไฟล์ CSV จริง แล้วใช้ไฟล์นั้น **แทน** `data/zoo_visitors.csv` เพื่อให้แน่ใจว่าใช้ Resource ID ถูกต้องครบข้อมูล หากไฟล์ข้อมูลเป็น XLS/XLSX ให้ดาวน์โหลด CSV ของ resource เดียวกันหรือบันทึกเป็น CSV UTF-8 โดยรักษาชื่อคอลัมน์/ตัวเลขเดิม

API เขียนให้รองรับชื่อคอลัมน์ที่ต่างกันในไฟล์จริง แสดงคอลัมน์ตามที่อ่านได้ ไม่สร้างคอลัมน์หรือข้อมูลปลอม

> ถ้าต้องการดึงผ่าน CKAN API โดยตรง ให้เปลี่ยนชื่อหรือลบ `data/zoo_visitors.csv` จากนั้นโค้ดจะทดลอง `https://data.go.th/api/3/action/datastore_search` พร้อม `resource_id` ที่ระบุ (ปลายทางนี้ยังไม่ได้ยืนยันว่าตอบข้อมูลทรัพยากรดังกล่าวได้จริง) ถ้าเชื่อมต่อไม่สำเร็จ API จะส่ง 503 พร้อมคำแนะนำ แทนการแสดงข้อมูลปลอม

## 1. เปิดโปรเจกต์บนคอม (Windows PowerShell)

```powershell
cd zoo_fastapi_2569
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

หาก Activate.ps1 ถูกบล็อก สามารถไม่ activate และใช้:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m uvicorn main:app --host 0.0.0.0 --port 8000
```

URL ทดสอบ:
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/api/zoo-visitors
- http://127.0.0.1:8000/api/zoo-visitors?limit=5&offset=0

## 2. ทดสอบด้วย Postman

1. เปิด Postman > New HTTP Request
2. Method = `GET`
3. URL = `http://127.0.0.1:8000/api/zoo-visitors?limit=5`
4. คลิก Send
5. ตรวจสอบ Status: `200 OK` และ Response Body เป็น JSON ซึ่งมี `dataset`, `fiscal_year`, `resource_id`, `source_url`, `data`

มีไฟล์ `postman_collection.json` สำหรับ Import ใน Postman (เปลี่ยนตัวแปร `baseUrl` เป็น URL ของ VPS เมื่อ Deploy)

## 3. รันบน VPS Ubuntu ผ่าน SSH

อัปโหลด ZIP ไปที่ VPS หรือคัดลอกโฟลเดอร์ด้วย SCP แล้วใน SSH:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip unzip
unzip zoo_fastapi_2569.zip
cd zoo_fastapi_2569
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

เมื่อ VPS อนุญาต TCP port 8000 ทั้งระดับ Ubuntu firewall และ firewall ผู้ให้บริการ ให้ทดสอบจากคอมด้วย:
- `http://YOUR_VPS_IP:8000/docs`
- `http://YOUR_VPS_IP:8000/api/zoo-visitors`

**สำหรับใช้งานจริง** แนะนำ Nginx reverse proxy และ HTTPS; คำสั่ง uvicorn ด้านบนใช้เพื่อทดลองก่อน (หยุดเมื่อปิด SSH)

## 4. หลักฐานส่งอาจารย์

- URL API ที่เปิดจากภายนอกได้
- URL `/docs`
- ภาพ Postman: Method `GET`, URL, Status `200 OK`, Body JSON
- JSON ตัวอย่าง response โดยคัดลอกจาก Postman
- Source code: `main.py`, `requirements.txt` และ CSV ต้นทางจริงพร้อมระบุที่มา
- หากมีไฟล์ Resource ที่ใช้ให้ระบุ UUID และตรวจสอบว่าไฟล์ที่เลือกตรงกับโจทย์

**หมายเหตุ:** ไฟล์ `data/zoo_visitors.csv` ที่แนบมาเป็นเพียงข้อมูลจริงบางส่วนสำหรับลองรัน (JSON จะระบุ `is_excerpt: true` โดยอัตโนมัติ) และไม่ควรส่งแทน CSV ของ Resource ID จริง
