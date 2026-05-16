"""Build a local SQLite analytics database and Tableau-ready CSV extracts."""

from __future__ import annotations

import csv
import sqlite3
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
DB_PATH = PROCESSED_DIR / "distribution_analytics.sqlite"


SOURCE_TABLES = [
    "advisors",
    "lead_sources",
    "clients",
    "leads",
    "accounts",
    "advisor_activities",
    "opportunities",
    "monthly_asset_snapshots",
    "compensation",
]

EXTRACT_VIEWS = [
    "mart_executive_scorecard",
    "mart_lead_source_quality",
    "mart_advisor_productivity",
    "mart_book_growth",
    "mart_client_retention_risk",
    "mart_compensation_alignment",
]


DDL = """
drop table if exists advisors;
drop table if exists lead_sources;
drop table if exists clients;
drop table if exists leads;
drop table if exists accounts;
drop table if exists advisor_activities;
drop table if exists opportunities;
drop table if exists monthly_asset_snapshots;
drop table if exists compensation;

create table advisors (
    advisor_id integer primary key,
    advisor_name text not null,
    team text not null,
    region text not null,
    hire_date text not null,
    tenure_band text not null,
    advisor_status text not null
);

create table lead_sources (
    lead_source_id integer primary key,
    lead_source_name text not null,
    channel text not null,
    source_category text not null,
    is_paid_source text not null
);

create table clients (
    client_id integer primary key,
    primary_advisor_id integer not null,
    client_since_date text not null,
    client_segment text not null,
    age_band text not null,
    household_income_band text not null,
    risk_tolerance text not null,
    client_status text not null
);

create table leads (
    lead_id integer primary key,
    lead_source_id integer not null,
    assigned_advisor_id integer not null,
    created_date text not null,
    contacted_date text,
    qualified_date text,
    converted_date text,
    lead_status text not null,
    estimated_asset_band text not null,
    client_id integer
);

create table accounts (
    account_id integer primary key,
    client_id integer not null,
    account_type text not null,
    open_date text not null,
    close_date text,
    account_status text not null
);

create table advisor_activities (
    activity_id integer primary key,
    advisor_id integer not null,
    lead_id integer,
    client_id integer,
    activity_date text not null,
    activity_type text not null,
    activity_outcome text not null,
    duration_minutes integer
);

create table opportunities (
    opportunity_id integer primary key,
    advisor_id integer not null,
    lead_id integer,
    client_id integer,
    created_date text not null,
    closed_date text,
    opportunity_stage text not null,
    opportunity_status text not null,
    estimated_assets real,
    closed_assets real
);

create table monthly_asset_snapshots (
    snapshot_month text not null,
    account_id integer not null,
    client_id integer not null,
    advisor_id integer not null,
    beginning_assets real not null,
    net_flows real not null,
    market_change real not null,
    ending_assets real not null,
    primary key (snapshot_month, account_id)
);

create table compensation (
    compensation_month text not null,
    advisor_id integer not null,
    base_compensation real not null,
    incentive_payout real not null,
    total_compensation real not null,
    compensation_plan text not null,
    primary key (compensation_month, advisor_id)
);
"""


