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

    #recover streamings history
    token = history.get_token(username, client_id, 
                              client_secret, redirect_uri, scope)
    
    streamings = history.get_streamings()
    print(f'Recovered {len(streamings)} streamings.')
    
    #getting a list of unique tracks in our history
    # Add artist names too as multiple artist can have same song name
    tracks = set([f"{streaming['trackName']}___{streaming['artistName']}" for streaming in streamings])
    print(f'Discovered {len(tracks)} unique tracks.')
    
    #getting saved ids for tracks
    track_ids = history.get_saved_ids(tracks)
    
    #checking tracks that still miss idd
    tracks_missing_idd = len([track for track in tracks if track_ids.get(track) is None])
    print(f'There are {tracks_missing_idd} tracks missing ID.')
    
    if tracks_missing_idd > 0:
        #using spotify API to recover track ids
        #note: this methods works only for tracks. 
        #podcasts and other items will be ignored.
        print('Connecting to Spotify to recover tracks IDs.')
        sleep(3)
        id_length = 22
        for track, idd in track_ids.items(): 
            if idd is None:
                try:
                    found_idd = history.get_api_id(track, token)
                    track_ids[track] = found_idd
                    print(f"{found_idd:<{id_length}} : {', '.join(track.split('___'))}")
                except:
                    pass
        
        #how many tracks did we identify? 
        identified_tracks = [track for track in track_ids
                         if track_ids[track] is not None]
        print(f'Successfully recovered the ID of {len(identified_tracks)} tracks.')
        
        #how many items did we fail to identify? 
        n_tracks_without_id = len(track_ids) - len(identified_tracks)
        print(f"Failed to identify {n_tracks_without_id} items. "
              "However, some of these may not be tracks (e.g. podcasts).")
        
        #using pandas to save tracks ids (so we don't have to API them in the future)
        ids_path = 'output/track_ids.csv'
        ids_dataframe = pd.DataFrame.from_dict(track_ids, 
                                               orient = 'index')
        ids_dataframe.to_csv(ids_path)
        print(f'track ids saved to {ids_path}.')
    
    #recovering saved features
    track_features = history.get_saved_features(tracks)
    tracks_without_features = [track for track in tracks if track_features.get(track) is None]
    print(f"There are still {len(tracks_without_features)} tracks without features.")
    path = 'output/features.csv'
    
    #connecting to spotify API to retrieve missing features
    if len (tracks_without_features):
        print('Connecting to Spotify to extract features...')
        acquired = 0
        for track, idd in track_ids.items():
            if idd is not None and track in tracks_without_features:
                try:
                    features = history.get_api_features(idd, token)
                    track_features[track] = features
                    features['albumName'], features['albumID'] = history.get_album(idd, token)
                    if features:
                        acquired += 1
                        print(f"Acquired features: {', '.join(track.split('___'))}. Total: {acquired}")
                except:
                    features = None
        tracks_without_features = [track for track in tracks if track_features.get(track) is None]
        print(f'Successfully recovered features of {acquired} tracks.')
        if len(tracks_without_features):
            print(f'Failed to identify {len(tracks_without_features)} items. Some of these may not be tracks.')
        
        #saving features 
        features_dataframe = pd.DataFrame(track_features).T
        features_dataframe.to_csv(path)
        print(f'Saved features to {path}.')
    
    #joining features and streamings
    print('Adding features to streamings...')
    streamings_with_features = []
    for streaming in sorted(streamings, key= lambda x: x['endTime']):
        track = streaming['trackName'] + "___" + streaming['artistName']
        features = track_features.get(track)
        if features:
            streamings_with_features.append({'name': track, **streaming, **features})
    print(f'Added features to {len(streamings_with_features)} streamings.')
    print('Saving streamings...')
    df_final = pd.DataFrame(streamings_with_features)
    df_final.to_csv('output/final.csv')
    perc_featured = round(len(streamings_with_features) / len(streamings) *100, 2)
    print(f"Done! Percentage of streamings with features: {perc_featured}%.") 
    print("Run the script again to try getting more information from Spotify.")


if __name__ == '__main__':
    main()
