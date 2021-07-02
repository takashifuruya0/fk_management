from django.core.management.base import BaseCommand
from kakeibo.models import Way, Resource, Kakeibo, Usage
import requests, pprint
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

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        url = "https://www.fk-management.com/drm/kakeibo/kakeibo/?limit=100"
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
                    # usage
                    if r['usage']:
                        usage = Usage.objects.get(name=r['usage']['name'])
                    elif r['move_from'] or r['move_to']:
                        # usageが設定されていないが、resourcesなし --> その他
                        usage = other
                    else:
                        # usageが設定されていないが、resourcesあり --> 振替
                        usage = transfer
                    # resources
                    resource_from = None
                    if r['move_from']:
                        if self.mapping_resource.get(r['move_from']['name'], None):
                            resource_from = Resource.objects.get(name=self.mapping_resource.get(r['move_from']['name']))
                        else:
                            resource_from = Resource.objects.get(name=r['move_from']['name'])
                    resource_to = None
                    if r['move_to']:
                        if self.mapping_resource.get(r['move_to']['name'], None):
                            resource_to = Resource.objects.get(name=self.mapping_resource.get(r['move_to']['name']))
                        else:
                            resource_to = Resource.objects.get(name=r['move_to']['name'])
                    # way
                    if Way.objects.filter(resource_to=resource_to, resource_from=resource_from).exists():
                        way = Way.objects.get(resource_to=resource_to, resource_from=resource_from)
                    else:
                        way = Way(resource_to=resource_to, resource_from=resource_from, name=r['way'])
                        way.save()
                    # init Kakeibo
                    d = {
                        "fee": r['fee'],
                        "date": r['date'],
                        "memo": r['memo'],
                        "way": way,
                        "usage": usage,
                    }
                    k = Kakeibo(**d)
                    kakeibo_list.append(k)
                    pprint.pprint(k)
                    pprint.pprint(d)
                except Exception as e:
                    error_list.append({"msg": e, "data": r})
                    self.stderr.write(str(e))
            if not json_data['next']:
                self.stdout.write(
                    ("=================={}/{}====================".format(len(kakeibo_list), json_data['count']))
                )
                break
            url = json_data['next']
        if error_list:
            self.stdout.write("====================")
            pprint.pprint(error_list)
        Kakeibo.objects.bulk_create(kakeibo_list)

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