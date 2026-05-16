-- Executive distribution scorecard mart
-- Grain: one row per reporting month.

create or replace view mart_executive_scorecard as
with months as (
    select distinct snapshot_month as reporting_month
    from monthly_asset_snapshots
),
lead_metrics as (
    select
        date_trunc('month', created_date)::date as reporting_month,
        count(*) as new_leads,
        count(contacted_date) as contacted_leads,
        count(converted_date) as converted_leads,
        count(distinct client_id) as new_clients
    from leads
    group by date_trunc('month', created_date)::date
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

