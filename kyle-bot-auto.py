#!encoding: utf-8
'''
	Requirements
		- Tokens must be added on user env
		- pip install slackclient
		- pip install twitter
		
	Slack Bot
	PH WOEID = 23424934
'''
import os, time, json
from slackclient import SlackClient
from twitter import *

config = {}
execfile("config.py", config)

BOT_NAME = 'kyle-bot'

#initialize slack client and twitter
slack_client = SlackClient(config["slack_token"])
twitter = Twitter(auth = OAuth(config["access_key"], config["access_secret"], config["consumer_key"], config["consumer_secret"]))


AVAILABLE_COMMANDS = ['start','help']

# get bot id to avoid hardcoded id
def get_bot_id():
	bot_id = ""
	api_call = slack_client.api_call('users.list')
	if api_call.get('ok'):
		users = api_call.get('members')
		for user in users:
			if 'name' in user and user.get('name') == BOT_NAME:
				bot_id = user['id']
	return bot_id

def fetch_twitter(channel):
	FETCH_TIME = 600 # every 10 minutes
	results = twitter.trends.place(_id = 23424934)
	rank = 1
	response = "Fetching top 10 Trends...\n"
	slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
	for location in results:
		for trend in location["trends"]:
			out = [{"color": "#36a64f","title": trend["name"],"title_link": trend["url"],"footer": "Rank: "+str(rank)+" | "+str(trend["tweet_volume"])+" Tweets"}]
			# out = [{"color": "#36a64f","title": status["user"]["screen_name"],"title_link": status["user"]["profile_image_url"],"text": status["text"],"footer": status["created_at"]}]	
			slack_client.api_call("chat.postMessage", parse="full", as_user=True, channel=channel, attachments=json.dumps(out))
			rank+=1
			if rank == 11:
				break

if __name__ == "__main__":
	bot_id = get_bot_id()
	at_bot = "<@" + bot_id + ">"
	
	print "List of public channels and their IDs"
	channels = slack_client.api_call("channels.list")
	for channel in channels["channels"]:
		print channel["name"], channel["id"]
	print ""
	print "List of private channels and their IDs"
	groups = slack_client.api_call("groups.list")
	for group in groups["groups"]:
		print group["name"], group["id"]

	DELAY = 600
	channel = "G81F17B1V" #you can change this. refer to list of channels.
	if slack_client.rtm_connect():
		print "Bot connected and running!"
		while True:
			fetch_twitter(channel)
			time.sleep(DELAY)
	else:
		print "Connection failed."

