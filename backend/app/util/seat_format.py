def format_seat_label(seat_number: int) -> str:
    """Map a numeric seat number to a human-friendly label like A1, B7, etc.

    Assumes 10 seats per row (1-10 = row A, 11-20 = row B, ...).
    """
    if seat_number < 1:
        return f"#{seat_number}"

    # 10 seats per row
    index = seat_number - 1
    row_index = index // 10
    col_index = index % 10

    # Limit rows to A-Z; beyond that, just return #<number>
    if row_index >= 26:
        return f"#{seat_number}"

    row_letter = chr(ord("A") + row_index)
    seat_in_row = col_index + 1
    return f"{row_letter}{seat_in_row}"
