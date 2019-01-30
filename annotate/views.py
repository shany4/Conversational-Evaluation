#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import xlrd
import csv
import json
import codecs
import datetime
from random import shuffle, randint
from django.conf import settings
from django.shortcuts import render
from .models import TestSet, TestCard, Question, QuestionBank, QUESTION_TYPE, Robot
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.db.models import F


backgroundColor = [
    {'dark': 'rgb(255, 99, 132)', 'light': 'rgba(255, 99, 132, 0.2)'},
    {'dark': 'rgb(255, 159, 64)', 'light': 'rgba(255, 159, 64, 0.2)'},
    {'dark': 'rgb(75, 192, 192)', 'light': 'rgba(75, 192, 192, 0.2)'},
    {'dark': 'rgb(153, 102, 255)', 'light': 'rgba(153, 102, 255, 0.2)'},
    {'dark': 'rgb(60,179,113)', 'light': 'rgba(60,179,113,0.2)'},
    {'dark': 'rgb(128,0,0)', 'light': 'rgba(128,0,0,0.2)'},
    {'dark': 'rgb(0, 130, 82)', 'light': 'rgba(0, 130, 82,0.2)'},
    {'dark': 'rgb(44, 61, 96)', 'light': 'rgba(44, 61, 96,0.2)'},
    {'dark': 'rgb(88, 96, 44)', 'light': 'rgba(88, 96, 44,0.2)'},
    {'dark': 'rgb(163, 107, 81)', 'light': 'rgba(163, 107, 81,0.2)'},
    {'dark': 'rgb(96,47,46)', 'light': 'rgba(96,47,46,0.2)'},
]

basic_choice_list = [u'回复中有与上文内容相关或重叠的实体词', u'回复中有发散，生成新的内容或实体',
                     u'回复内容延续了上文所探讨的话题',
                     #u'回复内容可以自然的与上文衔接',
                     u'回复中有主观态度或明显的情绪表达', u'回复内容可以引发新一轮的对话', u'回复不是明显的书面化表达',
                     u'回复内容不含糊，不存在歧义', u'回复内容信息量适当', u'回复内容会让人感到开心或难过', u'以上均不选']


@login_required
def get_home(request):
    return render(request, 'home.html')


def is_alpha(word):
    try:
        return word.encode('ascii').isalpha()
    except UnicodeEncodeError:
        return False


@login_required
def upload(request):
    """
    * only 'staff' user can upload and dispatch tests
    * only support '.xls' file and require the excel file to follow the format of template.xls

    1. read the content of the uploaded excel file
        * user cannot upload two tests with same test name
    2. create a list of all questions in the file and bulk create the objects
        * only 基本测试 and 答案相似度's type are determined, the other three types of test may require changes.
    """
    # context
    context = {}
    context['types'] = QUESTION_TYPE

    if request.POST.get('upload_new_testcase') is not None:
        user = request.user  # 出题人
        new_test_name = request.POST.get('new_test_name')
        new_test_type = request.POST.get('new_test_type')
        new_creation_date = request.POST.get('new_creation_date')
        new_file = request.FILES.get('file')

        question_list = []
        try:
            new_test = QuestionBank.objects.get(user=user, name=new_test_name, type=u'基本测试')
            context['message'] = 'There exists a test with same name, try a different test name'
            return render(request, 'upload.html', context)
        except QuestionBank.DoesNotExist:
            # create a new test and save it to QuestionBank
            new_test = QuestionBank(user=user, name=new_test_name,
                                    creation_date=new_creation_date,
                                    type=new_test_type,
                                    file=new_file)
            new_test.save()

            # Read the file
            question = ''
            answers = ''
            file_path = 'tasks/' + str(user) + '_' + str(new_creation_date) + str(new_test_name)
            # get robots from db and convert it into an array
            all_robot = Robot.objects.all()
            ROBOT = [r.name for r in all_robot]

            test_file = xlrd.open_workbook(os.path.join(settings.MEDIA_ROOT, file_path))
            table = test_file.sheets()[0]  # get the first sheet of excel file
            nrows = table.nrows
            ncols = table.ncols

            # create the questions

            bot = ''

            for i in xrange(1, nrows):
                question += table.cell(i, 0).value + '\n' + table.cell(i, 1).value
                for j in xrange(2, ncols - 1):
                    answers += table.cell(i, j).value + '\n'
                bot += table.cell(i, ncols - 1).value
                if bot not in ROBOT:
                    new_robot = Robot(name=bot)
                    new_robot.save()
                    ROBOT.append(bot)
                new_question = Question(q_id=str(new_test.id)+'_'+str(i-1), question=question,
                                        answers=answers, bot=bot)
                question_list.append(new_question)
                answers = ''
                question = ''
                bot = ''

            Question.objects.bulk_create(question_list)
            string = str(new_test.id)+'_'
            qs = Question.objects.filter(q_id__startswith=string)
            new_test.questions.set(qs)

            distinct_question_num = len(dict((q.question, q.answers) for q in question_list))
            new_test.num_distinct_questions = distinct_question_num
            new_test.save()
            return render(request, 'success.html')

    return render(request, 'upload.html', context)


