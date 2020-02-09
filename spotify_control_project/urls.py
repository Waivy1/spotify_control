from django.urls import path
from core import views

urlpatterns = [
    path('', views.IndexPage.as_view(), name='index_page'),
    path('player_view', views.PlayerView.as_view(), name='player_view'),
    path('mood/<str:track_id>', views.Mood.as_view(), name='mood'),
    path('playlist', views.Playlist.as_view(), name='playlist'),
    path('list_playlist/<str:playlist_id>', views.ListPlaylist.as_view(), name='list_playlist'),
    path('add_to/<str:playlist_id>/<str:track_id>', views.AddTo.as_view(), name='add_to'),
]


