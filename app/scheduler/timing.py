DEFAULT_TIMES = {
    "twitter":  ["08:00", "12:00", "18:00"],
    "reddit":   ["09:00", "13:00", "20:00"],
    "linkedin": ["08:30", "12:00", "17:30"],
    "facebook": ["09:00", "13:00", "19:00"],
}

def get_post_times(platform: str) -> list:
    return DEFAULT_TIMES.get(platform, ["09:00", "13:00", "18:00"])
