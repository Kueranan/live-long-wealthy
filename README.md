# Live Long Wealthy

แพลตฟอร์มวางแผนการเงินตลอดชีวิต (Trinity Hackathon 2026 · Track 2 Wealth for Everyone)
จำลองอนาคตทางการเงิน 2,000 เส้นทางด้วย Monte Carlo แล้วสรุปเป็นตัวเลขเดียว: **โอกาสที่เงินจะพอใช้ตลอดชีวิต**

## เว็บไซต์

https://kueranan.github.io/live-long-wealthy/

GitHub Pages เผยแพร่โฟลเดอร์ `web` อัตโนมัติเมื่อ push การเปลี่ยนแปลงเว็บไซต์เข้า `main` ผ่าน workflow `.github/workflows/pages.yml`

## รันบนเครื่อง

```bash
pip install -r requirements.txt
python model.py          # ทดสอบโมเดลกับผู้ใช้ตัวอย่าง 3 แบบ
streamlit run app.py     # เปิดหน้าเว็บ
```

## Deploy ฟรี (Streamlit Community Cloud)

1. push โฟลเดอร์นี้ขึ้น GitHub (public repo)
2. เข้า share.streamlit.io → New app → เลือก repo และไฟล์ `app.py`
3. ได้ลิงก์ `https://<ชื่อ>.streamlit.app` ใส่ในช่องลิงก์เดโม

## โครงสร้าง

| ไฟล์ | หน้าที่ |
|---|---|
| `model.py` | Financial Planning Model: Monte Carlo, glide path, Gompertz mortality, safe withdrawal, what-if |
| `app.py` | หน้าเว็บ Streamlit |
| `web/index.html` | เว็บเดโม HTML/JavaScript พร้อม CSS ที่สร้างจาก Tailwind ใช้โมเดลเดียวกัน เปิดในเบราว์เซอร์ได้ทันที หรือเปิด GitHub Pages ให้ชี้ไปที่โฟลเดอร์ `web` |

## ทฤษฎีที่ใช้

- Life-Cycle Hypothesis — Modigliani & Brumberg (1954)
- Modern Portfolio Theory — Markowitz (1952)
- Human Capital & asset allocation — Ibbotson, Milevsky, Chen & Zhu (2007)
- Longevity risk — Yaari (1965); อายุขัยแบบ Gompertz
- Safe Withdrawal Rate — Bengen (1994)
- Future self — Hershfield et al. (2011)
- Save More Tomorrow — Thaler & Benartzi (2004)

## สมมติฐาน

ผลตอบแทนหุ้นคาดหวัง 7.5%/ปี (SD ของค่าคาดหวัง 1.5%, ผันผวน 17%), ตราสารหนี้ 3% (0.5%, 5%),
เงินเฟ้อ 2.5% ± 1.2%, รายได้จริงเพิ่มปีละ 2%, ค่ารักษาพยาบาลเพิ่ม 1.5% ของค่าใช้จ่ายต่อปีหลังอายุ 60
ทุกจำนวนเงินเป็นมูลค่าจริง (อำนาจซื้อของวันนี้) ต้นแบบนี้ไม่ใช่คำแนะนำการลงทุน

## ตกแต่งเว็บด้วย Tailwind CSS

เปิด `web/index.html` ได้โดยตรง โดยเก็บ `web/styles.css` ไว้ในโฟลเดอร์เดียวกัน
CSS ถูก build ไว้แล้ว จึงไม่ต้องใช้ Node.js เพื่อเปิดหน้าเว็บ

เมื่อต้องการแก้ไขดีไซน์ ให้แก้คลาสใน `web/index.html` หรือสไตล์ใน `web/tailwind.css` แล้วรัน:

```bash
npm ci
npm run build:css
```

ใช้ `npm run watch:css` เพื่อสร้าง CSS อัตโนมัติระหว่างแก้ไข หน้าเว็บรองรับมือถือ แท็บเล็ต และโหมดมืดตามการตั้งค่าอุปกรณ์
