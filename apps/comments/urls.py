from django.urls import path
from .views import CommentUpdateView, CommentDeleteView

urlpatterns = [
    path("<int:pk>/edit/", CommentUpdateView.as_view(), name="comment_edit"),
    path("<int:pk>/delete/", CommentDeleteView.as_view(), name="comment_delete"),
]
