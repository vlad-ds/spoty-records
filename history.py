#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 27 18:41:32 2020

@author: vlad
"""

import ast
import requests
from datetime import datetime
from typing import List
import spotipy
import spotipy.util as util
from os import listdir
import pandas as pd

def get_token(user: str, 
              client_id: str,
              client_secret: str,
              redirect_uri: str,
              scope: str) -> str:
  
    token = util.prompt_for_user_token(user,scope,
                                               client_id=client_id,
                                               client_secret=client_secret,
                                               redirect_uri=redirect_uri)
    return token
        
def get_streamings(path: str = 'MyData', 
                ) -> List[dict]:
    
    '''Returns a list of streamings form spotify MyData dump.
    Will not acquire track features.'''
    
    files = ['MyData/' + x for x in listdir(path)
             if x.split('.')[0][:-1] == 'StreamingHistory']
    
    all_streamings = []
    
    for file in files: 
        with open(file, 'r', encoding='UTF-8') as f:
            new_streamings = ast.literal_eval(f.read())
            all_streamings += [streaming for streaming in new_streamings]
            
    #adding datetime field
    for streaming in all_streamings:
        streaming['datetime'] = datetime.strptime(streaming['endTime'], '%Y-%m-%d %H:%M')    
    return all_streamings

def get_api_id(track_info: str, token: str,
                artist: str = None) -> str:
    
    '''Performs a query on Spotify API to get a track ID.
    See https://curl.trillworks.com/'''

    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer ' + token,
    }
    track_name = track_info.split("___")[0]
    params = [
    ('q', track_name),
    ('type', 'track'),
    ]
    artist = track_info.split("___")[-1]
    if artist:
        params.append(('artist', artist))
        
    try:
        response = requests.get('https://api.spotify.com/v1/search', 
                    headers = headers, params = params, timeout = 5)
        json = response.json()
        results = json['tracks']['items']
        first_result = json['tracks']['items'][0]
        # Check if searched artist is in response as the first one isn't
        # necessarily the right one
        if artist:
            for result in results:
                if artist.strip() == result['artists'][0]['name'].strip():
                    track_id = result['id']
                    return track_id
        # If specific artist is not found from results, use the first one
        track_id = first_result['id']
        return track_id
    except:
        return None
    
def get_saved_ids(tracks, path: str = 'output/track_ids.csv') -> dict:
    track_ids = {track: None for track in tracks}
    folder, filename = path.split('/')
    if filename in listdir(folder):
        try:
            idd_dataframe = pd.read_csv('output/track_ids.csv', 
                                     names = ['name', 'idd'])
            idd_dataframe = idd_dataframe[1:]                    #removing first row
            added_tracks = 0
            for index, row in idd_dataframe.iterrows():
                if not row[1] == 'nan':                          #if the id is not nan
                    track_ids[row[0]] = row[1]                    #add the id to the dict
                    added_tracks += 1
            print(f'Saved IDs successfully recovered for {added_tracks} tracks.')
        except:
            print('Error. Failed to recover saved IDs!')
            pass
    return track_ids
    
def get_api_features(track_id: str, token: str) -> dict:
    sp = spotipy.Spotify(auth=token)
    try:
        features = sp.audio_features([track_id])
        return features[0]
    except:
        return None

def get_album(track_id: str, token: str) -> dict:
    sp = spotipy.Spotify(auth=token)
    try:
        album = sp.track(track_id)
        album_id = album['album']['id']
        album_name = album['album']['name']
        return album_name, album_id
    except:
        return None, None

def get_saved_features(tracks, path = 'output/features.csv'):
    folder, file = path.split('/')
    track_features = {track: None for track in tracks}
    if file in listdir(folder):
        features_df = pd.read_csv(path, index_col = 0)
        n_recovered_tracks = 0
        for track in features_df.index:
            features = features_df.loc[track, :]
            if not features.isna().sum():          #if all the features are there
                track_features[track] = dict(features)
                n_recovered_tracks += 1
        print(f"Added features for {n_recovered_tracks} tracks.")
        return track_features
    else:
        print("Did not find features file.")
        return track_features
