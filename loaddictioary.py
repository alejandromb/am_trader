cred_file = open('credentials.txt', 'r')
d = {}
Lines=cred_file.readlines()


API_KEY = Lines[0].split('=')[1]
API_SECRET = Lines[1].split('=')[1]
APCA_API_BASE_URL = Lines[2].split('=')[1]
print(API_KEY)
print(API_SECRET)
print(APCA_API_BASE_URL)

