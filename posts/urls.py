
from django.urls import path
from . import views

urlpatterns = [
    path("", views.PostList.as_view(), name='index'),
    path("add_post/",views.PostCreate.as_view(), name='add_post'),
    path("delete_post/<int:id>/",views.PostDelete.as_view(), name='delete_post'),
    path("edit_post/<int:id>/",views.PostUpdate.as_view(), name='edit_post'),
    path("post/<int:id>/",views.PostDetail.as_view(), name='view_post'),

    path("like_post/<int:post_id>/", views.like_post, name='like_post'),
    path("comment_on_post/<int:id>/", views.comment_on_post, name='comment_on_post'),
    path("delete_comment/<int:id>/", views.delete_comment, name='delete_comment'),
    path("edit_comment/<int:id>/", views.edit_comment, name='edit_comment'),

    path("register/", views.UserRegisterView.as_view(), name='register'),
    path("login/", views.UserLoginView.as_view(), name='login'),
    path("logout/", views.logout_view, name='logout'),
    path("profile/", views.ProfileUpdatView.as_view(), name='profile'),
    path("ask_for_admin",views.ask_for_admin, name='ask_for_admin'),
    path("liked_posts/", views.PostLikedList.as_view(), name='liked_posts'),
    path("add_post_to_favourites/<int:id>/", views.add_post_to_favourites, name='add_post_to_favourites'),
    path("favourite_posts/", views.PostFavouritesList.as_view(), name='favourite_posts'),
    path("show_people/", views.show_people, name='show_people'),
    path("show_profile/<int:id>/", views.ProfileView.as_view(), name='show_profile'),
    path("people_posts/<int:id>/", views.PostPeopleList.as_view(), name='people_posts'),
    path("friend_request/<int:id>/", views.send_friend_request, name='friend_request'),
    path("friend_requests/", views.FriendsRequestsList.as_view(), name='friend_requests'),
    path("accept_friend_request/<int:id>/", views.accept_friend_request, name='accept_friend_request'),
    path("decline_friend_request/<int:id>/", views.decline_friend_request, name='decline_friend_request'),
    path("friends/", views.FriendsListView.as_view(), name='friends_list'),
    path("search/", views.search, name='search'),



]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,document_root = settings.MEDIA_ROOT)