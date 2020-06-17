import auth
import praw
import json
import re
import statistics
import model
from textblob import TextBlob
from collections import Counter
from sklearn.utils import shuffle

reddit = praw.Reddit(client_id = auth.id,
                     client_secret = auth.secret,
                     user_agent = auth.agent,
                     username = auth.username,
                     password = auth.password)

################################################################################

def generateTrainingData():

    datastore = []

    rep = []
    dem = []
    rep_labels = []
    dem_labels = []

    republican = reddit.subreddit('Republican')
    democrats = reddit.subreddit('Democrats')

    for submission in republican.top('all', limit=9999):
        if not submission.stickied:
            title = re.sub("\"", "\'", submission.title)
            title = re.sub(r'[^\x00-\x7F]+','', title)
            rep.append(title)
            rep_labels.append(1)

    limit = len(rep)

    for submission in democrats.top('all', limit=limit):
        if not submission.stickied:
            title = re.sub("\"","\'", submission.title)
            title = re.sub(r'[^\x00-\x7F]+','', title)
            dem.append(title)
            dem_labels.append(0)


    if(len(rep) != len(dem)):
        n = len(rep) - len(dem)
        rep = rep[:len(rep)-n]
        rep_labels = rep_labels[:len(rep_labels)-n]

    training_data = rep + dem
    labels = rep_labels + dem_labels

    training_data, labels = shuffle(training_data, labels)

    for i in range(len(training_data)):
        item = {}
        item['title'] = training_data[i]
        item['label'] = labels[i]
        datastore.append(item)

    with open('training_data.json', 'w') as f:
        json.dump(datastore, f)

#generateTrainingData()

################################################################################

subreddit_list = ['politics',
                  'Conservative',
                  'uspolitics',
                  'socialism',
                  'esist',
                  'EnoughTrumpSpam',
                  'moderatepolitics',
                  'PoliticalHumor',
                  'The_Donald',
                  'LateStageCapitalism',
                  'PoliticalDiscussion',
                  'Libertarian',
                  'SandersForPresident',
                  'NeutralPolitics',
                  'YangForPresidentHQ']

limit = 100

dataframe = {}

sentiment = []
polarity = []
size = []
related = []
all_related_subs = []

################################################################################

def generateSubredditData(name, limit):

    subreddit = reddit.subreddit(name)

    samples = []
    users = []
    related_subs = []

    polarity_results = []

    for submission in subreddit.top('all', limit=limit):
        if not submission.stickied:
            if(hasattr(submission.author, 'name')):
                title = re.sub("\"", "\'", submission.title)
                title = re.sub(r'[^\x00-\x7F]+','', title)
                samples.append(title)
                users.append(submission.author.name)

    sentiment_results = list(model.queryModel(samples))

    for sample in samples:
        pol_score = TextBlob(sample).sentiment.polarity
        if(pol_score != 0 and pol_score != 1):
            polarity_results.append(pol_score)

    average_sentiment = statistics.mean(sentiment_results)
    average_sentiment = (average_sentiment*2)-1
    sentiment.append(average_sentiment)

    average_polarity = statistics.mean(polarity_results)
    polarity.append(average_polarity)

    size.append(subreddit.subscribers)

    for user in users:
        if not(hasattr(reddit.redditor(user), 'is_suspended')):
            for submission in reddit.redditor(user).submissions.top(limit=10):
                if not submission.stickied:
                    related_sub = submission.subreddit.display_name
                    if(related_sub not in subreddit_list):
                        related_subs.append(related_sub)
                        all_related_subs.append(related_sub)

    count = dict(Counter(related_subs).most_common(20))
    related.append(count)

    print(f"Generated data for r/{name}")


def generateDataframe():

    i = 0

    for subreddit in subreddit_list:
        generateSubredditData(subreddit, limit)

    all = {}
    all_count = dict(Counter(all_related_subs).most_common(20))
    all['related'] = all_count
    dataframe['all'] = all

    for subreddit in subreddit_list:
        item = {}
        item['sentiment'] = sentiment[i]
        item['polarity'] = polarity[i]
        item['size'] = size[i]
        item['related'] = related[i]

        dataframe[subreddit_list[i]] = item
        i += 1

    with open('subreddit_data.json', 'w') as f:
        json.dump(dataframe, f)

    print("Completed!")

generateDataframe()
