# Personal Investor Distribution Analytics

## Project Status

**Version 0.1: SQL Analytics Foundation**

This version includes a synthetic Personal Investor Distribution dataset, documented business case, relational data model, KPI dictionary, SQL schema, reusable mart logic, data validation scripts, a local analytics database build, Tableau-ready CSV extracts, and an initial executive insights summary.

Current build outputs:

- 1,800 leads
- 284 clients
- 383 accounts
- 2,115 advisor activities
- 4,261 monthly asset snapshots
- 576 compensation records
- 6 Tableau-ready reporting extracts

## Portfolio Objective

This project demonstrates the ability to translate distribution leadership questions into a working analytics product: structured data, SQL transformations, KPI marts, data quality checks, Tableau-ready outputs, and executive recommendations.

## Career Alignment

This project is designed as a role-aligned analytics portfolio case study for a data analytics role supporting Personal Investor Distribution at Vanguard. It demonstrates how SQL, Tableau, Python, business requirements gathering, and executive storytelling can be combined to help distribution leaders make better decisions about client acquisition, advisor productivity, client engagement, asset growth, and compensation strategy.

The project is intentionally structured to reflect the responsibilities of a senior analytics partner:

- Translate ambiguous leadership questions into measurable KPIs and dashboard requirements
- Build scalable SQL reporting assets from CRM, lead, advisor activity, client, account, and compensation data
- Validate data quality, accuracy, and reasonableness before reporting
- Design executive-ready Tableau dashboards with clear visual hierarchy and actionable insights
- Use Python for advanced analytics such as forecasting, segmentation, and driver analysis
- Document analytical decisions, requirements, assumptions, and best practices

## Business Case

### Project Overview

This project simulates a Personal Investor Distribution analytics environment for a financial services organization. The goal is to transform CRM, lead generation, advisor activity, client, account, and compensation data into scalable SQL-based reporting assets and Tableau dashboards.

The project focuses on supporting business decisions related to lead generation, sales book management, advisor productivity, compensation strategy, client retention, and asset growth.

### Business Context

Personal Investor Distribution teams are responsible for acquiring clients, deepening relationships, retaining clients, and growing assets. Leaders need reliable analytics products that help them evaluate sales channel performance, advisor productivity, client engagement, and the effectiveness of lead generation programs.

### Key Business Questions

1. Which lead sources generate the highest conversion rates and strongest asset growth?
2. Which advisors are most effective at converting leads into clients?
3. How productive are advisors across calls, meetings, follow-ups, and closed opportunities?
4. Which client segments show the strongest growth or highest retention risk?
5. Does compensation align with advisor productivity and business value?
6. What recurring KPIs should leadership monitor to guide strategy?

### Intended Stakeholders

- Distribution leadership
- Sales managers
- Advisor team leads
- Marketing and lead generation teams
- Compensation strategy partners
- Business intelligence and analytics teams

### Expected Deliverables

- Synthetic CRM and sales distribution dataset
- SQL schema and relational data model
- SQL transformation scripts
- KPI views for recurring reporting
- Data validation checks
- Tableau dashboard
- Executive insights summary
- Advanced analytics notebook for forecasting, segmentation, or driver analysis

## Analytics Scope

The project is organized around seven analytics domains:

- Lead source quality and conversion
- Advisor activity and productivity
- Client acquisition, engagement, and retention
- Account and asset growth
- Sales book management
- Compensation alignment
- Forecasting, segmentation, and driver analysis

## Technical Approach

The SQL assets are written in a Postgres-style dialect so the project can demonstrate production-oriented SQL patterns such as relational constraints, reusable views, date logic, conditional aggregation, window functions, and Tableau-ready marts.

## Generate and Validate Synthetic Data

From the project root, run:

```bash
python3 scripts/generate_synthetic_data.py
python3 scripts/validate_generated_data.py
python3 scripts/build_analytics_database.py
```

The build creates a local SQLite database in `data/processed/` and exports reporting extracts for the dashboard suite:

- `mart_executive_scorecard.csv`
- `mart_lead_source_quality.csv`
- `mart_advisor_productivity.csv`
- `mart_book_growth.csv`
- `mart_client_retention_risk.csv`
- `mart_compensation_alignment.csv`

For a sample of the generated outputs and initial findings, see `docs/data_preview.md` and `docs/executive_summary.md`.

## Planned Repository Structure

```text
.
├── data/
│   ├── raw/
│   └── processed/
├── docs/
│   ├── role_alignment.md
│   ├── data_model.md
│   ├── kpi_dictionary.md
│   ├── dashboard_requirements.md
│   ├── analytics_roadmap.md
│   └── executive_summary.md
├── notebooks/
├── scripts/
├── sql/
│   ├── ddl/
│   ├── transformations/
│   ├── marts/
│   └── validation/
├── tableau/
└── README.md
```

## Initial KPI Framework

### Lead Generation

- Lead volume
- Contact rate
- Meeting conversion rate
- Lead-to-client conversion rate
- Funded client rate
- Initial assets by lead source
- Asset growth after conversion

### Advisor Productivity

- Leads assigned
- Calls completed
- Meetings held
- Follow-ups completed
- Opportunities closed
- New clients acquired
- New assets gathered
- Productivity by advisor, team, region, and tenure

### Book Management

- Beginning assets under management
- Ending assets under management
- Net new assets
- Asset retention rate
- Client retention rate
- Segment-level growth
- At-risk client counts

### Compensation Alignment

- Incentive payout by advisor
- Payout per converted client
- Payout per dollar of net new assets
- Productivity rank versus compensation rank
- Growth contribution versus payout share

## Executive Reporting Goal

The final reporting layer should help leadership identify which lead sources deserve investment, which advisors need coaching or capacity support, which client segments require engagement, and whether incentive compensation is rewarding the outcomes that matter most to the business.

## Target Dashboard Suite

- Executive Distribution Scorecard
- Lead Source Quality Dashboard
- Advisor Productivity Dashboard
- Client Segment and Retention Dashboard
- Book Growth and Net New Assets Dashboard
- Compensation Alignment Dashboard

## Advanced Analytics Extensions

- Forecast monthly lead volume, conversion, and net new assets
- Segment clients by asset level, engagement behavior, and growth potential
- Identify drivers of lead conversion and client retention
- Flag clients with elevated retention risk based on engagement and asset movement
- Compare compensation outcomes with productivity, growth, and client quality metrics
