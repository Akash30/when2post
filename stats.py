import requests, json

class Stats:
    def __init__(self, access_token):
        self.access_token = access_token
        self.client_secret = "b32ac1a8ad6b47a5bf5e5ed3548cf675"
        user_info = requests.get('https://api.instagram.com/v1/users/self/?access_token={0}'.format(self.access_token))
        temp1 = json.loads(user_info.text)
        num_posts = ((temp1['data'])['counts'])['media']
        user_id = (temp1['data'])['id']
        print(num_posts)
        print(user_id)
        al = requests.get('https://api.instagram.com/v1/users/self/media/recent/?access_token={0}&count={1}'.format(self.access_token, num_posts))
        temp2 = json.loads(al.text)
        media = temp2['data']
        print(len(media))
        posts
        # posts = []
        # posts, next_ = self.api.user_recent_media(user_id)
        # while next_:
        #     more_posts, next_ = self.api.user_recent_media(with_next_url=next_)
        #     posts.extend(more_posts)
        # print(posts)