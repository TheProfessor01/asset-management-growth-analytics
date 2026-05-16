-- Data validation checks for source tables and reporting marts.
-- Expected result: each query should return zero rows unless noted otherwise.

-- Leads cannot be converted before they are created.
select *
from leads
where converted_date < created_date;

-- Leads cannot be contacted before they are created.
select *
from leads
where contacted_date < created_date;

-- Leads with converted status should have a converted date and client id.
select *
from leads
where lead_status = 'Converted'
  and (converted_date is null or client_id is null);

-- Every client should have a valid primary advisor.
select c.*
from clients c
left join advisors a
    on c.primary_advisor_id = a.advisor_id
where a.advisor_id is null;

-- Accounts cannot close before they open.
select *
from accounts
where close_date < open_date;

-- Asset snapshots should reconcile beginning assets, net flows, market change, and ending assets.
select *
from monthly_asset_snapshots
where round(beginning_assets + net_flows + market_change, 2) <> round(ending_assets, 2);

-- Compensation totals should reconcile base and incentive pay.
select *
from compensation
where round(base_compensation + incentive_payout, 2) <> round(total_compensation, 2);

-- Advisor activity should connect to either a lead or a client.
select *
from advisor_activities
where lead_id is null
  and client_id is null;

-- Closed-won opportunities should have closed assets.
select *
from opportunities
where opportunity_status = 'Closed Won'
  and (closed_assets is null or closed_assets <= 0);

