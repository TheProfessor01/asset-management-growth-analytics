"""Generate synthetic Personal Investor Distribution source data.

The generated CSVs are intentionally patterned, not random noise. Lead sources,
advisor productivity, client segment, and compensation outcomes vary enough to
support meaningful SQL analysis and executive dashboarding.
"""

from __future__ import annotations

import csv
import random
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


random.seed(42)

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"

START_DATE = date(2024, 1, 1)
END_DATE = date(2025, 12, 31)


@dataclass(frozen=True)
class LeadSourceProfile:
    lead_source_id: int
    lead_source_name: str
    channel: str
    source_category: str
    is_paid_source: bool
    conversion_rate: float
    quality_multiplier: float


LEAD_SOURCES = [
    LeadSourceProfile(1, "Website Consultation Request", "Digital", "Inbound", True, 0.31, 1.10),
    LeadSourceProfile(2, "Retirement Planning Webinar", "Digital", "Education", True, 0.24, 1.20),
    LeadSourceProfile(3, "Employer Plan Rollover", "Workplace", "Rollover", False, 0.38, 1.35),
    LeadSourceProfile(4, "Client Referral", "Referral", "Referral", False, 0.44, 1.45),
    LeadSourceProfile(5, "Paid Search", "Digital", "Paid Media", True, 0.18, 0.85),
    LeadSourceProfile(6, "Branch Event", "Event", "Local Event", True, 0.22, 0.95),
    LeadSourceProfile(7, "Existing Client Expansion", "Relationship", "Cross-Sell", False, 0.41, 1.30),
]

REGIONS = ["Northeast", "Southeast", "Midwest", "West"]
TEAMS = ["Acquisition", "Relationship Growth", "Retirement Specialists", "High Value"]
TENURE_BANDS = ["0-1 years", "1-3 years", "3-5 years", "5+ years"]
CLIENT_SEGMENTS = ["Emerging", "Core", "Mass Affluent", "High Value"]
AGE_BANDS = ["Under 35", "35-44", "45-54", "55-64", "65+"]
INCOME_BANDS = ["Under $100K", "$100K-$199K", "$200K-$349K", "$350K+"]
RISK_TOLERANCE = ["Conservative", "Moderate", "Growth", "Aggressive"]
ACCOUNT_TYPES = ["Brokerage", "IRA", "Roth IRA", "Managed Account"]


def daterange_months(start: date, end: date) -> list[date]:
    months = []
    current = date(start.year, start.month, 1)
    while current <= end:
        months.append(current)
        if current.month == 12:
            current = date(current.year + 1, 1, 1)
        else:
            current = date(current.year, current.month + 1, 1)
    return months


def random_date(start: date, end: date) -> date:
    days = (end - start).days
    return start + timedelta(days=random.randint(0, days))


def write_csv(filename: str, rows: list[dict]) -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    path = RAW_DIR / filename
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def money(value: float) -> str:
    return f"{value:.2f}"


def weighted_choice(items: list[str], weights: list[float]) -> str:
    return random.choices(items, weights=weights, k=1)[0]


def generate_advisors() -> list[dict]:
    advisors = []
    for advisor_id in range(1, 25):
        tenure_band = weighted_choice(TENURE_BANDS, [0.18, 0.28, 0.24, 0.30])
        advisors.append(
            {
                "advisor_id": advisor_id,
                "advisor_name": f"Advisor {advisor_id:02d}",
                "team": random.choice(TEAMS),
                "region": random.choice(REGIONS),
                "hire_date": random_date(date(2015, 1, 1), date(2024, 6, 30)).isoformat(),
                "tenure_band": tenure_band,
                "advisor_status": "Active",
                "productivity_factor": round(random.uniform(0.75, 1.35), 3),
            }
        )
    return advisors


def generate_lead_sources() -> list[dict]:
    return [
        {
            "lead_source_id": source.lead_source_id,
            "lead_source_name": source.lead_source_name,
            "channel": source.channel,
            "source_category": source.source_category,
            "is_paid_source": source.is_paid_source,
        }
        for source in LEAD_SOURCES
    ]


def asset_band_amount(segment: str, quality_multiplier: float) -> float:
    ranges = {
        "Emerging": (25000, 90000),
        "Core": (90000, 250000),
        "Mass Affluent": (250000, 850000),
        "High Value": (850000, 2500000),
    }
    low, high = ranges[segment]
    return random.uniform(low, high) * quality_multiplier


