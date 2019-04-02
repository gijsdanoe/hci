# Change credentials

def change_credentials(txt, credentials):
    with open('credentials.txt','w') as f:
        f.write("{")
        f.write("'app_key':'{}',".format(credentials[0]))
        f.write("'app_secret':'{}',".format(credentials[1]))
        f.write("'oauth_token':'{}',".format(credentials[2]))
        f.write("'oauth_token_secret':'{}',".format(credentials[3]))
        f.write("}")

def main():
    credentials=[]
    credentials.append(input("What is your API key?\n"))
    credentials.append(input("What is your secret API key?\n"))
    credentials.append(input("What is your OAUTH token?\n"))
    credentials.append(input("What is your secret OAUTH token?\n"))
    change_credentials('credentials.txt', credentials)

if __name__ == "__main__":
    main()
