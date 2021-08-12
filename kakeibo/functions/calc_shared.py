import math
from django.db.models import Sum
from kakeibo.models import Budget

def calc_payment(records_this_month):
    """
    Calculate payment and payment percentage
    """
    if records_this_month.exists():
        # Payment
        payment_total = records_this_month.aggregate(sum=Sum('fee'))['sum']
        payment_hoko = records_this_month.filter(paid_by__last_name="朋子").aggregate(sum=Sum('fee'))['sum']
        if payment_hoko:
            payment_takashi = payment_total - payment_hoko
        else:
            payment_takashi = payment_total
            payment_hoko = 0
        # Payment (%)
        pp_takashi = math.floor(100 * payment_takashi / payment_total)
        pp_hoko = 100 - pp_takashi
    else:
        # Payment
        payment_total = payment_hoko = payment_takashi = 0
        # Payment (%)
        pp_takashi = pp_hoko = 0
    return {
        "payment": {
            "takashi": payment_takashi,
            "hoko": payment_hoko,
            "total": payment_total,
        },
        "p_payment": {
            "takashi": pp_takashi,
            "hoko": pp_hoko,
        },
    }

def calc_seisan(budget:Budget, diff:int, payment:dict):
    """
    Calculate seisan
    """
    is_black = diff < 0
    if is_black:
        # seisan
        seisan_hoko = budget.hoko + diff - payment['hoko']
        seisan_takashi = 0 if seisan_hoko > 0 else abs(seisan_hoko)
    else:
        # seisan
        seisan_hoko = budget.hoko + diff/2 - payment['hoko']
        seisan_takashi = 0 if seisan_hoko > 0 else abs(seisan_hoko)
    seisan_hoko = 0 if seisan_hoko < 0 else math.floor(seisan_hoko/1000)*1000
    return {
        "seisan": {
            "takashi": seisan_takashi,
            "hoko": seisan_hoko,
        },
    }

def calc_p_budget(budget:Budget, diff:int):
    """
    Calculate percentage of budget
    """
    is_black = diff < 0
    if is_black:
        # budget (%)
        p_takashi = math.floor(100 * budget.takashi / budget.total)
        p_hoko = 100 - p_takashi
        p_over = 0
    else:
        # budget (%)
        p_over = math.floor(100 * abs(diff) / (budget.total + diff))
        p_takashi = math.floor(100 * budget.takashi / (budget.total + diff))
        p_hoko = 100 - p_takashi - p_over
    return {
        'p_budget': {
            "takashi": p_takashi,
            "hoko": p_hoko,
            "over": p_over,
        },
    }