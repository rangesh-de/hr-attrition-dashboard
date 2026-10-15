# Building the HR attrition dashboard in Tableau Public

Time: about 3 hours the first time. All calculated fields can be copied and pasted.

The dashboard answers one question for an HR leader: **who is leaving, why, and what is it costing us?**

## 0. Before you start

1. `python scripts/prepare_data.py` (creates `dashboard/data/` and `dashboard/kpi_check.md`)
2. Install **Tableau Public** (free, works on Mac).

## 1. Connect the data

1. Tableau Public → **Text file** → `dashboard/data/hr_clean.csv`.
2. Add a second data source (Data → New Data Source) → `attrition_drivers.csv`. Keep it **separate**: it's already aggregated, so it must not be joined to employee rows.
3. In `hr_clean`, make sure `Employee Number` is a **Dimension** (drag it above the line in the Data pane). It's an ID, not something to sum.

## 2. Calculated fields (hr_clean)

```
Employees
COUNTD([Employee Number])

Leavers
SUM([Attrition Flag])

Attrition Rate
SUM([Attrition Flag]) / COUNTD([Employee Number])

Company Attrition Rate
{ FIXED : SUM([Attrition Flag]) / COUNTD([Employee Number]) }

Vs Company Average
[Attrition Rate] - SUM([Company Attrition Rate]) / COUNTD([Employee Number])
```

`Company Attrition Rate` uses a **FIXED LOD expression**. It ignores the chart's dimensions, so every bar can be compared with the company-wide rate. This is a common interview question.

**Cost of attrition, with a parameter so the viewer can change the assumption:**

1. Create Parameter → name `Replacement Cost %` → Float → Range 0.2 to 2.0, step 0.1, current value **0.5**. Right-click → Show Parameter.
2. Then:

```
Attrition Cost
SUM(IF [Attrition Flag] = 1 THEN [Annual Income] END) * [Replacement Cost %]
```

Replacement cost is often estimated at somewhere between half and twice a year's salary. The slider lets the viewer apply their own assumption instead of trusting yours. Say this in interviews: it shows business sense.

**Overtime callout:**

```
Overtime Attrition
SUM(IF [Over Time] = "Yes" THEN [Attrition Flag] END)
/ COUNTD(IF [Over Time] = "Yes" THEN [Employee Number] END)
```

## 3. Build the sheets

**KPI tiles (5 sheets).** Employees, Leavers, Attrition Rate, Overtime Attrition, Attrition Cost. Large text, small label. Format rates as % with one decimal and cost as currency in millions (Format → Numbers → Currency (Custom) → Display units: Millions).

**Attrition by department and role.** Rows: `Department`, `Job Role`. Columns: `Attrition Rate`. Sort descending. Add a reference line: right-click axis → Add Reference Line → Value: `Company Attrition Rate` (Average), label "Company avg". Color bars by `Vs Company Average` (diverging, orange above, blue below).

**Overtime effect.** Columns: `Over Time`. Rows: `Attrition Rate`. Label with `Leavers` and `Employees`. Usually the single clearest finding.

**Attrition by age and tenure (heatmap).** Columns: `Tenure Band`. Rows: `Age Band`. Color: `Attrition Rate`. Label: `Employees`. Sort the bands in order: right-click → Sort → Manual. This shows whether early-career, new hires are the risk.

**Income band.** Columns: `Income Band` (manual sort, low to high). Rows: `Attrition Rate`.

**Satisfaction (3 small sheets).** Build three small bar charts: `Job Satisfaction`, `Environment Satisfaction` and `Work Life Balance`, each on Columns with `Attrition Rate` on Rows. Stack them side by side in the dashboard.

**Key drivers (uses attrition_drivers source).** Rows: `Factor`, `Level`. Columns: `Attrition Rate` (use AVG; there's one row per level). Color: `Vs Company Avg`. Filter: `Small Group` = False. Sort `Factor` by `Factor Spread` descending, so the strongest drivers appear first. This chart summarizes everything on one screen.

## 4. Assemble the dashboard

Size: **Fixed, 1200 × 1000**.

```
┌──────────────────────────────────────────────────────────────────────┐
│ Employee Attrition: Who is leaving and what it costs  [Dept] [Gender]│
│                                                  [Replacement cost %]│
├────────────┬────────────┬────────────┬──────────────┬────────────────┤
│ Employees  │  Leavers   │ Attrition% │ Overtime att.│ Attrition cost │
├────────────┴────────────┴─────┬──────┴──────────────┴────────────────┤
│ Attrition by department & role│ Key drivers (ranked)                  │
│ (with company-average line)   │                                       │
├───────────────────────────────┤                                       │
│ Overtime effect               │                                       │
├───────────────────────────────┼───────────────────────────────────────┤
│ Age × tenure heatmap          │ Income band  │  Satisfaction (3 small)│
└───────────────────────────────┴───────────────────────────────────────┘
```

1. Filters (`Department`, `Gender`, `Job Level`): Apply to Worksheets → **All using this data source**. They won't affect the drivers chart, which uses the other source. Add a note under that chart: "Company-wide, not filtered."
2. Filter action: Dashboard → Actions → Filter. Source: department & role chart. Target: all `hr_clean` sheets. Clicking a role filters the page.
3. Titles state the takeaway: "Employees working overtime leave at 3x the rate", not "Attrition by overtime".

## 5. Check and publish

1. With filters cleared, compare the tiles with `dashboard/kpi_check.md` (cost at 50% replacement should match).
2. File → **Save to Tableau Public** → name it "HR Employee Attrition Analysis".
3. Add the link and a screenshot (`dashboard/screenshot.png`) to the README.

## Interview talking points

- **FIXED LOD** for the company average line: the benchmark stays constant while the bars change.
- **Parameter for cost:** I didn't hard-code an assumption; the viewer can change it.
- **Small groups flagged:** roles with fewer than 30 people are excluded from the driver ranking, because one or two leavers swing their rate wildly.
- **Correlation, not causation:** overtime and attrition move together, but the data can't prove one causes the other. The recommendation is to investigate overtime-heavy teams, not to claim overtime alone causes leaving.
- **About the data:** it's a fictional dataset created by IBM for teaching. Say so up front; the skills are what you're showing.
