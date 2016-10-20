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

from Tkinter import *
import os
import threading
import random

# Actually joins the rooms
s = openSocket()

#dictionary for options and the people who voted for it
votes = dict()
#keeps track of if a user has voted
usermap = dict()

def restartPoll():
	votes = dict()
	usermap = dict()

#gets the ultimate winner
def getWinner():
	winner = ""
	maxVotes = 0
	for option in votes:
		if(len(votes[option])>maxVotes):
			winner = maxVotes
			maxVotes = len(votes[option])
	return winner

def vote(option, user):
	if(not votes.has_key(option)):
		response = "Sorry " + "@" + user + ": that is not a valid vote option"
		sendMessage(s, response, 0);

	if(votes[option].contains(user)):
		return
	else:
		if(usermap.has_key(user)):
			oldOption = usermap[user]
			votes[oldOption].remove(user)

		votes[option].append(user)
		usermap[user] = option

def updateMessage():
	response = "A poll is currently underway! Type !vote to have your voice heard!"
	sendMessage(s, response, 0);

def setTimer():
	timer = int(timerStr.get())

def addOption():
	global options
	if(optionStr.get() != '' and not votes.has_key(optionStr.get())):
		votes[optionStr.get()] = []
		newOpt = options.get() + optionStr.get() + '\n'
		options.set(newOpt)
		root.update()

def readVotes():
	root.quit()
	### joinRoom(s)
	readbuffer = ""
	id = 0
	starttime = time.time() + timer
	while time.time() < starttime:
			# Pulls a chunk off the buffer, puts it in "temp"
			readbuffer = readbuffer + s.recv(1024)
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
						if(message.startswith("!vote")):
							option = message.split(" ")[1:]
							vote(option, user)
								

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
	
updateMessage()

# Initialize GUI
root = Tk()
canvas = Canvas(root, width=550, height=400)
canvas.pack()

# default timer value
timer = 60
timeLeft = StringVar()
options = StringVar()

tip1Label = Label(root,text='Your current options are:\n').pack()

optionsLabel = Label(root,textvariable=options).pack()

tip2Label = Label(root,text='Cast your vote as "!vote [your_vote]"').pack()

timerStr = StringVar()
timerLabel = Label(root,text='Set Vote Timer').pack()
timerEntry = Entry(root,textvariable=timerStr).pack()
timerButton = Button(root,text='Enter',command = setTimer,fg='black',bg='white').pack()

optionStr = StringVar()
optionLabel = Label(root,text='Enter Vote Option').pack()
optionEntry = Entry(root,textvariable=optionStr).pack()
optionButton = Button(root,text='Enter',command = addOption,fg='black',bg='white').pack()

startButton = Button(root,text='Start',command = readVotes,fg='black',bg='white').pack()
canvas.destroy()
root.mainloop()
"""
	tip1Label.destroy()
	optionsLabel.destroy()
	tip2Label.destroy()
	timerLabel.destroy()
	timerEntry.destroy()
	timerButton.destroy()
	optionLabel.destroy()
	optionEntry.destroy()
	optionButton.destroy()
"""