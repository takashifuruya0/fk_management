# from django.core.management.base import BaseCommand
# from kakeibo.models import SharedResource
# from kakeibo.functions import notification
# from django.conf import settings
# from django.urls import reverse
# from allauth.socialaccount.models import SocialAccount
# from datetime import date
# import requests
# import json
# import pprint
# import logging
# logger = logging.getLogger('django')


# # BaseCommandを継承して作成
# class Command(BaseCommand):
#     # python manage.py help count_entryで表示されるメッセージ
#     help = 'Command Test'

#     def add_arguments(self, parser):
#         # Named (optional) arguments
#         parser.add_argument(
#             '--sr',
#             default=[],
#             nargs=1,
#             help='shared resource to report',
#         )

#     # コマンドライン引数を指定します。(argparseモジュール https://docs.python.org/2.7/library/argparse.html)
#     # コマンドが実行された際に呼ばれるメソッド
#     def handle(self, *args, **options):
#         msg = [
#             self.get_message(sr)
#             for sr in SharedResource.objects.filter(pk__in=options['sr'])
#         ]
#         if len(msg) == 1:
#             message = {
#                 "type": "flex",
#                 "altText": "this is a flex message",
#                 "contents": msg[0]
#             }
#             # LINEアカウントが紐付いているユーザを抽出
#             targets = SocialAccount.objects.filter(provider="line")
#             for target in targets:
#                 res = notification.push_line_messange(target.uid, [message,])
#                 if res['status']:
#                     self.stdout.write(self.style.SUCCESS(f"Send monthly report to {target.user.username}"))
#                 else:
#                     self.stderr.write(str(res['response']))

#     def get_message(self, sr:SharedResource):
#         """
#         指定年月の月次レポートを作成
#         """
#         path = reverse("kakeibo:shared_resource_detail", kwargs={"pk": sr.pk})
#         if sr.kind == "貯金":
#             bg_card = "#27ACB2"
#             bg_line = "#0D8186"
#             bg_line_remaining = "#27ACB2"
#         elif sr.kind == "返済":
#             bg_card = "#FF6B6E"
#             bg_line = "#DE5658"
#             bg_line_remaining = "#FAD2A76E"
#         # dictを返す
#         res = {
#             "type": "bubble",
            
#             "header": {
#                 "type": "box",
#                 "layout": "vertical",
#                 "contents": [
#                     {
#                         "type": "text",
#                         "text": f"{sr.name} : {sr.val_goal:,}円",
#                         "color": "#ffffff",
#                         "align": "start",
#                         "size": "lg",
#                         "gravity": "center",
#                         "weight": "bold"
#                     },
#                     {
#                         "type": "text",
#                         "text": f"進捗：{sr.progress_100}%",
#                         "color": "#ffffff",
#                         "align": "start",
#                         "size": "sm",
#                         "gravity": "center",
#                         "margin": "lg"
#                     },
#                     {
#                         "type": "box",
#                         "layout": "vertical",
#                         "contents": [
#                         {
#                             "type": "box",
#                             "layout": "vertical",
#                             "contents": [
#                             {
#                                 "type": "filler"
#                             },
#                             {
#                                 "type": "text",
#                                 "text": f"{sr.val_actual:,}円",
#                                 "size": "sm",
#                                 "margin": "xs",
#                                 "weight": "regular",
#                                 "color": "#DDDDDD",
#                                 "style": "normal",
#                                 "align": "center"
#                             }
#                             ],
#                             "width": f"{sr.progress_100}%",
#                             "backgroundColor": f"{bg_line}",
#                             "height": "20px",
#                             "cornerRadius": "xs"
#                         }
#                         ],
#                         "backgroundColor": f"{bg_line_remaining}",
#                         "height": "20px",
#                         "margin": "sm",
#                         "cornerRadius": "sm"
#                     }
#                 ],
#                 "backgroundColor": f"{bg_card}",
#                 "paddingTop": "19px",
#                 "paddingAll": "12px",
#                 "paddingBottom": "16px"
#             },
#             "body": {
#                 "type": "box",
#                 "layout": "vertical",
#                 "contents": [
#                 {
#                     "type": "box",
#                     "layout": "vertical",
#                     "contents": [
#                     {
#                         "type": "text",
#                         "text": f"{sr.date_open}〜{sr.date_close if sr.date_close else ''}"
#                     },
#                     {
#                         "type": "text",
#                         "text": f"{sr.detail}"
#                     }
#                     ],
#                     "flex": 1
#                 }
#                 ],
#                 "spacing": "md",
#                 "paddingAll": "12px"
#             },
#             "footer": {
#                 "type": "box",
#                 "layout": "vertical",
#                 "contents": [
#                     {
#                         "type": "button",
#                         "action": {
#                         "type": "uri",
#                         "label": "詳細はこちら",
#                         "uri": f"{settings.BASE_URL}{path}"
#                         },
#                         "style": "secondary"
#                     }
#                 ]
#             },
#             # "size": "giga",
#             "styles": {
#                 "footer": {
#                     "separator": False
#                 }
#             }
#         }
#         return res