@login_required
def test_list(request):
    """
    1. Show a list of tests that this user can dispatch
        * A user can only dispatch the files he/she uploaded
    """

    context = {}
    all_tests = [t for t in QuestionBank.objects.all()]
    own_tests = [t for t in all_tests if t.user == request.user and t.type == u'基本测试']

    if request.POST.get('delete_task') is not None:
        for t in own_tests:
            if request.POST.get(t.name) is not None:
                t.delete()
                file_path = 'tasks/' + str(request.user) + '_' + str(t.creation_date) + str(t.name)
                file_path = os.path.join(settings.MEDIA_ROOT, file_path)
                if os.path.exists(file_path):
                    os.remove(file_path)
                return test_list(request)
    context['own_tests'] = own_tests
    return render(request, 'test_list.html', context)


@login_required
def dispatch(request):
    """
    1. get the list of users and corresponded number of questions
    2. create an annotation suite for each user and annotation object for each dispatched question

    Adjustments:
    * require debugging about the 'number of question' input when adding one more user
    * require debugging about number of questions input exceeding the total amount of number
    """
    context = {}
    project_id = request.GET.get('project_id')
    task = QuestionBank.objects.get(id=int(project_id))
    all_users = [u for u in User.objects.all() if not u.is_superuser]
    context['task'] = task
    context['all_users'] = all_users

    if request.POST.get('dispatch_button') is not None:

        distribute_user = request.POST.getlist('distribute_user')
        num_distributed_question = request.POST.getlist('num_quest')
        question_list = task.questions.all().order_by('question', 'bot')
        question_list = [q for q in question_list]

        num_distinct_questions = task.num_distinct_questions
        num_bot = len(question_list)/num_distinct_questions
        current_q_indix = task.current_query_index
        dispatch_q_list = []

        if task.dispatched_questions != '':
            dispatch_q_list = task.dispatched_questions.split(",")

        for user, num in zip(distribute_user, num_distributed_question):
            testcard_list = []
            user_object = User.objects.get(username=str(user))
            try:
                testset = TestSet.objects.get(user=user_object, questionBank=task)
                if testset.num_question + int(num) > task.num_distinct_questions:
                    context['message'] = 'The available number of questions for the user (' + user + ') is ' \
                                         + str(task.num_distinct_questions - testset.num_question)
                    break
            except TestSet.DoesNotExist:
                testset = TestSet.objects.create(user=user_object, questionBank=task, type=task.type)

            # Add the question to testset:
            for i in xrange(0, int(num)):
                current_q = question_list[current_q_indix*num_bot + randint(0, num_bot-1)]
                while current_q.q_id in dispatch_q_list:
                    if len(dispatch_q_list) == len(question_list):
                        dispatch_q_list = []
                        current_q_indix = 0
                    current_q = question_list[current_q_indix*num_bot + randint(0, num_bot-1)]
                # find an avilable question
                current_q_indix += 1
                if current_q_indix == num_distinct_questions:
                    current_q_indix = 0
                testset.questions.add(current_q)
                dispatch_q_list.append(current_q.q_id)
                # create the new test card for the current question:
                card_id = str(testset.id) + '_' + str(testset.num_question + i)
                try:
                    TestCard.objects.get(card_id=card_id)
                except TestCard.DoesNotExist:
                    new_test_card = TestCard(card_id=card_id, question=current_q,
                                            testSet=testset, bot=current_q.bot)
                    testcard_list.append(new_test_card)
            TestCard.objects.bulk_create(testcard_list)
            testset.num_question += int(num)
            testset.save()
        # update the questionBank table in database
        task.current_query_index = current_q_indix
        task.dispatched_questions = ",".join([str(i) for i in dispatch_q_list])
        task.save()

    existing_testset = [u for u in TestSet.objects.all()]
    context['existing_testset'] = existing_testset
    return render(request, 'dispatch.html', context)