MART_SQL = """
drop view if exists mart_lead_source_quality;
create view mart_lead_source_quality as
with converted_client_assets as (
    select
        l.lead_id,
        l.lead_source_id,
        l.client_id,
        sum(mas.net_flows) as net_new_assets,
        max(mas.ending_assets) as latest_assets
    from leads l
    left join monthly_asset_snapshots mas
        on l.client_id = mas.client_id
    where l.client_id is not null
    group by l.lead_id, l.lead_source_id, l.client_id
),
lead_rollup as (
    select
        ls.lead_source_id,
        ls.lead_source_name,
        ls.channel,
        ls.source_category,
        ls.is_paid_source,
        count(l.lead_id) as lead_count,
        count(l.contacted_date) as contacted_leads,
        count(l.qualified_date) as qualified_leads,
        count(l.converted_date) as converted_leads,
        count(distinct l.client_id) as converted_clients,
        sum(case when cca.latest_assets > 0 then 1 else 0 end) as funded_clients,
        coalesce(sum(cca.net_new_assets), 0) as net_new_assets,
        avg(cca.latest_assets) as average_latest_assets
    from lead_sources ls
    left join leads l
        on ls.lead_source_id = l.lead_source_id
    left join converted_client_assets cca
        on l.lead_id = cca.lead_id
    group by
        ls.lead_source_id,
        ls.lead_source_name,
        ls.channel,
        ls.source_category,
        ls.is_paid_source
)
select
    *,
    contacted_leads * 1.0 / nullif(lead_count, 0) as contact_rate,
    qualified_leads * 1.0 / nullif(contacted_leads, 0) as qualification_rate,
    converted_leads * 1.0 / nullif(lead_count, 0) as lead_to_client_conversion_rate,
    funded_clients * 1.0 / nullif(converted_clients, 0) as funded_client_rate,
    net_new_assets / nullif(converted_clients, 0) as net_new_assets_per_converted_client
from lead_rollup;

drop view if exists mart_advisor_productivity;
create view mart_advisor_productivity as
with lead_metrics as (
    select
        assigned_advisor_id as advisor_id,
        count(*) as leads_assigned,
        count(contacted_date) as leads_contacted,
        count(qualified_date) as leads_qualified,
        count(converted_date) as leads_converted,
        count(distinct client_id) as new_clients_acquired
    from leads
    group by assigned_advisor_id
),
activity_metrics as (
    select
        advisor_id,
        sum(case when activity_type = 'Call' then 1 else 0 end) as calls_completed,
        sum(case when activity_type = 'Meeting' then 1 else 0 end) as meetings_held,
        sum(case when activity_type = 'Follow-up' then 1 else 0 end) as follow_ups_completed,
        count(*) as total_activities
    from advisor_activities
    group by advisor_id
),
opportunity_metrics as (
    select
        advisor_id,
        count(*) as opportunities_created,
        sum(case when opportunity_status = 'Closed Won' then 1 else 0 end) as opportunities_closed_won,
        coalesce(sum(case when opportunity_status = 'Closed Won' then closed_assets else 0 end), 0) as closed_assets
    from opportunities
    group by advisor_id
),
asset_metrics as (
    select
        advisor_id,
        coalesce(sum(net_flows), 0) as net_new_assets,
        coalesce(sum(ending_assets), 0) as ending_assets
    from monthly_asset_snapshots
    group by advisor_id
)
select
    a.advisor_id,
    a.advisor_name,
    a.team,
    a.region,
    a.tenure_band,
    a.advisor_status,
    coalesce(lm.leads_assigned, 0) as leads_assigned,
    coalesce(lm.leads_contacted, 0) as leads_contacted,
    coalesce(lm.leads_qualified, 0) as leads_qualified,
    coalesce(lm.leads_converted, 0) as leads_converted,
    coalesce(lm.new_clients_acquired, 0) as new_clients_acquired,
    coalesce(am.calls_completed, 0) as calls_completed,
    coalesce(am.meetings_held, 0) as meetings_held,
    coalesce(am.follow_ups_completed, 0) as follow_ups_completed,
    coalesce(am.total_activities, 0) as total_activities,
    coalesce(om.opportunities_created, 0) as opportunities_created,
    coalesce(om.opportunities_closed_won, 0) as opportunities_closed_won,
    coalesce(om.closed_assets, 0) as closed_assets,
    coalesce(asm.net_new_assets, 0) as net_new_assets,
    coalesce(asm.ending_assets, 0) as ending_assets,
    coalesce(lm.leads_contacted, 0) * 1.0 / nullif(lm.leads_assigned, 0) as contact_rate,
    coalesce(lm.leads_converted, 0) * 1.0 / nullif(lm.leads_assigned, 0) as advisor_conversion_rate,
    coalesce(asm.net_new_assets, 0) / nullif(lm.leads_converted, 0) as net_new_assets_per_converted_lead
from advisors a
left join lead_metrics lm
    on a.advisor_id = lm.advisor_id
left join activity_metrics am
    on a.advisor_id = am.advisor_id
left join opportunity_metrics om
    on a.advisor_id = om.advisor_id
left join asset_metrics asm
    on a.advisor_id = asm.advisor_id;

drop view if exists mart_book_growth;
create view mart_book_growth as
select
    mas.snapshot_month,
    a.advisor_id,
    a.advisor_name,
    a.team,
    a.region,
    count(distinct mas.client_id) as active_clients,
    count(distinct mas.account_id) as active_accounts,
    sum(mas.beginning_assets) as beginning_aum,
    sum(mas.net_flows) as net_new_assets,
    sum(mas.market_change) as market_change,
    sum(mas.ending_assets) as ending_aum,
    (sum(mas.ending_assets) - sum(mas.beginning_assets)) / nullif(sum(mas.beginning_assets), 0) as aum_growth_rate,
    1 - (abs(sum(case when mas.net_flows < 0 then mas.net_flows else 0 end)) / nullif(sum(mas.beginning_assets), 0)) as asset_retention_rate
from monthly_asset_snapshots mas
join advisors a
    on mas.advisor_id = a.advisor_id
group by
    mas.snapshot_month,
    a.advisor_id,
    a.advisor_name,
    a.team,
    a.region;

drop view if exists mart_client_retention_risk;
create view mart_client_retention_risk as
with latest_month as (
    select max(snapshot_month) as snapshot_month
    from monthly_asset_snapshots
),
latest_assets as (
    select
        mas.client_id,
        mas.advisor_id,
        sum(mas.ending_assets) as latest_assets
    from monthly_asset_snapshots mas
    join latest_month lm
        on mas.snapshot_month = lm.snapshot_month
    group by mas.client_id, mas.advisor_id
),
last_contact as (
    select
        client_id,
        max(activity_date) as last_contact_date,
        max(case when activity_type = 'Meeting' then activity_date end) as last_meeting_date
    from advisor_activities
    where client_id is not null
    group by client_id
),
recent_flows as (
    select
        mas.client_id,
        sum(mas.net_flows) as trailing_3_month_net_flows
    from monthly_asset_snapshots mas
    join latest_month lm
        on mas.snapshot_month >= date(lm.snapshot_month, '-2 months')
    group by mas.client_id
)
select
    c.client_id,
    c.primary_advisor_id as advisor_id,
    a.advisor_name,
    a.team,
    a.region,
    c.client_segment,
    c.age_band,
    c.household_income_band,
    c.risk_tolerance,
    c.client_status,
    coalesce(la.latest_assets, 0) as latest_assets,
    lc.last_contact_date,
    lc.last_meeting_date,
    cast(julianday((select snapshot_month from latest_month)) - julianday(lc.last_contact_date) as integer) as days_since_last_contact,
    coalesce(rf.trailing_3_month_net_flows, 0) as trailing_3_month_net_flows,
    case
        when lc.last_contact_date is null then 1
        when julianday((select snapshot_month from latest_month)) - julianday(lc.last_contact_date) > 120 then 1
        when coalesce(rf.trailing_3_month_net_flows, 0) < 0 then 1
        when c.client_segment = 'High Value'
             and (lc.last_meeting_date is null
                  or julianday((select snapshot_month from latest_month)) - julianday(lc.last_meeting_date) > 180) then 1
        else 0
    end as at_risk_flag
from clients c
join advisors a
    on c.primary_advisor_id = a.advisor_id
left join latest_assets la
    on c.client_id = la.client_id
left join last_contact lc
    on c.client_id = lc.client_id
left join recent_flows rf
    on c.client_id = rf.client_id;

drop view if exists mart_compensation_alignment;
create view mart_compensation_alignment as
with monthly_productivity as (
    select
        substr(created_date, 1, 7) || '-01' as performance_month,
        assigned_advisor_id as advisor_id,
        count(*) as leads_assigned,
        count(converted_date) as converted_leads
    from leads
    group by substr(created_date, 1, 7) || '-01', assigned_advisor_id
),
monthly_assets as (
    select
        snapshot_month as performance_month,
        advisor_id,
        sum(net_flows) as net_new_assets,
        sum(ending_assets) as ending_assets
    from monthly_asset_snapshots
    group by snapshot_month, advisor_id
),
base as (
    select
        c.compensation_month,
        c.advisor_id,
        a.advisor_name,
        a.team,
        a.region,
        c.compensation_plan,
        c.base_compensation,
        c.incentive_payout,
        c.total_compensation,
        coalesce(mp.leads_assigned, 0) as leads_assigned,
        coalesce(mp.converted_leads, 0) as converted_leads,
        coalesce(ma.net_new_assets, 0) as net_new_assets,
        coalesce(ma.ending_assets, 0) as ending_assets
    from compensation c
    join advisors a
        on c.advisor_id = a.advisor_id
    left join monthly_productivity mp
        on c.advisor_id = mp.advisor_id
        and c.compensation_month = mp.performance_month
    left join monthly_assets ma
        on c.advisor_id = ma.advisor_id
        and c.compensation_month = ma.performance_month
)
select
    *,
    incentive_payout / nullif(converted_leads, 0) as payout_per_converted_lead,
    incentive_payout / nullif(net_new_assets, 0) as payout_per_dollar_net_new_assets,
    percent_rank() over (partition by compensation_month order by total_compensation) as compensation_percentile,
    percent_rank() over (partition by compensation_month order by net_new_assets) as growth_percentile,
    percent_rank() over (partition by compensation_month order by converted_leads) as conversion_percentile
from base;

drop view if exists mart_executive_scorecard;
create view mart_executive_scorecard as
with months as (
    select distinct snapshot_month as reporting_month
    from monthly_asset_snapshots
),
lead_metrics as (
    select
        substr(created_date, 1, 7) || '-01' as reporting_month,
        count(*) as new_leads,
        count(contacted_date) as contacted_leads,
        count(converted_date) as converted_leads,
        count(distinct client_id) as new_clients
    from leads
    group by substr(created_date, 1, 7) || '-01'
),
asset_metrics as (
    select
        snapshot_month as reporting_month,
        sum(beginning_assets) as beginning_aum,
        sum(net_flows) as net_new_assets,
        sum(market_change) as market_change,
        sum(ending_assets) as ending_aum,
        count(distinct client_id) as active_clients
    from monthly_asset_snapshots
    group by snapshot_month
),
risk_metrics as (
    select
        (select max(snapshot_month) from monthly_asset_snapshots) as reporting_month,
        count(*) as clients_reviewed,
        sum(at_risk_flag) as at_risk_clients
    from mart_client_retention_risk
),
comp_metrics as (
    select
        compensation_month as reporting_month,
        sum(incentive_payout) as incentive_payout,
        sum(total_compensation) as total_compensation
    from compensation
    group by compensation_month
)
select
    m.reporting_month,
    coalesce(lm.new_leads, 0) as new_leads,
    coalesce(lm.contacted_leads, 0) as contacted_leads,
    coalesce(lm.converted_leads, 0) as converted_leads,
    coalesce(lm.new_clients, 0) as new_clients,
    coalesce(lm.contacted_leads, 0) * 1.0 / nullif(lm.new_leads, 0) as contact_rate,
    coalesce(lm.converted_leads, 0) * 1.0 / nullif(lm.new_leads, 0) as conversion_rate,
    coalesce(am.beginning_aum, 0) as beginning_aum,
    coalesce(am.net_new_assets, 0) as net_new_assets,
    coalesce(am.market_change, 0) as market_change,
    coalesce(am.ending_aum, 0) as ending_aum,
    coalesce(am.active_clients, 0) as active_clients,
    (am.ending_aum - am.beginning_aum) / nullif(am.beginning_aum, 0) as aum_growth_rate,
    case when rm.reporting_month = m.reporting_month then rm.at_risk_clients else null end as at_risk_clients,
    coalesce(cm.incentive_payout, 0) as incentive_payout,
    coalesce(cm.total_compensation, 0) as total_compensation,
    coalesce(am.net_new_assets, 0) / nullif(cm.incentive_payout, 0) as net_new_assets_per_incentive_dollar
from months m
left join lead_metrics lm
    on m.reporting_month = lm.reporting_month
left join asset_metrics am
    on m.reporting_month = am.reporting_month
left join risk_metrics rm
    on m.reporting_month = rm.reporting_month
left join comp_metrics cm
    on m.reporting_month = cm.reporting_month;
"""


