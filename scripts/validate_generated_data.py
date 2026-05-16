"""Validate generated source CSVs for obvious data quality issues."""

from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"


def read_csv(name: str) -> list[dict]:
    with (RAW_DIR / name).open(newline="") as handle:
        return list(csv.DictReader(handle))


def parse_date(value: str) -> date | None:
    return date.fromisoformat(value) if value else None


def assert_condition(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def parse_money(value: str) -> Decimal:
    return Decimal(value or "0")


def main() -> None:
    advisors = read_csv("advisors.csv")
    lead_sources = read_csv("lead_sources.csv")
    clients = read_csv("clients.csv")
    leads = read_csv("leads.csv")
    accounts = read_csv("accounts.csv")
    activities = read_csv("advisor_activities.csv")
    opportunities = read_csv("opportunities.csv")
    snapshots = read_csv("monthly_asset_snapshots.csv")
    compensation = read_csv("compensation.csv")

    advisor_ids = {row["advisor_id"] for row in advisors}
    lead_source_ids = {row["lead_source_id"] for row in lead_sources}
    client_ids = {row["client_id"] for row in clients}
    lead_ids = {row["lead_id"] for row in leads}
    account_ids = {row["account_id"] for row in accounts}

    assert_condition(len(advisors) > 0, "No advisors generated")
    assert_condition(len(lead_sources) > 0, "No lead sources generated")
    assert_condition(len(leads) > 0, "No leads generated")

    for row in clients:
        assert_condition(row["primary_advisor_id"] in advisor_ids, f"Invalid advisor for client {row['client_id']}")

    for row in leads:
        created_date = parse_date(row["created_date"])
        contacted_date = parse_date(row["contacted_date"])
        qualified_date = parse_date(row["qualified_date"])
        converted_date = parse_date(row["converted_date"])

        assert_condition(row["lead_source_id"] in lead_source_ids, f"Invalid source for lead {row['lead_id']}")
        assert_condition(row["assigned_advisor_id"] in advisor_ids, f"Invalid advisor for lead {row['lead_id']}")
        assert_condition(not contacted_date or contacted_date >= created_date, f"Contact before creation for lead {row['lead_id']}")
        assert_condition(not qualified_date or qualified_date >= created_date, f"Qualification before creation for lead {row['lead_id']}")
        assert_condition(not converted_date or converted_date >= created_date, f"Conversion before creation for lead {row['lead_id']}")
        if row["lead_status"] == "Converted":
            assert_condition(row["client_id"] in client_ids, f"Converted lead missing valid client {row['lead_id']}")

    for row in accounts:
        open_date = parse_date(row["open_date"])
        close_date = parse_date(row["close_date"])
        assert_condition(row["client_id"] in client_ids, f"Invalid client for account {row['account_id']}")
        assert_condition(not close_date or close_date >= open_date, f"Close before open for account {row['account_id']}")

    for row in activities:
        assert_condition(row["advisor_id"] in advisor_ids, f"Invalid advisor for activity {row['activity_id']}")
        assert_condition(row["lead_id"] in lead_ids or row["client_id"] in client_ids, f"Activity missing valid lead/client {row['activity_id']}")

    for row in opportunities:
        assert_condition(row["advisor_id"] in advisor_ids, f"Invalid advisor for opportunity {row['opportunity_id']}")
        assert_condition(row["lead_id"] in lead_ids, f"Invalid lead for opportunity {row['opportunity_id']}")
        if row["client_id"]:
            assert_condition(row["client_id"] in client_ids, f"Invalid client for opportunity {row['opportunity_id']}")
        if row["opportunity_status"] == "Closed Won":
            assert_condition(float(row["closed_assets"]) > 0, f"Closed-won opportunity missing assets {row['opportunity_id']}")

    for row in snapshots:
        assert_condition(row["account_id"] in account_ids, f"Invalid account for snapshot {row['account_id']}")
        assert_condition(row["client_id"] in client_ids, f"Invalid client for snapshot {row['client_id']}")
        assert_condition(row["advisor_id"] in advisor_ids, f"Invalid advisor for snapshot {row['advisor_id']}")
        expected = parse_money(row["beginning_assets"]) + parse_money(row["net_flows"]) + parse_money(row["market_change"])
        actual = parse_money(row["ending_assets"])
        assert_condition(abs(expected - actual) <= Decimal("0.03"), f"Asset snapshot does not reconcile for account {row['account_id']}")

    for row in compensation:
        assert_condition(row["advisor_id"] in advisor_ids, f"Invalid advisor for compensation {row['advisor_id']}")
        expected = parse_money(row["base_compensation"]) + parse_money(row["incentive_payout"])
        actual = parse_money(row["total_compensation"])
        assert_condition(abs(expected - actual) <= Decimal("0.01"), f"Compensation does not reconcile for advisor {row['advisor_id']}")

    print("Validation passed")
    print(f"Leads: {len(leads):,}")
    print(f"Clients: {len(clients):,}")
    print(f"Accounts: {len(accounts):,}")
    print(f"Asset snapshots: {len(snapshots):,}")


if __name__ == "__main__":
    main()
