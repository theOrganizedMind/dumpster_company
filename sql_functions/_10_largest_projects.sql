/*
This function should be ran once a year when the 
pollution liability insurance renews.

	Parameters:
	start_date (str): Start Date
	end_date (str): End Date
*/
BEGIN
    RETURN QUERY
    SELECT
        i.company::TEXT,
        MIN(i.street)::TEXT AS street,
        i.city::TEXT,
        SUM(i.price)::NUMERIC AS total_price
    FROM invoicing i
    WHERE i.date BETWEEN p_start_date AND p_end_date
    GROUP BY
        i.company,
        normalize_street(i.street),
        i.city
    ORDER BY total_price DESC
    LIMIT 10;
END; 
