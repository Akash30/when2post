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
        user_info = requests.get('https://api.instagram.com/v1/users/self/?access_token={0}'.format(self.access_token))
        user_info_obj = json.loads(user_info.text)
        num_posts = ((user_info_obj['data'])['counts'])['media']
        user_id = (user_info_obj['data'])['id']
        media_info = requests.get('https://api.instagram.com/v1/users/self/media/recent/?access_token={0}&count={1}'.format(self.access_token, num_posts))
        media_info_obj = json.loads(media_info.text)
        medias = media_info_obj['data']
        self.posts = []
        for obj in medias:
            post_id = obj['id']
            created_time = self.get_time_of_day(int(obj['created_time']))
            num_likes = (obj['likes'])['count']
            post = Post(post_id, created_time, num_likes)
            self.posts.append(post)

    def get_time_of_day(self, unix_time):
        # converts unix time to the time of the day in seconds from 12:00am
        time_obj = time.localtime(unix_time)
        secs = (time_obj.tm_hour * 60 * 60) + (time_obj.tm_min * 60) + time_obj.tm_sec
        return secs

    def get_comment_times(self, post_id):
        comments_info = requests.get('https://api.instagram.com/v1/media/{0}/comments?access_token={1}'.format(post_id, self.access_token))
        comments_info_obj = json.loads(comments_info.text)
        comments = comments_info_obj['data']
        comment_times = [self.get_time_of_day(int(comment['created_time'])) for comment in comments]
        return comment_times

    def weight_post_times(self, comment_weight):
        time_to_weight_mapping = defaultdict(int)
        for post in self.posts:
            # weight post
            time_to_weight_mapping[post.created_time] += post.num_likes
            comment_times = self.get_comment_times(post.post_id)
            for t in comment_times:
                time_to_weight_mapping[t] += comment_weight

        return time_to_weight_mapping

    def get_expected_time(self, time_to_weight_mapping):
        
        expected_time = 0
        total_weight = sum(time_to_weight_mapping.values())
        for k in time_to_weight_mapping.keys():
            probability = time_to_weight_mapping[k] / total_weight
            expected_time += (k * probability)

        return int(expected_time)

    def compute_optimal_time(self):
        if len(self.posts) == 0:
            print('No data found')
            return -1

        total_likes = sum([p.num_likes for p in self.posts])
        comment_weight = int(total_likes / len(self.posts))
        print('comment wt: {0}'.format(comment_weight))
        time_weights = self.weight_post_times(comment_weight)
        print('map = {}'.format(time_weights))
        return self.get_expected_time(time_weights)




        











