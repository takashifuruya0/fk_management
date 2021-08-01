from django.test import TestCase
from kakeibo.templatetags import my_templatetags
from datetime import date
from dateutil.relativedelta import relativedelta
import math
# Create your tests here.


class TemplateTagsTest(TestCase):

    def test_yen(self):
        # 3 digits
        val = 100
        self.assertEqual(my_templatetags.yen(val), f"¥{val}")
        # 7 digits
        val = 1000000
        self.assertEqual(my_templatetags.yen(val), "¥1,000,000")
        # none
        val = None
        self.assertEqual(my_templatetags.yen(val), "-")
        # digits after the decimal point
        val = 1000.12
        self.assertEqual(my_templatetags.yen(val), "¥1,000")
        self.assertEqual(my_templatetags.yen(val, 1), "¥1,000.1")
        # minus
        val = -1000.12
        self.assertEqual(my_templatetags.yen(val), "<font color='red'>-¥1,000</font>")
        self.assertEqual(my_templatetags.yen(val, 1), "<font color='red'>-¥1,000.1</font>")

    def test_yen_nocolor(self):
        # 3 digits
        val = 100
        self.assertEqual(my_templatetags.yen(val), f"¥{val}")
        # 7 digits
        val = 1000000
        self.assertEqual(my_templatetags.yen_no_color(val), "¥1,000,000")
        # none
        val = None
        self.assertEqual(my_templatetags.yen_no_color(val), "-")
        # digits after the decimal point
        val = 1000.12
        self.assertEqual(my_templatetags.yen_no_color(val), "¥1,000")
        self.assertEqual(my_templatetags.yen_no_color(val, 1), "¥1,000.1")
        # minus
        val = -1000.12
        self.assertEqual(my_templatetags.yen_no_color(val), "-¥1,000")
        self.assertEqual(my_templatetags.yen_no_color(val, 1), "-¥1,000.1")

    def test_pct(self):
        # 2 digits
        val = 10.123
        self.assertEqual(my_templatetags.pct(val), "10.12%")
        self.assertEqual(my_templatetags.pct(val, 0), "10.0%")
        # none
        val = None
        self.assertEqual(my_templatetags.pct(val), "-")
        # minus
        val = -12.321
        self.assertEqual(my_templatetags.pct(val), "<font color='red'>-12.32%</font>")
        self.assertEqual(my_templatetags.pct(val, 0), "<font color='red'>-12.0%</font>")

    def test_pct100(self):
        # 2 digits
        val = 0.10123
        self.assertEqual(my_templatetags.pct_100(val), "10.12%")
        self.assertEqual(my_templatetags.pct_100(val, 0), "10.0%")
        # none
        val = None
        self.assertEqual(my_templatetags.pct_100(val), "-")
        # minus
        val = -0.12321
        self.assertEqual(my_templatetags.pct_100(val), "<font color='red'>-12.32%</font>")
        self.assertEqual(my_templatetags.pct_100(val, 0), "<font color='red'>-12.0%</font>")

    def test_usd(self):
        # 3 digits
        val = 100
        self.assertEqual(my_templatetags.usd(val), f"${val}")
        # 7 digits
        val = 1000000
        self.assertEqual(my_templatetags.usd(val), "$1,000,000")
        # none
        val = None
        self.assertEqual(my_templatetags.usd(val), "-")
        # digits after the decimal point
        val = 1000.12
        self.assertEqual(my_templatetags.usd(val), "$1,000")
        self.assertEqual(my_templatetags.usd(val, 1), "$1,000.1")
        # minus
        val = -1000.12
        self.assertEqual(my_templatetags.usd(val), "<font color='red'>-$1,000</font>")
        self.assertEqual(my_templatetags.usd(val, 1), "<font color='red'>-$1,000.1</font>")