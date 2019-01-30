# -*- coding: utf-8 -*-
import sys

from django.contrib import admin
from .models import Question, QuestionBank, TestCard, TestSet


# Register your models here.
default_encoding = 'utf-8'
if sys.getdefaultencoding() != default_encoding:
    reload(sys)
    sys.setdefaultencoding(default_encoding)

admin.site.register(QuestionBank)
admin.site.register(TestCard)
admin.site.register(Question)
admin.site.register(TestSet)
