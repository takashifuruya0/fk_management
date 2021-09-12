from django.core.management.base import BaseCommand
from django.conf import settings
from asset.models import Entry, Stock, Order
from datetime import datetime
import requests
import pprint
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Get Entry data'

    MAPPING_STATUS = {
        "013_ブレイク狙い_追いかけ": "01.BeforeEntry",
        "023_トレンド狙い_追いかけ": "01.BeforeEntry",
        "022_トレンド狙い_監視": "01.BeforeEntry",
        "021_トレンド狙い_押し目待ち": "01.BeforeEntry",
        "012_ブレイク狙い_監視": "01.BeforeEntry",
        "011_ブレイク狙い_寸前": "01.BeforeEntry",
        "00_EntryPlan": "01.BeforeEntry",	
        "9_リバランス検討": "11.Open",
        "8_積立中": "11.Open",
        "7_天井探り": "11.Open",
        "6_判断中（含み益）": "11.Open",
        "5_判断中（含み損）": "11.Open",
        "4_上昇トレンド乗り": "11.Open",
        "3_売り逃げ判断": "11.Open",
        "2_急騰": "11.Open",
        "1_swing": "11.Open",
    }

    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        url = "https://www.fk-management.com/drm/web/order/?limits=100"
        data_list = list()
        error_list = list()
        while True:
            r = requests.get(url)
            if not r.status_code == 200:
                raise Exception(f"Status code should be 200 but {r.status_code}")
            json_data = r.json()
            self.stdout.write(self.style.SUCCESS("Order: {}".format(json_data['count'])))
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
                            f"Skipped Order of legacy_id={r['id']} because Stock {r['stock']['code']} does not exist"
                        )
                        continue
                    if Entry.objects.filter(legacy_id=r['entry']).exists():
                        entry = Entry.objects.get(legacy_id=r['entry'])
                    else:
                        # to simplify the command, the command does not create Stock data.
                        self.stdout.write(
                            f"Skipped Order of legacy_id={r['id']} because Entry {r['entry']} does not exist"
                        )
                        continue
                    # dict
                    d = {
                        "legacy_id": r["id"], 
                        "stock": stock,
                        "is_nisa": r["is_nisa"],
                        "datetime": r["datetime"],
                        "is_nisa": r['is_nisa'],
                        "is_buy": r['is_buy'],
                        "num": r['num'],
                        "val": r['val'],
                        "commission": r['commission'],
                        "entry": entry,
                    }
                    pprint.pprint(d)
                    # tranlate dict into Entry
                    self.stdout.write("------order------")
                    if not Order.objects.filter(legacy_id=r['id']).exists():
                        o = Order(**d)
                        # Add
                        data_list.append(o)
                        pprint.pprint(o.__dict__)
                    else:
                        # skip                        
                        self.stdout.write(f"Skip existing order of legacy_id={r['id']}")
                        continue
                except Exception as e:
                    error_list.append({"msg": e, "data": r})
                    self.stderr.write(str(e))
            if not json_data['next']:
                self.stdout.write(
                    ("=================={}/{}====================".format(len(data_list), json_data['count']))
                )
                break
            url = json_data['next']
        # Print Error List
        if error_list:
            self.stdout.write("====================")
            pprint.pprint(error_list)
        # Bulk Create
        Order.objects.bulk_create(data_list)
        
            

# {
#     "id": 121,
#     "stock": {
#         "code": "3186",
#         "name": "(株)ネクステージ"
#     },
#     "datetime": "2019-01-18T10:43:00+09:00",
#     "is_nisa": true,
#     "is_buy": true,
#     "is_simulated": false,
#     "num": 100,
#     "val": 1304.0,
#     "commission": 0,
#     "chart": "https://www.fk-management.com/document/images/2020-01-06_3186_iMKNCRF.png",
#     "fkmanage_id": 69,
#     "user": 1,
#     "entry": 18
# },