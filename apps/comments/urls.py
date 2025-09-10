from django.urls import path
from .views import CommentView, CommentDeleteView

urlpatterns = [
    path("form/", CommentView.as_view(), name="comment_form"),
    path("<int:pk>/delete/", CommentDeleteView.as_view(), name="comment_delete"),
]
