from django.core.management.base import BaseCommand
from django.conf import settings
from asset.models import AssetTarget
import requests
import pprint
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Get AssetTarget data'
        
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        url = "https://www.fk-management.com/drm/web/assettarget/?limit=100"
        data_list = list()
        error_list = list()
        while True:
            r = requests.get(url)
            json_data = r.json()
            self.stdout.write(self.style.SUCCESS("AssetTarget: {}".format(json_data['count'])))
            for r in json_data['results']:
                try:
                    self.stdout.write("============")
                    self.stdout.write("------response------")
                    pprint.pprint(r)
                    # prepare dict
                    self.stdout.write("------data------")
                    d = {
                        "legacy_id": r["id"],
                        "date": r["date"],
                        "memo": r["memo"],
                        "val_investment": r["val_investment"],
                        "val_target": r["val_target"],
                    }
                    pprint.pprint(d)
                    # tranlate dict into AssetTarget
                    self.stdout.write("------AssetTarget------")
                    if not AssetTarget.objects.filter(legacy_id=r['id']).exists():
                        s = AssetTarget(**d)
                        # Add
                        data_list.append(s)
                        pprint.pprint(s)
                    else:
                        self.stdout.write(f"AssetTarget of legacy_id={r['id']} exists")
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
        AssetTarget.objects.bulk_create(data_list)
        
            

# {
#     "id": 1778,
#     "date": "2020-02-21",
#     "buying_power": 72326,
#     "investment": 2300000,
#     "nisa_power": 1000000,
#     "sum_stock": 1358200,
#     "sum_trust": 776267,
#     "sum_other": 0,
#     "user": 1
# }