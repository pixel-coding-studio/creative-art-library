def remap(value, old_start, old_end, new_start, new_end):
    """
    Re-maps a number from one range to another
    :param value:
    :param old_start:
    :param old_end:
    :param new_start:
    :param new_end:
    :return:
    """
    return (((value - old_start) * (new_end - new_start)) / (old_end - old_start)) + new_start