from django.core.management.base import BaseCommand
from django.conf import settings
from asset.models import Stock, StockValueData
import requests
import pprint
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Get stock value data'
        
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        url = "https://www.fk-management.com/drm/web/stockvaluedata/?limit=1000"
        stock_list = list()
        error_list = list()
        while True:
            r = requests.get(url)
            if not r.status_code == 200:
                raise Exception(f"Status code should be 200 but {r.status_code}")
            json_data = r.json()
            self.stdout.write(self.style.SUCCESS("StockValueData: {}".format(json_data['count'])))
            for r in json_data['results']:
                try:
                    self.stdout.write("============")
                    self.stdout.write("------response------")
                    pprint.pprint(r)
                    # prepare dict
                    self.stdout.write("------data------")
                    if Stock.objects.filter(code=r['stock']['code']).exists():
                        stock = Stock.objects.get(code=r['stock']['code'])
                    else:
                        # to simplify the command, the command does not create Stock data.
                        self.stdout.write(
                            f"Skipped StockValueData of legacy_id={r['id']} because Stock {r['stock']['code']} does not exist"
                        )
                        continue
                    d = {
                        "legacy_id": r["id"],
                        "val_high": r['val_high'],
                        "val_low": r['val_low'],
                        "val_open": r['val_open'],
                        "val_close": r['val_close'],
                        "turnover": r["turnover"],
                        "stock": stock,
                    }
                    pprint.pprint(d)
                    # tranlate dict into Stock
                    self.stdout.write("------StockValueData------")
                    if not StockValueData.objects.filter(legacy_id=r['id']).exists():
                        svd = StockValueData(**d)
                        # Add
                        stock_list.append(svd)
                        pprint.pprint(svd)
                    else:
                        self.stdout.write(f"StockValueData of legacy_id={r['id']} exists")
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
        StockValueData.objects.bulk_create(stock_list)
        
            

# {
#     "id": 12677,
#     "stock": {
#         "code": "64317081",
#         "name": "SMT J-REITインデックス･オープン"
#     },
#     "date": "2008-01-09",
#     "val_high": 10000.0,
#     "val_low": 10000.0,
#     "val_open": 10000.0,
#     "val_close": 10000.0,
#     "turnover": 423000000.0
# }