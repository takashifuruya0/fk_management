from dateutil.relativedelta import relativedelta
from django.core.management.base import BaseCommand
from kakeibo.models import Budget, SharedKakeibo, Usage
from kakeibo.functions import calculation_shared, notification
from django.conf import settings
from django.db.models import Sum
from allauth.socialaccount.models import SocialAccount
from datetime import date
import requests
import json
import logging
logger = logging.getLogger('django')


# BaseCommandを継承して作成
class Command(BaseCommand):
    # python manage.py help count_entryで表示されるメッセージ
    help = 'Command Test'

    def add_arguments(self, parser):
        # Named (optional) arguments
        last_month = date.today() - relativedelta(months=1)
        parser.add_argument(
            '--year',
            default=[last_month.year],
            nargs=1,
            help='target year to report',
        )
        parser.add_argument(
            '--month',
            default=[last_month.month],
            nargs=1,
            help='target month to report',
        )

    # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
    # コマンドが実行された際に呼ばれるメソッド
    def handle(self, *args, **options):
        message = {
            "type": "flex",
            "altText": "this is a flex message",
            "contents": self.get_message(
                year=int(options['year'][0]), month=int(options['month'][0])
            )
        }
        # LINEアカウントが紐付いているユーザを抽出
        targets = SocialAccount.objects.filter(provider="line")
        for target in targets:
            res = notification.push_line_messange(target.uid, [message,])
            if res['status']:
                self.stdout.write(self.style.SUCCESS(f"Send monthly report to {target.user.username}"))
            else:
                self.stderr.write(str(res['response']))

    def get_message(self, year, month):
        """
        指定年月の月次レポートを作成
        """
        # 年月指定
        target_ym = date(year, month, 1)
        # 対象データ抽出
        records_this_month = SharedKakeibo.objects.filter(
            is_active=True, date__year=target_ym.year, date__month=target_ym.month
        )
        budget = Budget.objects.filter(date__lte=target_ym).latest('date')
        # payment
        payment = calculation_shared.calc_payment(records_this_month)['payment']
        # Black/Red
        diff = payment['total']- budget.total
        is_black = diff < 0
        # seisan
        seisan = calculation_shared.calc_seisan(budget, diff, payment)['seisan']
        # Usages
        usages_shared = Usage.objects.filter(is_active=True, is_shared=True).prefetch_related('sharedkakeibo_set')
        usages = dict()
        for us in usages_shared.order_by('pk'):
            tm_sum = us.sharedkakeibo_set.filter(
                is_active=True, date__year=target_ym.year, date__month=target_ym.month).aggregate(sum=Sum('fee'))['sum']
            usages[us.name] = tm_sum if tm_sum else 0
        # box
        boxes = list()
        for k,v in usages.items():
            box = {
                "type": "box",
                "layout": "horizontal",
                "contents": [
                {
                    "type": "text",
                    "text": f"{k}",
                    "size": "sm",
                    "color": "#555555"
                },
                {
                    "type": "text",
                    "text": f"{v:,}円",
                    "size": "sm",
                    "color": "#111111",
                    "align": "end"
                }
                ]
            }
            boxes.append(box)
        # dictを返す
        return {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "text",
                    "text": "月次レポート",
                    "weight": "bold",
                    "color": "#1DB446",
                    "size": "sm"
                },
                {
                    "type": "text",
                    "text": f"{target_ym.year}年{target_ym.month}月",
                    "weight": "bold",
                    "size": "xxl",
                    "margin": "md"
                },
                {
                    "type": "text",
                    "text": f"発行日：{date.today()}",
                    "size": "xs",
                    "color": "#aaaaaa",
                    "wrap": True
                },
                {
                    "type": "separator",
                    "margin": "xxl"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "xxl",
                    "spacing": "sm",
                    "contents": [
                    {
                        "type": "text",
                        "text": "概要",
                        "size": "md",
                        "weight": "bold"
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "text",
                            "text": "支出",
                            "size": "sm",
                            "color": "#555555",
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": f"{payment['total']:,}円",
                            "size": "sm",
                            "color": "#111111",
                            "align": "end"
                        }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "text",
                            "text": "予算",
                            "size": "sm",
                            "color": "#555555",
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": f"{budget.takashi+budget.hoko:,}円",
                            "size": "sm",
                            "color": "#111111",
                            "align": "end"
                        }
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "horizontal",
                        "contents": [
                        {
                            "type": "text",
                            "text": "精算",
                            "size": "sm",
                            "color": "#555555",
                            "flex": 0
                        },
                        {
                            "type": "text",
                            "text": f"{seisan['hoko']:,}円",
                            "size": "sm",
                            "color": "#111111",
                            "align": "end"
                        }
                        ]
                    },
                    {
                        "type": "separator",
                        "margin": "xxl"
                    },
                    {
                        "type": "text",
                        "text": "分類別",
                        "size": "md",
                        "weight": "bold",
                        "margin": "lg"
                    },
                    ] + boxes
                },
                {
                    "type": "separator",
                    "margin": "xxl"
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "md",
                    "contents": [
                    {
                        "type": "text",
                        "text": "PAYMENT ID",
                        "size": "xs",
                        "color": "#aaaaaa",
                        "flex": 0
                    },
                    {
                        "type": "text",
                        "text": "#743289384279",
                        "color": "#aaaaaa",
                        "size": "xs",
                        "align": "end"
                    }
                    ]
                }
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                {
                    "type": "button",
                    "action": {
                        "type": "uri",
                        "label": "fk-management",
                        "uri": settings.BASE_URL
                    },
                    "style": "primary"
                }
                ]
            },
            "styles": {
                "footer": {
                "separator": True
                }
            }
            }
        
