/*
- This function calculates the disposal price difference for 
  'yard' or 'ton' for Tons >= 0.
- Disposal is 'Disposal Location One', 'Disposal Location Two'.

	Parameters:
	start_date (str): Start Date
	end_date (str): End Date
	pricing_mode(text): Default='ton', set to 'ton' or 'yard'
	ton_pricing(numeric):
	yard_pricing(numeric):

	Returns:
	total_tons(numeric)
	current_disposal_cost(numeric)
	new_disposal_cost(numeric)
	disposal_price_diff(numeric)
*/
BEGIN
    -- Validate pricing mode and required parameter
    IF lower(p_pricing_mode) NOT IN ('ton', 'yard') THEN
        RAISE EXCEPTION 'Invalid p_pricing_mode: %. Use ''ton'' or ''yard''.', p_pricing_mode;
    END IF;

    IF lower(p_pricing_mode) = 'ton' AND p_ton_pricing IS NULL THEN
        RAISE EXCEPTION 'p_ton_pricing is required when p_pricing_mode = ''ton''.';
    END IF;

    IF lower(p_pricing_mode) = 'yard' AND p_yard_pricing IS NULL THEN
        RAISE EXCEPTION 'p_yard_pricing is required when p_pricing_mode = ''yard''.';
    END IF;

    RETURN QUERY
    WITH filtered AS (
        SELECT
            i.tons,
            i.disposalcost,
            i.size,
            CASE
                WHEN lower(p_pricing_mode) = 'ton' THEN
                    COALESCE(i.tons, 0) * p_ton_pricing
                ELSE
                    COALESCE(
                        NULLIF(
                            substring(COALESCE(i.size::text, '') FROM '([0-9]+(\.[0-9]+)?)'),
                            ''
                        )::numeric,
                        0
                    ) * p_yard_pricing
            END AS comparison_cost
        FROM invoicing i
        WHERE i.tons >= 0
          AND i.disposal IN (
                'Disposal Location One', -- <-- Add Disposal Locations
                'Disposal Location Two'
          )
          AND i.date BETWEEN p_start_date AND p_end_date
    )
    SELECT
        ROUND(COALESCE(SUM(f.tons), 0)::numeric, 2) AS total_tons,
        ROUND(COALESCE(SUM(f.disposalcost), 0)::numeric, 2) AS current_disposal_cost,
        ROUND(COALESCE(SUM(f.comparison_cost), 0)::numeric, 2) AS new_disposal_cost,
        ROUND(
            (COALESCE(SUM(f.comparison_cost), 0) - COALESCE(SUM(f.disposalcost), 0))::numeric,
            2
        ) AS disposal_price_diff
    FROM filtered f;
END;
