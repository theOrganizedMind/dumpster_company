/*Function to display disposal information.*/
BEGIN
    RETURN QUERY
    SELECT
        i.disposal::TEXT,
        COUNT(*) AS dumpster_count,
        COALESCE(SUM(i.tons), 0)::NUMERIC AS total_tons,
        ROUND(COALESCE(AVG(i.tons), 0)::NUMERIC, 2) AS avg_tons,
        COALESCE(SUM(i.disposalcost), 0)::NUMERIC AS total_disposal_cost,
        ROUND(COALESCE(AVG(i.disposalcost), 0)::NUMERIC, 2) AS avg_disposal_cost,
        ROUND(
            COALESCE(
                (SUM(i.disposalcost) / NULLIF(SUM(i.tons), 0))::NUMERIC,
                0
            ),
            2
        ) AS cost_per_ton,
        ROUND(
            COALESCE(
                (
                    SUM(i.grossprofit)
                    / NULLIF(SUM(i.price), 0)
                ) * 100,
                0
            )::NUMERIC,
            2
        ) AS percent_profit
    FROM invoicing i
    WHERE
        (p_start_date IS NULL OR i."date" >= p_start_date)
        AND
        (p_end_date IS NULL OR i."date" <= p_end_date)
    GROUP BY
        i.disposal
    ORDER BY
        total_disposal_cost DESC;
END;
