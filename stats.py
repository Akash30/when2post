import requests, json
from instagram.client import InstagramAPI
class Stats:
	def __init__(self, access_token):
		self.access_token = access_token
		self.client_secret = "b32ac1a8ad6b47a5bf5e5ed3548cf675"
		self.api = InstagramAPI(access_token=access_token, client_secret=client_secret)
        user_info = requests.get('https://api.instagram.com/v1/users/self/?access_token=' + self.access_token)
        temp1 = json.loads(user_info.text)
        num_posts = ((temp['data'])['counts'])['media']
        user_id = (temp['data'])['id']
        posts = []
        posts, next_ = self.api.user_recent_media(user_id)
        while next_:
        	more_posts, next_ = self.api.user_recent_media(with_next_url=next_)
        	posts.extend(more_posts)
       # need to get all posts...currently instagram returns only 20 of the most recent posts