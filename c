[1mdiff --git a/annotate/views.py b/annotate/views.py[m
[1mindex be2c046..6bf4ad9 100644[m
[1m--- a/annotate/views.py[m
[1m+++ b/annotate/views.py[m
[36m@@ -699,7 +699,7 @@[m [mdef result(request, testset_id):[m
 [m
             if question_count[i] != 0:[m
                 percentage = (question_count[i] - zero_answer_count[i]) * 100 / question_count[i][m
[31m-                print percentage[m
[32m+[m[32m                print(percentage)[m
                 result[i] = str(ROBOT[i]) + '\n答案接受度: ' + str(percentage) + '%\n测试题目总数: ' + str(question_count[i]) + \[m
                     '\n可接受题目总数: ' + str(question_count[i] - zero_answer_count[i])[m
                 all_result += result[i] + '\n\n'[m
[1mdiff --git a/annotation/settings.py b/annotation/settings.py[m
[1mindex 82af5cd..232d05d 100644[m
[1m--- a/annotation/settings.py[m
[1m+++ b/annotation/settings.py[m
[36m@@ -41,7 +41,7 @@[m [mINSTALLED_APPS = [[m
     'annotate',[m
 ][m
 [m
[31m-MIDDLEWARE = [[m
[32m+[m[32mMIDDLEWARE_CLASSES = [[m
     'django.middleware.security.SecurityMiddleware',[m
     'django.contrib.sessions.middleware.SessionMiddleware',[m
     'django.middleware.common.CommonMiddleware',[m
