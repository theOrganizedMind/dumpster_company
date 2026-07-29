/*
Displays percentages grouped by city.
If no dates are provided it shows all dates.

	Parameters:
		start_date
		end_date

	Returns:
		city(text)
		percentage(numeric)
*/
BEGIN
    RETURN QUERY
    SELECT
        i.city::TEXT,
        ROUND(
            COUNT(*) * 100.0 /
            (
                SELECT COUNT(*)
                FROM invoicing t
                WHERE (p_start_date IS NULL OR t.date >= p_start_date)
                  AND (p_end_date   IS NULL OR t.date <= p_end_date)
            ),
            2
        ) AS percentage
    FROM invoicing i
    WHERE (p_start_date IS NULL OR i.date >= p_start_date)
      AND (p_end_date   IS NULL OR i.date <= p_end_date)
    GROUP BY i.city
    ORDER BY percentage DESC;
END;
