-- Asset Management Growth Analytics Dashboard
-- Raw synthetic source schema only. No analytical views are created here.

drop table if exists fact_daily_balances;
drop table if exists fact_transactions;
drop table if exists fact_market_returns;
drop table if exists dim_accounts;
drop table if exists dim_funds;
drop table if exists dim_clients;

create table dim_clients (
    client_id integer primary key,
    client_segment varchar(30) not null check (
        client_segment in ('Retail', 'High Net Worth', 'Institutional', 'Retirement Plan')
    ),
    region varchar(30) not null,
    state char(2) not null,
    join_date date not null,
    age_band varchar(20) not null,
    risk_profile varchar(20) not null,
    acquisition_channel varchar(40) not null
);

create table dim_accounts (
    account_id integer primary key,
    client_id integer not null references dim_clients(client_id),
    account_type varchar(30) not null check (
        account_type in ('Brokerage', 'IRA', 'Roth IRA', '401k', '529', 'Institutional')
    ),
    open_date date not null,
    close_date date,
    account_status varchar(20) not null check (account_status in ('Active', 'Closed')),
    check (close_date is null or close_date >= open_date)
);

create table dim_funds (
    fund_id integer primary key,
    fund_name varchar(120) not null,
    fund_category varchar(40) not null check (
        fund_category in (
            'Index Fund',
            'ETF',
            'Target Date Fund',
            'Bond Fund',
            'Active Equity Fund',
            'Money Market'
        )
    ),
    asset_class varchar(30) not null check (
        asset_class in ('Equity', 'Fixed Income', 'Balanced', 'Cash')
    ),
    expense_ratio numeric(8, 6) not null check (expense_ratio >= 0),
    inception_date date not null
);

create table fact_transactions (
    transaction_id bigint primary key,
    transaction_date date not null,
    account_id integer not null references dim_accounts(account_id),
    fund_id integer not null references dim_funds(fund_id),
    transaction_type varchar(40) not null check (
        transaction_type in (
            'Contribution',
            'Withdrawal',
            'Transfer In',
            'Transfer Out',
            'Dividend Reinvestment',
            'Fee'
        )
    ),
    amount numeric(18, 2) not null
);

create table fact_daily_balances (
    balance_date date not null,
    account_id integer not null references dim_accounts(account_id),
    fund_id integer not null references dim_funds(fund_id),
    market_value numeric(18, 2) not null check (market_value >= 0),
    primary key (balance_date, account_id, fund_id)
);

create table fact_market_returns (
    return_date date not null,
    fund_id integer not null references dim_funds(fund_id),
    daily_return numeric(12, 6) not null,
    primary key (return_date, fund_id)
);

create index idx_dim_accounts_client_id on dim_accounts(client_id);
create index idx_fact_transactions_date on fact_transactions(transaction_date);
create index idx_fact_transactions_account_fund on fact_transactions(account_id, fund_id);
create index idx_fact_daily_balances_date on fact_daily_balances(balance_date);
create index idx_fact_daily_balances_account_fund on fact_daily_balances(account_id, fund_id);
create index idx_fact_market_returns_fund_date on fact_market_returns(fund_id, return_date);
