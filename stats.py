import requests, json
import time
from collections import defaultdict
from colorthief import ColorThief
import urllib
import operator
import os
import colormap
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
        
    
    
    def populate_media_helper(self, media_info_obj):
        medias = media_info_obj['data']
        for obj in medias:
            post_id = obj['id']
            created_time = self.get_time_of_day(int(obj['created_time']))
            num_likes = (obj['likes'])['count']
            filter_str = obj['filter']
            tags = obj["tags"]
            if obj["type"] == "image":
                image_url = obj["images"]["standard_resolution"]["url"]
            else:
                image_url = None
            if post_id not in self.post_id_set:
                post = Post(post_id, created_time, num_likes, "me", filter_str, image_url, tags)
                self.posts.append(post)
                self.post_id_set.add(post_id)

    def populate_my_media(self):
        my_media_info = requests.get('https://api.instagram.com/v1/users/self/media/recent/?access_token={0}'.format(self.access_token))
        my_media_info_obj = json.loads(my_media_info.text)
        self.populate_media_helper(my_media_info_obj)
        
        while my_media_info_obj['pagination']:
            my_media_info = requests.get(my_media_info_obj['pagination']['next_url'])
            my_media_info_obj = json.loads(my_media_info.text)
            self.populate_media_helper(my_media_info_obj)

    def populate_nearby_media(self):
        location_request = requests.get('http://freegeoip.net/json')
        location_req_json = json.loads(location_request.text)
        lat = location_req_json['latitude']
        lng = location_req_json['longitude']
        
        media_info = requests.get('https://api.instagram.com/v1/media/search?lat={0}&lng={1}&access_token={2}'.format(lat, lng, self.access_token))
       
        media_info_obj = json.loads(media_info.text)
        medias = media_info_obj['data']
      
        for obj in medias:
            post_id = obj['id']
            created_time = self.get_time_of_day(int(obj['created_time']))
            num_likes = (obj['likes'])['count']
            filter_str = obj['filter']
            image_url = obj["images"]["standard_resolution"]["url"]
            if post_id not in self.post_id_set:
                post = Post(post_id, created_time, num_likes, "nearby", filter_str, image_url)
                self.posts.append(post)
                self.post_id_set.add(post_id)

    def populate_my_followers_media(self):
        followers_info = requests.get('https://api.instagram.com/v1/users/self/followed-by?access_token={0}'.format(self.access_token))
        followers_obj = json.loads(followers_info.text)
        print(followers_obj)
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
                image_url = obj["images"]["standard_resolution"]["url"]
                if post_id not in self.post_id_set:
                    post = Post(post_id, created_time, num_likes, "follower", filter_str, image_url)
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
                comment_weight /= 2
            elif post.post_type == 'nearby':
                n_likes = post.num_likes / 10
                comment_weight /= 10
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
        print('total likes = {} and average likes = {}'.format(total_likes, comment_weight))
        return self.get_expected_time(time_weights)



    def get_dominant_colors(self):
        color_frequencies = defaultdict(int)
        color_weights = defaultdict(int)
        for p in self.posts:
            if p.image_url is None:
                continue
            urllib.request.urlretrieve(p.image_url, 'image')
            color_thief = ColorThief('image')
            palette = color_thief.get_palette(color_count=5, quality=1)
            for color in palette:
                color_weights[color] += p.num_likes
                color_frequencies[color] += 1
        os.remove('image')
        for k in color_weights.keys():
            color_weights[k] = color_weights[k] / color_frequencies[k]
        sorted_colors = sorted(color_weights.items(), key=operator.itemgetter(1))
        return [colormap.rgb2hex(c[0][0], c[0][1], c[0][2]) for c in sorted_colors[-1:-6:-1]]
        


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
        return 'wordcloud.png'




#what to do if there are no posts
#what to do if there are no likes
#what to do if there are no comments
#no followers-get the mean time of posts near current location
#get optimal location to post
#get optimal hashtag
#get optimal colors
#get optimal filter- the one with the highest mean number of likes
#to post video or image



        











