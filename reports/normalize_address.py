import re

def normalize_address(location):
    """
    Normalize the address by replacing common abbreviations.
    """
    location = location.lower()
    # Remove apartment/unit/suite numbers
    location = re.sub(r'\b(apt|apartment|unit|ste|suite|#)\s*\w+\b', '', location)
    # Standardize directions
    location = re.sub(r'\b(north|n\.?)\b', 'n', location)
    location = re.sub(r'\b(south|s\.?)\b', 's', location)
    location = re.sub(r'\b(east|e\.?)\b', 'e', location)
    location = re.sub(r'\b(west|w\.?)\b', 'w', location)
    # Standardize street types
    location = re.sub(r'\b(road|rd\.?)\b', 'rd', location)
    location = re.sub(r'\b(drive|dr\.?)\b', 'dr', location)
    location = re.sub(r'\b(street|st\.?)\b', 'st', location)
    location = re.sub(r'\b(avenue|ave\.?)\b', 'ave', location)
    location = re.sub(r'\b(court|ct\.?)\b', 'ct', location)
    location = re.sub(r'\b(boulevard|blvd\.?)\b', 'blvd', location)
    location = re.sub(r'\b(lane|ln\.?)\b', 'ln', location)
    location = re.sub(r'\b(place|pl\.?)\b', 'pl', location)
    location = re.sub(r'\b(terrace|ter\.?)\b', 'ter', location)
    location = re.sub(r'\b(parkway|pkwy\.?)\b', 'pkwy', location)
    location = re.sub(r'\b(circle|cir\.?)\b', 'cir', location)
    location = re.sub(r'\b(highway|hwy\.?)\b', 'hwy', location)
    location = re.sub(r'\b(expressway|expy\.?)\b', 'expy', location)
    location = re.sub(r'\b(square|sq\.?)\b', 'sq', location)
    location = re.sub(r'[.,;]', '', location)  # Remove punctuation (commas, semicolons, etc.)
    location = re.sub(r'\s+', ' ', location)  # Replace multiple spaces with one
    location = location.strip()
    return location
