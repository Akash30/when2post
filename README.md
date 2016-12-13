# when2post
What our app does: This app analyzes your instagram posts and gives you an optimal time to make your next post to maximize activity=likes+comments. The optimal time uses an expected time kind of calculation where the likes are weighted by comments and likes.
It also tells you which are the 5 most dominant colors used in all your posts, again weighted by the number of likes.
It also tells you the most frequently used and most popular hashtags (again weighted by likes and comments) in the form of word cloud representations. It also lets you know which are the best filter to use where the filters are again weighted and ranked by the average number of likes and comments they receive.

How to use our app:
1) Clone the github repository.
2) Make sure all the modules used in stats.py and app.py have been installed.
3) Log out of your instagram account on your browser, if you were previously logged in on your PC on the desktop instagram wesbite.
3) Run "python3 app.py"
4) Then, open up a browser and go to http://localhost:5000
5) Click on the "Login with Instagram"
6) Type in your INSTAGRAM username and password and click "Log In" on the popup window that appears. Note our app requires you to use your Instagram username and password; and doesn't provide functionality to "Log in with Facebook"
7) Once you type in your credentials, you'll get a window asking for permissions. Please accept.
8) Wait for a while and the results will be displayed!

How we satisfy the requirements:
1) We defined our own custom class Stats, which we implement the methods which perform the various statistical calculations on instagram data. We also make the API calls in this class. We then instantiate a Stats Object in app.py and use this instance to get all the results, by calling its methods. Apart from __init__, we defined the __int__ magic method which we used to cast a variety of the results from our calculations in stats.py to integers.
2) The modules we used from class: collections, os, itertools, math, requests, BeautifulSoup, flask, json, matplotlib
3) weight_post_times, color_helper, weight_posts: These are some of the methods in stats.py, within which we created generators and called these generators until we exhausted it (that is, got a StopIterationException). Also in the method "exp_calc", we used the "yield" keyword to iterate through the list and add to exp_time, without having to explicitly return it and hence return from the entire method.


Names of Group Members:
1) Akash Subramanian
2) Visakh Nair
