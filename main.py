#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 29 10:29:55 2020

@author: vlad
"""

import history
import pandas as pd
from time import sleep
from config import *

def main():

    #recover listenings history
    token = history.get_token(user, client_id, 
                              client_secret, redirect_uri, scope)
    listenings = history.get_listenings()
    print(f'Recovered {len(listenings)} listenings.')
    
    #getting a list of unique songs in our history
    songs = set([listening['trackName'] for listening in listenings])
    print(f'Discovered {len(songs)} unique songs.')
    
    #getting saved ids for songs
    song_ids = history.get_saved_ids(songs)
    
    #checking songs that still miss idd
    songs_missing_idd = len([song for song in songs if song_ids.get(song) is None])
    print(f'There are {songs_missing_idd} songs missing ID.')
    
    if songs_missing_idd > 0:
        #using spotify API to recover song ids
        #note: this methods works only for songs. 
        #podcasts and other items will be ignored.
        print('Connecting to Spotify to recover songs IDs.')
        sleep(3)
        for song, idd in song_ids.items(): 
            if idd is None: 
                try:
                    found_idd = history.get_song_id(song, token)
                    song_ids[song] = found_idd
                    print(song, found_idd)
                except:
                    pass
        
        #how many songs did we identify? 
        identified_songs = [song for song in song_ids
                         if song_ids[song] is not None]
        print(f'Successfully recovered the ID of {len(identified_songs)} songs.')
        
        #how many items did we fail to identify? 
        n_songs_without_id = len(song_ids) - len(identified_songs)
        print(f"Failed to identify {n_songs_without_id} items. "
              "However, some of these may not be songs (e.g. podcasts).")
        
        #using pandas to save songs ids (so we don't have to API them in the future)
        ids_path = 'output/song_ids.csv'
        ids_dataframe = pd.DataFrame.from_dict(song_ids, 
                                               orient = 'index')
        ids_dataframe.to_csv(ids_path)
        print(f'Song ids saved to {ids_path}.')
    
    #recovering saved features
    song_features = history.get_saved_features(songs)
    songs_without_features = [song for song in songs if song_features.get(song) is None]
    print(f"There are still {len(songs_without_features)} songs without features.")
    path = 'output/features.csv'
    
    #connecting to spotify API to retrieve missing features
    if len (songs_without_features):
        print('Connecting to Spotify to extract features...')
        acquired = 0
        for song, idd in song_ids.items(): 
            if idd is not None and song in songs_without_features:
                try:
                    features = history.get_api_features(idd, token)
                    song_features[song] = features
                    if features:
                        acquired += 1
                        print(f'Acquired features: {song}. Total: {acquired}')
                except:
                    features = None
        songs_without_features = [song for song in songs if song_features.get(song) is None]
        print(f'Successfully recovered features of {acquired} songs.')
        if len(songs_without_features):
            print(f'Failed to identify {len(songs_without_features)} items. Some of these may not be songs.')
        
        #saving features 
        features_dataframe = pd.DataFrame(song_features).T
        features_dataframe.to_csv(path)
        print(f'Saved features to {path}.')
    
    #joining features and listenings
    print('Adding features to listenings...')
    listenings_with_features = []
    for listening in listenings:
        song = listening['trackName']
        features = song_features[song]
        if features:
            listenings_with_features.append({'name': song, **listening, **features})
    print(f'Added features to {len(listenings_with_features)} listenings.')
    print('Saving listenings...')
    df_final = pd.DataFrame(listenings_with_features)
    df_final.to_csv('output/final.csv')
    perc_featured = round(len(listenings_with_features) / len(listenings) *100, 2)
    print(f"Done! Percentage of listenings with features: {perc_featured}%.") 
    print("Run the script again to try getting more information from Spotify.")
    
if __name__ == '__main__':
    main()