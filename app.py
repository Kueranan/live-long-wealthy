"""Live Long Wealthy — Streamlit app.   รัน: streamlit run app.py"""
from dataclasses import replace

import numpy as np
import pandas as pd
import streamlit as st

from model import PERSONAS, Profile, Scenarios, equity_share, safe_spend, simulate, survival, what_ifs

st.set_page_config(page_title="Live Long Wealthy", layout="wide")


@st.cache_resource
def scenarios() -> Scenarios:
    return Scenarios()


sc = scenarios()

st.caption("Trinity Hackathon 2026 · Track 2 Wealth for Everyone")
st.title("Live Long Wealthy")
st.write("แพลตฟอร์มวางแผนการเงินตลอดชีวิต จำลองอนาคต 2,000 เส้นทางเพื่อตอบคำถามเดียว: เงินของคุณจะพอใช้ไปตลอดชีวิตหรือไม่")

with st.sidebar:
    st.header("ข้อมูลการเงินวันนี้")
    persona = st.radio("ตัวอย่างผู้ใช้", list(PERSONAS), horizontal=False)
    d: Profile = PERSONAS[persona]
    age = st.slider("อายุ", 20, 64, d.age)
    income = st.number_input("รายได้ต่อเดือน (บาท)", 0, 1_000_000, int(d.income), 1_000)
    saving = st.number_input("เงินออม/ลงทุนต่อเดือน (บาท)", 0, 500_000, int(d.saving), 500)
    assets = st.number_input("เงินเก็บที่มีอยู่ (บาท)", 0, 100_000_000, int(d.assets), 5_000)
    st.subheader("หนี้")
    debt = st.number_input("หนี้คงค้าง (บาท)", 0, 10_000_000, int(d.debt), 5_000)
    debt_rate = st.slider("ดอกเบี้ยหนี้ต่อปี (%)", 0, 33, int(d.debt_rate * 100))
    debt_payment = st.number_input("ผ่อนหนี้ต่อเดือน (บาท)", 0, 500_000, int(d.debt_payment), 500)
    st.subheader("เป้าหมายเกษียณ")
    retire_age = st.slider("อายุเกษียณ", 45, 70, max(d.retire_age, age + 1))
    retire_spend = st.number_input("ค่าใช้จ่ายหลังเกษียณต่อเดือน (มูลค่าวันนี้)", 1_000, 1_000_000, int(d.retire_spend), 1_000)
    risk = st.select_slider("ระดับความเสี่ยงที่รับได้", options=[0.7, 1.0, 1.25], value=d.risk,
                            format_func={0.7: "ระมัดระวัง", 1.0: "ปานกลาง", 1.25: "สูง"}.get)
    smt = st.checkbox("Save More Tomorrow (เพิ่มอัตราออมปีละ 1%)", d.save_more_tomorrow)
    pdf = st.checkbox("ปิดหนี้ดอกเบี้ยสูงก่อน", d.pay_debt_first)

p = Profile(age, income, saving, assets, debt, debt_rate / 100, debt_payment,
            max(retire_age, age + 1), retire_spend, risk, smt, pdf)
res = simulate(p, sc)

c1, c2, c3 = st.columns(3)
c1.metric("โอกาสที่เงินพอใช้ตลอดชีวิต", f"{res.success:.0%}")
ruin = res.ruin_age[~np.isnan(res.ruin_age)]
c2.metric("ถ้าเงินไม่พอ มักหมดตอนอายุ", f"{np.median(ruin):.0f} ปี" if ruin.size else "–")
c3.metric("ใช้หลังเกษียณได้ไม่เกิน (สำเร็จ ≥ 85%)", f"{safe_spend(p, sc):,.0f} บาท/เดือน")

st.subheader("ตัวเราในอนาคต")
cols = st.columns(3)
for col, a in zip(cols, [60, 80, 90]):
    a = max(a, age + 1)
    t = a - age
    w = res.wealth[:, t]
    with col:
        st.markdown(f"### อายุ {a}")
        st.write(f"เงินคงเหลือ (ค่ากลาง): **{max(0, np.median(w)):,.0f} บาท**")
        st.write(f"โอกาสยังมีเงินเหลือ: **{(w > 0).mean():.0%}**")
        st.write(f"โอกาสมีชีวิตถึงอายุนี้: **{survival(age, a):.0%}**")
        if a < p.retire_age:
            st.caption(f"ช่วงสะสม สัดส่วนหุ้นราว {float(equity_share(a, risk)):.0%}")

st.subheader("ความมั่งคั่งตลอดชีวิต (ล้านบาท)")
pct = res.percentiles()
upto = min(len(res.ages), 100 - age + 1)
chart = pd.DataFrame(pct[:, :upto].T / 1e6, index=res.ages[:upto], columns=["P10", "P25", "P50", "P75", "P90"])
st.line_chart(chart)

st.subheader("ลองปรับดู แล้วเห็นผลทันที")
st.dataframe(pd.DataFrame([(n, f"{d:+.0%}") for n, d in what_ifs(p, sc)], columns=["ถ้า...", "โอกาสสำเร็จเปลี่ยน"]),
             hide_index=True, use_container_width=True)

with st.expander("ทฤษฎีที่อยู่เบื้องหลัง"):
    st.markdown("""
- **Life-Cycle Hypothesis** (Modigliani, 1954) แบ่งแผนเป็นช่วงสะสมและช่วงใช้เงิน
- **Human Capital + MPT** (Ibbotson et al., 2007; Markowitz, 1952) สัดส่วนหุ้นลดลงตามอายุ
- **Longevity risk** (Yaari, 1965) อายุขัยแบบ Gompertz
- **Monte Carlo + Bayesian** ผลตอบแทนคาดหวังสุ่มจาก prior รวมความไม่แน่นอนของพารามิเตอร์
- **Safe Withdrawal Rate** (Bengen, 1994)
- **Behavioral Finance** Hershfield et al. (2011), Thaler & Benartzi (2004)
""")
st.caption("ต้นแบบเพื่อการแข่งขัน ใช้สมมติฐานอย่างง่าย ผลลัพธ์ไม่ใช่คำแนะนำการลงทุน")
