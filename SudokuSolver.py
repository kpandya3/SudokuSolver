#!/usr/bin/python
import sys
import Tkinter
import timeit
from Tkinter import *
from tkFileDialog import askopenfilename
from copy import deepcopy

class PuzzleGUI(Tkinter.Tk):
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
			self.puzzle.setGUIUpdatable(True)
		# Else we tell puzzle not to update gui at each cycle
		else:
			self.puzzle.setGUIUpdatable(False)

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
		self.puzzle.setPuzzle(self.puzzle.grid)

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
		self.algRuntime = 0
		self.commandLine = False

	def run(self, alg):
		"""
		Run the given algorithm alg on the puzzle
		"""
		# Get the function to run for the given algorithm alg (string) and run that function
		self.algs[alg]()

	def setGUIUpdatable(self, checked):
		"""
		Set if the puzzle should update the GUI at each cycle or not
		"""
		self.guiUpdateEnabled = checked

	def setCommandLineInstance(self, checked):
		"""
		Set if the this is command line version of the puzzle or not
		"""
		self.commandLine = checked

	def setNodes(self, nodes):
		"""
		Set the total nodes expanded for the puzzle and on the gui
		"""
		self.nodesExpanded = nodes
		# Call gui's setNodes method to set nodes on gui
		if not self.commandLine:
			self.gui.setNodes(nodes)
			self.update_gui()

	def setAlgTime(self, algTime):
		"""
		Set algorithm runtime to algTime
		"""
		self.algRuntime = algTime*1000
		# Update gui with the algorithm runtime
		if not self.commandLine:
			self.gui.setAlgTime(algTime*1000)
			self.update_gui()

	def setPuzzle(self, puzzle_grid):
		"""
		set the puzzle to it's given state
		"""
		for i in range(9):
			for j in range(9):
				# Go through each x-y values on 9x9 grid
				# And set all of them to given state
				self.grid[i][j] = puzzle_grid[i][j]
				if not self.commandLine:
					self.gui.setCell(i,j,puzzle_grid[i][j])
		if not self.commandLine:
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
		if updateGUI and not self.commandLine:
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

		# Find the center of the block the coordinate is on
		center = [coord[0], coord[1]]
		for i in range(2):
			# We can find out if coordinate is on left or right/top or bottom side of the center
			if (coord[i]+1)%3 == 1:
				center[i]+=1
			elif (coord[i]+1)%3 == 0:
				center[i]-=1
		# Create list of values in the block
		blockList = [ self.grid[center[0]-1][center[1]-1], self.grid[center[0]][center[1]-1], self.grid[center[0]+1][center[1]-1]
					, self.grid[center[0]-1][center[1]],  self.grid[center[0]][center[1]],  self.grid[center[0]+1][center[1]]
					, self.grid[center[0]-1][center[1]+1], self.grid[center[0]][center[1]+1], self.grid[center[0]+1][center[1]+1]]
		# Make sure values arent in the block
		if val in blockList:
			return False
		return True

	def getEmptyCells(self):
		"""
		Returns list of x,y coordinate tuples that are empty
		"""
		remaining_list = []
		for i in xrange(9):
			for j in xrange(9):
				# The cell is empty if its value is 0
				if self.grid[i][j] == 0:
					remaining_list.append((i, j))
		return remaining_list

	def BF(self):
		"""
		Bruteforce algorithm
		"""
		self.setPuzzle(self.initgrid)

		self.setNodes(0)
		self.setAlgTime(0)

		def bf_helper(remaining_list):
			"""
			Recursive function to Find the solution by Bruteforce
			"""
			# If no empty cells remain, the puzzle is Full
			if not remaining_list:
				# If the puzzle is solved, we return True; else False
				if self.isSolved():
					return True
				else:
					return False
			# We try all values from 1 to 9 on the first cell of remaining_list
			for i in xrange(1, 10):
				# Set the first cell to i
				self.setCell(remaining_list[0][0], remaining_list[0][1], i, self.guiUpdateEnabled)
				# Try runnning the algorithm recursively on rest of the cells
				tmp = bf_helper(remaining_list[1:])
				# If it succeeds, we return true
				if tmp:
					return True
				# Else we set the value back to 0 and visit next node
				self.setCell(remaining_list[0][0], remaining_list[0][1], 0, self.guiUpdateEnabled)
			return False

		start = timeit.default_timer()

		# Setup empty cells and call recursive algorithm
		remaining_list = self.getEmptyCells()
		bf_helper(remaining_list)

		end = timeit.default_timer()

		# Set total nodecount and runtime
		self.setAlgTime(end-start)
		self.setNodes(self.nodesExpanded)

	def BT(self):
		"""
		Backtracking algorithm
		"""
		self.setPuzzle(self.initgrid)

		def bt_helper(remaining_list):
			"""
			Backtracking recursive algorithm to find solution
			"""
			# If no nodes remaining, the puzzle is full
			if not remaining_list:
				return True
			# Try all values from 1 to 9 on first cell of remaining_list
			for i in xrange(1, 10):
				# Set the cell to i
				self.setCell(remaining_list[0][0], remaining_list[0][1], i, self.guiUpdateEnabled)
				# We set grid to 0 temporarily
				# We do this so isValidMove function runs faster since it wont have to ignore its current location
				self.grid[remaining_list[0][0]][remaining_list[0][1]] = 0
				# Check if i is valid at the current cell
				if self.isValidMove(remaining_list[0], i):
					# If valid, we set grid to i
					self.grid[remaining_list[0][0]][remaining_list[0][1]] = i
					# Run Bruteforce recursively
					tmp = bt_helper(remaining_list[1:])
					# If this solves puzzle, return true
					if tmp:
						return True
				# If its not valid or if it doesnt solve the puzzle, we set the cell back to 0
				self.setCell(remaining_list[0][0], remaining_list[0][1], 0, self.guiUpdateEnabled)
			return False

		self.setNodes(0)
		self.setAlgTime(0)
		start = timeit.default_timer()

		# Generate empty cells list and call recursive function
		remaining_list = self.getEmptyCells()
		bt_helper(remaining_list)

		end = timeit.default_timer()
		
		# Set total nodes and runtime
		self.setAlgTime(end-start)
		self.setNodes(self.nodesExpanded)

	def FCMRV(self):
		"""
		Forward Checking algorithm with Minimum Remaining Value Heuristics
		"""
		self.setPuzzle(self.initgrid)

		def setupMRV():
			"""
			Initial setup of MRV
			"""
			remaining = {}
			# Go through each cell in grid
			for i in xrange(9):
				for j in xrange(9):
					# If the cell is empty, we need to add it to dict
					if self.grid[i][j] == 0:
						center = [i, j]
						for k in range(2):
							if (center[k]+1)%3 == 1:
								center[k]+=1
							elif (center[k]+1)%3 == 0:
								center[k]-=1
						# We find all valid values for the cell and add them to dictionary for heuristics
						# We also add center to improve speed (we wont need to manually check for the block this belongs to)
						remaining[(i, j)] = [[k for k in xrange(1,10) if self.isValidMove((i, j), k)], center]
			return remaining

		def getLowestMRV(mrv):
			"""
			Return lowest MRV value in the dictionary
			"""
			return min(mrv, key=lambda item: len(mrv.get(item)[0])) if len(mrv) > 0 else False

		def useMRV(remaining, key, val, i):
			"""
			Removes i from heuristics of cells that are in same rows, columns and blocks
			"""
			removed_list = []
			# Go over all collected heuristics
			for ik, iv in remaining.iteritems():
				# See if the cell is in the same row, column or block of the current cell
				if ik[0]==key[0] or ik[1]==key[1] or val[1] == iv[1]:
					if i in iv[0]:
						# remove i from the list of possible values
						iv[0].remove(i)
						removed_list.append(ik)
						# We check if the possible values at ik are empty after removing val
						if not iv[0]:
							# If so, we cannot use this val for the current cell
							# We put back all removed values and return false
							setMRVback(remaining, removed_list, i)
							return False
			return removed_list

		def setMRVback(mrv, removed_list, i):
			"""
			Puts back all removed values back into the heuristics
			"""
			for item in removed_list:
				mrv.get(item)[0].append(i)

		def fcmrv_helper(remaining):
			"""
			Recursive function that uses FC with MRV to find a solution
			"""
			# Get the cell with minimum remaining value
			lowest = getLowestMRV(remaining)
			# if we could not find lowest, we have used up all values and found a solution
			if not lowest:
				return True
			# Get the value at cell, which has list of list of possible values and center coordinates and remove the pair
			lowest_val = remaining.pop(lowest, None)
			# Try all possible values from the list
			for i in lowest_val[0]:
				# Set cell to i
				self.setCell(lowest[0], lowest[1], i, self.guiUpdateEnabled)
				# call useMRV to remove i from its row,column and block
				removed_list = useMRV(remaining, lowest, lowest_val, i)
				# If there was no domain wipeout, move ahead
				if removed_list is not False:
					# Try recursively on rest of remaining values, if it returns solution, return true
					if fcmrv_helper(remaining):
						return True
					# If it doesnt work, we put all removed values back
					setMRVback(remaining, removed_list, i)
				# If i is no good for current cell, we set the cell back to 0
				self.setCell(lowest[0], lowest[1], 0, self.guiUpdateEnabled)
			remaining[lowest] = lowest_val
			return False

		self.setNodes(0)
		self.setAlgTime(0)
		start = timeit.default_timer()

		# Set up MRV heuristic
		mrv_heuristics = setupMRV()
		fcmrv_helper(mrv_heuristics)

		end = timeit.default_timer()
		
		# Set node count and runtime
		self.setAlgTime(end-start)
		self.setNodes(self.nodesExpanded)

	def __str__(self):
		"""
		Return string with all rows in the Puzzle
		"""
		s = 'Sudoku grid:\n'
		s+= "-------------------------------------\n"
		for row in self.grid:
			s+= '| '+' | '.join(map(str, row))+' |\n'
			s+= "-------------------------------------\n"
		return s

