-- Book growth mart
-- Grain: one row per advisor per month.

create or replace view mart_book_growth as
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