@login_required
def my_tasks(request):
    """
        1. Allow the user to pick the tests dispatched to him/her.
        2. If the test is finished, the test name becomes grey
    """
    context = {}
    tasks = TestSet.objects.filter(current_index__lt=F('num_question'), user=request.user, type=u'基本测试')
    finished_tasks = TestSet.objects.filter(user=request.user, current_index__gte=F('num_question'), type=u'基本测试')
    context['tasks'] = tasks
    context['finished_tasks'] = finished_tasks
    return render(request, 'my_tasks.html', context)


def question_card_handler(request, testset_id):
    """
    1. if from test set pickup page, the question_bank_id will be 0, question_id will be -1:
        a. if the testSet is finished, redirect to feedback page and display the result.
        b. else, needs to determine the picked testset's question_bank_id redirect.
    2. if from ques card page by clicking 'next question', then get the form info and update data, then redirect to
        display the question card page.

        (The reason we need a handler is that if not redirect, when refreshing the page, the form will resubmit.
        to prevent resubmit "POST", we will have to use a POST/ REDIRECT/ GET programming pattern.

    """
    try:
        if testset_id == '-1':
            picked_testset_id = int(request.POST.get('testset_result'))
            picked_testset = TestSet.objects.get(id=picked_testset_id)
            if picked_testset.current_index == picked_testset.num_question:
                return result(request, picked_testset_id)
            return redirect('/annotate/my_task/%d' % picked_testset_id)

        else:
            picked_testset = TestSet.objects.get(id=testset_id)
            card_id = str(testset_id) + '_' + str(picked_testset.current_index)
            q_card = TestCard.objects.filter(card_id=card_id).first()
            # get the chosen choices for the previous question:

            if request.POST.get('previous') is not None:
                picked_testset.current_index -= 1
                picked_testset.save()
            elif request.POST.get('unacceptable') is not None:
                q_card.answer = '0'
                q_card.save()
                picked_testset.current_index += 1
                picked_testset.save()
            elif request.POST.get('next_question') is not None:
                answer = request.POST.getlist('annotation')
                q_card.answer = " ".join(answer).strip()
                q_card.save()
                picked_testset.current_index += 1
                picked_testset.save()

            if picked_testset.current_index == picked_testset.num_question:
                return result(request, testset_id)
            return redirect('/annotate/my_task/%s' % testset_id)
    except:
        return redirect('/annotate/my_tasks')


@login_required
def question_card(request, testset_id):
    """
    This view is just for rendering the question_card page.

    """
    picked_testset = TestSet.objects.get(id=testset_id)

    if picked_testset.current_index == picked_testset.num_question:
        return result(request, testset_id)

    card_id = str(testset_id) + '_' + str(picked_testset.current_index)
    current_card = TestCard.objects.filter(card_id=card_id).first()
    # get the content for rendering the html file

    current_question = current_card.question
    query_text = current_question.question
    answer_text = current_question.answers
    choice_list = basic_choice_list
    question_text_list = (query_text + '\n' + answer_text).encode("utf-8").split('\n')
    context = {}
    context['testset_id'] = testset_id
    context['current_index'] = picked_testset.current_index
    context['question_text'] = question_text_list
    context['choice_list'] = choice_list
    context['total'] = picked_testset.num_question
    context['type'] = picked_testset.type
    context['existed_answer'] = current_card.answer.encode("utf-8").split(' ')
    return render(request, 'annotate.html', context)


