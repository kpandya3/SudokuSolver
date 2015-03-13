#!/usr/bin/python

import Tkinter
import timeit
from Tkinter import *
from tkFileDialog import askopenfilename
from copy import deepcopy

class simpleapp_tk(Tkinter.Tk):
	"""Main tkinter class for GUI"""
	def __init__(self,parent, puzzle):
		"""
		Initializer for main GUI class
		"""
		Tkinter.Tk.__init__(self,parent)
		self.parent = parent
		# set the puzzle for the GUI
		self.puzzle = puzzle
		# set the GUI for the puzzle (Doing this instead of callbacks since it's easier)
		self.puzzle.setGUI(self)
		# create the window
		self.initialize()

	def initList(self):
		"""
		Creates nested list of 9x9 StringVars
		"""
		# create empty 9x9 grid (list of lists) for gui variables
		self.list = [[],[],[],[],[],[],[],[],[]]
		for i in range(9):
			for j in range(9):
				# add StringVar()s in the 9x9 list. 81 StringVars to store the Sudoku values
				self.list[i].append(StringVar())
				# set default to 0 since file not loaded yet
				self.list[i][j].set(0)

	def initialize(self):
		"""
		Add items to the window and update the window
		"""
		self.grid()
		self.initList()

		# we keep space in our grid after each 3 rows and columns to differentiate 3x3 blocks
		listRange = [0,1,2,4,5,6,8,9,10]
		for i in range(9):
			for j in range(9):
				# These labels are for the 9x9 puzzle on gui
				# We use StringVars initialized in self.list so that we can update these later
				l = Tkinter.Label(self,textvariable=self.list[i][j], anchor="center", fg="white", bg="blue", width=5, height=2, relief=GROOVE)
				l.grid(column=listRange[j],row=listRange[i],columnspan=1,sticky='EW')

		# Reference to 1px by 1px image (explained later)
		img = "R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
		img = PhotoImage(data=img)
		# Create borders around 3x3 blocks
		# we use 3rd and 7th, rows and columns to keeps some space in that row and column
		for i in [3,7]:
			l = Tkinter.Label(self, bd=0, width=0, height=1)
			l.grid(column=i,row=1,columnspan=1,sticky='EW')
			l = Tkinter.Label(self, image=img,bd=0, width=0, height=2)
			l.grid(column=1,row=i,columnspan=1,sticky='NS')

		# create checkbox to enable/disable GUI update while algorithm is going on
		# this is useful because with GUI update enabled, algorithm slows down a lot
		self.guiUpdateEnabled = IntVar()
		self.guiUpdateEnabled.set(1)
		c = Checkbutton(self, text="Update GUI", variable=self.guiUpdateEnabled, command=self.updateGUIchecked)
		c.grid(column=11,row=0,columnspan=2, sticky=N+S+E+W)
		self.updateGUIchecked()

		# Create a label to display selected filename
		self.fileName = StringVar()
		browseLabel = Tkinter.Label(self, textvariable=self.fileName, bd=0, width=0, height=1, padx=10, pady=10)
		browseLabel.grid(column=11,row=1,columnspan=2,sticky='EW')
		self.fileName.set("Select File")

		# created button that would ask user for filename
		bBrowse = Button(self, text="Select", command=self.loadFile)
		bBrowse.grid(column=11,row=2,columnspan=2, sticky=N+S+E+W)

		# dropdown menu to select the Algorithm to run on puzzle
		self.alg = StringVar(self)
		optM = OptionMenu(self, self.alg, "BF", "BT", "FC-MRV")
		optM.grid(column=11,row=5,columnspan=2, sticky=N+S+E+W)

		# Button to run the algorithm
		bRun = Button(self, text="Run", command=self.run)
		bRun.grid(column=11,row=6,columnspan=2, sticky=N+S+E+W)

		# label to display expanded nodes pretext
		l = Tkinter.Label(self, text="Nodes Expanded:")
		l.grid(column=11, row=8, columnspan=1, sticky=N+S+E+W)

		# label to show expanded nodes in milliseconds
		self.nodesExpanded = StringVar()
		self.nodesExpanded.set(0)
		l = Tkinter.Label(self, textvariable=self.nodesExpanded)
		l.grid(column=12, row=8, columnspan=1, sticky=N+S+E+W)

		# label to display total time pretext
		l = Tkinter.Label(self, text="Total time:")
		l.grid(column=11, row=9, columnspan=1, sticky=N+S+E+W)

		# label to show expanded nodes in milliseconds
		self.totalTime = StringVar()
		self.totalTime.set("00000000")
		l = Tkinter.Label(self, textvariable=self.totalTime)
		l.grid(column=12, row=9, columnspan=1, sticky=N+S+E+W)

		# label to display just the algorithm running time - pretext
		l = Tkinter.Label(self, text="Alg time:")
		l.grid(column=11, row=10, columnspan=1, sticky=N+S+E+W)

		# label to show algorithm runtime in milliseconds
		self.algTime = StringVar()
		self.algTime.set("00000000")
		l = Tkinter.Label(self, textvariable=self.algTime)
		l.grid(column=12, row=10, columnspan=1, sticky=N+S+E+W)

		self.resizable(True,True)
		self.update()
		self.geometry(self.geometry())

	def setCell(self, x, y, val):
		"""
		Sets the cell value to val at given x-y coordinates
		"""
		self.list[x][y].set(val)

	def setNodes(self, nodes):
		"""
		Sets the total nodes expanded label value to nodes
		"""
		self.nodesExpanded.set(nodes)

	def setTotalTime(self, time):
		"""
		Sets the total algorithm runtime to time
		"""
		self.totalTime.set("{0:.2f}".format(round(time, 2)))

	def setAlgTime(self, time):
		"""
		Sets the algorithm runtime to time
		"""
		self.algTime.set("{0:.2f}".format(round(time, 2)))

	def updateGUIchecked(self):
		"""
		Handler when the checkbox is checked for gui update
		"""
		# If checkbox checked, we tell puzzle to update gui at each cycle
		if self.guiUpdateEnabled.get():
			self.puzzle.setGUIUpdateEnabled(True)
		# Else we tell puzzle not to update gui at each cycle
		else:
			self.puzzle.setGUIUpdateEnabled(False)

	def loadFile(self):
		"""
		Handler for select file button
		"""
		# Open file dialog and let user pick a file that ends with .txt
		fname = askopenfilename(parent=self, filetypes = [("Puzzle files", "*.txt")])
		# Set the filename label to the name of the file
		self.fileName.set(fname.split('/')[-1])
		# Open the file
		f = open(fname, "r")
		# Put all contents of the file in lines variable
		lines = [map(int, line.strip().split(' ')) for line in f]			
		f.close()
		# Tell puzzle to load the lines found in the file
		self.puzzle.load(lines)
		# Finally print the generated puzzle
		print self.puzzle

	def run(self):
		"""
		Handler for run button click
		"""
		# reset total time
		self.setTotalTime(0)
		start = timeit.default_timer()
		# tell puzzle to run the selected algorithm
		self.puzzle.run(self.alg.get())
		end = timeit.default_timer()
		# Set total time to end-start time
		self.setTotalTime((end - start)*1000)
		# print the solved final puzzle
		print self.puzzle