class PuzzleCommandLine(object):
	"""Run puzzle from command line"""

	def __init__(self, puzzle):
		"""
		Init class
		"""
		# Set puzzle to play with
		self.puzzle = puzzle

	def load(self, fname):
		"""
		Loads file into the puzzle
		"""
		# Open the file
		f = open(fname, "r")
		# Put all contents of the file in lines variable
		lines = [map(int, line.strip().split(' ')) for line in f]			
		f.close()
		# Tell puzzle to load the lines found in the file
		self.puzzle.load(lines)

	def run(self, fname, alg):
		"""
		Runs given algorithm alg on file fname
		"""
		# Note: Total time also includes file read time
		self.time = 0
		start = timeit.default_timer()

		# Load the file and run algorithm alg on it
		self.load(fname)
		self.puzzle.run(alg)

		end = timeit.default_timer()
		# Set total runtime
		self.time = (end-start)*1000

	def save(self, fin):
		"""
		Saves the solution and performance of the given puzzle
		"""
		with open(fin.replace("puzzle","solution"), 'w') as fout:
			for row in self.puzzle.grid:
				fout.write(' '.join(map(str, row))+'\n')
		with open(fin.replace("puzzle","performance"), 'w') as fout:
			s = "Total clock time: "+str(self.time)
			s+= "\nSearch clock time: "+str(self.puzzle.algRuntime)
			s+= "\nNumber of nodes generated: "+str(self.puzzle.nodesExpanded)
			fout.write(s)

	def __str__(self):
		"""
		Returns string with puzzle, total time, search time and total nodes
		>>> Total clock time: 1000.00
		    Search clock time: 800.00
		    Number of nodes generated: 500
		"""
		s = str(puzzle)
		s+= "\nTotal clock time: "+str(self.time)
		s+= "\nSearch clock time: "+str(self.puzzle.algRuntime)
		s+= "\nNumber of nodes generated: "+str(self.puzzle.nodesExpanded)
		return s

if __name__ == "__main__":
	puzzle = Puzzle()

	# Check if to use GUI or command line
	if len(sys.argv) == 1:
		app = PuzzleGUI(None, puzzle)
		app.title('Sudoku')
		app.mainloop()
	else:
		# Make sure gui updates are off for puzzle
		puzzle.setGUIUpdatable(False)
		puzzle.setCommandLineInstance(True)

		# Create class to run puzzle without gui
		pi = PuzzleCommandLine(puzzle)
		# Run it on given file and algorithm
		pi.run(sys.argv[1], sys.argv[2])
		# Print out the result
		print pi
		# Save results to files
		pi.save(sys.argv[1])
