# KPI Dictionary

## Purpose

This KPI dictionary defines the recurring metrics used across the SQL marts and Tableau dashboards. Each KPI is tied to a business question and includes the intended calculation logic.

## Lead Generation KPIs

| KPI | Business Question | Calculation |
| --- | --- | --- |
| Lead Volume | How many prospects entered the funnel? | Count of leads created in the period |
| Contact Rate | Are advisors reaching assigned leads? | Contacted leads / total leads |
| Qualification Rate | Are leads becoming viable prospects? | Qualified leads / contacted leads |
| Lead-to-Client Conversion Rate | Which sources and advisors convert leads most effectively? | Converted leads / total leads |
| Funded Client Rate | Which sources produce clients who open funded accounts? | Converted clients with ending assets greater than 0 / converted clients |
| Average Initial Assets | Which sources produce higher-value clients? | Average first-month ending assets for converted clients |
| Net New Assets from Converted Leads | Which sources create asset growth? | Sum of net flows for clients converted from leads |

## Advisor Productivity KPIs

| KPI | Business Question | Calculation |
| --- | --- | --- |
| Leads Assigned | What is each advisor's lead workload? | Count of leads assigned to advisor |
| Calls Completed | Are advisors completing outbound activity? | Count of activities where `activity_type = 'Call'` |
| Meetings Held | Are advisors moving prospects into deeper engagement? | Count of activities where `activity_type = 'Meeting'` |
| Follow-Ups Completed | Are advisors maintaining pipeline discipline? | Count of activities where `activity_type = 'Follow-up'` |
| Opportunities Closed | Are advisors converting pipeline into outcomes? | Count of opportunities with closed status |
| New Clients Acquired | Which advisors are acquiring clients? | Count of converted leads by assigned advisor |
| New Assets Gathered | Which advisors are bringing in assets? | Sum of closed assets or net flows from newly converted clients |
| Advisor Conversion Rate | Which advisors convert leads most effectively? | Converted leads / leads assigned |
| Assets per Converted Lead | Which advisors create higher-value outcomes? | New assets gathered / converted leads |

## Book Growth KPIs

| KPI | Business Question | Calculation |
| --- | --- | --- |
| Beginning AUM | What asset base did the advisor start with? | Sum of beginning assets for the period |
| Ending AUM | What asset base did the advisor end with? | Sum of ending assets for the period |
| Net New Assets | How much growth came from flows? | Sum of net flows |
| Market Change | How much growth came from market movement? | Sum of market change |
| AUM Growth Rate | How quickly is the book growing? | (Ending AUM - Beginning AUM) / Beginning AUM |
| Asset Retention Rate | Are advisors retaining client assets? | 1 - asset outflows / beginning assets |
| Client Retention Rate | Are clients staying with the firm? | Retained clients / beginning clients |

## Client Engagement and Risk KPIs

| KPI | Business Question | Calculation |
| --- | --- | --- |
| Engagement Rate | Which segments are being actively served? | Clients with activity in period / total active clients |
| Days Since Last Contact | Which clients may need outreach? | Report date - most recent activity date |
| At-Risk Client Count | Which clients show retention risk? | Count of clients meeting risk criteria |
| Under-Engaged High-Value Clients | Which valuable clients need attention? | Clients above asset threshold with no recent activity |
| Asset Decline Rate | Which segments are shrinking? | Clients with negative net flows or declining ending assets / total clients |

## Compensation Alignment KPIs

| KPI | Business Question | Calculation |
| --- | --- | --- |
| Total Compensation | What is the all-in compensation level? | Base compensation + incentive payout |
| Incentive Payout | How much variable pay was awarded? | Sum of incentive payout |
| Payout per Converted Client | Is acquisition incentive-efficient? | Incentive payout / converted clients |
| Payout per Dollar of Net New Assets | Is asset growth incentive-efficient? | Incentive payout / net new assets |
| Productivity Rank | Which advisors produce the most activity and outcomes? | Rank based on weighted productivity score |
| Compensation Rank | Which advisors receive the most compensation? | Rank based on total compensation |
| Rank Variance | Does compensation align with productivity? | Compensation rank - productivity rank |
| Payout Share versus Growth Share | Are payouts aligned with business contribution? | Advisor payout share compared with advisor net-new-asset share |

## Executive KPIs

| KPI | Business Question | Calculation |
| --- | --- | --- |
| Monthly Lead Volume | Is demand rising or falling? | Count of leads created by month |
| Monthly Conversion Rate | Is funnel quality improving? | Converted leads / total leads by month |
| Monthly Net New Assets | Is the distribution organization growing assets? | Sum of net flows by month |
| Monthly Retention Rate | Are clients and assets being retained? | Retention KPIs by month |
| Advisor Productivity Index | Which teams are executing best? | Weighted score of activity, conversion, and asset outcomes |
| Compensation Efficiency | Are incentives producing business value? | Net new assets or converted clients per incentive dollar |

## At-Risk Client Definition

A client will be flagged as at risk when one or more of the following conditions are met:

- No advisor contact in the last 120 days
- Negative net flows over the last three months
- Ending assets declined by more than 10 percent over the last three months
- High-value segment with no meeting in the last 180 days

## Productivity Index Draft

The advisor productivity index will be a weighted score:

```text
(0.20 * normalized calls completed)
+ (0.20 * normalized meetings held)
+ (0.25 * normalized converted clients)
+ (0.25 * normalized net new assets)
+ (0.10 * normalized follow-ups completed)
```

The weights can be adjusted after dashboard review to better reflect leadership priorities.