class Puzzle:
	"""Puzzle class that has 9x9 grid and solving algorithms"""
	def __init__(self):
		"""
		Initializer for puzzle class
		"""
		self.initgrid = None
		self.grid = None
		self.guiUpdateEnabled = False
		# setup functions to call based on dropdown text
		self.algs = { 'BF': self.BF, 'BT': self.BT, 'FC-MRV': self.FCMRV }
		self.nodesExpanded = 0
		self.totalRuntime = 0
		self.algRuntime = 0

	def run(self, alg):
		"""
		Run the given algorithm alg on the puzzle
		"""
		# Get the function to run for the given algorithm alg (string) and run that function
		self.algs[alg]()

	def setGUIUpdateEnabled(self, checked):
		"""
		Set if the puzzle should update the GUI at each cycle or not
		"""
		self.guiUpdateEnabled = checked

	def setNodes(self, nodes):
		"""
		Set the total nodes expanded for the puzzle and on the gui
		"""
		self.nodesExpanded = nodes
		# Call gui's setNodes method to set nodes on gui
		self.gui.setNodes(nodes)
		self.update_gui()

	def setAlgTime(self, algTime):
		"""
		Set algorithm runtime to algTime
		"""
		self.algRuntime = algTime*1000
		# Update gui with the algorithm runtime
		self.gui.setAlgTime(algTime*1000)
		self.update_gui()

	def resetPuzzle(self):
		"""
		Reset the puzzle to it's initial state
		"""
		for i in range(9):
			for j in range(9):
				# Go through each x-y values on 9x9 grid
				# And set all of them to it's initial state that was taken from file
				self.grid[i][j] = self.initgrid[i][j]
				self.gui.setCell(i,j,self.initgrid[i][j])
		self.update_gui()

	def setGUI(self, gui):
		"""
		Set the gui 
		"""
		self.gui = gui

	def setCell(self, x, y, val, updateGUI):
		"""
		Set the cell value at x-y coordinates to value and update the gui if required
		"""
		# Set the grid value for the puzzle at x-y to val
		self.grid[x][y] = val
		if val != 0:
			# Only update the nodes expanded if we are not resetting the cell value back to 0
			self.nodesExpanded += 1
		if updateGUI:
			# If asked, update the gui with new cell values too
			self.gui.setCell(x,y,val)
			self.update_gui()

	def update_gui(self):
		"""
		Update the idle tasks in the gui
		"""
		self.gui.update_idletasks()

	def load(self, data):
		"""
		Load the initial data that was read from file
		"""
		# Copy the data over so that we can reset it back later if needed
		self.initgrid = deepcopy(data)
		# The actual grid data we will be playing around with
		self.grid = data
		for i in xrange(9):
			for j in xrange(9):
				# Set the cells on the GUI with file data
				self.setCell(i,j, self.grid[i][j], True)

	def isFull(self):
		"""
		Returns True if puzzle is full (not necessarily valid) else False
		"""
		for item in self.grid:
			if 0 in item:
				return False
		return True

	def isSolved(self):
		"""
		Return true if the puzzle has been solved else return False
		"""
		# Make sure all rows have unique and there are no 0s in them
		for i in self.grid:
			if len(i) > len(set(i)) and 0 not in i:
				return False
		# Make sure all columnss have unique and there are no 0s in them
		for i in zip(*self.grid):
			if len(i) > len(set(i)) and 0 not in i:
				return False
		# Make sure all 3x3 blocks are unique and there are no 0s in them
		for i in [1, 4, 7]:
			for j in [1, 4, 7]:
				# Find points around center and check
				tmp =   [ self.grid[i-1][j-1], self.grid[i][j-1], self.grid[i+1][j-1],
						  self.grid[i-1][j],  self.grid[i][j],  self.grid[i+1][j],
						  self.grid[i-1][j+1], self.grid[i][j+1], self.grid[i+1][j+1]]
				if len(tmp) > len(set(tmp)) and 0 not in tmp:
					return False
		return True

	def isValidMove(self, coord, val):
		"""
		Check if the value val at given coordinates coord is valid value there
		"""
		# Check if the value is in the row or column of those coordinates
		if val in self.grid[coord[0]] or val in zip(*self.grid)[coord[1]]:
			return False

		center = [coord[0], coord[1]]
		for i in range(2):
			if (coord[i]+1)%3 == 1:
				center[i]+=1
			elif (coord[i]+1)%3 == 0:
				center[i]-=1
		blockList = [ self.grid[center[0]-1][center[1]-1], self.grid[center[0]][center[1]-1], self.grid[center[0]+1][center[1]-1]
					, self.grid[center[0]-1][center[1]],  self.grid[center[0]][center[1]],  self.grid[center[0]+1][center[1]]
					, self.grid[center[0]-1][center[1]+1], self.grid[center[0]][center[1]+1], self.grid[center[0]+1][center[1]+1]]
		if val in blockList:
			return False
		return True

	def BF(self):
		self.resetPuzzle()
		remaining_list = []
		for i in xrange(9):
			for j in xrange(9):
				if self.grid[i][j] == 0:
					remaining_list.append((i, j))

		def bf_helper(remaining_list):
			if not remaining_list:
				if self.isSolved():
					return True
				else:
					return False
			for i in xrange(1, 10):
				self.setCell(remaining_list[0][0], remaining_list[0][1], i, self.guiUpdateEnabled)
				tmp = bf_helper(remaining_list[1:])
				if tmp:
					return True
				self.setCell(remaining_list[0][0], remaining_list[0][1], 0, self.guiUpdateEnabled)
			return False
		self.setNodes(0)
		self.setAlgTime(0)
		start = timeit.default_timer()
		bf_helper(remaining_list)
		end = timeit.default_timer()
		self.setAlgTime(end-start)
		self.setNodes(self.nodesExpanded)

	def BT(self):
		self.resetPuzzle()
		remaining_list = []
		for i in xrange(9):
			for j in xrange(9):
				if self.grid[i][j] == 0:
					remaining_list.append((i, j))

		def bt_helper(remaining_list):
			if not remaining_list:
				return True
			for i in xrange(1, 10):
				if self.isValidMove(remaining_list[0], i):
					self.setCell(remaining_list[0][0], remaining_list[0][1], i, self.guiUpdateEnabled)
					tmp = bt_helper(remaining_list[1:])
					if tmp:
						return True
					self.setCell(remaining_list[0][0], remaining_list[0][1], 0, self.guiUpdateEnabled)
			return False
		self.setNodes(0)
		self.setAlgTime(0)
		start = timeit.default_timer()
		bt_helper(remaining_list)
		end = timeit.default_timer()
		self.setAlgTime(end-start)
		self.setNodes(self.nodesExpanded)

	def FCMRV(self):
		self.resetPuzzle()
		def setUpMRV():
			remaining = {}
			for i in xrange(9):
				for j in xrange(9):
					if self.grid[i][j] == 0:
						center = [i, j]
						for k in range(2):
							if (center[k]+1)%3 == 1:
								center[k]+=1
							elif (center[k]+1)%3 == 0:
								center[k]-=1
						remaining[(i, j)] = [[k for k in xrange(1,10) if self.isValidMove((i, j), k)], center]
			return remaining

		def getLowestMRV(mrv):
			return min(mrv, key=lambda item: len(mrv.get(item)[0])) if len(mrv) > 0 else 0

		def useMRV(remaining, key, val, i):
			removed_list = []
			for ik, iv in remaining.iteritems():
				if ik[0]==key[0] or ik[1]==key[1] or val[1] == iv[1]:
					try:
						iv[0].remove(i)
						removed_list.append(ik)
						if not iv[0]:
							setMRVback(remaining, removed_list, i)
							return False
					except ValueError:
						pass
			return removed_list

		def setMRVback(mrv, removed_list, i):
			for item in removed_list:
				mrv.get(item)[0].append(i)

		def fcmrv_helper(remaining):
			lowest = getLowestMRV(remaining)
			if lowest == 0:
				return True
			lowest_val = remaining.pop(lowest, None)
			for i in lowest_val[0]:
				self.setCell(lowest[0], lowest[1], i, self.guiUpdateEnabled)
				removed_list = useMRV(remaining, lowest, lowest_val, i)
				if removed_list is not False:
					tmp = fcmrv_helper(remaining)
					if tmp:
						return True
					setMRVback(remaining, removed_list, i)
				self.setCell(lowest[0], lowest[1], 0, self.guiUpdateEnabled)
			remaining[lowest] = lowest_val
			return False

		mrv_dict = setUpMRV()
		self.setNodes(0)
		self.setAlgTime(0)
		start = timeit.default_timer()
		fcmrv_helper(mrv_dict)
		end = timeit.default_timer()
		self.setAlgTime(end-start)
		self.setNodes(self.nodesExpanded)

	def __str__(self):
		s = 'Sudoku grid:\n'
		s+= "-------------------------------------\n"
		for row in self.grid:
			s+= '| '+' | '.join(map(str, row))+' |\n'
			s+= "-------------------------------------\n"
		return s

if __name__ == "__main__":
	puzzle = Puzzle()
	app = simpleapp_tk(None, puzzle)
	app.title('Sudoku')
	app.mainloop()
