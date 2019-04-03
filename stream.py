import tweepy
import json
from tweepy import Stream
from tweepy.streaming import StreamListener

# Import credentials from text file
def import_credentials(txt):
    with open(txt,'r') as f:
        credentials = eval(f.read())
    return credentials

# Setting the credentials
credentials = import_credentials('credentials.txt')
API_key = credentials['app_key']
API_secret = credentials['app_secret']
OAUTH_token = credentials['oauth_token']
OAUTH_token_secret = credentials['oauth_token_secret']

# Basic listener, prints the stream to std output
class Listener(StreamListener):

    def on_data(self, data):
        with open('text1.txt', 'a') as output:
            json.dump(data, output)
            return True

    def on_error(self, status):
        print(status)

if __name__ == '__main__':
    listener = Listener()
    auth = tweepy.OAuthHandler(API_key, API_secret)
    auth.set_access_token(OAUTH_token, OAUTH_token_secret)
    stream = Stream(auth, listener)
    stream.filter(track=["baudet"],languages=['nl'], async=True)
    

    '''with open('text1.json') as output:
        dat = output.read()
        for line in dat:
            print(line)'''