def rating(score):
    if score == 0:
        return '<i class="far fa-star"></i> <i class="far fa-star"></i>' \
               ' <i class="far fa-star"></i> <i class="far fa-star"></i> <i class="far fa-star"></i>'
    elif score <= 50:
        return '<i class="fas fa-star"></i> <i class="far fa-star"></i> <i class="far fa-star"></i> ' \
               '<i class="far fa-star"></i> <i class="far fa-star"></i>'
    elif score <= 62:
        return '<i class="fas fa-star"></i> <i class="fas fa-star"></i> <i class="far fa-star"></i> ' \
               '<i class="far fa-star"></i> <i class="far fa-star"></i>'
    elif score <= 73:
        return '<i class="fas fa-star"></i> <i class="fas fa-star"></i> <i class="fas fa-star"></i> ' \
               '<i class="far fa-star"></i> <i class="far fa-star"></i>'
    elif score <= 84:
        return '<i class="fas fa-star"></i> <i class="fas fa-star"></i> <i class="fas fa-star"></i> ' \
               '<i class="fas fa-star"></i> <i class="far fa-star"></i>'
    else:
        return '<i class="fas fa-star"></i> <i class="fas fa-star"></i> <i class="fas fa-star"></i> ' \
               '<i class="fas fa-star"></i> <i class="fas fa-star"></i>'


