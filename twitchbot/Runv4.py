import string
import csv
import time
import operator
from Readv3 import getUser, getMessage, getChannelname, getBannedUser, getBannedChannelname
from Readv3 import getslowmode, getr9k, getsubmode, getroomstatechannelname
from Readv3 import getOwner, getTurbo, getSub, getMod
from Socketv2 import openSocket, sendMessage
from Settingsv2 import HOST, PORT, PASS, IDENT
from datetime import datetime

import os
import threading
import random

# Actually joins the rooms
s = openSocket()

#dictionary for user's and the funds they have
userFunds = dict()

#dictionary for user's and the tickets they currently have active
userTickets = dict()

winnings = 30;

#check the ticket stash for winners
def checkTickets():
	threading.Timer(60, checkTickets).start()
	global winnings;
	global userFunds;
	global userTickets;

	ticket =  [random.randint(0, 20), random.randint(0, 20), random.randint(0, 20), random.randint(0, 20), random.randint(0, 20), random.randint(0, 20)]
	sendMessage(s, "The ticket " + str(ticket) + " has been drawn!", 0);
	for user in userTickets:
		winnings = 0;
		matchCount = 0;
		for userTicket in userTickets[user]:
			for idx, number in enumerate(userTicket):
				if(idx < 6):
					if number == ticket[idx]:
						matchCount += 1
			if(matchCount == 1):
				winnings = max(winnings, 1)
			if(matchCount == 2):
				winnings = max(winnings, 5)
			if(matchCount == 3):
				winnings = max(winnings, 10)
			if(matchCount == 4):
				winnings = max(winnings, 30)
			if(matchCount == 5):
				winnings = max(winnings, 100)
			if(matchCount == 6):
				winnings = max(winnings, 200)
		userTickets[user] = []
		if(matchCount > 0):
			time.sleep(1.0)
			sendMessage(s, "@" + user + " Congratulations! You have gained " + str(winnings) + " tickets", 0);
			userFunds[user] += winnings;
	time.sleep(1.0)
	sendMessage(s, "The drawing has concluded, the ticket pool has been cleaned for the next drawing", 0);

def updateMessage():
	threading.Timer(30, checkTickets).start()
	response = "A drawing is currently under way! Register to get tickets! Type !help for more info. "
	response += "This stream does NOT encourage players to gamble recklessly"
	sendMessage(s, response, 0);

checkTickets()
updateMessage()


### joinRoom(s)
readbuffer = ""


id = 0

# Sets how long the scraper will run for (in seconds)
starttime = time.time() + 100000

