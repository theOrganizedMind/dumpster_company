/*
This program calculates the difference between different landfills for Tons <= 5.
- Disposal is 'Triune (Centennial)', 'Triune (Hermitage)', 'Music City Transfer'.

	Parameters:
	start_date (str): Start Date
	end_date (str): End Date
*/
BEGIN
    RETURN QUERY
    SELECT
        ROUND(COALESCE(SUM(i.tons), 0)::NUMERIC, 2) AS total_tons,
        ROUND(COALESCE(SUM(i.disposalcost), 0)::NUMERIC, 2) AS current_disposal_cost,
        ROUND((COALESCE(SUM(i.tons), 0) * 92)::NUMERIC, 2) AS new_disposal_cost, --Add Comparision Rate
        ROUND(
            (
                COALESCE(SUM(i.disposalcost), 0)
                - (COALESCE(SUM(i.tons), 0) * 92) --Add Comparision Rate
            )::NUMERIC,
            2
        ) AS disposal_price_diff
    FROM invoicing i
    WHERE i.tons <= 5
      AND i.disposal IN (
            'Triune (Centennial)',
            'Triune (Hermitage)',
            'Music City Transfer'
      )
      AND i.date BETWEEN p_start_date AND p_end_date;
END;