@login_required
def result(request, testset_id):
    """ process the choices of each questions in test set
        and save it to testSet's result field
    """
    # get robots from db and convert it into an array
    all_robot = Robot.objects.all()
    ROBOT = [r.name for r in all_robot]

    context = {}
    testset = TestSet.objects.get(id=testset_id)
    testset_questions = testset.questions.all()
    question_list = [q for q in testset_questions]
    result = [''] * len(ROBOT)
    question_count = [0] * len(ROBOT)
    zero_answer_count = [0] * len(ROBOT)

    # 图中显示的分数
    content_score_list = [0] * len(ROBOT)
    format_score_list = [0] * len(ROBOT)
    diverge_score_list = [0] * len(ROBOT)
    emotion_score_list = [0] * len(ROBOT)
    connection_score_list = [0] * len(ROBOT)

    # 其他得分用于评级，在图旁边列出各项等级
    basic_score_list = [0] * len(ROBOT)
    task_score_list = [0] * len(ROBOT)
    chat_score_list = [0] * len(ROBOT)
    multiround_score_list = [0] * len(ROBOT)
    total_score_list = [0] * len(ROBOT)

    all_result = ''
    backend_result = ''
    # if testset.type == u'基本测试':
    for q in question_list:
        q_card = TestCard.objects.get(testSet=testset, question=q)
        answer = q_card.answer
        bot_name = q.bot
        bot_index = ROBOT.index(bot_name)
        question_count[bot_index] += 1
        # 算分：
        # 内容：不含糊＊40；有发散＊60；有引导＊60
        # 形式：不书面＊50；不啰嗦＊50；
        # 发散：有发散＊50 %； 有引导＊100 %；有态度＊30 %
        # 情感：有态度＊100 % ； 发笑＊60 %；有发散＊10 %
        # 关联：可以接＊80％ ；词关联＊40 %；理解意图＊60 %

        # 列在图下的内容：
        # 基本：不书面＊25％ ＋ 不啰嗦＊20 ＋ 不含糊＊20 ＋词关联＊5％ ＋ 有态度＊10％ ＋ 有发散＊5 % ＋ 有引导＊5 %
        # 任务：理解意图＊70 %；不啰嗦＊20 *；不含糊＊30；关联词＊10
        # 闲聊：有发散＊30％； 可以接＊30％；有态度＊40％；发笑＊40％；不啰嗦＊20％；理解意图＊40％
        # 多轮：有发散＊50％；有态度＊20％；有引导＊100％；不啰嗦＊10％；理解意图＊30％

        # 总分： 基本＊40 % ＋ 任务＊20 % ＋ 闲聊＊20 % ＋ 多轮＊20 %

        content_score = 0
        format_score = 0
        diverge_score = 0
        emotion_score = 0
        connection_score = 0

        # 其他得分用于评级，在图旁边列出各项等级
        basic_score = 0
        task_score = 0
        chat_score = 0
        multiround_score = 0

        if '10' in answer:
            answer = '10'
            basic_score = 0
        if '1' in answer:
            connection_score = min(connection_score + 40, 100)
            basic_score = min(basic_score + 5, 100)
            task_score = min(task_score + 10, 100)
        if '2' in answer:
            content_score = min(content_score + 60, 100)
            diverge_score = min(diverge_score + 50, 100)
            basic_score = min(basic_score + 5, 100)
            chat_score = min(chat_score + 30, 100)
            multiround_score = min(multiround_score + 50, 100)
        if '3' in answer:
            connection_score = min(connection_score + 60, 100)
            task_score = min(task_score + 70, 100)
            chat_score = min(chat_score + 40, 100)
            multiround_score = min(multiround_score + 30, 100)

   #     if '4' in answer:
   #         connection_score = min(connection_score + 80, 100)
   #         chat_score = min(chat_score + 30, 100)

        if '4' in answer:
            diverge_score = min(diverge_score + 30, 100)
            emotion_score = 100
            basic_score = min(basic_score + 10, 100)
            chat_score = min(chat_score + 40, 100)
            multiround_score = min(multiround_score + 20, 100)
        if '5' in answer:
            content_score = min(content_score + 60, 100)
            diverge_score = 100
            basic_score = min(basic_score + 5, 100)
            multiround_score = 100
        if '6' in answer:
            format_score = min(format_score + 50, 100)
            basic_score = min(basic_score + 25, 100)
        if '7' in answer:
            content_score = min(content_score + 40, 100)
            basic_score = min(basic_score + 20, 100)
            task_score = min(task_score + 30, 100)
        if '8' in answer:
            format_score = min(format_score + 50, 100)
            basic_score = min(basic_score + 20, 100)
            task_score = min(task_score + 20, 100)
            chat_score = min(chat_score + 20, 100)
            multiround_score = min(chat_score + 10, 100)
        if '9' in answer:
            emotion_score = min(emotion_score + 60, 100)
            chat_score = min(chat_score + 40, 100)

        # 图中显示的分数
        content_score_list[bot_index] += content_score
        format_score_list[bot_index] += format_score
        diverge_score_list[bot_index] += diverge_score
        emotion_score_list[bot_index] += emotion_score
        connection_score_list[bot_index] += connection_score

        # 其他得分用于评级，在图旁边列出各项等级
        basic_score_list[bot_index] += basic_score
        task_score_list[bot_index] += task_score
        chat_score_list[bot_index] += chat_score
        multiround_score_list[bot_index] += multiround_score

        if answer == '0':
            zero_answer_count[bot_index] += 1

    for i in xrange(0, len(ROBOT)):

        if question_count[i] != 0 and question_count[i] - zero_answer_count[i] != 0:
            content_score_list[i] = content_score_list[i] / (question_count[i] - zero_answer_count[i])
            format_score_list[i] = format_score_list[i] / (question_count[i] - zero_answer_count[i])
            diverge_score_list[i] = diverge_score_list[i] / (question_count[i] - zero_answer_count[i])
            emotion_score_list[i] = emotion_score_list[i] / (question_count[i] - zero_answer_count[i])
            connection_score_list[i] = connection_score_list[i] / (question_count[i] - zero_answer_count[i])

            basic_score_list[i] = basic_score_list[i] / (question_count[i] - zero_answer_count[i])
            task_score_list[i] = task_score_list[i] / (question_count[i] - zero_answer_count[i])
            chat_score_list[i] = chat_score_list[i] / (question_count[i] - zero_answer_count[i])
            multiround_score_list[i] = multiround_score_list[i] / (question_count[i] - zero_answer_count[i])

            total_score_list[i] = basic_score_list[i] * 0.4 + task_score_list[i] * 0.2 + chat_score_list[i]*0.2 + \
                             multiround_score_list[i] * 0.2
            result[i] = str(ROBOT[i]) +'\n基本能力: '+rating(basic_score_list[i]) +\
                        '\n任务解决: '+rating(task_score_list[i]) +\
                        '\n闲聊能力: '+rating(chat_score_list[i]) +\
                        '\n多轮对话: '+rating(multiround_score_list[i]) +\
                        '\n总体评级: '+rating(total_score_list[i]) + \
                        ('\n严重错误答案: '+str(zero_answer_count[i])).ljust(34)+'测试题目总数: ' + str(question_count[i])
            all_result += result[i] + '\n\n'
            backend_result += str(ROBOT[i])+'\n内容分:'+str(content_score_list[i]) + \
                             '\n形式分:'+str(format_score_list[i]) + \
                             '\n发散分:' + str(diverge_score_list[i]) + \
                             '\n情感分:' + str(emotion_score_list[i]) + \
                             '\n关联分:' + str(connection_score_list[i]) +\
                             '\n基本能力:'+ str(basic_score_list[i]) + \
                             '\n任务解决:'+str(task_score_list[i]) + \
                             '\n闲聊能力:'+str(chat_score_list[i]) + \
                             '\n多轮对话:'+str(multiround_score_list[i]) + \
                             '\n总体评级:'+str(total_score_list[i]) + \
                             '\n严重错误答案:'+str(zero_answer_count[i])+'\n测试题目总数:' + str(question_count[i]) + '\n\n'
        elif question_count[i] != 0 and question_count[i] - zero_answer_count[i] == 0:

            result[i] = str(ROBOT[i])+'\n内容分: 0\n形式分: 0\n发散分: 0\n情感分: 0\n关联分: 0\n严重错误答案: ' + \
                        str(zero_answer_count[i]) + '\n测试题目总数: ' + str(question_count[i]) + \
                        '\n基本能力: ' + rating(0) + '\n任务解决: ' + rating(0) + '\n闲聊能力: ' + rating(0) + \
                        '\n多轮对话: '+rating(0) + '\n总体评级: ' + rating(0)
            all_result += result[i] + '\n\n'
            backend_result += str(ROBOT[i])+'\n内容分:0\n形式分:0\n发散分:0\n情感分:0\n关联分:0\n基本能力:0\n任务解决:0' +\
                             '\n闲聊能力:0\n多轮对话:0\n总体评级:0'+ '\n严重错误答案:'+str(zero_answer_count[i])+\
                              '\n测试题目总数:' + str(question_count[i]) + '\n\n'

    testset.result = backend_result
    testset.save()
    context['test'] = testset.questionBank.name
    context['questionBank_id'] = testset.questionBank.id
    context['all_result'] = all_result
    context['type'] = testset.type
    return render(request, 'result.html', context)


