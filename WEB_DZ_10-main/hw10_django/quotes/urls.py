from django.urls import path

from .views import *

app_name = 'quotes'

urlpatterns = [
    path('', main, name='root'),
    path('<int:page>', main, name='root_paginate'),
    path('add_quote/', add_quote, name='add_quote'),
    path('author/<int:author_id>/', author_detail, name='author_detail'),
    path('author/<int:author_id>/edit/', edit_author, name='edit_author'),
    path('delete_quote/<int:quote_id>/', delete_quote, name='delete_quote'),
    path('tag/<str:tag_name>/', TagQuotesView.as_view(), name='tag_quotes'),
]
