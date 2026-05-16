-- Advisor productivity mart
-- Grain: one row per advisor.

create or replace view mart_advisor_productivity as
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

