import requests, json
import time


class Post:
    def __init__(self, media_id, created_time, num_likes):
        self.media_id = media_id
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
        time_obj = time.gmtime(unix_time)
        secs = (time_obj.tm_hour * 60 * 60) + (time_obj.tm_min * 60) + time_obj.tm_sec
        return secs

    def weight_post_times(post_list, comment_weight):
        time_to_weight_mapping = {}
        for post in post_list:
            # weight post
            day_time = get_time_of_day(post.created_time)
            time_to_weight_mapping[day_time] = post.num_likes




    def compute_optimal_time(post_list):
        if len(post_list) == 0:
            print('No data found')

        total_likes = sum([p.num_likes for p in post_list])
        comment_weight = int(total_likes / len(post_list))


        










