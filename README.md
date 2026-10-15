# HR Employee Attrition Analysis

A Tableau dashboard that answers the questions an HR leader asks about turnover: **who is leaving, why, and what is it costing us?** Built on IBM's HR Analytics dataset (1,470 employees, 35 attributes), with a tested Python preparation step and a ranked key-driver analysis.

**Skills shown:** data validation and cleaning in pandas, feature engineering (bands, decoded survey scales), driver analysis, Tableau LOD expressions and parameters, dashboard design with business framing, unit tests.

## Dashboard

> Add after publishing: **[View on Tableau Public](LINK)**
>
> ![Dashboard](dashboard/screenshot.png)

What's on it:
- KPI tiles: headcount, leavers, attrition rate, overtime attrition, and estimated **cost of attrition** with a slider for the replacement-cost assumption
- Attrition by department and job role against a company-average line
- The overtime effect
- Age × tenure heatmap, income bands, and satisfaction scores
- A ranked **key-driver chart**: which factors separate leavers from stayers most

## Key findings

> Fill in after running `prepare_data.py` on the real file. It prints the KPIs and the strongest drivers. Each finding = a number + a recommendation. Example format:
> - **Employees who work overtime leave at X% vs Y% for those who don't.** Review workload in overtime-heavy roles before adding headcount elsewhere.

- 
- 
- 

## How it works

1. **Validate.** The script checks for the expected 35 columns, unique employee IDs, no missing values, and Yes/No attrition values, and stops with a clear message if anything's wrong.
2. **Clean.** Drops the 3 columns that are the same for everyone. Decodes survey codes into readable labels (`3` → `3 High`); the number prefix keeps them sorted correctly in Tableau.
3. **Enrich.** Attrition flag (1/0), annual income, and bands for age, income, tenure, commute distance and time since promotion.
4. **Driver table.** Attrition rate for every level of 18 factors, compared with the company average. Groups under 30 employees are flagged, because their rates aren't reliable. Factors are ranked by **spread**: the gap between their highest- and lowest-attrition levels.
5. **KPI check.** Writes the numbers the dashboard should show, so the Tableau build can be verified.

## How to run it

```bash
pip install -r requirements.txt
# 1. Download the CSV from Kaggle into data/ (see data/README.md)
python scripts/prepare_data.py
python -m pytest
# 2. Build the dashboard: docs/TABLEAU_DASHBOARD.md
```

## Project structure

```
├── dashboard/                  Prepared data + KPI check (generated), screenshot
├── data/                       Raw Kaggle CSV (not committed)
├── docs/TABLEAU_DASHBOARD.md   Step-by-step Tableau build guide + interview notes
├── scripts/prepare_data.py     Validate, clean, enrich, driver table
└── tests/test_prepare.py
```

## Limitations

- **Fictional data.** IBM created this dataset for teaching, so findings show method, not real-world facts.
- **One snapshot.** There are no dates, so this shows who left, not trends over time.
- **Correlation, not causation.** The driver ranking shows which factors go together with leaving, not what causes it.

## Data source

[IBM HR Analytics Employee Attrition & Performance](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) on Kaggle.
