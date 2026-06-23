"""Generate synthetic source data for an asset management growth dashboard.

This script creates raw CSV tables only. It intentionally does not calculate
analytics such as AUM, net new assets, retention, or growth attribution. The
generated facts are connected enough for an analyst to calculate those metrics
in SQL or Tableau later.
"""

from __future__ import annotations

import argparse
import csv
import random
from collections import defaultdict
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path


START_DATE = date(2021, 1, 1)
END_DATE = date(2025, 12, 31)

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"

CLIENT_SEGMENTS = ["Retail", "High Net Worth", "Institutional", "Retirement Plan"]
AGE_BANDS = ["Under 35", "35-44", "45-54", "55-64", "65+"]
RISK_PROFILES = ["Conservative", "Moderate", "Growth", "Aggressive"]
ACQUISITION_CHANNELS = ["Advisor Referral", "Digital", "Employer", "Branch", "Direct Mail", "Partner"]
ACCOUNT_TYPES = ["Brokerage", "IRA", "Roth IRA", "401k", "529", "Institutional"]
FUND_CATEGORIES = ["Index Fund", "ETF", "Target Date Fund", "Bond Fund", "Active Equity Fund", "Money Market"]
ASSET_CLASSES = ["Equity", "Fixed Income", "Balanced", "Cash"]
TRANSACTION_TYPES = [
    "Contribution",
    "Withdrawal",
    "Transfer In",
    "Transfer Out",
    "Dividend Reinvestment",
    "Fee",
]

STATE_REGION = {
    "CA": "West",
    "WA": "West",
    "OR": "West",
    "AZ": "West",
    "CO": "West",
    "TX": "South",
    "FL": "South",
    "GA": "South",
    "NC": "South",
    "VA": "South",
    "NY": "Northeast",
    "NJ": "Northeast",
    "MA": "Northeast",
    "PA": "Northeast",
    "CT": "Northeast",
    "IL": "Midwest",
    "OH": "Midwest",
    "MI": "Midwest",
    "MN": "Midwest",
    "WI": "Midwest",
}


@dataclass(frozen=True)
class ClientProfile:
    client_id: int
    client_segment: str
    region: str
    state: str
    join_date: date
    age_band: str
    risk_profile: str
    acquisition_channel: str


@dataclass(frozen=True)
class AccountProfile:
    account_id: int
    client_id: int
    account_type: str
    open_date: date
    close_date: date | None
    account_status: str


@dataclass(frozen=True)
class FundProfile:
    fund_id: int
    fund_name: str
    fund_category: str
    asset_class: str
    expense_ratio: float
    inception_date: date


def all_dates(start: date, end: date) -> list[date]:
    days = []
    current = start
    while current <= end:
        days.append(current)
        current += timedelta(days=1)
    return days


def random_date(start: date, end: date) -> date:
    return start + timedelta(days=random.randint(0, (end - start).days))


def weighted_choice(items: list[str], weights: list[float]) -> str:
    return random.choices(items, weights=weights, k=1)[0]


