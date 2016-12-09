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
        opt_time = statsObj.compute_optimal_time()
        f_read = open('templates/results.html', 'r')
        soup = BeautifulSoup(f_read, 'html.parser')
        f_read.close()
        new_tag = soup.new_tag("p")
        new_tag.string = 'Optimal time to Post: {}'.format(opt_time)
        original_tag = soup.div
        original_tag.append(new_tag)
        html_str = soup.prettify()
        f_write = open('templates/results.html', 'wb')
        f_write.write(html_str)
        if not access_token:
            return 'Could not get access token'
    except Exception as e:
        print(e)

    return render_template('results.html')

# start the server with the 'run()' method
if __name__ == '__main__':
    app.run(debug=True)
