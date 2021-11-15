from django.core.management.base import BaseCommand
from ...models import Event, Kakeibo
import requests
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Get Event data'

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        url = "https://www.fk-management.com/drm/kakeibo/event/?limit=40"
        r = requests.get(url)
        json_data = r.json()
        msg = "Event: {}".format(json_data['count'])
        self.stdout.write(self.style.SUCCESS(msg))
        self.stdout.write("============")
        event_list = list()
        for r in json_data['results']:
            msg = "{}_{}".format(r['name'], r['date'])
            self.stdout.write(self.style.SUCCESS(msg))
            is_closed = False if r['is_active'] else True
            if not Event.objects.filter(name=r['name']).exists():
                event = Event(
                    name=r['name'], legacy_id=r['pk'], sum_plan=r['sum_plan'],
                    memo=r['memo'], detail=r['detail'], is_closed=is_closed,
                    date=r['date'],
                )
                event.save()
                event_list.append(event)
                # Link with Kakeibo
                kakeibo_list = list()
                for rk in r['kakeibos']:
                    k = Kakeibo.objects.get(legacy_id=rk['pk'])
                    k.event = event
                    k.save()
                    kakeibo_list.append(k)
                self.stdout.write("{}件の家計簿を{}に紐付けました".format(len(kakeibo_list), event))
        self.stdout.write("イベント追加数：{}".format(len(event_list)))
