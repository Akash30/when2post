import requests, json
import time
from collections import defaultdict
from colorthief import ColorThief
import urllib
import operator
import os
import colormap
import itertools
from wordcloud import WordCloud

class Post:
    def __init__(self, post_id, created_time, num_likes, post_type, filter_str, image_url, tags):
        self.post_id = post_id
        self.created_time = created_time
        self.num_likes = num_likes
        self.post_type = post_type
        self.filter_str = filter_str
        self.image_url = image_url
        self.tags = tags

class Stats:
    def __init__(self, access_token):
        self.post_id_set = set()
        self.access_token = access_token
        self.client_secret = "b32ac1a8ad6b47a5bf5e5ed3548cf675"
        self.posts = []
        self.populate_my_media() #what if we have no posts
        # self.populate_my_followers_media() #what if we have no followers
        #what if there is no nearby media
    
    def helper_posts(self, obj, post_type):
        post_id = obj['id']
        created_time = self.get_time_of_day(int(obj['created_time']))
        num_likes = (obj['likes'])['count']
        filter_str = obj['filter']
        image_url = obj["images"]["standard_resolution"]["url"]
        tags = obj['tags']
        if post_id not in self.post_id_set:
            post = Post(post_id, created_time, num_likes, post_type, filter_str, image_url, tags)
            self.posts.append(post)
            self.post_id_set.add(post_id)

    def populate_media_helper(self, media_info_obj, post_type):
        medias = media_info_obj['data']
        gen = (self.helper_posts(obj, post_type) for obj in medias)
        while True:
            try:
                next(gen)
            except Exception as e:
                print(e)
                break

    def populate_my_media(self):
        my_media_info = requests.get('https://api.instagram.com/v1/users/self/media/recent/?access_token={0}'.format(self.access_token))
        my_media_info_obj = json.loads(my_media_info.text)
        self.populate_media_helper(my_media_info_obj, "me")
        while my_media_info_obj['pagination']:
            my_media_info = requests.get(my_media_info_obj['pagination']['next_url'])
            my_media_info_obj = json.loads(my_media_info.text)
            self.populate_media_helper(my_media_info_obj, "me")

    def populate_nearby_media(self):
        location_request = requests.get('http://freegeoip.net/json')
        location_req_json = json.loads(location_request.text)
        lat = location_req_json['latitude']
        lng = location_req_json['longitude']
        media_info = requests.get('https://api.instagram.com/v1/media/search?lat={0}&lng={1}&access_token={2}'.format(lat, lng, self.access_token))
        media_info_obj = json.loads(media_info.text)
        self.populate_media_helper(media_info_obj, "nearby")

        while media_info_obj['pagination']:
            media_info = requests.get(media_info_obj['pagination']['next_url'])
            media_info_obj = json.loads(media_info.text)
            self.populate_media_helper(media_info_obj, "nearby")
    
    def followers_helper(self, follower):
        follower_id = int(follower['id'])
        follower_media = requests.get('https://api.instagram.com/v1/users/{0}/media/recent/?access_token={1}'.format(follower_id, self.access_token))
        follower_media_obj = json.loads(follower_medias.text)
        self.populate_media_helper(follower_media_obj, "follower")

        while follower_media_obj['pagination']:
            media_info = requests.get(follower_media_obj['pagination']['next_url'])
            follower_media_obj = json.loads(media_info.text)
            self.populate_media_helper(follower_media_obj, "follower")

    def populate_my_followers_media(self):
        followers_info = requests.get('https://api.instagram.com/v1/users/self/followed-by?access_token={0}'.format(self.access_token))
        followers_obj = json.loads(followers_info.text)
        followers = followers_obj['data']
        gen = (self.followers_helper(follower) for follower in followers)
        while True:
            try:
                next(gen)
            except StopIteration:
                break

    def get_time_of_day(self, unix_time):
        # converts unix time to the time of the day in seconds from 12:00am
        time_obj = time.localtime(unix_time)
        secs = (time_obj.tm_hour * 60 * 60) + (time_obj.tm_min * 60) + time_obj.tm_sec
        return secs

    def get_comment_times(self, post_id):
        comments_info = requests.get('https://api.instagram.com/v1/media/{0}/comments?access_token={1}'.format(post_id, self.access_token))
        comments_info_obj = json.loads(comments_info.text)
        comments = comments_info_obj['data']
        return [self.get_time_of_day(int(comment['created_time'])) for comment in comments]

    def increment_times(self, d, weight, t):
        d[t] += weight
    
    def weight_posts(self, post, d, comment_weight):
        n_likes = 0
        if post.post_type == 'follower':
            n_likes = post.num_likes / 2
            comment_weight /= 2
        elif post.post_type == 'nearby':
            n_likes = post.num_likes / 10
            comment_weight /= 10
        else:
            n_likes = post.num_likes
        d[post.created_time] += n_likes
        comment_times = self.get_comment_times(post.post_id)
        gen = (self.increment_times(d, comment_weight, t) for t in comment_times)
        while True:
            try:
                next(gen)
            except StopIteration:
                break

    def weight_post_times(self, comment_weight):
        time_to_weight_mapping = defaultdict(int)
        gen = (self.weight_posts(post, time_to_weight_mapping, comment_weight) for post in self.posts)
        while True:
            try:
                next(gen)
            except StopIteration:
                break
        return time_to_weight_mapping
    
    def exp_calc(self, total_wt, time_to_weight_mapping):
        exp_time = 0
        for time in time_to_weight_mapping.keys():
            probability = time_to_weight_mapping[time] / total_wt
            exp_time += (time * probability)
            yield exp_time


    def get_expected_time(self, time_to_weight_mapping):
        total_weight = sum(time_to_weight_mapping.values())
        expected_times = itertools.islice(self.exp_calc(total_weight, time_to_weight_mapping), 0, None)
        return int(list(expected_times)[len(time_to_weight_mapping.keys()) - 1])

    def compute_optimal_time(self):
        if len(self.posts) == 0:
            print('No posts data found')
            return -1
        total_likes = sum([p.num_likes for p in self.posts])
        comment_weight = int(total_likes / len(self.posts))
        time_weights = self.weight_post_times(comment_weight)
        return self.get_expected_time(time_weights)
    
    def color_palette_helper(self, color, color_weights, color_frequencies, post):
        color_weights[color] += post.num_likes
        color_frequencies[color] += 1

    def color_helper(self, post, color_weights, color_frequencies):
        urllib.request.urlretrieve(post.image_url, 'image')
        color_thief = ColorThief('image')
        palette = color_thief.get_palette(color_count=5)
        gen = (self.color_palette_helper(color, color_weights, color_frequencies, post) for color in palette)
        while True:
            try:
                next(gen)
            except StopIteration:
                break

    def color_wt_helper(self, color_weights, color_frequencies, k):
        color_weights[k] = color_weights[k] / color_frequencies[k]

    def get_dominant_colors(self):
        color_frequencies = defaultdict(int)
        color_weights = defaultdict(int)
        gen1 = (self.color_helper(p, color_weights, color_frequencies) for p in self.posts)
        while True:
            try:
                next(gen1)
            except StopIteration:
                break
        os.remove('image')
        gen2 = (self.color_wt_helper(color_weights, color_frequencies, k) for k in color_weights.keys())
        while True:
            try:
                next(gen2)
            except StopIteration:
                break
        sorted_colors = sorted(color_weights.items(), key=operator.itemgetter(1))
        return [colormap.rgb2hex(c[0][0], c[0][1], c[0][2]) for c in sorted_colors[-1:-6:-1]]
           
    def best_filter_helper(self, post, filter_dict_frequencies, filter_dict_likes):
        filter_str = post.filter_str
        filter_dict_frequencies[filter_str] += 1
        filter_dict_likes[filter_str] += post.num_likes

    def best_filter_avg_helper(self, filter_dict_frequencies, filter_dict_likes, key):
        filter_dict_frequencies[key] = filter_dict_likes[key]/filter_dict_frequencies[key]

    def get_best_filter(self):
        if len(self.posts) == 0:
            print('No posts data found')
            return -1
        filter_dict_frequencies = defaultdict(int)
        filter_dict_likes = defaultdict(int)
        gen1 = (self.best_filter_helper(post, filter_dict_frequencies, filter_dict_likes) for post in self.posts)
        while True:
            try:
                next(gen1)
            except StopIteration:
                break
        gen2 = (self.best_filter_avg_helper(filter_dict_frequencies, filter_dict_likes, key) for key in filter_dict_frequencies.keys())
        while True:
            try:
                next(gen2)
            except StopIteration:
                break
        max_filter = ""
        mx = 0
        for key in filter_dict_frequencies:
            if filter_dict_frequencies[key] > mx:
                mx = filter_dict_frequencies[key]
                max_filter = key
        return max_filter

    def create_tags_wordcloud(self):
        if len(self.posts) == 0:
            print('No posts data found')
            return -1
        text = ''
        for post in self.posts:
            for tag in post.tags:
                text += tag + '\n'
        
        wordcloud = WordCloud().generate(text)
        image = wordcloud.to_image()
        image.save('wordcloud.png')
        




#what to do if there are no posts
#what to do if there are no likes
#what to do if there are no comments
#no followers-get the mean time of posts near current location
#get optimal location to post
#get optimal hashtag
#get optimal colors
#get optimal filter- the one with the highest mean number of likes
#to post video or image



        











