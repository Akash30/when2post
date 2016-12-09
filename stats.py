import requests, json
import time


class Post:
    def __init__(self, post_id, created_time, num_likes):
        self.post_id = post_id
        self.created_time = created_time
        self.num_likes = num_likes


class Stats:
    def __init__(self, access_token):
        self.access_token = access_token
        self.client_secret = "b32ac1a8ad6b47a5bf5e5ed3548cf675"
        user_info = requests.get('https://api.instagram.com/v1/users/self/?access_token={0}'.format(self.access_token))
        temp1 = json.loads(user_info.text)
        num_posts = ((temp1['data'])['counts'])['media']
        user_id = (temp1['data'])['id']
        al = requests.get('https://api.instagram.com/v1/users/self/media/recent/?access_token={0}&count={1}'.format(self.access_token, num_posts))
        temp2 = json.loads(al.text)
        media = temp2['data']
        self.posts = []
        for obj in media:
            post_id = obj['id']
            created_time = int(obj['created_time'])
            num_likes = (obj['likes'])['count']
            post = Post(post_id, created_time, num_likes)
            self.posts.append(post)
   
    def get_time_of_day(unix_time):
        # converts unix time to the time of the day in seconds from 12:00am
        time_obj = time.gmtime(unix_time)
        secs = (time_obj.tm_hour * 60 * 60) + (time_obj.tm_min * 60) + time_obj.tm_sec
        return secs

    def weight_post_times(comment_weight):
        time_to_weight_mapping = {}
        for post in posts:
            # weight post
            day_time = get_time_of_day(post.created_time)
            time_to_weight_mapping[day_time] = post.num_likes

    def compute_optimal_time(post_list):
        if len(post_list) == 0:
            print('No data found')

        total_likes = sum([p.num_likes for p in post_list])
        comment_weight = int(total_likes / len(post_list))


        











