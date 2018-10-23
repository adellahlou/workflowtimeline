def normalize_str_width(s, maxwidth):
    ABBREVIATE_AFTER = 6
    if maxwidth < 6:
        raise ValueError("maxwidth cannot be negative.")
        
    if len(s) < maxwidth:
        return s
    
    if maxwidth < ABBREVIATE_AFTER:
        return s[:maxwidth]
    
    mn3 = maxwidth - 3
    frontamt = int(mn3 // 2)
    rearamt = int((mn3 // 2) + (mn3 % 2))
    return s[: frontamt] + "..." + s[len(s) - rearamt:]

def get_categories(data, categorycol, include=[]):
    keys = data[categorycol].unique().tolist()
    keys.extend(include)
    return list(set(keys))