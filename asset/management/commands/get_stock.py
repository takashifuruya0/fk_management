from django.core.management.base import BaseCommand
from django.conf import settings
from asset.models import Stock
import requests
import pprint
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Get stock data'
        
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        url = "https://www.fk-management.com/drm/web/stock/?limit=100"
        stock_list = list()
        error_list = list()
        while True:
            r = requests.get(url)
            json_data = r.json()
            self.stdout.write(self.style.SUCCESS("Stock: {}".format(json_data['count'])))
            for r in json_data['results']:
                try:
                    self.stdout.write("============")
                    self.stdout.write("------response------")
                    pprint.pprint(r)
                    # prepare dict
                    self.stdout.write("------data------")
                    d = {
                        "legacy_id": r["id"],
                        "name": r['name'],
                        "code": r['code'],
                        "is_trust": r['is_trust'],
                        "is_listed": r['is_listed'],
                        "market": r['market'],
                        "industry": r["industry"],
                        "feature": r["feature"],
                        "consolidated_business": r["consolidated_business"],
                        "settlement_date": r["settlement_date"],
                        "unit": r['unit'],
                    }
                    pprint.pprint(d)
                    # tranlate dict into Stock
                    self.stdout.write("------stock------")
                    if not Stock.objects.filter(code=r['code']).exists():
                        s = Stock(**d)
                        # Add
                        stock_list.append(s)
                        pprint.pprint(s)
                    else:
                        self.stdout.write(f"{r['code']} exists")
                        continue
                except Exception as e:
                    error_list.append({"msg": e, "data": r})
                    self.stderr.write(str(e))
            if not json_data['next']:
                self.stdout.write(
                    ("=================={}/{}====================".format(len(stock_list), json_data['count']))
                )
                break
            url = json_data['next']
        # Print Error List
        if error_list:
            self.stdout.write("====================")
            pprint.pprint(error_list)
        # Bulk Create
        Stock.objects.bulk_create(stock_list)
        
            

# {
#     "id": 10,
#     "created_at": "2020-07-04T14:25:47.769408+09:00",
#     "updated_at": "2020-08-14T21:18:25.063523+09:00",
#     "code": "1813",
#     "name": "(株)不動テトラ",
#     "is_trust": false,
#     "market": "東証1部",
#     "industry": "建設業",
#     "fkmanage_id": 12,
#     "feature": "不動建設の土木部門とテトラが合併。海上土木が得意、地盤改良と２本柱。独自工法に強み",
#     "consolidated_business": "【連結事業】土木47(4)、地盤改良47(9)、ブロック5(13)、他0(3)(2020.3)",
#     "settlement_date": "3月末日",
#     "unit": "100株",
#     "dividend": 55,
#     "dividend_yield": 3.91,
#     "is_listed": true
# }