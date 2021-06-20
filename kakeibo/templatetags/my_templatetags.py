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
def datetime_twitter(datetime_str):
    """Tue Sep 22 11:21:27 +0000 2020"""
    d = datetime_str.split(" ")
    months = {
        "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
        "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
    }
    hh, mm = d[3][:5].split(":")
    dt = datetime(int(d[5]), months[d[1]], int(d[2]), int(hh), int(mm))
    return dt