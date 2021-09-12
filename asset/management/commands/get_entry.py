from django.core.management.base import BaseCommand
from django.conf import settings
from asset.models import Entry, Stock, ReasonWinLoss
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
        url = "https://www.fk-management.com/drm/web/entry/?limits=100"
        data_list = list()
        error_list = list()
        while True:
            r = requests.get(url)
            if not r.status_code == 200:
                raise Exception(f"Status code should be 200 but {r.status_code}")
            json_data = r.json()
            self.stdout.write(self.style.SUCCESS("Entry: {}".format(json_data['count'])))
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
                            f"Skipped Entry of legacy_id={r['id']} because Stock {r['stock']['code']} does not exist"
                        )
                        continue
                    # reason_win_loss

                    # status
                    if r['status'] is None:
                        status = "91.Others"
                    else:
                        status = self.MAPPING_STATUS[r["status"]["status"]]
                    # dict
                    d = {
                        "legacy_id": r["id"], 
                        "stock": stock,
                        "is_closed": r["is_closed"],
                        "is_nisa": r["is_nisa"],
                        "is_plan": r["is_plan"],
                        "status": status,
                        "reason_win_loss": None,
                        "entry_type": r["entry_type"],
                        "border_loss_cut": r["border_loss_cut"],
                        "border_profit_determination": r["border_profit_determination"],
                        "val_plan": r["val_plan"],
                        "num_plan": r["num_plan"],
                        "memo": r["memo"],
                    }
                    pprint.pprint(d)
                    # tranlate dict into Entry
                    self.stdout.write("------entry------")
                    if not Entry.objects.filter(legacy_id=r['id']).exists():
                        entry = Entry(**d)
                        # Add
                        data_list.append(entry)
                        pprint.pprint(entry.__dict__)
                    else:
                        entry = Entry.objects.get(legacy_id=r["id"])
                        updated_at = datetime.strptime(r['updated_at'], "%Y-%m-%dT%H:%M:%S.%f%z")
                        if entry.last_updated_at > updated_at:
                            # update
                            self.stdout.write(f"Update existing data of Legacy ID {r['id']}")
                        else:
                            # skip                        
                            self.stdout.write(f"Skip existing data of Legacy ID {r['id']}")
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
        Entry.objects.bulk_create(data_list)
        
            

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