<div style='padding:0.4em; background-color: #63D1F4; color: #000033'>
<span>
<p style='margin-top:1em; text-align:center; font-size: 2em'>
<b>Geocoded Tweets Analysis Dashboard</b></p>
<p style='margin-left:1em;'>
This is an <b>INTERACTIVE</b>, <b>CONFIGURABLE</b> and <b>GENERIC</b> dashboard. 
It helps in visualizing key insights from tweets of <b>country-specific</b> or **global** users. 
</p>
</p></span>
</div>

> The application is built using [Plotly Dash](https://plotly.com/dash/).



The key insights include:
- Top influential users and their country
- Top influential countries and analyzing tweets from those countries 
- Communities of users; networking graph and communities' tweets analysis
- Reactive tweets (among the most quoted tweets) - tweets that received extreme sentiments
- Viral local retweets (By users' based in the specified country. For global level, viral local tweets are ignored)
- Viral global retweets (By users' NOT based in the specified country.)
- Potentially sensitive tweets analysis
- Popular mentions and hashtags
- Sentiment analysis 
- Daily tweets counts 
- Basic statistics - total tweets, avg no. of tweets per day, no. of unique users, and date range of the collected tweets
  
![Alt text](assets/dash_glimpse.png)


Checkout the demos for: 
- Country-specific 
    - [Singapore](http://sg-tweets-monitoring.herokuapp.com/) 
    - [India](http://sg-tweets-monitoring.herokuapp.com/)
    - [United States](http://sg-tweets-monitoring.herokuapp.com/)
- [Global level](http://sg-tweets-monitoring.herokuapp.com/) 

## Content

<!-- toc -->
- [Setup](#setup)
  - [Dependencies](#dependencies)
  - [Expected directory structure of the data](#expected-directory-structure-of-the-data)
  - [Diversity in Context and People Dataset](#diversity-in-context-and-people-dataset)
  - [Pose generation](#pose-generation)
- [Usage](#usage)
  - [Training Samples](#training-samples)
  - [Evaluation Sample](#evaluation-sample)
- [Contact](#contact)
- [References](#references)
- [License](#license)
<!-- tocstop -->


## Content

The repository contains code for: 
- Fetching followers of 59 Singapore-based official accounts (such as Ministry of Education, Health, and so on)  
- Geocoding tweets by using location, user description, place, and coordinates data
- Filtering Singapore-based tweets that are already ingested into MongoDB 
- Notebooks containing exploratory data analysis on the collected tweets
- Pipeline for generating key insights i.e., dashboard data (CSV and JSON files)
- Plotly Dash application for visualizing the insights


## Setup for Country-specific or Global Level Tweets Insights Generation

###  Step 1: Setup MongoDB configurations 

Create an .env file, and add the below required details for fetching tweets from MongoDB
```
MONGO_HOST= <mongo_host>
MONGO_USER= <mongo_username>
MONGO_PASS= <mongo_password>
```

<div class="warning" style='padding:0.1em; background-color:#E9D8FD; color:#69337A'>
<span>
<p style='margin-top:1em; text-align:center'>
<b>On the importance of sentence length</b></p>
<p style='margin-left:1em;'>
This sentence has five words. Here are five more words. Five-word sentences are fine. But several together bocome monotonous. Listen to what is happening. The writing is getting boring. The sound of it drones. It's like a stuck record. The ear demands some variety.<br><br>
    Now listen. I vary the sentence length, and I create music. Music. The writing sings. It has a pleasent rhythm, a lilt, a harmony. I use short sentences. And I use sentences of medium length. And sometimes when I am certain the reader is rested, I will engage him with a sentence of considerable length, a sentence that burns with energy and builds with all the impetus of a crescendo, the roll of the drums, the crash of the cymbals -- sounds that say listen to this, it is important.
</p>
<p style='margin-bottom:1em; margin-right:1em; text-align:right; font-family:Georgia'> <b>- Gary Provost</b> <i>(100 Ways to Improve Your Writing, 1985)</i>
</p></span>
</div>
--------------------------------------------------------------------------------



## Running the Application on Sample Data 

###  Step 1: Git clone the repository in local

```
git clone https://github.com/anshu0612/geocoded-tweets-analysis.git
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
docker image build -t geocoded-tweets-insights-dash:latest .
```

- Run the image 
```
docker container run -d -p 5000:5000 geocoded-tweets-insights-dash
```

### Step 3: Access the application on your local
Open  http://localhost:5000/  to see the application running 


## Generating Data 

### 1. Fetching followers of the Singapore-based official accounts`

Running the below command fetches the followers of the 59 collected Singapore-based official accounts. 
```
python3 get_sg_users.py --min_following_required 2
```
**Arguments**

| Argument | Description | Default
| ---- | --- | --- |
| min_following_required | Filter users following at least these number of Singapore-based official accounts | 2 |

The file `/data/min_following_users.txt` contains the user ids of the collected twitter Singapore-based official accounts.

The list of followers will be saved in `/data/sg_accounts_followers` folder.

### 2. Creating geocoded tweets data 
<!-- Tweets from the streaming twitter API are first ingested into MongoDB.  -->
```
python3 get_tweets.py --db_name "COVID_VACCINE" --collection_no_list 1,2,3,4,5
```

**Arguments**

| Argument | Description | Default
| ---- | --- | --- |
| db_name | Database name to fetch tweets from | - |
| collection_no_list | List of Mongo collections | - |
| running_tw_save_count | Number of tweets to save during tweets processing | 1000 |
| max_csv_tw_count | Maximum no. of tweets to save in a csv | 10000 |


### 3. Creating dashboard data 
```
python3 generate_dash_data.py 
```
You can setup the dashboard related constants in the `data/dash_constants.py`

