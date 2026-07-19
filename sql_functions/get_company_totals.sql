/*
Calculates Financial Information by Customer.

	Parameters:
	start_date(str): Start Date
	end_date(str): End Date

	Returns:
	company (text)
	total_price (numeric)
	total_grossprofit (numeric)
	profit_percentage (numeric)
*/
BEGIN
    RETURN QUERY
    SELECT
        i.company::TEXT,
        ROUND(SUM(i.price)::NUMERIC, 2) AS total_price,
        ROUND(SUM(i.grossprofit)::NUMERIC, 2) AS total_grossprofit,
        ROUND(
            CASE
                WHEN SUM(i.price) = 0 THEN 0
                ELSE (SUM(i.grossprofit) / SUM(i.price)) * 100
            END::NUMERIC,
            2
        ) AS profit_percentage
    FROM invoicing i
    WHERE
        (p_start_date IS NULL OR i.date >= p_start_date)
        AND
        (p_end_date IS NULL OR i.date <= p_end_date)
    GROUP BY
        i.company
    ORDER BY
        i.company;
END;
