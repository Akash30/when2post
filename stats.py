import requests, json
import time
from collections import defaultdict

class Post:
    def __init__(self, post_id, created_time, num_likes, post_type, filter_str):
        self.post_id = post_id
        self.created_time = created_time
        self.num_likes = num_likes
        self.post_type = post_type
        self.filter_str = filter_str

class Stats:
    def __init__(self, access_token):
        self.post_id_set = set()
        self.access_token = access_token
        self.client_secret = "b32ac1a8ad6b47a5bf5e5ed3548cf675"
        self.posts = []
        self.populate_my_media() #what if we have no posts
        #self.populate_my_followers_media() #what if we have no followers
        #what if there is no nearby media
    
    def populate_my_media(self):
        my_media_info = requests.get('https://api.instagram.com/v1/users/self/media/recent/?access_token={0}'.format(self.access_token))
        my_media_info_obj = json.loads(my_media_info.text)
        my_medias = my_media_info_obj['data']
        print(my_medias)
        for obj in my_medias:
            post_id = obj['id']
            created_time = self.get_time_of_day(int(obj['created_time']))
            num_likes = (obj['likes'])['count']
            filter_str = obj['filter']
            if post_id not in self.post_id_set:
                post = Post(post_id, created_time, num_likes, "me", filter_str)
                self.posts.append(post)
                self.post_id_set.add(post_id)

    def populate_nearby_media(self):
        location_request = requests.get('http://freegeoip.net/json')
        location_req_json = json.loads(location_request.text)
        lat = location_req_json['latitude']
        lng = location_req_json['longitude']
        print(lat)
        print(lng)
        media_info = requests.get('https://api.instagram.com/v1/media/search?lat={0}&lng={1}&access_token={2}'.format(lat, lng, self.access_token))
        print(media_info.text)
        media_info_obj = json.loads(media_info.text)
        medias = media_info_obj['data']
      
        for obj in medias:
            post_id = obj['id']
            created_time = self.get_time_of_day(int(obj['created_time']))
            num_likes = (obj['likes'])['count']
            filter_str = obj['filter']
            if post_id not in self.post_id_set:
                post = Post(post_id, created_time, num_likes, "nearby", filter_str)
                self.posts.append(post)
                self.post_id_set.add(post_id)

    def populate_my_followers_media(self):
        followers_info = requests.get('https://api.instagram.com/v1/users/self/followed-by?access_token={0}'.format(self.access_token))
        followers_obj = json.loads(followers_info.text)
        followers = followers_obj['data']
        for follower in followers:
            follower_id = int(follower['id'])
            follower_medias = requests.get('https://api.instagram.com/v1/users/{0}/media/recent/?access_token={1}'.format(follower_id, self.access_token))
            follower_medias_obj = json.loads(follower_medias.text)
            follower_medias = follower_medias_obj['data']
            for obj in follower_medias:
                post_id = obj['id']
                created_time = self.get_time_of_day(int(obj['created_time']))
                num_likes = (obj['likes'])['count']
                filter_str = obj['filter']
                if post_id not in self.post_id_set:
                    post = Post(post_id, created_time, num_likes, "follower", filter_str)
                    self.posts.append(post)
                    self.post_id_set.add(post_id)

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
            n_likes = 0
            if post.post_type == 'follower':
                n_likes = post.num_likes / 2
            elif post.post_type == 'nearby':
                n_likes = post.num_likes / 10
            else:
                n_likes = post.num_likes
            time_to_weight_mapping[post.created_time] += n_likes
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
            print('No posts data found')
            return -1
        total_likes = sum([p.num_likes for p in self.posts])
        comment_weight = int(total_likes / len(self.posts))
        time_weights = self.weight_post_times(comment_weight)
        return self.get_expected_time(time_weights)

    def get_best_filter(self):
        if len(self.posts) == 0:
            print('No posts data found')
            return -1
        filter_dict_frequencies = defaultdict(int)
        filter_dict_likes = defaultdict(int)
        for post in self.posts:
            filter_str = post.filter_str
            filter_dict_frequencies[filter_str] += 1
            filter_dict_likes[filter_str] += post.num_likes
        for key in filter_dict_frequencies.keys():
            filter_dict_frequencies[filter_str] = filter_dict_likes[key]/filter_dict_frequencies[key]
        max_filter = ""
        max = 0
        for key in filter_dict_frequencies:
            if filter_dict_frequencies[key] > max:
                max = filter_dict_frequencies[key]
                max_filter = key
        return max_filter


#what to do if there are no posts
#what to do if there are no likes
#what to do if there are no comments
#no followers-get the mean time of posts near current location
#get optimal location to post
#get optimal hashtag
#get optimal colors
#get optimal filter- the one with the highest mean number of likes
#to post video or image



        











