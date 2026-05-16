# Data Preview

## Generated Dataset

| Dataset | Rows |
| --- | ---: |
| Advisors | 24 |
| Lead Sources | 7 |
| Leads | 1,800 |
| Clients | 284 |
| Accounts | 383 |
| Advisor Activities | 2,115 |
| Opportunities | 1,800 |
| Monthly Asset Snapshots | 4,261 |
| Compensation | 576 |

## Tableau-Ready Extracts

| Extract | Rows | Grain |
| --- | ---: | --- |
| `mart_executive_scorecard.csv` | 23 | One row per reporting month |
| `mart_lead_source_quality.csv` | 7 | One row per lead source |
| `mart_advisor_productivity.csv` | 24 | One row per advisor |
| `mart_book_growth.csv` | 503 | One row per advisor per month |
| `mart_client_retention_risk.csv` | 284 | One row per client |
| `mart_compensation_alignment.csv` | 576 | One row per advisor per month |

## Lead Source Quality Snapshot

| Lead Source | Leads | Conversion Rate | Net New Assets | Net New Assets per Converted Client |
| --- | ---: | ---: | ---: | ---: |
| Employer Plan Rollover | 278 | 22.7% | $5.9M | $93K |
| Client Referral | 252 | 21.4% | $7.2M | $133K |
| Existing Client Expansion | 264 | 19.3% | $4.3M | $85K |
| Website Consultation Request | 227 | 15.9% | $2.8M | $78K |
| Branch Event | 249 | 12.0% | $2.0M | $68K |

## Advisor Productivity Snapshot

| Advisor | Team | Region | Converted Leads | Conversion Rate | Net New Assets |
| --- | --- | --- | ---: | ---: | ---: |
| Advisor 24 | Retirement Specialists | Southeast | 23 | 31.5% | $4.2M |
| Advisor 12 | Retirement Specialists | Northeast | 14 | 15.9% | $2.4M |
| Advisor 04 | Relationship Growth | West | 7 | 10.9% | $2.3M |
| Advisor 08 | Acquisition | West | 18 | 22.2% | $1.6M |
| Advisor 06 | Retirement Specialists | Northeast | 11 | 17.5% | $1.5M |

## Initial Interpretation

The first-pass results show a clear difference between lead volume and lead quality. Client Referral and Employer Plan Rollover sources produce stronger conversion and asset outcomes than broader paid acquisition sources. Advisor productivity is also uneven, with a small set of advisors driving a disproportionate share of net new assets.

These patterns create a strong Tableau story: where to invest in lead generation, which advisor behaviors to study, which client segments need outreach, and how compensation should be evaluated against productivity and growth.
