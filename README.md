# Singapore-based geocoded tweets analysis

This is an **interactive**, **configurable** and **generic** dashboard for visualizing key insights from Singapore-based users' tweets. The key insights include:
- Top influential users and their country
- Top influential countries and analyzing tweets from those countries 
- Communities of users; networking graph and communities' tweets analysis
- Reactive tweets (among the most quoted tweets) - tweets that received extreme sentiments
- Viral local retweets (By Singapore-based users' accounts)
- Viral global retweets (By non-Singapore-based users' accounts)
- Potentially sensitive tweets analysis
- Popular mentions and hashtags
- Sentiment analysis 
- Daily tweets counts 
- Basic stats - total tweets, avg no. of tweets per day, no. of unique users, and so on
  
![Alt text](dash_glimpse.png)

Checkout the [demo](http://sg-tweets-monitoring.herokuapp.com/) here. 

The repository contains code for: 
- Fetching followers of 59 Singapore-based official accounts (such as Ministry of Education, Health, and so on)  
- Geocoding tweets by using location, user description, place, and coordinates data
- Filtering Singapore-based tweets that are already ingested into MongoDB 
- Notebooks containing exploratory data analysis on the collected tweets
- Pipeline for generating key insights i.e., dashboard data (CSV and JSON files)
- Plotly Dash application for visualizing the insights

--------------------------------------------------------------------------------

## Running the application  

###  Step 1: Git clone the repository in local

```
git clone https://github.com/anshu0612/singapore-geocoded-tweets-analysis.git
```

###  Step 2: Setting up the environment and running the application

- Install dependencies 
```
pip3 install -r requirements.txt
```

- Run the application 
```
python3 app.py
```

If you face environment dependencies then you can use **Docker Image** instead. 

- Install Docker on your system 

- Run the below command to build the docker image
```
docker image build -t sg-dash:latest .
```

- Run the image 
```
docker container run -d -p 5000:5000 sg-dash
```

### Step 3: Access the application on your local
Open  http://localhost:5000/  to see the application running 

