-- SQL views to support court operations reporting.

CREATE OR REPLACE VIEW vw_monthly_case_metrics AS
SELECT
  to_char(filing_date, 'YYYY-MM') AS month,
  COUNT(*) AS total_cases,
  COUNT(*) FILTER (WHERE status IN ('DISPOSED', 'DISMISSED', 'PAID')) AS disposed_cases,
  COUNT(*) FILTER (WHERE status NOT IN ('DISPOSED', 'DISMISSED', 'PAID')) AS non_disposed_cases,
  AVG(EXTRACT(DAY FROM CURRENT_DATE - filing_date)) AS avg_case_age_days
FROM cases
GROUP BY to_char(filing_date, 'YYYY-MM');

