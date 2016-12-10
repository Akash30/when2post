# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request
import requests
import json
from stats import Stats
from bs4 import BeautifulSoup
import base64


# create the application object
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/callback/instagram')
def on_callback():
    error = request.args.get('error')
    if error:
        return "Error: " + error
    code = request.args.get("code")
    if not code:
        return 'Instagram not allowed'
    try:
        response = requests.post('https://api.instagram.com/oauth/access_token', data = {'client_id':'f3ef7014dfdc4a64a832af7d487d787a', 'client_secret': 'b32ac1a8ad6b47a5bf5e5ed3548cf675', 
                                     'grant_type': 'authorization_code', 'redirect_uri': 'http://localhost:5000/callback/instagram', 'code': code})
        json_obj = json.loads(response.text)
        access_token = json_obj['access_token']
        statsObj = Stats(access_token)
        opt_time = statsObj.compute_optimal_time()
        statsObj.create_tags_wordcloud()
        print('created wordcloud')
        hours = int(opt_time / 3600)
        minutes = int((opt_time - hours * 3600) / 60)
        seconds = (opt_time - hours * 3600 - minutes * 60)
        formatted_time = '{}:{}:{}'.format(hours, minutes, seconds)
        best_filter = statsObj.get_best_filter()
        f_read = open('templates/results.html', 'r')
        soup = BeautifulSoup(f_read, 'html.parser')
        new_tag1 = soup.new_tag("p")
        new_tag1.string = 'Optimal time to Post: {}'.format(formatted_time)
        original_tag1 = soup.div
        if original_tag1.p is not None:
            original_tag1.p.replace_with(new_tag1)
        else:
            original_tag1.append(new_tag1)
        new_tag2 = soup.new_tag("h2")
        new_tag2.string = 'Best Filter to Use: {}'.format(best_filter)
        original_tag2 = soup.div
        if original_tag2.h2 is not None:
            original_tag2.h2.replace_with(new_tag2)
        else:
            original_tag2.append(new_tag2)
        colors = statsObj.get_dominant_colors()
        head = soup.head
        new_tag3 = soup.new_tag("style", type="text/css")
        new_tag3.string = 'body{{margin:0;padding:0;font:100%/1.3 arial,helvetica,sans-serif;background:#FFFFFF;}}#wrap{{width:900px;margin:0 auto;text-align:center;font-weight:bold;color:#FFF;}}#nav{{min-height:50px;background:{4};}}#header{{min-height:200px;background:{0};}}#main{{width:100%;overflow:hidden;}}#content{{float:left;width:600px;min-height:200px;background:{1};}}#links{{float:left;width:300px;min-height:200px;background:{2};}}#footer{{min-height:50px;background:{3};}}'.format(colors[0], colors[1], colors[2], colors[3], colors[4])
        if head.style is not None:
            head.style.replace_with(new_tag3)
        else: 
            head.append(new_tag3)
        src_bytes = None
        with open('wordcloud.png', 'rb') as image_file:
            src_bytes = base64.b64encode(image_file.read())
        src_text = str(src_bytes)
        src_text = src_text[2:len(src_text) - 1]
        src_text = 'data:image/png;base64,' + src_text
        new_tag4 = soup.new_tag('img', src=src_text)
        
        body = soup.body
        if body.img is not None:
            body.img.replace_with(new_tag4)
        else:
            body.append(new_tag4)
        html_str = soup.prettify(formatter="html")
        f_read.close()
        f_write = open('templates/results.html', 'w')
        f_write.write(html_str)
        f_write.close()
        if not access_token:
            return 'Could not get access token'
    except Exception as e:
        print(e)
    return render_template('results.html')

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
