import locale


def format_brl(value):
    return locale.currency(value, grouping=True)
