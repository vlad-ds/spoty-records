Medium article: 

Welcome to spoty-records! This script will extract your Spotify streaming history, connect to the Spotify API to acquire the songs' features, and organize everything into a handy .csv file to examine with Pandas or other tools. 

Dependencies:

	> Pandas: https://pandas.pydata.org/
	> Spotipy: https://spotipy.readthedocs.io/en/2.7.1/
	> Requests: https://requests.readthedocs.io/en/master/

Steps:

1. Enter your account dashboard at https://www.spotify.com/. In the privacy settings, apply for the download of your personal data. This might take a few days. When you get the mail, download the zip archive and place the MyData folder into the script folder. 

2. Sign up at Spotify for Developers at https://developer.spotify.com/. Select 'Create an app'. From the app panel, take note of your Client ID and Client Secret. Then select 'Edit settings' and whitelist a link in Redirect URIs. If you don't have a site, http://localhost:7777/callback will do. Take note of this link too.

3. Open config.py and insert your Spotify username, Client ID, Client Secret and Redirect URI. You can leave the scope as is.

4. Execute main.py. If it's the first time, Spotipy will need user authentication. It will try to open a link in your browser, or failing that, will print the link in your console/terminal. Follow the link, log in with your Spotify account, and accept the permissions. Then you will be taken to the Redirect URI. Paste the URI in the console. 

5. The script will now reconstruct your listening history, connect to Spotify API to get the song IDs, and then use those IDs to extract the features. 

5. If you still miss IDs or features, you can run the script again and retry your luck with the API. Collected IDs and features are saved, so we don't make repeated requests. 

6. Find your song history, complete with features, in 'output/final.csv'. Happy exploration! 
