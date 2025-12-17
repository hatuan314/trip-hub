def validate_pagination(limit: int, offset: int) -> None:
    if limit <= 0:
        raise ValueError("limit must be positive")
    if offset < 0:
        raise ValueError("offset cannot be negative")
