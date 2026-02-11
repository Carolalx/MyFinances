import locale

locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


def format_brl(value):
    return locale.currency(value, grouping=True)
