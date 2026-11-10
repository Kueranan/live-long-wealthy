"""Live Long Wealthy — Financial Planning Model

โมเดลจำลองชีวิตการเงินตลอดชีวิตแบบ Monte Carlo
- Life-Cycle Hypothesis (Modigliani, 1954): ช่วงสะสม -> ช่วงใช้เงิน
- Human Capital + MPT (Ibbotson et al., 2007; Markowitz, 1952): glide path สัดส่วนหุ้นลดลงตามอายุ
- Longevity risk (Yaari, 1965): อายุขัยแบบ Gompertz
- Parameter uncertainty (Bayesian): ผลตอบแทนคาดหวังของแต่ละเส้นทางสุ่มจาก prior
- Safe withdrawal (Bengen, 1994): หาค่าใช้จ่ายสูงสุดที่ยังสำเร็จ >= 85%
- Save More Tomorrow (Thaler & Benartzi, 2004)
ทุกจำนวนเงินเป็นมูลค่าจริง (อำนาจซื้อของวันนี้)
"""
from __future__ import annotations

from dataclasses import dataclass, replace

import numpy as np

MAX_AGE = 105
N_PATHS = 2000
SEED = 20261110

# Gompertz mortality h(x) = A * exp(B x), median adult lifespan ~82
GOMPERTZ_A = 0.00004
GOMPERTZ_B = 0.09

# capital-market assumptions (nominal, per year)
EQ_MU, EQ_MU_SD, EQ_VOL = 0.075, 0.015, 0.17
BD_MU, BD_MU_SD, BD_VOL = 0.03, 0.005, 0.05
INFL_MU, INFL_VOL = 0.025, 0.012
REAL_WAGE_GROWTH = 0.02
HEALTH_COST_GROWTH = 0.015  # extra spending per year of age after 60


@dataclass(frozen=True)
class Profile:
    age: int = 23
    income: float = 20_000          # บาท/เดือน
    saving: float = 1_500           # บาท/เดือน
    assets: float = 15_000          # เงินเก็บที่มีอยู่
    debt: float = 40_000
    debt_rate: float = 0.18
    debt_payment: float = 2_000     # บาท/เดือน
    retire_age: int = 60
    retire_spend: float = 15_000    # บาท/เดือน มูลค่าวันนี้
    risk: float = 1.0               # 0.7 ระมัดระวัง, 1.0 ปานกลาง, 1.25 สูง
    save_more_tomorrow: bool = False
    pay_debt_first: bool = False


PERSONAS = {
    "First jobber (23)": Profile(),
    "วัยทำงาน (35)": Profile(age=35, income=50_000, saving=8_000, assets=600_000,
                           debt=0, debt_rate=0, debt_payment=0, retire_spend=30_000),
    "ใกล้เกษียณ (55)": Profile(age=55, income=70_000, saving=15_000, assets=3_500_000,
                             debt=0, debt_rate=0, debt_payment=0, retire_spend=35_000, risk=0.7),
}


class Scenarios:
    """Common random numbers: every what-if is compared on the same futures."""

    def __init__(self, n: int = N_PATHS, seed: int = SEED):
        rng = np.random.default_rng(seed)
        years = MAX_AGE - 20 + 1
        self.n = n
        self.u_death = rng.uniform(1e-9, 1.0, n)
        self.mu_eq = EQ_MU + EQ_MU_SD * rng.standard_normal(n)
        self.mu_bd = BD_MU + BD_MU_SD * rng.standard_normal(n)
        self.z_eq = rng.standard_normal((n, years))
        self.z_bd = rng.standard_normal((n, years))
        self.z_in = rng.standard_normal((n, years))


def death_age(age: float, u: np.ndarray) -> np.ndarray:
    v = np.exp(GOMPERTZ_B * age) - GOMPERTZ_B * np.log(u) / GOMPERTZ_A
    return np.minimum(MAX_AGE, np.log(v) / GOMPERTZ_B)


def survival(age: float, x: float) -> float:
    return float(np.exp(-GOMPERTZ_A / GOMPERTZ_B * (np.exp(GOMPERTZ_B * x) - np.exp(GOMPERTZ_B * age))))


def equity_share(age: np.ndarray | float, risk: float):
    return np.clip((110 - np.asarray(age)) / 100 * risk, 0.1, 0.9)


