/*Function to display driver stats*/
    SELECT
        i.driver,
        COUNT(*) AS dumpster_count,
        SUM(i.disposalcost) AS total_disposal_cost,
        SUM(i.price) AS total_price,
        SUM(i.grossprofit) AS total_gross_profit
    FROM invoicing i
    WHERE
        p_start_date IS NULL
        OR p_end_date IS NULL
        OR i."date" BETWEEN p_start_date AND p_end_date
    GROUP BY i.driver
    ORDER BY i.driver;
