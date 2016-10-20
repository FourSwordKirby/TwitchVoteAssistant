from Tkinter import *

results = dict()

def timerFired(canvas):
	canvas.delete(ALL)
	delay = 250 # milliseconds
	with open('votes.txt') as f:
		lines = f.read().splitlines()
	i = 0
	for entry in lines:
		# update written vote info
		optionInfo[i].set(entry)
		# update rectangles
		i+=1

	def g():
		timerFired(canvas)
	canvas.after(delay, g) # pause, then call timerFired again

# Initialize GUI
root = Tk()
canvas = Canvas(root, width=550, height=400)
canvas.pack()
with open('votes.txt') as f:
	lines = f.read().splitlines()
optionInfo = []
cols = len(lines)
i = 0
for entry in lines:
	newEntry = StringVar()
	newEntry.set(entry)
	optionInfo.append(newEntry)
	Label(root,textvariable=optionInfo[i]).pack()
	i+=1
timerFired(canvas)

root.mainloop()