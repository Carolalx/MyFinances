# utils.py
def price_format(val):
    return f'R$ {val:,.2f}'.replace(",", "X").replace(".", ",").replace("X", ".")
