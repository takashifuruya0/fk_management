from django.core.management.base import BaseCommand
from django.conf import settings
from asset.models import Ipo, Stock, Entry
import requests
import pprint
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Get Ipo data'
        
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        url = "https://www.fk-management.com/drm/web/ipo/?limit=100"
        data_list = list()
        error_list = list()
        while True:
            r = requests.get(url)
            json_data = r.json()
            self.stdout.write(self.style.SUCCESS("Ipo: {}".format(json_data['count'])))
            for r in json_data['results']:
                try:
                    self.stdout.write("============")
                    self.stdout.write("------response------")
                    pprint.pprint(r)
                    # prepare dict
                    if Stock.objects.filter(code=r['stock']['code']).exists():
                        stock = Stock.objects.get(code=r['stock']['code'])
                    else:
                        # to simplify the command, the command does not create Stock data.
                        self.stdout.write(
                            f"Skipped Ipo of legacy_id={r['id']} because Stock {r['stock']['code']} does not exist"
                        )
                        continue
                    if not r["entry"]:
                        entry = None
                    elif Entry.objects.filter(legacy_id=r['entry']).exists():
                        entry = Entry.objects.get(legacy_id=r['entry'])
                    else:
                        # to simplify the command, the command does not create Stock data.
                        self.stdout.write(
                            f"Skipped Order of legacy_id={r['id']} because Entry {r['entry']} does not exist"
                        )
                        continue
                    self.stdout.write("------data------")
                    d = {
                        "legacy_id": r["id"],
                        "stock": stock,
                        "datetime_open": r["datetime_open"],
                        "datetime_close": r["datetime_close"],
                        "status": r["status"],
                        "val_list": r['val_list'],
                        "date_list": r["date_list"],
                        "datetime_select": r["datetime_select"],
                        "is_applied": r["is_applied"],
                        "date_applied": r["date_applied"],
                        "num_applied": r["num_applied"],
                        "point": r["point"],
                        "result_select": r["result_select"],
                        "datetime_purchase_open": r["datetime_purchase_open"],
                        "datetime_purchase_close": r["datetime_purchase_close"],
                        "num_select": r["num_select"],
                        "rank": r["rank"],
                        "val_predicted": r["val_predicted"],
                        "url": r["url"],
                        "val_initial": r["val_initial"],
                        "memo": r["memo"],
                        "entry": entry,
                    }
                    pprint.pprint(d)
                    # tranlate dict into Ipo
                    self.stdout.write("------Ipo------")
                    if not Ipo.objects.filter(legacy_id=r['id']).exists():
                        s = Ipo(**d)
                        # Add
                        data_list.append(s)
                        pprint.pprint(s)
                    else:
                        self.stdout.write(f"Ipo of legacy_id={r['id']} exists")
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
        Ipo.objects.bulk_create(data_list)
        
            

# {
#     "id": 9,
#     "stock": {
#         "code": "6227",
#         "name": "ＡＩメカテック(株)"
#     },
#     "created_at": "2021-07-19T21:54:52.782463+09:00",
#     "updated_at": "2021-07-30T18:00:04.950807+09:00",
#     "datetime_open": "2021-07-12T00:00:00+09:00",
#     "datetime_close": "2021-07-16T11:00:00+09:00",
#     "status": "4.落選（上場後）",
#     "val_list": 1920.0,
#     "date_list": "2021-07-30",
#     "datetime_select": null,
#     "is_applied": false,
#     "date_applied": null,
#     "num_applied": null,
#     "point": null,
#     "result_select": null,
#     "datetime_purchase_open": "2021-07-20T00:00:00+09:00",
#     "datetime_purchase_close": "2021-07-26T12:00:00+09:00",
#     "result_buy": "-",
#     "num_select": null,
#     "rank": "C",
#     "val_predicted": 1991.0,
#     "url": "https://kabu.96ut.com/article/ipo/2021065/index.php#yoso",
#     "val_initial": 1941.0,
#     "memo": "",
#     "entry": null
# }