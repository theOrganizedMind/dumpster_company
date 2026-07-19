/*
This function calculates a $50 pricing difference for {company}. 
For a 30 yard C&D dumpster. 
*/
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) AS total_count,
        SUM(i.price)::NUMERIC AS total_price,
        (COUNT(*) * 50)::NUMERIC AS price_diff
    FROM invoicing i
    WHERE i.company = '{company}' --Add Company Name.
      AND i.size = '30 yard' --Change Dumpster Size
      AND i.type = 'C&D' --Change material type.
      AND i.description NOT IN (
            'Initial Drop',
            'Relocate',
            'Dead Haul',
            'Live Load'
      )
      AND i.date BETWEEN p_start_date AND p_end_date;
END;
