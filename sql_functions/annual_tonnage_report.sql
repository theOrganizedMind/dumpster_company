/*
Report for Waste Services.

	Parameters:
	start_date (str): Start Date
	end_date (str): End Date
*/
BEGIN
    RETURN QUERY
    SELECT
        i.disposal::TEXT,
        i.city::TEXT,
        SUM(i.tons)::NUMERIC AS total_tons
    FROM invoicing i
    WHERE i.city LIKE '%{city}' --Add City (%) Accounts for extra spaces.
      AND i.tons IS NOT NULL
      AND i.date BETWEEN p_start_date AND p_end_date
    GROUP BY
        i.disposal,
        i.city
    ORDER BY total_tons DESC;
END;
