import sys
from pathlib import Path

import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scripts"))
from prepare_data import EXPECTED_COLUMNS, clean, driver_table, kpis, validate  # noqa: E402


def make_rows():
    base = {c: 1 for c in EXPECTED_COLUMNS}
    base.update({"EmployeeCount": 1, "Over18": "Y", "StandardHours": 80, "Gender": "Male",
                 "Department": "Sales", "JobRole": "Sales Executive", "MaritalStatus": "Single",
                 "BusinessTravel": "Travel_Rarely", "EducationField": "Medical", "PerformanceRating": 3})
    rows = []
    for i in range(40):
        r = dict(base, EmployeeNumber=i + 1, Age=22 + i, MonthlyIncome=2000 + 300 * i,
                 YearsAtCompany=i % 12, DistanceFromHome=1 + i % 25, YearsSinceLastPromotion=i % 7,
                 JobSatisfaction=1 + i % 4, OverTime="Yes" if i < 20 else "No",
                 Attrition="Yes" if i < 10 or i == 39 else "No")
        rows.append(r)
    return pd.DataFrame(rows)


def test_validate_rejects_wrong_file():
    with pytest.raises(ValueError, match="Missing columns"):
        validate(pd.DataFrame({"a": [1]}))


def test_validate_rejects_duplicate_ids():
    df = make_rows()
    df.loc[1, "EmployeeNumber"] = 1
    with pytest.raises(ValueError, match="Duplicate"):
        validate(df)


def test_clean_drops_constant_columns_and_decodes():
    df = clean(make_rows())
    for col in ["EmployeeCount", "Over18", "StandardHours"]:
        assert col not in df.columns
    assert df.loc[0, "JobSatisfaction"] == "1 Low"
    assert df.loc[0, "Education"] == "1 Below College"     # a column with one value is kept, not dropped
    assert set(df["JobSatisfaction"]) == {"1 Low", "2 Medium", "3 High", "4 Very High"}
    assert df["AttritionFlag"].sum() == 11
    assert df.loc[0, "AnnualIncome"] == 24000


def test_bands_cover_every_row():
    df = clean(make_rows())
    for col in ["AgeBand", "IncomeBand", "TenureBand", "DistanceBand", "PromotionBand"]:
        assert (df[col] != "nan").all(), col


def test_driver_table_rates_and_small_groups():
    df = clean(make_rows())
    t = driver_table(df)
    ot = t[t["factor"] == "Overtime"].set_index("level")
    assert ot.loc["Yes", "attrition_rate"] == 0.5          # 10 of 20
    assert ot.loc["No", "attrition_rate"] == 0.05          # 1 of 20
    assert ot["small_group"].all()                          # 20 < 30 employees


def test_kpis():
    k = kpis(clean(make_rows()))
    assert k["employees"] == 40 and k["leavers"] == 11
    assert k["attrition_rate_pct"] == 27.5
    assert k["attrition_overtime_yes_pct"] == 50.0
