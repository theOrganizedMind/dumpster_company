/*Calculates {company} weight overage fee's for tons > 10*/
BEGIN
    RETURN QUERY
    SELECT
        ROUND(
            COALESCE(
                SUM((i.tons - 10) * 100), --Change weight overage tonnage
                0
            )::NUMERIC,
            2
        ) AS weight_overage_fees
    FROM invoicing i
    WHERE i.tons > 10
      AND i.company = '{comany}' --Add Company Name
      AND i.date BETWEEN p_start_date AND p_end_date;
END;
