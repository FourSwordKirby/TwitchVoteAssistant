import os
import signal
import subprocess
from Tkinter import *

votes = dict()

def setTimer():
	timer = int(timerStr.get())

def addOption():
	global options
	if(optionStr.get() != '' and not votes.has_key(optionStr.get())):
		votes[optionStr.get()] = []
		newOpt = options.get() + optionStr.get() + '\n'
		options.set(newOpt)
		root.update()

def startReading():
	cmd = 'runv4.py %d' % timer
	for key in votes:
		cmd += ' %s' % key
	pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                       shell=True) 
	cmd = 'VoteTracker.py'
	pro = subprocess.Popen(cmd, stdout=subprocess.PIPE, 
                       shell=True) 
	quit()
	
# Initialize GUI
root = Tk()
canvas = Canvas(root, width=550, height=400)
canvas.pack()

# default timer value
timer = 10
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

startButton = Button(root,text='Start',command = startReading,fg='black',bg='white').pack()
canvas.destroy()
root.mainloop()