@login_required
def history(request):
    # return render(request, 'history.html')
    return history_basic(request)

@login_required
def history_basic(request):
    # get robots from db and convert it into an array
    all_robot = Robot.objects.all()
    ROBOT = [r.name for r in all_robot]
    robot_evaluation_list = [{"robot": r, "eval_str": ''} for r in ROBOT]
    context = {}
    dataSet = []
    total_str = '['
    unaccept_str = '['
    robots_str = ''
    if request.POST.get('basic_testset_result') is not None:
        picked_questionbank_id = int(request.POST.get('basic_testset_result'))
        picked_questionbank = QuestionBank.objects.get(id=picked_questionbank_id)
        task_list = TestSet.objects.filter(questionBank=picked_questionbank, current_index__gte=F('num_question'))
        if request.POST.get('action') == 'export':
            return redirect('export_basic_csv', picked_questionbank_id)
        if not task_list.exists():
            context['message'] = "This test set has not received any response yet."
        elif request.POST.get('action') == 'show_result':
            robot_score = [[0] * 12 for _ in range(len(ROBOT))]

            for t in task_list:
                total_result = t.result
                robot_total_result = total_result.split('\n\n')
                robot_total_result = [r for r in robot_total_result if r.strip() != '']
                for r in robot_total_result:
                    r_list = r.split('\n')
                    bot = r_list[0]
                    bot_index = ROBOT.index(bot)
                    score_l = robot_score[bot_index]
                    score_l[0] += int(r_list[1].split(u':')[1]) * (
                                int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 内容分
                    score_l[1] += int(r_list[2].split(u':')[1]) * (
                                int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 形式分
                    score_l[2] += int(r_list[3].split(u':')[1]) * (
                            int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 发散分
                    score_l[3] += int(r_list[4].split(u':')[1]) * (
                                int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 情感分
                    score_l[4] += int(r_list[5].split(u':')[1]) * (
                                int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 关联分
                    score_l[5] += int(r_list[6].split(u':')[1]) * (
                            int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 基本能力
                    score_l[6] += int(r_list[7].split(u':')[1]) * (
                            int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 任务解决
                    score_l[7] += int(r_list[8].split(u':')[1]) * (
                            int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 闲聊能力
                    score_l[8] += int(r_list[9].split(u':')[1]) * (
                            int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 多轮对话
                    #score_l[9] += int(r_list[10].split(u':')[1]) * (
                    #        int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 总体评级
                    score_l[10] += int(r_list[11].split(u':')[1])  # 严重错误答案
                    score_l[11] += int(r_list[12].split(u':')[1])  # 测试题目总数

            # 算总分：
            for i in xrange(0, len(ROBOT)):
                if robot_score[i][11] != 0:  # 测试题目总数!=0
                    backColor = backgroundColor[i % 9]

                    data_str = '{label:\"'+ROBOT[i]+'\", fill: true, backgroundColor: "'+backColor['light'] + \
                               '", borderColor: "' + backColor['dark'] + '", pointHoverBorderColor: "' + \
                               backColor['light'] + '", pointBorderColor: "#fff", ' + \
                                                             'pointHoverBackgroundColor:"#fff", '
                    net_question = robot_score[i][11] - robot_score[i][10]
                    if net_question == 0:
                        data_str += 'data:[0,0,0,0,0]}'
                    else:
                        total_score = robot_score[i][5] / net_question * 0.4 + \
                                      robot_score[i][6] / net_question * 0.2 + \
                                      robot_score[i][7] / net_question * 0.2 + \
                                      robot_score[i][8] / net_question * 0.2
                        robot_evaluation_list[i]["eval_str"] = '基本能力: ' + rating(robot_score[i][5] / net_question) + \
                                                               '\n任务解决: ' + rating(robot_score[i][6] / net_question) + \
                                                               '\n闲聊能力: ' + rating(robot_score[i][7] / net_question) + \
                                                               '\n多轮对话: '+rating(robot_score[i][8] / net_question) + \
                                                               '\n总体评级: ' + rating(total_score)
                        data_str += 'data:[%d, %d, %d ,%d , %d]}' % (robot_score[i][0] / net_question,
                                                                     robot_score[i][1] / net_question,
                                                                     robot_score[i][2] / net_question,
                                                                     robot_score[i][3] / net_question,
                                                                     robot_score[i][4] / net_question)

                    total_str = total_str + str(robot_score[i][11]) + ', '
                    unaccept_str = unaccept_str + str(robot_score[i][10]) + ', '
                    robots_str = robots_str + '"' + ROBOT[i] + '", '
                    dataSet.append(data_str.encode('utf-8'))
            unaccept_str += ']'
            total_str += ']'
    test_sets = QuestionBank.objects.filter(type=u'基本测试', user=request.user)
    context['test_sets'] = test_sets
    context['dataSet'] = dataSet
    context['unaccept'] = unaccept_str
    context['total'] = total_str
    context['robots'] = robots_str
    context['test'] = '<span class="fa fa-star checked"></span>'
    context['robot_evaluations'] = robot_evaluation_list
    return render(request, 'history_basic.html', context)

@login_required
def export_basic_csv(request, testset_id):
    # get robots from db and convert it into an array
    all_robot = Robot.objects.all()
    ROBOT = [r.name for r in all_robot]

    picked_questionbank = QuestionBank.objects.get(id=testset_id)
    question_qs = picked_questionbank.questions.all()
    task_list = TestSet.objects.filter(questionBank=picked_questionbank, current_index__gte=F('num_question'))

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="%s_result.csv"' % picked_questionbank.name
    writer = csv.writer(response)
    header = [u'问题', u'回答', u'机器人', u'参与总人数', u'特殊标注', u'回复中有与上文内容相关或重叠的实体词', u'回复中有发散，生成新的内容或实体',
                     u'回复内容延续了上文所探讨的话题',
                     #u'回复内容可以自然的与上文衔接',
                     u'回复中有主观态度或明显的情绪表达', u'回复内容可以引发新一轮的对话', u'回复不是明显的书面化表达',
                     u'回复内容不含糊，不存在歧义', u'回复内容信息量适当', u'回复内容会让人感到开心或难过', u'以上均不选']

    writer.writerow(header)
    for q in question_qs:
        row = [q.question.replace('Query:\n', '').strip(), q.answers.replace('Answer:\n', '').strip(), q.bot]
        total_count = 0
        count = [0] * 12
        for t in task_list:
            try:
                card = TestCard.objects.get(question=q, testSet=t)
                total_count += 1
                choices = card.answer
                choices = choices.split(' ')
                for c in choices:
                    count[int(c)] += 1
            except TestCard.DoesNotExist:
                total_count += 0
        row.append(total_count)
        for i in xrange(0, 12):
            row.append(count[i])
        writer.writerow(row)
    general_score_header = [u'机器人', u'内容分', u'形式分', u'发散分', u'情感分', u'关联分',
                            u'基本能力', u'任务解决', u'闲聊能力', u'多轮对话', u'总体评级', u'严重错误答案',u'测试题目总数']

    writer.writerow(general_score_header)

    robot_score = [[0]*12 for _ in range(len(ROBOT))]
    for t in task_list:
        total_result = t.result
        robot_total_result = total_result.split('\n\n')
        robot_total_result = [r for r in robot_total_result if r.strip() != '']

        for r in robot_total_result:

            r_list = r.split('\n')
            bot = r_list[0]
            bot_index = ROBOT.index(bot)
            score_l = robot_score[bot_index]
            score_l[0] += int(r_list[1].split(u':')[1]) * (
                    int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 内容分
            score_l[1] += int(r_list[2].split(u':')[1]) * (
                    int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 形式分
            score_l[2] += int(r_list[3].split(u':')[1]) * (
                    int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 发散分
            score_l[3] += int(r_list[4].split(u':')[1]) * (
                    int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 情感分
            score_l[4] += int(r_list[5].split(u':')[1]) * (
                    int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 关联分
            score_l[5] += int(r_list[6].split(u':')[1]) * (
                    int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 基本能力
            score_l[6] += int(r_list[7].split(u':')[1]) * (
                    int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 任务解决
            score_l[7] += int(r_list[8].split(u':')[1]) * (
                    int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 闲聊能力
            score_l[8] += int(r_list[9].split(u':')[1]) * (
                    int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 多轮对话
            # score_l[9] += int(r_list[10].split(u':')[1]) * (
            #        int(r_list[12].split(u':')[1]) - int(r_list[11].split(u':')[1]))  # 总体评级
            score_l[10] += int(r_list[11].split(u':')[1])  # 严重错误答案
            score_l[11] += int(r_list[12].split(u':')[1])  # 测试题目总数
    # 算总分：

    for i in xrange(0, len(ROBOT)):
        general_score_row = ''
        if robot_score[i][5] != 0:  # 测试题目总数!=0
            net_question = robot_score[i][11] - robot_score[i][10]
            if net_question == 0:
                general_score_row = [ROBOT[i], 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, robot_score[i][10], robot_score[i][11]]
            else:
                total_score = robot_score[i][5] / net_question * 0.4 + \
                              robot_score[i][6] / net_question * 0.2 + \
                              robot_score[i][7] / net_question * 0.2 + \
                              robot_score[i][8] / net_question * 0.2
                general_score_row = [ROBOT[i], robot_score[i][0] / net_question, robot_score[i][1] / net_question,
                                     robot_score[i][2] / net_question, robot_score[i][3] / net_question,
                                     robot_score[i][4] / net_question, robot_score[i][5] / net_question,
                                     robot_score[i][6] / net_question, robot_score[i][7] / net_question,
                                     robot_score[i][8] / net_question, total_score,
                                     robot_score[i][10], robot_score[i][11]]
            writer.writerow(general_score_row)

    return response
