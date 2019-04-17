"""
from django.db import models
from django.utils import timezone
# Create your models here.

class Category(models.Model):
    category = models.CharField("クラスタリングのタイトル", max_length=20)
    created_at = models.DateTimeField('日付', auto_now= True)
    def __str__(self):
        return self.subclass



class Url(models.Model):
    site = models.URLField("URL", max_length=140)
    site_name = models.CharField('URLの説明', max_length=20)
    category = models.ForeignKey(
      Category, verbose_name='タイトルの名前', on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField('日付', auto_now=True)

    def __str__(self):
        return self.site_name
"""