def _invest_schedule(p: Profile, years: int) -> np.ndarray:
    """Yearly amount invested (today's baht) after debt payments."""
    out = np.zeros(years)
    d = p.debt
    for t in range(years):
        base_pay = p.debt_payment * 12
        extra = p.saving * 12 if p.pay_debt_first else 0.0
        if d > 0:
            d *= 1 + p.debt_rate
            pay = min(d, base_pay + extra)
            d -= pay
            out[t] = max(0.0, p.saving * 12 - max(0.0, pay - base_pay)) if p.pay_debt_first else p.saving * 12
        else:
            out[t] = p.saving * 12 + p.debt_payment * 12
    return out


@dataclass
class Result:
    success: float
    wealth: np.ndarray          # (paths, years+1)
    ages: np.ndarray
    death: np.ndarray
    ruin_age: np.ndarray        # nan if never ruined

    def percentiles(self, qs=(10, 25, 50, 75, 90)) -> np.ndarray:
        return np.percentile(self.wealth, qs, axis=0)


def simulate(p: Profile, sc: Scenarios) -> Result:
    years = MAX_AGE - p.age
    ages = p.age + np.arange(years + 1)
    idx = ages[:-1] - 20
    w = equity_share(ages[:-1], p.risk)
    nominal = w * (sc.mu_eq[:, None] + EQ_VOL * sc.z_eq[:, idx]) + (1 - w) * (sc.mu_bd[:, None] + BD_VOL * sc.z_bd[:, idx])
    infl = INFL_MU + INFL_VOL * sc.z_in[:, idx]
    real = (1 + nominal) / (1 + infl) - 1

    t = np.arange(years)
    working = ages[:-1] < p.retire_age
    contrib = _invest_schedule(p, years) * (1 + REAL_WAGE_GROWTH) ** t
    if p.save_more_tomorrow:
        contrib = contrib + p.income * 12 * (1 + REAL_WAGE_GROWTH) ** t * np.minimum(0.10, 0.01 * t)
    health = np.where(ages[:-1] > 60, 1 + HEALTH_COST_GROWTH * (ages[:-1] - 60), 1.0)
    flow = np.where(working, contrib, -p.retire_spend * 12 * health)

    wealth = np.empty((sc.n, years + 1))
    wealth[:, 0] = p.assets
    W = np.full(sc.n, float(p.assets))
    ruin = np.full(sc.n, np.nan)
    for k in range(years):
        W = np.where(W > 0, W * (1 + real[:, k]), W) + flow[k]
        newly = (W < 0) & np.isnan(ruin)
        ruin[newly] = ages[k] + 1
        wealth[:, k + 1] = W

    death = death_age(p.age, sc.u_death)
    ok = np.isnan(ruin) | (ruin > death)
    return Result(float(ok.mean()), wealth, ages, death, ruin)


def safe_spend(p: Profile, sc: Scenarios, target: float = 0.85) -> float:
    lo, hi = 1_000.0, max(20_000.0, p.retire_spend * 4)
    for _ in range(14):
        mid = (lo + hi) / 2
        if simulate(replace(p, retire_spend=mid), sc).success >= target:
            lo = mid
        else:
            hi = mid
    return lo


def what_ifs(p: Profile, sc: Scenarios) -> list[tuple[str, float]]:
    base = simulate(p, sc).success
    options = [
        ("ออมเพิ่มเดือนละ 500 บาท", replace(p, saving=p.saving + 500)),
        ("ออมเพิ่มเดือนละ 2,000 บาท", replace(p, saving=p.saving + 2_000)),
        ("เกษียณช้าลง 3 ปี", replace(p, retire_age=min(70, p.retire_age + 3))),
        ("ลดค่าใช้จ่ายหลังเกษียณ 10%", replace(p, retire_spend=p.retire_spend * 0.9)),
    ]
    if not p.save_more_tomorrow:
        options.append(("เปิด Save More Tomorrow", replace(p, save_more_tomorrow=True)))
    if p.debt > 0 and not p.pay_debt_first:
        options.append(("ปิดหนี้ดอกเบี้ยสูงก่อน", replace(p, pay_debt_first=True)))
    if p.risk < 1.25:
        options.append(("ลงทุนเสี่ยงสูงขึ้นหนึ่งระดับ", replace(p, risk=1.0 if p.risk < 1 else 1.25)))
    return [(name, simulate(q, sc).success - base) for name, q in options]


if __name__ == "__main__":
    sc = Scenarios()
    for name, prof in PERSONAS.items():
        r = simulate(prof, sc)
        print(f"{name}: โอกาสเงินพอใช้ตลอดชีวิต {r.success:.0%}, ใช้ได้ไม่เกิน {safe_spend(prof, sc):,.0f} บาท/เดือน")
        for label, d in what_ifs(prof, sc):
            print(f"   {label}: {d:+.0%}")
