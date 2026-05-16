-- Compensation alignment mart
-- Grain: one row per advisor per month.

create or replace view mart_compensation_alignment as
with monthly_productivity as (
    select
        date_trunc('month', l.created_date)::date as performance_month,
        l.assigned_advisor_id as advisor_id,
        count(*) as leads_assigned,
        count(l.converted_date) as converted_leads
    from leads l
    group by
        date_trunc('month', l.created_date)::date,
        l.assigned_advisor_id
),
monthly_assets as (
    select
        snapshot_month as performance_month,
        advisor_id,
        sum(net_flows) as net_new_assets,
        sum(ending_assets) as ending_assets
    from monthly_asset_snapshots
    group by
        snapshot_month,
        advisor_id
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

