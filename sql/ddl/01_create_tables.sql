-- Personal Investor Distribution Analytics
-- Source-style relational schema for synthetic CRM, sales, client, account,
-- asset, and compensation data.

create table if not exists advisors (
    advisor_id integer primary key,
    advisor_name varchar(100) not null,
    team varchar(100) not null,
    region varchar(50) not null,
    hire_date date not null,
    tenure_band varchar(50) not null,
    advisor_status varchar(25) not null
);

create table if not exists lead_sources (
    lead_source_id integer primary key,
    lead_source_name varchar(100) not null,
    channel varchar(50) not null,
    source_category varchar(50) not null,
    is_paid_source boolean not null
);

create table if not exists clients (
    client_id integer primary key,
    primary_advisor_id integer not null,
    client_since_date date not null,
    client_segment varchar(50) not null,
    age_band varchar(50) not null,
    household_income_band varchar(50) not null,
    risk_tolerance varchar(25) not null,
    client_status varchar(25) not null,
    foreign key (primary_advisor_id) references advisors(advisor_id)
);

create table if not exists leads (
    lead_id integer primary key,
    lead_source_id integer not null,
    assigned_advisor_id integer not null,
    created_date date not null,
    contacted_date date,
    qualified_date date,
    converted_date date,
    lead_status varchar(25) not null,
    estimated_asset_band varchar(50) not null,
    client_id integer,
    foreign key (lead_source_id) references lead_sources(lead_source_id),
    foreign key (assigned_advisor_id) references advisors(advisor_id),
    foreign key (client_id) references clients(client_id)
);

create table if not exists accounts (
    account_id integer primary key,
    client_id integer not null,
    account_type varchar(50) not null,
    open_date date not null,
    close_date date,
    account_status varchar(25) not null,
    foreign key (client_id) references clients(client_id)
);

create table if not exists advisor_activities (
    activity_id integer primary key,
    advisor_id integer not null,
    lead_id integer,
    client_id integer,
    activity_date date not null,
    activity_type varchar(50) not null,
    activity_outcome varchar(50) not null,
    duration_minutes integer,
    foreign key (advisor_id) references advisors(advisor_id),
    foreign key (lead_id) references leads(lead_id),
    foreign key (client_id) references clients(client_id)
);

create table if not exists opportunities (
    opportunity_id integer primary key,
    advisor_id integer not null,
    lead_id integer,
    client_id integer,
    created_date date not null,
    closed_date date,
    opportunity_stage varchar(50) not null,
    opportunity_status varchar(25) not null,
    estimated_assets decimal(18, 2),
    closed_assets decimal(18, 2),
    foreign key (advisor_id) references advisors(advisor_id),
    foreign key (lead_id) references leads(lead_id),
    foreign key (client_id) references clients(client_id)
);

create table if not exists monthly_asset_snapshots (
    snapshot_month date not null,
    account_id integer not null,
    client_id integer not null,
    advisor_id integer not null,
    beginning_assets decimal(18, 2) not null,
    net_flows decimal(18, 2) not null,
    market_change decimal(18, 2) not null,
    ending_assets decimal(18, 2) not null,
    primary key (snapshot_month, account_id),
    foreign key (account_id) references accounts(account_id),
    foreign key (client_id) references clients(client_id),
    foreign key (advisor_id) references advisors(advisor_id)
);

create table if not exists compensation (
    compensation_month date not null,
    advisor_id integer not null,
    base_compensation decimal(18, 2) not null,
    incentive_payout decimal(18, 2) not null,
    total_compensation decimal(18, 2) not null,
    compensation_plan varchar(50) not null,
    primary key (compensation_month, advisor_id),
    foreign key (advisor_id) references advisors(advisor_id)
);

