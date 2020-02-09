import json

import requests
from core import models
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views import View


class IndexPage(View):
    def get(self, request):
        res = requests.get(f'http://spotify.api/api/v1/current')
        if not res.ok:
            return render(request, 'index_page.html')

        resp = res.json()
        artist_name = resp['item']['album']['artists'][0]['name']
        song_name = resp['item']['name']
        album_name = resp['item']['album']['name']
        release_date = resp['item']['album']['release_date']
        progress = resp['progress_ms']
        duration = resp['item']['duration_ms']
        percent_progress = round((progress * 100) / duration)

        return render(request, 'index_page.html', {
            'resp': resp,
            'artist_name': artist_name,
            'song_name': song_name,
            'release_date': release_date,
            'album_name': album_name,
            'percent_progress': percent_progress,

        })


class PlayerView(View):
    def get(self, request):
        res = requests.get(f'http://spotify.api/api/v1/current')
        if not res.ok:
            return redirect('http://spotify.api/login')

        resp = res.json()
        artist_name = resp['item']['album']['artists'][0]['name']
        song_name = resp['item']['name']
        album_name = resp['item']['album']['name']
        release_date = resp['item']['album']['release_date']
        progress = resp['progress_ms']
        duration = resp['item']['duration_ms']
        percent_progress = round((progress * 100) / duration)
        track_id = resp['item']['id']
        playlist_id = resp['context']['uri']
        playlist_id = playlist_id.split(":")[-1]

        return JsonResponse({
            'artist_name': artist_name,
            'song_name': song_name,
            'release_date': release_date,
            'album_name': album_name,
            'percent_progress': percent_progress,
            'track_id': track_id,
            'playlist_id': playlist_id,
        })


class Mood(View):
    def get(self, request, track_id):
        cached_song = models.Song.objects.filter(track_id=track_id)  # query_set

        if not cached_song:
            resp, status_code = self._get_from_spotify(track_id)
            mood = json.dumps(resp)

            new_song = models.Song(track_id=track_id, mood=mood)
            new_song.save()

        else:
            mood = cached_song.first().mood
            resp = json.loads(mood)
            status_code = 200

        allowed_response = self._to_dict(['acousticness', 'danceability', 'energy', 'tempo',
                                          'loudness', 'speechiness', 'valence'], resp)

        return JsonResponse(allowed_response, status=status_code)

    @staticmethod
    def _get_from_spotify(track_id):
        res = requests.get(f'http://spotify.api/api/v1/mood/{track_id}')
        resp = res.json()
        status_code = res.status_code

        return resp, status_code

    @staticmethod
    def _to_dict(keys, from_dict):
        res = {}
        for key in keys:
            res.update({key: from_dict[key]})

        return res


class Playlist(View):
    def post(self, request):
        input_data = json.loads(request.body)

        res = requests.post(f'http://spotify.api/api/v1/playlist/', json=input_data)

        return JsonResponse(res.json())


class ListPlaylist(View):
    def get(self, request, playlist_id):
        playlis = requests.get(f'http://spotify.api/api/v1/playlist/{playlist_id}')

        playlist = playlis.json()
        list_songs = []

        for track in playlist['tracks']['items']:
            d = {
                'name': track['track']['name'],
                'album': track['track']['album']['name'],
                'artist': track['track']['album']['artists'][0]['name'],
                'track_id': track['track']['id'],
            }

            list_songs.append(d)
        return JsonResponse({'list_songs': list_songs, 'name': playlist['name']})


class AddTo(View):
    def get(self, request, playlist_id, track_id):
        input_data = {'uris': [track_id]}
        res = requests.post(f'http://spotify.api/api/v1/playlist/{playlist_id}', json=input_data)

        return JsonResponse(res.json())
