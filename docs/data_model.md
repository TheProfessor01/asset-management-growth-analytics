# Data Model

## Purpose

The data model simulates a Personal Investor Distribution analytics environment. It is designed to support SQL-based analysis of lead generation, advisor productivity, client engagement, account growth, compensation alignment, and executive reporting.

## Modeling Approach

The model separates operational entities from analytical outputs:

- Source-style tables represent CRM, sales, client, account, asset, and compensation data.
- Transformation queries will standardize business logic and calculate reusable measures.
- Mart tables or views will provide Tableau-ready reporting layers for leadership dashboards.

## Core Entities

### advisors

Represents financial advisors or relationship managers responsible for lead follow-up, client engagement, and book growth.

Grain: one row per advisor.

Key fields:

- `advisor_id`
- `advisor_name`
- `team`
- `region`
- `hire_date`
- `tenure_band`
- `advisor_status`

### lead_sources

Represents the channels or programs that generate leads.

Grain: one row per lead source.

Key fields:

- `lead_source_id`
- `lead_source_name`
- `channel`
- `source_category`
- `is_paid_source`

### leads

Represents prospective clients entering the distribution funnel.

Grain: one row per lead.

Key fields:

- `lead_id`
- `lead_source_id`
- `assigned_advisor_id`
- `created_date`
- `contacted_date`
- `qualified_date`
- `converted_date`
- `lead_status`
- `estimated_asset_band`
- `client_id`

### clients

Represents clients acquired or served by the distribution organization.

Grain: one row per client.

Key fields:

- `client_id`
- `primary_advisor_id`
- `client_since_date`
- `client_segment`
- `age_band`
- `household_income_band`
- `risk_tolerance`
- `client_status`

### accounts

Represents investment or advisory accounts held by clients.

Grain: one row per account.

Key fields:

- `account_id`
- `client_id`
- `account_type`
- `open_date`
- `close_date`
- `account_status`

### advisor_activities

Represents advisor interactions and sales activities.

Grain: one row per advisor activity.

Key fields:

- `activity_id`
- `advisor_id`
- `lead_id`
- `client_id`
- `activity_date`
- `activity_type`
- `activity_outcome`
- `duration_minutes`

### opportunities

Represents sales opportunities associated with leads or clients.

Grain: one row per opportunity.

Key fields:

- `opportunity_id`
- `advisor_id`
- `lead_id`
- `client_id`
- `created_date`
- `closed_date`
- `opportunity_stage`
- `opportunity_status`
- `estimated_assets`
- `closed_assets`

### monthly_asset_snapshots

Represents monthly account balance snapshots used to measure asset growth, retention, and book management.

Grain: one row per account per month.

Key fields:

- `snapshot_month`
- `account_id`
- `client_id`
- `advisor_id`
- `beginning_assets`
- `net_flows`
- `market_change`
- `ending_assets`

### compensation

Represents advisor compensation and incentive payouts.

Grain: one row per advisor per month.

Key fields:

- `compensation_month`
- `advisor_id`
- `base_compensation`
- `incentive_payout`
- `total_compensation`
- `compensation_plan`

## Relationship Summary

```text
lead_sources 1--many leads
advisors 1--many leads
advisors 1--many advisor_activities
advisors 1--many opportunities
advisors 1--many clients
clients 1--many accounts
clients 1--many advisor_activities
clients 1--many opportunities
accounts 1--many monthly_asset_snapshots
advisors 1--many compensation
```

## Reporting Marts

Planned Tableau-ready marts:

- `mart_executive_scorecard`
- `mart_lead_source_quality`
- `mart_advisor_productivity`
- `mart_book_growth`
- `mart_client_retention_risk`
- `mart_compensation_alignment`

## Design Assumptions

- A lead may convert to one client.
- A client has one primary advisor at a point in time.
- A client may have multiple accounts.
- Asset snapshots are monthly and account-level.
- Compensation is monthly and advisor-level.
- Synthetic data will intentionally include realistic variation by lead source, advisor productivity, client segment, and compensation efficiency.

