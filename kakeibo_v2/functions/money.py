# coding:utf-8
import requests

def get_rate(currency="USD"):
    """Get rate from aoikujira

    Args:
        currency (str): USD/EUR/etc. Default value is USD

    Returns:
        float|none: rate
    
    """
    url = f"http://api.aoikujira.com/kawase/json/{currency}"
    res = requests.get(url)
    if res.status_code == 200:
        res_json = res.json()
        try:
            rate = float(res_json["JPY"])
        except Exception as e:
            rate = None
    else:
        rate = None
    return rate