def write_rows(path: Path, fieldnames: list[str], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def money(value: float) -> str:
    return f"{value:.2f}"


def pct(value: float) -> str:
    return f"{value:.6f}"


def segment_weight(segment: str) -> float:
    return {
        "Retail": 1.0,
        "High Net Worth": 8.0,
        "Institutional": 95.0,
        "Retirement Plan": 35.0,
    }[segment]


def generate_clients(client_count: int) -> list[ClientProfile]:
    clients = []
    states = list(STATE_REGION)
    for client_id in range(1, client_count + 1):
        segment = weighted_choice(CLIENT_SEGMENTS, [0.68, 0.18, 0.06, 0.08])
        state = random.choice(states)
        age_weights = {
            "Retail": [0.18, 0.24, 0.25, 0.20, 0.13],
            "High Net Worth": [0.04, 0.12, 0.26, 0.32, 0.26],
            "Institutional": [0.02, 0.08, 0.22, 0.34, 0.34],
            "Retirement Plan": [0.04, 0.15, 0.30, 0.32, 0.19],
        }[segment]
        channel_weights = {
            "Retail": [0.12, 0.46, 0.05, 0.16, 0.14, 0.07],
            "High Net Worth": [0.42, 0.14, 0.02, 0.20, 0.04, 0.18],
            "Institutional": [0.32, 0.04, 0.12, 0.08, 0.02, 0.42],
            "Retirement Plan": [0.18, 0.05, 0.50, 0.04, 0.02, 0.21],
        }[segment]
        clients.append(
            ClientProfile(
                client_id=client_id,
                client_segment=segment,
                region=STATE_REGION[state],
                state=state,
                join_date=random_date(START_DATE, date(2025, 9, 30)),
                age_band=weighted_choice(AGE_BANDS, age_weights),
                risk_profile=weighted_choice(RISK_PROFILES, [0.20, 0.43, 0.28, 0.09]),
                acquisition_channel=weighted_choice(ACQUISITION_CHANNELS, channel_weights),
            )
        )
    return clients


def generate_accounts(clients: list[ClientProfile], min_accounts: int, max_accounts: int) -> list[AccountProfile]:
    target_count = random.randint(min_accounts, max_accounts)
    accounts = []
    account_id = 1

    # Retail households often have several small-purpose accounts; institutions
    # and retirement plans usually have fewer but much larger relationships.
    for client in clients:
        count_weights = {
            "Retail": [0.40, 0.36, 0.17, 0.07],
            "High Net Worth": [0.24, 0.34, 0.25, 0.17],
            "Institutional": [0.78, 0.18, 0.04, 0.00],
            "Retirement Plan": [0.62, 0.28, 0.09, 0.01],
        }[client.client_segment]
        account_count = weighted_choice(["1", "2", "3", "4"], count_weights)
        for _ in range(int(account_count)):
            if len(accounts) >= target_count:
                break
            type_weights = {
                "Retail": [0.36, 0.24, 0.18, 0.08, 0.14, 0.00],
                "High Net Worth": [0.48, 0.22, 0.14, 0.02, 0.08, 0.06],
                "Institutional": [0.05, 0.00, 0.00, 0.00, 0.00, 0.95],
                "Retirement Plan": [0.03, 0.04, 0.01, 0.86, 0.00, 0.06],
            }[client.client_segment]
            open_date = random_date(client.join_date, min(END_DATE, client.join_date + timedelta(days=720)))
            close_date = None
            status = "Active"

            # Closures are intentionally sparse. Retail closure probability is
            # higher than institutional, keeping overall retention near 94%-98%.
            years_open = max(0.0, (END_DATE - open_date).days / 365.25)
            annual_close_rate = {
                "Retail": 0.028,
                "High Net Worth": 0.014,
                "Institutional": 0.006,
                "Retirement Plan": 0.010,
            }[client.client_segment]
            if years_open > 0.5 and random.random() < min(0.22, annual_close_rate * years_open):
                close_date = random_date(open_date + timedelta(days=180), END_DATE)
                status = "Closed"

            accounts.append(
                AccountProfile(
                    account_id=account_id,
                    client_id=client.client_id,
                    account_type=weighted_choice(ACCOUNT_TYPES, type_weights),
                    open_date=open_date,
                    close_date=close_date,
                    account_status=status,
                )
            )
            account_id += 1
    return accounts


def generate_funds(fund_count: int) -> list[FundProfile]:
    funds = []
    category_asset = {
        "Index Fund": "Equity",
        "ETF": "Equity",
        "Target Date Fund": "Balanced",
        "Bond Fund": "Fixed Income",
        "Active Equity Fund": "Equity",
        "Money Market": "Cash",
    }
    category_names = {
        "Index Fund": ["Total Market Index", "Large Cap Index", "Small Cap Index", "International Index"],
        "ETF": ["Core Equity ETF", "Dividend ETF", "Growth ETF", "International ETF"],
        "Target Date Fund": ["Target Retirement 2030", "Target Retirement 2040", "Target Retirement 2050"],
        "Bond Fund": ["Total Bond", "Short Term Bond", "Municipal Bond", "Core Plus Bond"],
        "Active Equity Fund": ["Active Growth", "Value Opportunities", "Global Equity", "Strategic Equity"],
        "Money Market": ["Federal Money Market", "Treasury Money Market", "Prime Cash Reserves"],
    }
    if fund_count < len(FUND_CATEGORIES):
        raise ValueError(f"--funds must be at least {len(FUND_CATEGORIES)} so every category is represented")

    required_categories = FUND_CATEGORIES.copy()
    random.shuffle(required_categories)
    for fund_id in range(1, fund_count + 1):
        if required_categories:
            category = required_categories.pop()
        else:
            category = weighted_choice(FUND_CATEGORIES, [0.22, 0.24, 0.16, 0.17, 0.13, 0.08])
        asset_class = category_asset[category]
        expense_range = {
            "Index Fund": (0.0003, 0.0012),
            "ETF": (0.0004, 0.0025),
            "Target Date Fund": (0.0008, 0.0035),
            "Bond Fund": (0.0015, 0.0045),
            "Active Equity Fund": (0.0045, 0.0100),
            "Money Market": (0.0006, 0.0022),
        }[category]
        base_name = random.choice(category_names[category])
        funds.append(
            FundProfile(
                fund_id=fund_id,
                fund_name=f"{base_name} Fund {fund_id:02d}",
                fund_category=category,
                asset_class=asset_class,
                expense_ratio=random.uniform(*expense_range),
                inception_date=random_date(date(1995, 1, 1), date(2020, 12, 31)),
            )
        )
    return funds


def generate_market_returns(funds: list[FundProfile], dates: list[date]) -> dict[int, dict[date, float]]:
    returns_by_fund: dict[int, dict[date, float]] = {}
    for fund in funds:
        fund_returns = {}
        for day in dates:
            # The common regime creates a broad market drawdown in 2022, a short
            # stress period in early 2023, and uneven recovery afterward.
            if date(2022, 1, 3) <= day <= date(2022, 10, 14):
                regime_drift = -0.00033
                regime_vol = 1.45
            elif date(2023, 3, 1) <= day <= date(2023, 4, 14):
                regime_drift = -0.00020
                regime_vol = 1.75
            elif date(2023, 6, 1) <= day <= date(2024, 12, 31):
                regime_drift = 0.00034
                regime_vol = 0.95
            else:
                regime_drift = 0.00018
                regime_vol = 1.00

            asset_params = {
                "Equity": (0.00022, 0.0110),
                "Fixed Income": (0.00008, 0.0038),
                "Balanced": (0.00015, 0.0065),
                "Cash": (0.00006, 0.00035),
            }[fund.asset_class]
            drift, volatility = asset_params
            if fund.fund_category == "Active Equity Fund":
                volatility *= 1.18
            if fund.fund_category == "Money Market":
                regime_drift = max(regime_drift, 0.0) * 0.15
                regime_vol = 0.60

            weekend_multiplier = 0.12 if day.weekday() >= 5 else 1.0
            raw_return = (drift + regime_drift) * weekend_multiplier
            raw_return += random.gauss(0, volatility * regime_vol * weekend_multiplier)
            fund_returns[day] = max(-0.075, min(0.065, raw_return))
        returns_by_fund[fund.fund_id] = fund_returns
    return returns_by_fund


def initial_allocation(client: ClientProfile, funds: list[FundProfile]) -> list[tuple[int, float]]:
    categories = {
        "Retail": ["ETF", "Index Fund", "Target Date Fund", "Bond Fund", "Money Market"],
        "High Net Worth": ["ETF", "Index Fund", "Active Equity Fund", "Bond Fund", "Money Market"],
        "Institutional": ["Index Fund", "ETF", "Bond Fund", "Money Market", "Active Equity Fund"],
        "Retirement Plan": ["Target Date Fund", "Index Fund", "Bond Fund", "Money Market"],
    }[client.client_segment]
    category_weights = {
        "Retail": [0.28, 0.24, 0.24, 0.14, 0.10],
        "High Net Worth": [0.24, 0.24, 0.18, 0.22, 0.12],
        "Institutional": [0.36, 0.24, 0.22, 0.10, 0.08],
        "Retirement Plan": [0.52, 0.24, 0.16, 0.08],
    }[client.client_segment]
    fund_count = weighted_choice(["1", "2", "3", "4"], [0.28, 0.38, 0.24, 0.10])
    selected = []
    while len(selected) < int(fund_count):
        category = weighted_choice(categories, category_weights)
        candidates = [fund for fund in funds if fund.fund_category == category]
        chosen = random.choice(candidates)
        if chosen.fund_id not in [fund_id for fund_id, _ in selected]:
            selected.append((chosen.fund_id, random.random() + 0.25))
    total = sum(weight for _, weight in selected)
    return [(fund_id, weight / total) for fund_id, weight in selected]


def starting_balance(client: ClientProfile) -> float:
    ranges = {
        "Retail": (6000, 90000),
        "High Net Worth": (180000, 1800000),
        "Institutional": (4500000, 65000000),
        "Retirement Plan": (700000, 12000000),
    }[client.client_segment]
    return random.uniform(*ranges)


def contribution_amount(segment: str, fund_category: str, transaction_type: str) -> float:
    base = {
        "Retail": (150, 4500),
        "High Net Worth": (2500, 50000),
        "Institutional": (75000, 1750000),
        "Retirement Plan": (18000, 375000),
    }[segment]
    amount = random.uniform(*base) * random.lognormvariate(0.0, 0.45)
    if fund_category in ["ETF", "Target Date Fund"] and transaction_type in ["Contribution", "Transfer In"]:
        amount *= random.uniform(1.08, 1.42)
    if fund_category == "Money Market":
        amount *= random.uniform(0.75, 1.25)
    return amount


def signed_transaction_amount(
    client: ClientProfile,
    fund_category: str,
    transaction_type: str,
    current_balance: float,
) -> float:
    if transaction_type in ["Contribution", "Transfer In", "Dividend Reinvestment"]:
        amount = contribution_amount(client.client_segment, fund_category, transaction_type)
        if transaction_type == "Dividend Reinvestment":
            amount = max(2.0, current_balance * random.uniform(0.0002, 0.0025))
        return amount
    if transaction_type == "Fee":
        return -min(current_balance * random.uniform(0.00003, 0.00018), current_balance * 0.20)

    withdrawal_bias = 1.0
    if client.age_band == "55-64":
        withdrawal_bias = 1.25
    elif client.age_band == "65+":
        withdrawal_bias = 1.75
    amount = contribution_amount(client.client_segment, fund_category, transaction_type) * withdrawal_bias
    return -min(amount, current_balance * random.uniform(0.05, 0.55))


def transaction_type_for_day(client: ClientProfile, fund_category: str, day: date, is_volatile: bool) -> str:
    if fund_category == "Money Market" and is_volatile:
        weights = [0.25, 0.10, 0.36, 0.14, 0.03, 0.12]
    elif client.age_band == "65+":
        weights = [0.24, 0.30, 0.13, 0.10, 0.10, 0.13]
    elif fund_category in ["ETF", "Target Date Fund"]:
        weights = [0.47, 0.12, 0.20, 0.07, 0.08, 0.06]
    else:
        weights = [0.39, 0.16, 0.18, 0.09, 0.08, 0.10]
    return weighted_choice(TRANSACTION_TYPES, weights)


def date_activity_multiplier(day: date) -> float:
    multiplier = 1.0
    if day.day <= 5 or day.day >= 26:
        multiplier += 0.28
    if day.month in [1, 4, 12]:
        multiplier += 0.18
    if date(2022, 1, 3) <= day <= date(2022, 10, 14) or date(2023, 3, 1) <= day <= date(2023, 4, 14):
        multiplier += 0.35
    return multiplier


def generate_facts(
    clients: list[ClientProfile],
    accounts: list[AccountProfile],
    funds: list[FundProfile],
    returns_by_fund: dict[int, dict[date, float]],
    target_transactions: int,
) -> None:
    dates = all_dates(START_DATE, END_DATE)
    client_by_id = {client.client_id: client for client in clients}
    fund_by_id = {fund.fund_id: fund for fund in funds}

    balances: dict[tuple[int, int], float] = {}
    account_funds: dict[int, list[int]] = defaultdict(list)
    account_by_id = {account.account_id: account for account in accounts}

    for account in accounts:
        client = client_by_id[account.client_id]
        for fund_id, allocation in initial_allocation(client, funds):
            value = starting_balance(client) * allocation
            balances[(account.account_id, fund_id)] = value
            account_funds[account.account_id].append(fund_id)

    tx_path = RAW_DIR / "fact_transactions.csv"
    bal_path = RAW_DIR / "fact_daily_balances.csv"
    with tx_path.open("w", newline="") as tx_handle, bal_path.open("w", newline="") as bal_handle:
        tx_writer = csv.DictWriter(
            tx_handle,
            fieldnames=[
                "transaction_id",
                "transaction_date",
                "account_id",
                "fund_id",
                "transaction_type",
                "amount",
            ],
        )
        bal_writer = csv.DictWriter(
            bal_handle,
            fieldnames=["balance_date", "account_id", "fund_id", "market_value"],
        )
        tx_writer.writeheader()
        bal_writer.writeheader()

        transaction_id = 1
        active_accounts_by_date: dict[date, list[AccountProfile]] = {}
        for day in dates:
            active_accounts_by_date[day] = [
                account
                for account in accounts
                if account.open_date <= day and (account.close_date is None or account.close_date >= day)
            ]

        # Probabilities are scaled to hit the requested row count while keeping
        # transaction timing tied to account activity, age, fund category, and
        # volatility regimes.
        active_combo_days = sum(
            len(account_funds[account.account_id])
            for day in dates
            for account in active_accounts_by_date[day]
        )
        base_probability = min(0.20, target_transactions / max(1, active_combo_days))

        for day in dates:
            is_volatile = date(2022, 1, 3) <= day <= date(2022, 10, 14) or date(2023, 3, 1) <= day <= date(2023, 4, 14)
            for account in active_accounts_by_date[day]:
                client = client_by_id[account.client_id]
                for fund_id in account_funds[account.account_id]:
                    fund = fund_by_id[fund_id]
                    key = (account.account_id, fund_id)
                    balance = balances[key]
                    probability = base_probability * date_activity_multiplier(day)
                    probability *= 0.86 + (segment_weight(client.client_segment) ** 0.18) / 2.6
                    if fund.fund_category in ["ETF", "Target Date Fund"]:
                        probability *= 1.18
                    if fund.fund_category == "Money Market" and is_volatile:
                        probability *= 1.90
                    if client.age_band in ["55-64", "65+"]:
                        probability *= 1.14

                    if random.random() < probability:
                        tx_type = transaction_type_for_day(client, fund.fund_category, day, is_volatile)
                        amount = signed_transaction_amount(client, fund.fund_category, tx_type, balance)
                        if abs(amount) >= 1.00:
                            balance = max(0.0, balance + amount)
                            balances[key] = balance
                            tx_writer.writerow(
                                {
                                    "transaction_id": transaction_id,
                                    "transaction_date": day.isoformat(),
                                    "account_id": account.account_id,
                                    "fund_id": fund_id,
                                    "transaction_type": tx_type,
                                    "amount": money(amount),
                                }
                            )
                            transaction_id += 1

                    balance = balances[key] * (1.0 + returns_by_fund[fund_id][day])
                    if account.close_date == day:
                        # Closed accounts are drained on the close date so the
                        # final daily balance connects to the account status.
                        if balance > 1.00:
                            tx_writer.writerow(
                                {
                                    "transaction_id": transaction_id,
                                    "transaction_date": day.isoformat(),
                                    "account_id": account.account_id,
                                    "fund_id": fund_id,
                                    "transaction_type": "Transfer Out",
                                    "amount": money(-balance),
                                }
                            )
                            transaction_id += 1
                        balance = 0.0
                    balances[key] = max(0.0, balance)

                    bal_writer.writerow(
                        {
                            "balance_date": day.isoformat(),
                            "account_id": account.account_id,
                            "fund_id": fund_id,
                            "market_value": money(balances[key]),
                        }
                    )

        if transaction_id <= target_transactions:
            actual = transaction_id - 1
            raise RuntimeError(
                f"Generated {actual:,} transactions, below requested minimum {target_transactions:,}. "
                "Use a lower --transactions value or increase account volume."
            )


def write_dimensions(clients: list[ClientProfile], accounts: list[AccountProfile], funds: list[FundProfile]) -> None:
    write_rows(
        RAW_DIR / "dim_clients.csv",
        [
            "client_id",
            "client_segment",
            "region",
            "state",
            "join_date",
            "age_band",
            "risk_profile",
            "acquisition_channel",
        ],
        [
            {
                "client_id": client.client_id,
                "client_segment": client.client_segment,
                "region": client.region,
                "state": client.state,
                "join_date": client.join_date.isoformat(),
                "age_band": client.age_band,
                "risk_profile": client.risk_profile,
                "acquisition_channel": client.acquisition_channel,
            }
            for client in clients
        ],
    )
    write_rows(
        RAW_DIR / "dim_accounts.csv",
        ["account_id", "client_id", "account_type", "open_date", "close_date", "account_status"],
        [
            {
                "account_id": account.account_id,
                "client_id": account.client_id,
                "account_type": account.account_type,
                "open_date": account.open_date.isoformat(),
                "close_date": account.close_date.isoformat() if account.close_date else "",
                "account_status": account.account_status,
            }
            for account in accounts
        ],
    )
    write_rows(
        RAW_DIR / "dim_funds.csv",
        ["fund_id", "fund_name", "fund_category", "asset_class", "expense_ratio", "inception_date"],
        [
            {
                "fund_id": fund.fund_id,
                "fund_name": fund.fund_name,
                "fund_category": fund.fund_category,
                "asset_class": fund.asset_class,
                "expense_ratio": pct(fund.expense_ratio),
                "inception_date": fund.inception_date.isoformat(),
            }
            for fund in funds
        ],
    )


def write_market_returns(funds: list[FundProfile], returns_by_fund: dict[int, dict[date, float]], dates: list[date]) -> None:
    path = RAW_DIR / "fact_market_returns.csv"
    with path.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["return_date", "fund_id", "daily_return"])
        writer.writeheader()
        for day in dates:
            for fund in funds:
                writer.writerow(
                    {
                        "return_date": day.isoformat(),
                        "fund_id": fund.fund_id,
                        "daily_return": pct(returns_by_fund[fund.fund_id][day]),
                    }
                )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate synthetic asset management source CSVs.")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--clients", type=int, default=10_000)
    parser.add_argument("--min-accounts", type=int, default=12_000)
    parser.add_argument("--max-accounts", type=int, default=18_000)
    parser.add_argument("--funds", type=int, default=52)
    parser.add_argument("--transactions", type=int, default=525_000)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    random.seed(args.seed)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    clients = generate_clients(args.clients)
    accounts = generate_accounts(clients, args.min_accounts, args.max_accounts)
    funds = generate_funds(args.funds)
    dates = all_dates(START_DATE, END_DATE)
    returns_by_fund = generate_market_returns(funds, dates)

    write_dimensions(clients, accounts, funds)
    write_market_returns(funds, returns_by_fund, dates)
    generate_facts(clients, accounts, funds, returns_by_fund, args.transactions)

    print(f"Wrote CSV files to {RAW_DIR}")
    print(f"Clients: {len(clients):,}")
    print(f"Accounts: {len(accounts):,}")
    print(f"Funds: {len(funds):,}")
    print(f"Requested minimum transactions: {args.transactions:,}")


if __name__ == "__main__":
    main()
