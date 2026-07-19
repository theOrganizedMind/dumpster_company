/*
Calculates metrics based on {size} yard dumpster.

	Parameters:
	yard_size (int): Dumpster yard size.
*/
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*) AS total_dumpster_count,
        COUNT(*) * p_yard_size AS total_cubic_yards,
        ROUND(SUM(tons)::NUMERIC, 2) AS total_tons,
        ROUND(SUM(disposalcost)::NUMERIC, 2) AS total_disposal_cost,
        ROUND(SUM(grossprofit)::NUMERIC, 2) AS gross_profit,
        ROUND(SUM(price)::NUMERIC, 2) AS total_price,
        ROUND(AVG(price)::NUMERIC, 2) AS avg_yard_price,
        ROUND(AVG(disposalcost)::NUMERIC, 2) AS avg_yard_disposal_cost,
        ROUND(AVG(grossprofit)::NUMERIC, 2) AS avg_yard_gross_profit
    FROM invoicing
    WHERE size ILIKE '%' || p_yard_size || ' yard%'
      AND type NOT IN ('Recycling', 'Clean-Fill')
      AND description NOT IN ('Initial Drop', 'Dead Haul', 'Relocate', 'Rental Fee');
END;
