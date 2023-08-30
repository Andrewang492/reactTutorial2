import time
from flask import Flask, request, url_for, session, redirect
import spotipy #spotipy is an app that wraps spotify API in a module.
from spotipy.oauth2 import SpotifyOAuth
import pandas as pd

app = Flask(__name__)

app.secret_key = "jdifjedf" # a random string used to sign the session cookie
app.config['SESSION_COOKIE_NAME'] = 'my cookie' #a session is where we store data of a user's session, ie dont need login to different pages because in a session.

@app.route('/')
def login():
    sp_oauth = create_spotify_oauth()
    auth_url = sp_oauth.get_authorize_url() #this function has an object, getauthorizeurl...
    return redirect(auth_url) # This much me matched on the Spotify Developers website.

@app.route('/redirect')
def redirectPage():
    sp_oauth = create_spotify_oauth() #create a new one...
    session.clear() # in this redirected state, clear everything else
    code = request.args.get('code')
    token_info = sp_oauth.get_access_token(code) #tokeninfo has refresh token, access token, expiresAt.
    session["token_info"] = token_info #save this token information in this session.
    return redirect(url_for('getTracks', _external = True))

@app.route('/getTracks')
def getTracks():
    try:
        token_info = get_token()
    except:
        print("user not logged in")
        redirect("/") #url_for('login', _external = False)
        return redirect("/")
    #our token is up to date :

    sp = spotipy.Spotify(auth = token_info['access_token'])
    get_all_songs(sp) #creates a csv
    return "done"

def get_all_songs(sp):
    results = []
    iter = 0
    while True:
        offset = iter * 50
        iter += 1
        curGroup = sp.current_user_saved_tracks(limit=50, offset=offset)['items'] #offeet is start index.
        # for idx, item in enumerate(curGroup):
        #     track = item['track']
        #     val = track['name'] + " - " + track['artists'][0]['name']
        #     results += [val]
        # if (len(curGroup) < 50): #ie its the last page
        #     break
        
        item = curGroup[0]
        track = item['track']
        val = track['name'] + " - " + track['artists'][0]['name']
        results += [val]
        item = curGroup[1]
        track = item['track']
        val = track['name'] + " - " + track['artists'][0]['name']
        results += [val]
        break
    
    df = pd.DataFrame(results, columns=["song names"]) 
    df.to_csv('songs.csv', index=False)

def get_token():
    token_info = session.get("token_info", None) # i.e if token info doesnt exist this is None.
    if not token_info:
        raise "exception"
    now = int(time.time())
    is_expired = token_info['expires_at'] = now < 60
    if (is_expired):
        sp_oauth = create_spotify_oauth()
        token_info = sp_oauth.refresh_access_token(token_info['refresh_token'])
    return token_info

clientID = "0c73de93343d4c72a6a923ba8aa35980"
clientSecret = "2c7c5836852b44b5a26a605741a63b9e"

def create_spotify_oauth():
    #make this special object. Every time you use need this object, make a new one.
    return SpotifyOAuth(
        client_id = clientID,
        client_secret = clientSecret,
        redirect_uri = url_for('redirectPage', _external = True), # don't need to hardcode using url_for and updates. Use function name, not address
        scope = "user-library-read"
    )
