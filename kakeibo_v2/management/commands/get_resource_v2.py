from django.core.management.base import BaseCommand
from ...models.models_kakeibo import Resource
from django.conf import settings
import requests
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Get Resource data'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        url = "https://www.fk-management.com/drm/kakeibo/resource/?limit=40"
        mapping_resource = settings.MAPPING_RESOURCE
        r = requests.get(url)
        json_data = r.json()
        msg = "Resource: {}".format(json_data['count'])
        self.stdout.write(self.style.SUCCESS(msg))
        self.stdout.write("============")
        resouce_list = list()
        for r in json_data['results']:
            msg = "{}_{}".format(r['name'], r['is_saving'])
            self.stdout.write(self.style.SUCCESS(msg))
            rname = mapping_resource.get(r['name'], r['name'])
            if not Resource.objects.filter(name=rname).exists():
                r = Resource(name=rname, is_investment=r['is_saving'], legacy_id=r['pk'])
                resouce_list.append(r)
        self.stdout.write("追加数：{}".format(len(resouce_list)))
        Resource.objects.bulk_create(resouce_list)
