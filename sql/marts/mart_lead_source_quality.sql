-- Lead source quality mart
-- Grain: one row per lead source.

create or replace view mart_lead_source_quality as
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
    group by
        l.lead_id,
        l.lead_source_id,
        l.client_id
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

