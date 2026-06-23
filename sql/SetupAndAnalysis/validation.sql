SELECT version();
---
SELECT current_database();
---
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
ORDER BY table_name;
----
SELECT 'dim_clients' AS table_name, COUNT(*) FROM dim_clients
UNION ALL
SELECT 'dim_funds', COUNT(*) FROM dim_funds
UNION ALL
SELECT 'dim_accounts', COUNT(*) FROM dim_accounts
UNION ALL
SELECT 'fact_market_returns', COUNT(*) FROM fact_market_returns
UNION ALL
SELECT 'fact_transactions', COUNT(*) FROM fact_transactions
UNION ALL
SELECT 'fact_daily_balances', COUNT(*) FROM fact_daily_balances;
-----
SELECT * FROM dim_clients LIMIT 10;
SELECT * FROM dim_accounts LIMIT 10;
SELECT * FROM dim_funds LIMIT 10;
SELECT * FROM fact_transactions LIMIT 10;
SELECT * FROM fact_daily_balances LIMIT 10;
SELECT * FROM fact_market_returns LIMIT 10;
-------
SELECT 
  MIN(transaction_date) AS first_transaction,
  MAX(transaction_date) AS last_transaction
FROM fact_transactions
UNION ALL
SELECT 
  MIN(balance_date) AS first_balance,
  MAX(balance_date) AS last_balance
FROM fact_daily_balances
UNION ALL
SELECT 
  MIN(return_date) AS first_return,
  MAX(return_date) AS last_return
FROM fact_market_returns;
------
SELECT
  balance_date,
  SUM(market_value) AS total_aum
FROM fact_daily_balances
GROUP BY balance_date
ORDER BY balance_date;
-------
SELECT
    count(*)
FROM dim_clients;
--------
SELECT
    client_id,
    count(*)
FROM dim_accounts
GROUP BY client_id;
---------
SELECT COUNT(*)
FROM fact_daily_balances;
--------
SELECT
    d.fund_name,
    f.fund_id,
    SUM(f.market_value) as total_market_value
FROM fact_daily_balances f
INNER JOIN dim_funds d
    ON f.fund_id = d.fund_id
WHERE f.balance_date = (
  SELECT MAX(balance_date)
  FROM fact_daily_balances
)
GROUP BY f.fund_id, d.fund_name    
ORDER BY total_market_value DESC;
--------
SELECT
    d.fund_name,
    COUNT(DISTINCT f.account_id) AS account_count,
    SUM(f.market_value) AS total_market_value,
    AVG(f.market_value) AS avg_market_value
FROM fact_daily_balances f
INNER JOIN dim_funds d
    ON f.fund_id = d.fund_id
WHERE f.balance_date = (
    SELECT MAX(balance_date)
    FROM fact_daily_balances
)
GROUP BY
    d.fund_name
ORDER BY avg_market_value DESC;