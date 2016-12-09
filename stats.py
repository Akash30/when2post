import requests, json
import time
from collections import defaultdict



class Post:
    def __init__(self, post_id, created_time, num_likes):
        self.post_id = post_id
        self.created_time = created_time
        self.num_likes = num_likes


class Stats:
    def __init__(self, access_token):
        self.access_token = access_token
        self.client_secret = "b32ac1a8ad6b47a5bf5e5ed3548cf675"
        self.api = InstagramAPI(access_token=access_token, client_secret=client_secret)
        user_info = requests.get('https://api.instagram.com/v1/users/self/?access_token={}'.format(self.access_token))
        temp1 = json.loads(user_info.text)
        num_posts = ((temp['data'])['counts'])['media']
        user_id = (temp['data'])['id']
        posts = []
        posts, next_ = self.api.user_recent_media(user_id)
        while next_:
            more_posts, next_ = self.api.user_recent_media(with_next_url=next_)
            posts.extend(more_posts)
       # need to get all posts...currently instagram returns only 20 of the most recent posts


    def get_time_of_day(unix_time):
        # converts unix time to the time of the day in seconds from 12:00am
        time_obj = time.localtime(unix_time)
        secs = (time_obj.tm_hour * 60 * 60) + (time_obj.tm_min * 60) + time_obj.tm_sec
        return secs

    def weight_post_times(comment_weight):
        time_to_weight_mapping = defaultdict(int)
        for post in self.posts:
            # weight post
            time_to_weight_mapping[post.created_time] += post.num_likes
            comment_times = self.get_comment_times(post.post_id)
            time_to_weight_mapping = {t: time_to_weight_mapping[t] + comment_weight for t in comment_times}

        return time_to_weight_mapping


    def get_expected_time(time_to_weight_mapping):
        expected_time = 0
        total_weight = sum(time_to_weight_mapping.values())
        for k, v in time_to_weight_mapping:
            probability = v / total_weight
            expected_time += (k * probability)

        return int(expected_time)


    def compute_optimal_time():
        if len(self.posts) == 0:
            print('No data found')

        total_likes = sum([p.num_likes for p in self.posts])
        comment_weight = int(total_likes / len(self.posts))
        time_weights = weight_post_times(comment_weight)
        return get_expected_time(time_weights)




        










