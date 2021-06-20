from django.core.management.base import BaseCommand
from kakeibo.models import Way, Resource, Kakeibo, Usage
import requests
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Get Kakeibo data'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        url = "https://www.fk-management.com/drm/kakeibo/usage/?limit=40"
        r = requests.get(url)
        json_data = r.json()
        msg = "Usage: {}".format(json_data['count'])
        self.stdout.write(self.style.SUCCESS(msg))
        self.stdout.write("============")
        usage_list = list()
        for r in json_data['results']:
            msg = "{}_{}".format(r['name'], r['is_expense'])
            self.stdout.write(self.style.SUCCESS(msg))
            if not Usage.objects.filter(name=r['name']).exists():
                u = Usage(name=r['name'], is_expense=r['is_expense'])
                usage_list.append(u)
        self.stdout.write("追加数：{}".format(len(usage_list)))
        Usage.objects.bulk_create(usage_list)
