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
        
def get_listenings(path: str = 'MyData', 
                ) -> List[dict]:
    
    '''Returns a list of listenings form spotify MyData dump.
    Will not acquire song features.'''
    
    files = ['MyData/' + x for x in listdir(path)
             if x.split('.')[0][:-1] == 'StreamingHistory']
    
    all_listenings = []
    
    for file in files: 
        with open(file, 'r', encoding='UTF-8') as f:
            new_listenings = ast.literal_eval(f.read())
            all_listenings += [listening for listening in new_listenings]
            
    #adding datetime field
    for listening in all_listenings:
        listening['datetime'] = datetime.strptime(listening['endTime'], '%Y-%m-%d %H:%M')    
    return all_listenings

def get_song_id(song_name: str, token: str, 
                artist: str = None) -> str:
    
    '''Performs a query on Spotify API to get a song ID.
    See https://curl.trillworks.com/'''
   
    headers = {
    'Accept': 'application/json',
    'Content-Type': 'application/json',
    'Authorization': f'Bearer ' + token,
    }
    
    params = [
    ('q', song_name),
    ('type', 'track'),
    ]
    
    if artist: 
        params.append(('artist', artist))
        
    try:
        response = requests.get('https://api.spotify.com/v1/search', 
                    headers = headers, params = params, timeout = 5)
        json = response.json()
        first_result = json['tracks']['items'][0]
        song_id = first_result['id']
        return song_id
    except:
        return None
    
def get_saved_ids(songs, path: str = 'output/song_ids.csv') -> dict:
    song_ids = {song: None for song in songs}
    folder, filename = path.split('/')
    if filename in listdir(folder):
        try:
            idd_dataframe = pd.read_csv('output/song_ids.csv', 
                                     names = ['name', 'idd'])
            idd_dataframe = idd_dataframe[1:]                    #removing first row
            added_songs = 0
            for index, row in idd_dataframe.iterrows():
                if not row[1] == 'nan':                          #if the id is not nan
                    song_ids[row[0]] = row[1]                    #add the id to the dict
                    added_songs += 1
            print(f'Saved IDs successfully recovered for {added_songs} songs.')
        except:
            print('Error. Failed to recover saved IDs!')
            pass
    return song_ids
    
def get_api_features(song_id: str, token: str) -> dict:
    sp = spotipy.Spotify(auth=token)
    try:
        features = sp.audio_features([song_id])
        return features[0]
    except:
        return None
    
def get_saved_features(songs, path = 'output/features.csv'):
    folder, file = path.split('/')
    song_features = {song: None for song in songs}
    if file in listdir(folder):
        features_df = pd.read_csv(path, index_col = 0)
        n_recovered_songs = 0
        for song in features_df.index:
            features = features_df.loc[song, :]
            if not features.isna().sum():          #if all the features are there
                song_features[song] = dict(features)
                n_recovered_songs += 1
        print(f"Added features for {n_recovered_songs} songs.")
        return song_features
    else:
        print("Did not find features file.")
        return song_features