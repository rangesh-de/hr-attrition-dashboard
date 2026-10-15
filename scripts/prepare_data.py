"""
Prepare the IBM HR Attrition dataset for a Tableau dashboard.

Steps:
  1. Validate: expected columns, unique employee IDs, no missing values.
  2. Clean: drop columns that never vary, decode 1-4 / 1-5 survey codes into labels.
  3. Enrich: attrition flag, annual salary, age / income / tenure / distance bands.
  4. Analyze: attrition rate for every level of every factor ("driver table").
  5. Write the expected KPI values so the dashboard can be checked.

Usage:
    python scripts/prepare_data.py                       # reads data/WA_Fn-UseC_-HR-Employee-Attrition.csv
    python scripts/prepare_data.py path/to/file.csv
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_INPUT = ROOT / "data" / "WA_Fn-UseC_-HR-Employee-Attrition.csv"
OUT_DIR = ROOT / "dashboard" / "data"

EXPECTED_COLUMNS = {
    "Age", "Attrition", "BusinessTravel", "DailyRate", "Department", "DistanceFromHome", "Education",
    "EducationField", "EmployeeCount", "EmployeeNumber", "EnvironmentSatisfaction", "Gender", "HourlyRate",
    "JobInvolvement", "JobLevel", "JobRole", "JobSatisfaction", "MaritalStatus", "MonthlyIncome",
    "MonthlyRate", "NumCompaniesWorked", "Over18", "OverTime", "PercentSalaryHike", "PerformanceRating",
    "RelationshipSatisfaction", "StandardHours", "StockOptionLevel", "TotalWorkingYears",
    "TrainingTimesLastYear", "WorkLifeBalance", "YearsAtCompany", "YearsInCurrentRole",
    "YearsSinceLastPromotion", "YearsWithCurrManager",
}

# Codes from the dataset's documentation
SATISFACTION = {1: "1 Low", 2: "2 Medium", 3: "3 High", 4: "4 Very High"}
DECODE = {
    "Education": {1: "1 Below College", 2: "2 College", 3: "3 Bachelor", 4: "4 Master", 5: "5 Doctor"},
    "EnvironmentSatisfaction": SATISFACTION,
    "JobInvolvement": SATISFACTION,
    "JobSatisfaction": SATISFACTION,
    "RelationshipSatisfaction": SATISFACTION,
    "PerformanceRating": {1: "1 Low", 2: "2 Good", 3: "3 Excellent", 4: "4 Outstanding"},
    "WorkLifeBalance": {1: "1 Bad", 2: "2 Good", 3: "3 Better", 4: "4 Best"},
}

# Factors included in the driver table (column -> display name)
DRIVERS = {
    "OverTime": "Overtime",
    "JobRole": "Job role",
    "Department": "Department",
    "JobLevel": "Job level",
    "MaritalStatus": "Marital status",
    "BusinessTravel": "Business travel",
    "StockOptionLevel": "Stock option level",
    "AgeBand": "Age",
    "IncomeBand": "Monthly income",
    "TenureBand": "Years at company",
    "DistanceBand": "Distance from home",
    "PromotionBand": "Years since promotion",
    "JobSatisfaction": "Job satisfaction",
    "EnvironmentSatisfaction": "Environment satisfaction",
    "WorkLifeBalance": "Work-life balance",
    "JobInvolvement": "Job involvement",
    "Gender": "Gender",
    "EducationField": "Education field",
}
MIN_GROUP = 30   # smaller groups are flagged: their rates swing too much to trust


def validate(df: pd.DataFrame) -> None:
    missing = EXPECTED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing columns: {sorted(missing)}. Is this the IBM HR Attrition file?")
    if df["EmployeeNumber"].duplicated().any():
        raise ValueError("Duplicate EmployeeNumber values")
    nulls = df[list(EXPECTED_COLUMNS)].isna().sum()
    if nulls.any():
        raise ValueError(f"Unexpected missing values:\n{nulls[nulls > 0]}")
    if not set(df["Attrition"].unique()) <= {"Yes", "No"}:
        raise ValueError("Attrition should only contain Yes/No")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    # These three have one value for every employee, so they carry no information.
    # Dropped by name (only if truly constant) so no column the analysis needs is ever removed.
    constant = [c for c in ("EmployeeCount", "Over18", "StandardHours") if df[c].nunique() == 1]
    df = df.drop(columns=constant)

    for col, mapping in DECODE.items():
        df[col] = df[col].map(mapping)

    df["AttritionFlag"] = (df["Attrition"] == "Yes").astype(int)
    df["AnnualIncome"] = df["MonthlyIncome"] * 12
    df["JobLevel"] = "Level " + df["JobLevel"].astype(str)
    df["StockOptionLevel"] = "Level " + df["StockOptionLevel"].astype(str)

    df["AgeBand"] = pd.cut(df["Age"], [17, 25, 30, 35, 45, 60],
                           labels=["18-25", "26-30", "31-35", "36-45", "46-60"]).astype(str)
    df["IncomeBand"] = pd.cut(df["MonthlyIncome"], [0, 2500, 5000, 10000, 1e9],
                              labels=["Under $2.5k", "$2.5k-5k", "$5k-10k", "$10k+"]).astype(str)
    df["TenureBand"] = pd.cut(df["YearsAtCompany"], [-1, 1, 3, 5, 10, 100],
                              labels=["0-1 yrs", "2-3 yrs", "4-5 yrs", "6-10 yrs", "10+ yrs"]).astype(str)
    df["DistanceBand"] = pd.cut(df["DistanceFromHome"], [0, 5, 10, 20, 100],
                                labels=["Under 5 mi", "5-10 mi", "11-20 mi", "20+ mi"]).astype(str)
    df["PromotionBand"] = pd.cut(df["YearsSinceLastPromotion"], [-1, 0, 2, 5, 100],
                                 labels=["Promoted this year", "1-2 yrs", "3-5 yrs", "6+ yrs"]).astype(str)
    return df


def driver_table(df: pd.DataFrame) -> pd.DataFrame:
    overall = df["AttritionFlag"].mean()
    parts = []
    for col, name in DRIVERS.items():
        g = df.groupby(col, observed=True)["AttritionFlag"].agg(employees="count", leavers="sum").reset_index()
        g = g.rename(columns={col: "level"})
        g.insert(0, "factor", name)
        parts.append(g)
    t = pd.concat(parts, ignore_index=True)
    t["attrition_rate"] = (t["leavers"] / t["employees"]).round(4)
    t["vs_company_avg"] = (t["attrition_rate"] / overall).round(2)      # 2.0 = twice the average
    t["small_group"] = t["employees"] < MIN_GROUP
    # How much each factor separates leavers from stayers: highest minus lowest rate (reliable groups only)
    spread = (t[~t["small_group"]].groupby("factor")["attrition_rate"]
              .agg(lambda s: s.max() - s.min()).round(4).rename("factor_spread"))
    return t.merge(spread, on="factor", how="left").sort_values(
        ["factor_spread", "attrition_rate"], ascending=[False, False])


def kpis(df: pd.DataFrame) -> dict:
    leavers = df[df["AttritionFlag"] == 1]
    ot = df.groupby("OverTime")["AttritionFlag"].mean()
    return {
        "employees": len(df),
        "leavers": int(df["AttritionFlag"].sum()),
        "attrition_rate_pct": round(100 * df["AttritionFlag"].mean(), 1),
        "avg_age": round(df["Age"].mean(), 1),
        "avg_monthly_income": round(df["MonthlyIncome"].mean(), 0),
        "avg_years_at_company": round(df["YearsAtCompany"].mean(), 1),
        "attrition_overtime_yes_pct": round(100 * ot.get("Yes", float("nan")), 1),
        "attrition_overtime_no_pct": round(100 * ot.get("No", float("nan")), 1),
        "annual_salary_of_leavers": int(leavers["AnnualIncome"].sum()),
        "cost_at_50pct_replacement": int(0.5 * leavers["AnnualIncome"].sum()),
    }


def main():
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_INPUT
    if not path.exists():
        sys.exit(f"File not found: {path}\nDownload it from Kaggle first (see data/README.md).")

    raw = pd.read_csv(path)
    validate(raw)
    df = clean(raw)
    drivers = driver_table(df)
    k = kpis(df)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_DIR / "hr_clean.csv", index=False)
    drivers.to_csv(OUT_DIR / "attrition_drivers.csv", index=False)

    lines = ["# Expected KPI values\n", "Your Tableau KPI tiles should show these with all filters cleared.\n"]
    lines += [f"- **{key}**: {value:,}" if isinstance(value, int) else f"- **{key}**: {value}" for key, value in k.items()]
    (ROOT / "dashboard" / "kpi_check.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Clean data: {len(df):,} employees, {df.shape[1]} columns -> {OUT_DIR / 'hr_clean.csv'}")
    print(f"Driver table: {len(drivers)} rows -> {OUT_DIR / 'attrition_drivers.csv'}\n")
    for key, value in k.items():
        print(f"  {key:<28} {value:,}" if isinstance(value, int) else f"  {key:<28} {value}")
    print("\nStrongest drivers (largest gap between highest and lowest attrition rate):")
    top = drivers.drop_duplicates("factor").head(6)
    for _, r in top.iterrows():
        print(f"  {r['factor']:<26} spread {r['factor_spread']:.1%}")


if __name__ == "__main__":
    main()
