from django.core.management.base import BaseCommand
from django.conf import settings
from ...models.models_kakeibo import Resource, Kakeibo, Usage
import requests
import pprint
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Get Kakeibo data'
    mapping_resource = {
        "SBI敬士": "SBI",
        "投資口座": "投資元本",
        "一般財形": "財形",
    }
    mapping_way = {
        "支出（現金）": "支出",
        "支出（クレジット）": "支出",
        "支出（Suica）": "その他",
        "引き落とし": "支出",
        "収入": "収入",
        "振替": "振替",
        "共通支出": "その他",
        "その他": "その他",
    }
    mapping_usage = {
        "書籍": "自己研鑽",
        "喫茶店": "娯楽費",
    }
    

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
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

        
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        url = "https://www.fk-management.com/drm/kakeibo/kakeibo/?limit=100"
        if options['date_from'] and options['date_to']:
            url = f"{url}&date_range_after={options['date_from'][0]}&date_range_before={options['date_to'][0]}"
        elif options['date_from']:
            url = f"{url}&date_range_after={options['date_from'][0]}"
        elif options['date_to']:
            url = f"{url}&date_range_before={options['date_to'][0]}"
        # raise Exception(url)
        kakeibo_list = list()
        error_list = list()
        transfer = Usage.objects.get(name="振替")
        other = Usage.objects.get(name="その他")
        while True:
            r = requests.get(url)
            json_data = r.json()
            self.stdout.write(self.style.SUCCESS("Kakeibo: {}".format(json_data['count'])))
            for r in json_data['results']:
                try:
                    self.stdout.write("============")
                    pprint.pprint(r)
                    if Kakeibo.objects.filter(is_active=True, legacy_id=r['pk']).exists():
                        self.stdout.write("{} already existed".format(r['pk']))
                        continue
                    # currency
                    currency = r['currency']
                    pprint.pprint(f"currency: {currency}")
                    # usage
                    if r['usage']:
                        name = self.mapping_usage.get(r['usage']['name'], r['usage']['name'])
                        usages = Usage.objects.filter(name=name, is_active=True)
                        if (n:=usages.count()) != 1:
                            raise Exception(f"Multiple Found Error: {n} Usage {name} were found")
                        else:
                            usage = usages[0]
                    elif not r['move_from'] or not r['move_to']:
                        # usageが設定されていないが、resourcesなし --> その他
                        usage = other
                    else:
                        # usageが設定されていないが、resourcesあり --> 振替
                        usage = transfer
                    # resources
                    resource_from = None
                    if r['move_from']:
                        name = self.mapping_resource.get(r['move_from']['name'], r['move_from']['name'])
                        resources_from = Resource.objects.filter(name=name, is_active=True)
                        if (n:=resources_from.count()) != 1:
                            raise Exception(f"Multiple Found Error: {n} ResourceFrom {name} were found")
                        else:
                            resource_from = resources_from[0]
                        pprint.pprint(f"resource_from: {resource_from}")
                    resource_to = None
                    if r['move_to']:
                        name = self.mapping_resource.get(r['move_to']['name'], r['move_to']['name'])
                        resources_to = Resource.objects.filter(name=name, is_active=True)
                        if (n:=resources_to.count()) != 1:
                            raise Exception(f"Multiple Found Error: {n} ResourceTo {name} were found")
                        else:
                            resource_to = resources_to[0]
                        pprint.pprint(f"resource_to: {resource_to}")
                    # way
                    way = self.mapping_way[r['way']]
                    if "Exchange" in usage.name:
                        way = "両替"
                    pprint.pprint(f"way: {way}")
                    # init Kakeibo
                    d = {
                        "fee": r['fee'],
                        "date": r['date'],
                        "memo": r['memo'],
                        "way": way,
                        "usage": usage,
                        "resource_from": resource_from,
                        "resource_to": resource_to,
                        "fee_converted": r['fee_converted'],  # save以外は自動算出されない
                        "legacy_id": r['pk'],
                        "currency": currency,
                        "rate": r['rate'],
                    }
                    k = Kakeibo(**d)
                    kakeibo_list.append(k)
                    pprint.pprint(k)
                    pprint.pprint(d)
                except Exception as e:
                    error_list.append({"msg": e, "data": r})
                    self.stderr.write(str(e))
            if not json_data['next']:
                Kakeibo.objects.bulk_create(kakeibo_list)
                self.stdout.write("======================================")
                if error_list:
                    self.stdout.write(self.style.WARNING("------------ Errors ------------"))
                    pprint.pprint(error_list)
                    self.stdout.write(self.style.WARNING("--------------------------------"))
                self.stdout.write(self.style.SUCCESS("Success: {}".format(len(kakeibo_list))))
                self.stdout.write(self.style.ERROR("Fail: {}".format(len(error_list))))
                self.stdout.write("Total: {}".format(len(json_data['count'])))
                self.stdout.write("======================================")
                break
            url = json_data['next']

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