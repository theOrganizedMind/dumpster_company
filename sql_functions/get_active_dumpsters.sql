 /*
 Active Dumpster Inventory

    Parameters:
    None

    Returns:
    company (text)
    street (text)
    city (text)
    size (text): Dumpster Size.
    active_count (bigint): Active Dumpster Count.
 */
    SELECT
        i.company,
        MIN(i.street) AS street,
        i.city,
        i.size,
        COUNT(*) FILTER (WHERE i.description = 'Initial Drop')
        - COUNT(*) FILTER (WHERE i.description = 'Dump & Remove')
        AS active_count
    FROM invoicing i
    GROUP BY
        i.company,
        normalize_street(i.street),
        i.city,
        i.size
    HAVING
        COUNT(*) FILTER (WHERE i.description = 'Initial Drop')
        - COUNT(*) FILTER (WHERE i.description = 'Dump & Remove') > 0
    ORDER BY
        i.company,
        i.city,
        MIN(i.street);