# Runs until time is up
while time.time() < starttime:
		# Pulls a chunk off the buffer, puts it in "temp"
		readbuffer = readbuffer + s.recv(1024)
		temp = string.split(readbuffer, "\n")
		readbuffer = temp.pop()


		# Iterates through the chunk
		for line in temp:
			print line
			id = id + 1
		
			# Parses lines and writes them to the file
			if "PRIVMSG" in line:
				try:

					# Gets user, message, and channel from a line
					user = getUser(line)
					message = getMessage(line)
					channelname = getChannelname(line)
					owner = getOwner(line)
					mod = getMod(line)
					sub = getSub(line)
					turbo = getTurbo(line)
		
					if owner == 1:
						mod = 1
		
					# Writes Message ID, channel, user, date/time, and cleaned message to file
					with open('outputlog.csv', 'ab') as fp:
						ab = csv.writer(fp, delimiter=',')
						data = [id, channelname, user, datetime.now(), message.strip(), owner, mod, sub, turbo];
						ab.writerow(data)
					if(message.startswith("!register")):
						if(userFunds.has_key(user)):
							sendMessage(s, "@" + user + " You have already registered for the drawing", 0);
							continue

						if(not userFunds.has_key(user)):
							userFunds[user] = 10;
						if(not userTickets.has_key(user)):
							userTickets[user] = []

						response = user + " has registered for the drawings!"
						sendMessage(s, response, 0);

					if(message.startswith("!help")):
						response = "@" + user + " To buy a ticket, type in !ticket followed by the player, followed by 6 numbers between 0 and 99. "
						response += "For example, [!ticket 12 34 56 78 90 99] will purchase a ticket with numbers [12 34 56 78 90 99] "
						response += "You get 10 tickets a day. Win drawings to earn more. Check your tickets with !myTickets"
						sendMessage(s, response, 0);

					if(message.startswith("!myTickets") or message.startswith("!mytickets")):
						if(not userFunds.has_key(user)):
							sendMessage(s, "@" + user + " Please register before buying tickets", 0);
							continue

						response = "@" + user + " you have " + str(userFunds[user]) + " tickets remaining. "
						if(len(userTickets[user]) > 0):
							response += "Your active tickets are: "
							for ticketNumber in userTickets[user]:
								response +=  str(ticketNumber)
						sendMessage(s, response, 0);

					if(message.startswith("!ticket")):
						if(not userFunds.has_key(user)):
							sendMessage(s, "@" + user + " Please register before buying tickets", 0);
						else:
							if (not len(message.split(" ")) == 7):
								sendMessage(s, "@" + user + " Please format your request properly, type !help", 0);
								continue

							ticketNums = message.split(" ")[1:];
							ticketNumber = ""
							for num in ticketNums:
								ticketNumber += num.rstrip() + " "
							ticketNumber = ticketNumber.rstrip();
							
							if(not len(filter(lambda x: not x.rstrip().isdigit(), ticketNums)) == 0):
								response = "@" + user + " the numbers you have entered is not valid"
								sendMessage(s, response, 0);
								continue
							
							if(not len(filter(lambda x: int(x.rstrip()) > 99 or int(x.rstrip()) < 0, ticketNums)) == 0):
								response = "@" + user + " a number you entered was out of the accepted range";
								sendMessage(s, response, 0);
								continue
							

							if(userFunds[user] <= 0):
								response = "@" + user + " you lack the funds to purchase tickets"
								sendMessage(s, response, 0);
								continue

							if(ticketNumber in userTickets[user]):
								response = "@" + user + " you have already purchased that ticket"
								sendMessage(s, response, 0);
								continue

							ticketNumber = []
							for num in ticketNums:
								ticketNumber.append(int(num))
							
							userFunds[user] -= 1
							if(not userTickets.has_key(user)):
								userTickets[user] = [];
							userTickets[user].append(ticketNumber)

							response = "@" + user + " You have just purchased ticket " + str(ticketNumber)
							sendMessage(s, response, 0);

				# Survives if there's a message problem
				except Exception as e:
					print "MESSAGE PROBLEM"
					print line
					print e
		
			# Responds to PINGs from twitch so it doesn't get disconnected
			elif "PING" in line:
				try:
					separate = line.split(":", 2)
					s.send("PONG %s\r\n" % separate[1])
					print ("PONG %s\r\n" % separate[1])
					print "I PONGED BACK"
				
				# Survives if there's a ping problem
				except:
					print "PING problem PING problem PING problem"
					print line
		
			# Parses ban messages and writes them to the file
			elif "CLEARCHAT" in line:
				try:
			
					# Gets banned user's name and channel name from a line
					user = getBannedUser(line)
					channelname = getBannedChannelname(line)
				
					# Writes Message ID, channel, user, date/time, and an indicator that it was a ban message.
					#	I use "oghma.ban" because the bot's name is oghma, and I figure it's not a phrase that's
					#	likely to show up in a message so it's easy to search for.
					with open('outputlog.csv', 'ab') as fp:
						ab = csv.writer(fp, delimiter=',');
						data = [id, channelname, user, datetime.now(), "oghma.ban"];
						ab.writerow(data);
			
				# Survives if there's a ban message problem
				except Exception as e:
					print "BAN PROBLEM"
					print line
					print e
				