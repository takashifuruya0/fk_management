from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from ...models import SharedKakeibo, Usage
import requests
import pprint
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Get SharedKakeibo data'
    mapping_paid_by = {
        "敬士": get_user_model().objects.first(),
        "朋子": get_user_model().objects.last(),
    }

    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            '--date_from',
            default='',
            nargs=1,
            help='add filter by date_from',
        )
        parser.add_argument(
            '--date_to',
            default='',
            nargs=1,
            help='add filter by date_to',
        )


    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        url = "https://www.fk-management.com/drm/kakeibo/shared/?limit=100"
        if options['date_from'] and options['date_to']:
            url = f"{url}&date_range_after={options['date_from'][0]}&date_range_before={options['date_to'][0]}"
        elif options['date_from']:
            url = f"{url}&date_range_after={options['date_from'][0]}"
        elif options['date_to']:
            url = f"{url}&date_range_before={options['date_to'][0]}"
        skakeibo_list = list()
        error_list = list()
        transfer = Usage.objects.get(name="振替")
        while True:
            r = requests.get(url)
            json_data = r.json()
            self.stdout.write(self.style.SUCCESS("SharedKakeibo: {}".format(json_data['count'])))
            for r in json_data['results']:
                try:
                    self.stdout.write("============")
                    pprint.pprint(r)
                    if SharedKakeibo.objects.filter(is_active=True, legacy_id=r['pk']).exists():
                        self.stdout.write("{} already existed".format(r['pk']))
                        continue
                    # mapping
                    if r['usage']:
                        usage = Usage.objects.get(name=r['usage']['name'])
                    else:
                        usage = transfer
                    d = {
                        "fee": r['fee'],
                        "date": r['date'],
                        "memo": r['memo'],
                        "usage": usage,
                        "paid_by": self.mapping_paid_by[r['paid_by']],
                        "legacy_id": r['pk'],
                    }
                    sk = SharedKakeibo(**d)
                    skakeibo_list.append(sk)
                    pprint.pprint(sk)
                    pprint.pprint(d)
                except Exception as e:
                    error_list.append({"msg": e, "data": r})
                    self.stderr.write(str(e))

            if not json_data['next']:
                print("=================={}/{}====================".format(len(skakeibo_list), json_data['count']))
                break
            url = json_data['next']
        if error_list:
            self.stdout.write("====================")
            pprint.pprint(error_list)
        SharedKakeibo.objects.bulk_create(skakeibo_list)

# {
#     "pk": 1536,
#     "date": "2017-04-11",
#     "fee": 510,
#     "way": "支出（現金）",
#     "usage": {
#         "pk": 11,
#         "name": "外食費",
#         "is_expense": true
#     },
#     "move_to": null,
#     "move_from": {
#         "pk": 3,
#         "name": "財布",
#         "is_saving": false
#     },
#     "memo": "昼食"
# },