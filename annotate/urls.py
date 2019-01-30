from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^upload$', views.upload, name='upload'),
    url(r'^home$', views.get_home, name='home'),
    url(r'^test_list', views.test_list, name='test_list'),
    url(r'^dispatch$', views.dispatch, name='dispatch'),
    url(r'^my_tasks$', views.my_tasks, name='my_tasks'),
    url(r'^question_card/(?P<testset_id>[0-9A-Fa-f-]+)',
        views.question_card_handler, name='question_card_handler'),
    url(r'^my_task/(?P<testset_id>[0-9A-Fa-f-]+)',
        views.question_card, name='question_card'),
    url(r'^history$', views.history, name='history'),
    # url(r'^history/similarity$', views.history_similarity, name='history_similarity'),
    # url(r'^history/answer_acceptance', views.history_answer_acceptance, name='history_answer_acceptance'),
    url(r'^history/basic$', views.history_basic, name='history_basic'),
    # url(r'^export/similarity/(?P<testset_id>[0-9A-Fa-f-]+)', views.export_similarity_json, name='export_similarity_json'),
    url(r'^export/basic/(?P<testset_id>[0-9A-Fa-f-]+)', views.export_basic_csv, name='export_basic_csv'),

]