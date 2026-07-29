/*
Calculates Monthly Dumpster Count.

	Parameters:
	start_date(str): Start Date
	end_date(str): End Date

	Returns:
	year_month(text): YYYY-MM
	monthly_dumpster_count(bigint)
*/
BEGIN
    RETURN QUERY
    SELECT
        TO_CHAR(DATE_TRUNC('month', t."date"), 'YYYY-MM') AS year_month,
        COUNT(*) AS monthly_dumpster_count
    FROM invoicing t
    WHERE
        (p_start_date IS NULL OR t."date" >= p_start_date)
        AND
        (p_end_date IS NULL OR t."date" <= p_end_date)
    GROUP BY DATE_TRUNC('month', t."date")
    ORDER BY DATE_TRUNC('month', t."date");
END;
