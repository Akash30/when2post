# import the Flask class from the flask module
from flask import Flask, render_template, redirect, url_for, request
import requests
import json
from stats import Stats
from bs4 import BeautifulSoup

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
        color_list = statsObj.get_dominant_colors()
        opt_time = statsObj.compute_optimal_time()

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
