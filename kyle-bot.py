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

def command_handler(command, channel):
	"""
		Receive a command and will handle it if found in AVAILABLE_COMMANDS
	"""
	response = "I don't get what you mean, here's the available commands: " + ", ".join(AVAILABLE_COMMANDS)

	split_command = command.split(" ")
	first_arg = split_command[0]
	second_arg = ""
	# check if multiple arguments are entered and set the second argument to second_arg
	if len(split_command) > 1:
		second_arg = split_command[1]

	if first_arg in AVAILABLE_COMMANDS:

		if first_arg == "start":
			if len(second_arg) > 0:
				if not second_arg.isalpha():
					fetch_twitter(channel,second_arg)
					response = "Done fetching trends"
				else:
					response = "@kyle-bot start n (where 'n' is the number of update interval)"
			else:
				response = "@kyle-bot start n (where 'n' is the number of update interval)"
		elif first_arg == "help":
			response = "@kyle-bot help - display this message\n@kyle-bot start n (where 'n' is the number of update interval every 10 minutes)"

	slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)

def parse_output(rtm_output, at_bot, bot_id):
	"""
		this will parse the output that will be passed to command and channel
		Example output:
		{u'source_team': u'T7N5MDTJ6', u'text': u'<@U80CPAWLA> help', u'ts': u'1510709180.000184', u'user': u'U7PEJEMDY', u'team': u'T7N5MDTJ6', u'type': u'message', u'channel': u'G81F17B1V'}
		Example parsed output to return:
		help G81F17B1V
	"""
	output_list = rtm_output
	if output_list and len(output_list) > 0:
		for output in output_list:
			if output and 'text' in output and at_bot in output['text']:
				return output['text'].split(at_bot)[1].strip().lower(),output['channel']
	return None, None

def fetch_twitter(channel, second_arg):
	FETCH_TIME = 600 # every 10 minutes
	# print_text = ""
	
	n = int(second_arg)
	while (n > 0):
		rank = 1
		# response = "Fetching Tweets... Intervals left: "+str(n)
		response = "Fetching Trends... Intervals left: "+str(n)
		slack_client.api_call("chat.postMessage", channel=channel, text=response, as_user=True)
		results = twitter.trends.place(_id = 23424934)
		for location in results:
			for trend in location["trends"]:

		# statuses = twitter.statuses.home_timeline(count = 15)
		# for status in statuses:
				out = [{"color": "#36a64f","title": trend["name"],"title_link": trend["url"],"footer": str(trend["tweet_volume"])+" Tweets - Rank "+str(rank)}]
			# out = [{"color": "#36a64f","title": status["user"]["screen_name"],"title_link": status["user"]["profile_image_url"],"text": status["text"],"footer": status["created_at"]}]	
				slack_client.api_call("chat.postMessage", parse="full", as_user=True, channel=channel, attachments=json.dumps(out))
				rank += 1
		n -= 1
		if n == 0:
			break
		time.sleep(FETCH_TIME)
		


if __name__ == "__main__":
	bot_id = get_bot_id()
	at_bot = "<@" + bot_id + ">"
	DELAY = 1
	if slack_client.rtm_connect():
		print "Bot connected and running!"
		while True:
			command, channel = parse_output(slack_client.rtm_read(), at_bot, bot_id)
			if command and channel:
				command_handler(command, channel)
			time.sleep(DELAY)
	else:
		print "Connection failed."