def read_csv_rows(table: str) -> tuple[list[str], list[dict]]:
    path = RAW_DIR / f"{table}.csv"
    with path.open(newline="") as handle:
        reader = csv.DictReader(handle)
        return reader.fieldnames or [], list(reader)


def normalize_value(value: str) -> str | None:
    return value if value != "" else None


def load_table(connection: sqlite3.Connection, table: str) -> int:
    columns, rows = read_csv_rows(table)
    placeholders = ", ".join(["?"] * len(columns))
    column_list = ", ".join(columns)
    values = [[normalize_value(row[column]) for column in columns] for row in rows]
    connection.executemany(f"insert into {table} ({column_list}) values ({placeholders})", values)
    return len(rows)


def export_view(connection: sqlite3.Connection, view_name: str) -> int:
    cursor = connection.execute(f"select * from {view_name}")
    rows = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    path = PROCESSED_DIR / f"{view_name}.csv"
    with path.open("w", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(columns)
        writer.writerows(rows)
    return len(rows)


def main() -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    if DB_PATH.exists():
        DB_PATH.unlink()

    with sqlite3.connect(DB_PATH) as connection:
        connection.executescript(DDL)

        print("Loaded source tables")
        for table in SOURCE_TABLES:
            row_count = load_table(connection, table)
            print(f"{table}: {row_count:,} rows")

        connection.executescript(MART_SQL)

        print("\nExported Tableau-ready extracts")
        for view in EXTRACT_VIEWS:
            row_count = export_view(connection, view)
            print(f"{view}: {row_count:,} rows")

    print(f"\nBuilt database: {DB_PATH}")


if __name__ == "__main__":
    main()

