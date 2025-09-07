from django.urls import path
from .views import HomeView, TagView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('tag/<slug:slug>/', TagView.as_view(), name='tag'),
    path('tag/<slug:slug>/page/<int:page>/', TagView.as_view(), name='tag_page'),
]
