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

1,470 employees, 237 of whom left: a **16.1% attrition rate**. Leavers' combined annual salaries total $13.6M, so at a replacement cost of half a year's salary, turnover costs about **$6.8M**.

- **The first year is the danger zone.** 34.9% of employees in their first year left, vs 8.1% of those with 10+ years. Onboarding and first-year check-ins are the highest-value place to spend retention effort.
- **Overtime triples the risk.** 30.5% of employees working overtime left, vs 10.4% of those who don't. With 416 people on overtime, workload is the most actionable lever in the data.
- **Sales Representatives leave at 2.5× the company rate (39.8%).** Laboratory Technicians follow at 23.9%. Managers (4.9%) and Research Directors (2.5%) almost never leave. Retention budgets should go to specific roles, not company-wide programs.
- **Pay and equity matter most at the bottom.** Employees earning under $2,500 a month leave at 34.1%, vs 8.9% above $10,000. Employees with no stock options leave at 24.4%, vs 9.4% with a basic grant, which makes a small equity grant a candidate retention tool worth testing.
- **These risks pile onto the same people.** Leavers are disproportionately young (35.8% of 18–25-year-olds left), entry-level (26.3% at job level 1), single (25.5%) and frequent travelers (24.9%). Together they describe one early-career profile, which is easier to target than any single factor.
- **Gender and department matter far less than role and workload.** Attrition is 17.0% for men vs 14.8% for women, and Sales vs R&D differ by 7 points. Job role alone creates a 37-point spread.

_The factors overlap (young employees tend to be junior, lower-paid and newer), and the data shows correlation, not cause. The dataset is fictional, created by IBM for teaching._

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
