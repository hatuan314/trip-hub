def validate_limit(limit: int):
    if limit <= 0:
        raise ValueError("limit must be positive")
