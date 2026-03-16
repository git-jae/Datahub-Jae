import re

def clean_values(values: list) -> list:
    seen, out = set(), []
    for v in values:
        v = re.sub(r"\s+", " ", str(v)).strip()
        if v and v.lower() not in seen:
            seen.add(v.lower()); out.append(v)
    return out

def to_sql_tuple(values: list):
    c = clean_values(values)
    return tuple(c) if c else ("__EMPTY__",)
