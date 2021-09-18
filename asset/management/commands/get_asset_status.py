from django.core.management.base import BaseCommand
from django.conf import settings
from asset.models import AssetStatus
import requests
import pprint
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Get AssetStatus data'
        
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        url = "https://www.fk-management.com/drm/web/assetstatus/?limit=100"
        data_list = list()
        error_list = list()
        while True:
            r = requests.get(url)
            json_data = r.json()
            self.stdout.write(self.style.SUCCESS("AssetStatus: {}".format(json_data['count'])))
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
                        "buying_power": r["buying_power"],
                        "investment": r["investment"],
                        "nisa_power": r["nisa_power"],
                        "sum_stock": r["sum_stock"],
                        "sum_trust": r["sum_trust"],
                        "sum_other": r["sum_other"],
                    }
                    pprint.pprint(d)
                    # tranlate dict into AssetStatus
                    self.stdout.write("------AssetStatus------")
                    if not AssetStatus.objects.filter(legacy_id=r['id']).exists():
                        s = AssetStatus(**d)
                        # Add
                        data_list.append(s)
                        pprint.pprint(s)
                    else:
                        self.stdout.write(f"AssetStatus of legacy_id={r['id']} exists")
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
        AssetStatus.objects.bulk_create(data_list)
        
            

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