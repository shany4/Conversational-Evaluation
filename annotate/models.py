# -*- coding: utf-8 -*-
import datetime
from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


def get_file_path(instance, filename):
    return 'tasks/' + str(instance.user) + '_' + str(instance.creation_date) + str(instance.name)


# 测试类型：
AB_TEST = 'AB_Test'
CONTEXT_BASED_AB_TEST = 'Content Based AB_Test'
CONTEXT_BASED = u"上下文对话"
BASIC_TEST = u'基本测试'
SIMILARITY = u'答案相似度'
ANSWER_ACCEPTANCE = u'答案接受度对比'
QUESTION_CHOICES = (
    (AB_TEST, AB_TEST),
    (CONTEXT_BASED_AB_TEST, CONTEXT_BASED_AB_TEST),
    (CONTEXT_BASED, CONTEXT_BASED),
    (BASIC_TEST, BASIC_TEST),
    (SIMILARITY, SIMILARITY),
    (ANSWER_ACCEPTANCE, ANSWER_ACCEPTANCE),
)

QUESTION_TYPE = [
    AB_TEST,
    CONTEXT_BASED_AB_TEST,
    CONTEXT_BASED,
    BASIC_TEST,
    SIMILARITY,
    ANSWER_ACCEPTANCE
]


####################################################
# database schema
####################################################
class Question(models.Model):
    """Model class that represents a question."""
    q_id = models.CharField(max_length=30, default='')
    question = models.TextField()
    answers = models.TextField()
    bot = models.TextField(default='None')

    def __str__(self):
        return str(self.id) + ' ' + str(self.question)


class QuestionBank(models.Model):
    """Model class that represents the bank of the uploaded question set."""
    # fields:
    user = models.ForeignKey(User)  # 上传的人
    name = models.CharField(max_length=30)
    num_distinct_questions = models.IntegerField(default=0)
    creation_date = models.DateField()
    type = models.CharField(max_length=30, choices=QUESTION_CHOICES)
    file = models.FileField(upload_to=get_file_path)
    questions = models.ManyToManyField(Question)
    current_query_index = models.IntegerField(default=0)
    dispatched_questions = models.TextField(default='')

    def __str__(self):
        return str(self.name)


class TestSet(models.Model):
    """Model class that represents each dispatched test"""
    user = models.ForeignKey(User)  # 做题的人
    questions = models.ManyToManyField(Question)
    questionBank = models.ForeignKey(QuestionBank)
    num_question = models.IntegerField(default=0)
    current_index = models.IntegerField(default=0)
    type = models.CharField(max_length=30, choices=QUESTION_CHOICES)
    result = models.TextField(null=True, blank=True)

    def __str__(self):
        return str(self.questionBank) + '_' + str(self.user) + '_' + str(self.num_question)


class TestCard(models.Model):
    """Model class that represents question card."""
    card_id = models.CharField(max_length=30, default='')
    question = models.ForeignKey(Question)
    testSet = models.ForeignKey(TestSet)
    answer = models.TextField(default='None', null=True, blank=True)
    bot = models.TextField(default='None')

    def __str__(self):
        return str(self.card_id)


class Robot(models.Model):
    """Model class that contains all robot service."""
    name = models.CharField(max_length=30, default='')

    def __str__(self):
        return str(self.name)