def generate_business_data(advisors: list[dict]) -> dict[str, list[dict]]:
    source_by_id = {source.lead_source_id: source for source in LEAD_SOURCES}
    advisor_by_id = {advisor["advisor_id"]: advisor for advisor in advisors}

    leads = []
    clients = []
    accounts = []
    activities = []
    opportunities = []
    asset_snapshots = []
    compensation = []

    lead_id = 1
    client_id = 1
    account_id = 1
    activity_id = 1
    opportunity_id = 1

    for _ in range(1800):
        source = random.choice(LEAD_SOURCES)
        advisor = random.choice(advisors)
        created_date = random_date(START_DATE, END_DATE)
        productivity_factor = advisor["productivity_factor"]
        conversion_probability = min(source.conversion_rate * productivity_factor, 0.72)

        contacted = random.random() < min(0.62 * productivity_factor, 0.96)
        qualified = contacted and random.random() < 0.68
        converted = qualified and random.random() < conversion_probability

        contacted_date = created_date + timedelta(days=random.randint(1, 10)) if contacted else None
        qualified_date = contacted_date + timedelta(days=random.randint(1, 14)) if qualified else None
        converted_date = qualified_date + timedelta(days=random.randint(3, 45)) if converted else None

        segment = weighted_choice(CLIENT_SEGMENTS, [0.32, 0.36, 0.22, 0.10])
        lead_client_id = client_id if converted else ""
        lead_status = "Converted" if converted else ("Qualified" if qualified else ("Contacted" if contacted else "New"))

        leads.append(
            {
                "lead_id": lead_id,
                "lead_source_id": source.lead_source_id,
                "assigned_advisor_id": advisor["advisor_id"],
                "created_date": created_date.isoformat(),
                "contacted_date": contacted_date.isoformat() if contacted_date else "",
                "qualified_date": qualified_date.isoformat() if qualified_date else "",
                "converted_date": converted_date.isoformat() if converted_date else "",
                "lead_status": lead_status,
                "estimated_asset_band": segment,
                "client_id": lead_client_id,
            }
        )

        for activity_type in ["Call", "Follow-up"]:
            if contacted and random.random() < 0.72:
                activities.append(
                    {
                        "activity_id": activity_id,
                        "advisor_id": advisor["advisor_id"],
                        "lead_id": lead_id,
                        "client_id": lead_client_id,
                        "activity_date": (created_date + timedelta(days=random.randint(1, 30))).isoformat(),
                        "activity_type": activity_type,
                        "activity_outcome": "Completed",
                        "duration_minutes": random.choice([10, 15, 20, 30]),
                    }
                )
                activity_id += 1

        if qualified and random.random() < 0.58:
            activities.append(
                {
                    "activity_id": activity_id,
                    "advisor_id": advisor["advisor_id"],
                    "lead_id": lead_id,
                    "client_id": lead_client_id,
                    "activity_date": (qualified_date + timedelta(days=random.randint(1, 21))).isoformat(),
                    "activity_type": "Meeting",
                    "activity_outcome": "Completed",
                    "duration_minutes": random.choice([30, 45, 60]),
                }
            )
            activity_id += 1

        estimated_assets = asset_band_amount(segment, source.quality_multiplier)
        opportunities.append(
            {
                "opportunity_id": opportunity_id,
                "advisor_id": advisor["advisor_id"],
                "lead_id": lead_id,
                "client_id": lead_client_id,
                "created_date": created_date.isoformat(),
                "closed_date": converted_date.isoformat() if converted_date else "",
                "opportunity_stage": "Closed" if converted else ("Proposal" if qualified else "Discovery"),
                "opportunity_status": "Closed Won" if converted else ("Open" if qualified else "Inactive"),
                "estimated_assets": money(estimated_assets),
                "closed_assets": money(estimated_assets * random.uniform(0.72, 1.08)) if converted else "",
            }
        )
        opportunity_id += 1

        if converted:
            clients.append(
                {
                    "client_id": client_id,
                    "primary_advisor_id": advisor["advisor_id"],
                    "client_since_date": converted_date.isoformat(),
                    "client_segment": segment,
                    "age_band": weighted_choice(AGE_BANDS, [0.10, 0.16, 0.24, 0.30, 0.20]),
                    "household_income_band": weighted_choice(INCOME_BANDS, [0.22, 0.38, 0.26, 0.14]),
                    "risk_tolerance": weighted_choice(RISK_TOLERANCE, [0.18, 0.46, 0.28, 0.08]),
                    "client_status": "Active",
                }
            )

            account_count = 1 if random.random() < 0.68 else 2
            total_initial_assets = estimated_assets * random.uniform(0.72, 1.08)
            for account_number in range(account_count):
                account_open_date = converted_date + timedelta(days=random.randint(0, 20))
                account_assets = total_initial_assets / account_count * random.uniform(0.85, 1.15)
                accounts.append(
                    {
                        "account_id": account_id,
                        "client_id": client_id,
                        "account_type": random.choice(ACCOUNT_TYPES),
                        "open_date": account_open_date.isoformat(),
                        "close_date": "",
                        "account_status": "Open",
                    }
                )

                current_assets = account_assets
                for snapshot_month in daterange_months(
                    date(account_open_date.year, account_open_date.month, 1), date(2025, 12, 1)
                ):
                    flow_rate = random.uniform(-0.025, 0.045)
                    if segment == "High Value":
                        flow_rate += 0.008
                    market_rate = random.uniform(-0.035, 0.045)
                    beginning_assets = current_assets
                    net_flows = beginning_assets * flow_rate
                    market_change = beginning_assets * market_rate
                    ending_assets = max(beginning_assets + net_flows + market_change, 0)
                    asset_snapshots.append(
                        {
                            "snapshot_month": snapshot_month.isoformat(),
                            "account_id": account_id,
                            "client_id": client_id,
                            "advisor_id": advisor["advisor_id"],
                            "beginning_assets": money(beginning_assets),
                            "net_flows": money(net_flows),
                            "market_change": money(market_change),
                            "ending_assets": money(ending_assets),
                        }
                    )
                    current_assets = ending_assets

                account_id += 1

            client_id += 1

        lead_id += 1

    months = daterange_months(START_DATE, END_DATE)
    snapshots_by_advisor_month: dict[tuple[int, date], float] = {}
    conversions_by_advisor_month: dict[tuple[int, date], int] = {}

    for row in asset_snapshots:
        key = (int(row["advisor_id"]), date.fromisoformat(row["snapshot_month"]))
        snapshots_by_advisor_month[key] = snapshots_by_advisor_month.get(key, 0) + float(row["net_flows"])

    for row in leads:
        if row["converted_date"]:
            converted_month = date.fromisoformat(row["converted_date"])
            key = (int(row["assigned_advisor_id"]), date(converted_month.year, converted_month.month, 1))
            conversions_by_advisor_month[key] = conversions_by_advisor_month.get(key, 0) + 1

    for advisor in advisors:
        for month in months:
            key = (advisor["advisor_id"], month)
            net_flows = snapshots_by_advisor_month.get(key, 0)
            converted_count = conversions_by_advisor_month.get(key, 0)
            base_comp = random.uniform(6500, 9500)
            incentive = max(0, net_flows * 0.0007) + converted_count * random.uniform(250, 550)
            incentive *= random.uniform(0.78, 1.22)
            compensation.append(
                {
                    "compensation_month": month.isoformat(),
                    "advisor_id": advisor["advisor_id"],
                    "base_compensation": money(base_comp),
                    "incentive_payout": money(incentive),
                    "total_compensation": money(base_comp + incentive),
                    "compensation_plan": "Growth Plus" if advisor_by_id[advisor["advisor_id"]]["team"] == "High Value" else "Standard",
                }
            )

    for advisor in advisors:
        advisor.pop("productivity_factor", None)

    return {
        "leads": leads,
        "clients": clients,
        "accounts": accounts,
        "advisor_activities": activities,
        "opportunities": opportunities,
        "monthly_asset_snapshots": asset_snapshots,
        "compensation": compensation,
    }


def main() -> None:
    advisors = generate_advisors()
    generated = generate_business_data(advisors)

    write_csv("advisors.csv", advisors)
    write_csv("lead_sources.csv", generate_lead_sources())
    for name, rows in generated.items():
        write_csv(f"{name}.csv", rows)

    print(f"Generated synthetic data in {RAW_DIR}")
    for name, rows in {"advisors": advisors, "lead_sources": generate_lead_sources(), **generated}.items():
        print(f"{name}: {len(rows):,} rows")


if __name__ == "__main__":
    main()

