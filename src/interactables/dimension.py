def is_in_dimension(dimension_type: str, is_corrupted: bool) -> bool:
    """
    Unified helper to check if an entity assigned to 'normal', 'corrupt', or 'both'
    is physically active in the current dimension.
    """
    if dimension_type == "both":
        return True
    if dimension_type == "corrupt":
        return is_corrupted
    if dimension_type == "normal":
        return not is_corrupted
    return False
