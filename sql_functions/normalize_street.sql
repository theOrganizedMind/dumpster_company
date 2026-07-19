/*Normalizes the address for separate functions*/
BEGIN
    addr := lower(addr);

    -- Remove punctuation
    addr := regexp_replace(addr, '[.,#]', '', 'g');

    -- Normalize directions
    addr := regexp_replace(addr, '\m(north|n)\M', 'n', 'gi');
    addr := regexp_replace(addr, '\m(south|s)\M', 's', 'gi');
    addr := regexp_replace(addr, '\m(east|e)\M',  'e', 'gi');
    addr := regexp_replace(addr, '\m(west|w)\M',  'w', 'gi');

    -- Normalize suffixes
    addr := regexp_replace(addr, '\m(street|st)\M',      'st',   'gi');
    addr := regexp_replace(addr, '\m(avenue|ave)\M',     'ave',  'gi');
    addr := regexp_replace(addr, '\m(road|rd)\M',        'rd',   'gi');
    addr := regexp_replace(addr, '\m(drive|dr)\M',       'dr',   'gi');
    addr := regexp_replace(addr, '\m(lane|ln)\M',        'ln',   'gi');
    addr := regexp_replace(addr, '\m(court|ct)\M',       'ct',   'gi');
    addr := regexp_replace(addr, '\m(circle|cir)\M',     'cir',  'gi');
    addr := regexp_replace(addr, '\m(place|pl)\M',       'pl',   'gi');
    addr := regexp_replace(addr, '\m(terrace|ter)\M',    'ter',  'gi');
    addr := regexp_replace(addr, '\m(parkway|pkwy)\M',   'pkwy', 'gi');
    addr := regexp_replace(addr, '\m(boulevard|blvd)\M', 'blvd', 'gi');
    addr := regexp_replace(addr, '\m(highway|hwy)\M',    'hwy',  'gi');
    addr := regexp_replace(addr, '\m(trail|trl)\M',      'trl',  'gi');
    addr := regexp_replace(addr, '\m(way)\M',            'way',  'gi');
    addr := regexp_replace(addr, '\m(loop)\M',           'loop', 'gi');

    -- Collapse multiple spaces
    addr := regexp_replace(addr, '\s+', ' ', 'g');

    RETURN btrim(addr);
END;
