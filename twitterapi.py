import tweepy

def import_credentials(txt):
    with open(txt,'r') as f:
        credentials = eval(f.read())
    return credentials
    
def main():
    credentials = import_credentials('credentials.txt')
    
    API_key = credentials['app_key']
    API_secret = credentials['app_secret']
    OAUTH_token = credentials['oauth_token']
    OAUTH_token_secret = credentials['oauth_token_secret']

    auth = tweepy.OAuthHandler(API_key, API_secret)
    auth.set_access_token(OAUTH_token, OAUTH_token_secret)
    api = tweepy.API(auth)

    public_tweets = api.home_timeline()
    for tweet in public_tweets:
        print(tweet.text)
    
if __name__ == "__main__":
    main()
