from django import template
from datetime import datetime
register = template.Library()


@register.filter
def yen(val, digit=0):
    if not val:
        return "-"
    elif val >= 0 and digit == 0:
        return "¥{:,}".format(round(val))
    elif val >= 0 and digit > 0:
        return "¥{:,}".format(round(val, digit))
    elif val < 0 and digit == 0:
        return "<font color='red'>-¥{:,}</font>".format(round(-val))
    else:
        return "<font color='red'>-¥{:,}</font>".format(round(-val, digit))


@register.filter
def yen_no_color(val, digit=0):
    if not val:
        return "-"
    elif val >= 0 and digit == 0:
        return "¥{:,}".format(round(val))
    elif val >= 0 and digit > 0:
        return "¥{:,}".format(round(val, digit))
    elif val < 0 and digit == 0:
        return "-¥{:,}".format(round(-val))
    else:
        return "-¥{:,}".format(round(-val, digit))


@register.filter
def pct(val, digit=2):
    if not val:
        return "-"
    elif val >= 0:
        return "{}%".format(round(val, digit))
    else:
        return "<font color='red'>-{}%</font>".format(round(-val, digit))


@register.filter
def pct_100(val, digit=2):
    if not val:
        return "-"
    elif val >= 0:
        return "{}%".format(round(val*100, digit))
    else:
        return "<font color='red'>-{}%</font>".format(round(-val*100, digit))


@register.filter
def usd(val, digit=0):
    if not val:
        return "-"
    elif val >= 0 and digit == 0:
        return "${:,}".format(round(val))
    elif val >= 0 and digit > 0:
        return "${:,}".format(round(val, digit))
    elif val < 0 and digit == 0:
        return "<font color='red'>-${:,}</font>".format(round(-val))
    else:
        return "<font color='red'>-${:,}</font>".format(round(-val, digit))
