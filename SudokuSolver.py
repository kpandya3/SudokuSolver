#!/usr/bin/python

import Tkinter
from Tkinter import *
from tkFileDialog import askopenfilename
from copy import deepcopy

class simpleapp_tk(Tkinter.Tk):
	def __init__(self,parent, puzzle):
		Tkinter.Tk.__init__(self,parent)
		self.parent = parent
		self.puzzle = puzzle
		self.puzzle.setGUI(self)
		self.algs = { 'BF': self.puzzle.BF, 'BT': self.puzzle.BT, 'FC-MRV': self.puzzle.FCMRV}
		self.initialize()

	def initList(self):
		self.list = [[],[],[],[],[],[],[],[],[]]
		for i in range(9):
			for j in range(9):
				self.list[i].append(StringVar())
				self.list[i][j].set(0)

	def initialize(self):
		self.grid()
		self.initList()

		listRange = [0,1,2,4,5,6,8,9,10]
		for i in range(9):
			for j in range(9):
				l = Tkinter.Label(self,textvariable=self.list[i][j], anchor="center", fg="white", bg="blue", width=5, height=2, relief=GROOVE)
				l.grid(column=listRange[j],row=listRange[i],columnspan=1,sticky='EW')

		img = "R0lGODlhAQABAIAAAP///////yH5BAEKAAEALAAAAAABAAEAAAICTAEAOw=="
		img = PhotoImage(data=img)
		for i in [3,7]:
			l = Tkinter.Label(self, bd=0, width=0, height=1)
			l.grid(column=i,row=1,columnspan=1,sticky='EW')
			l = Tkinter.Label(self, image=img,bd=0, width=0, height=2)
			l.grid(column=1,row=i,columnspan=1,sticky='NS')

		self.fileName = StringVar()
		browseLabel = Tkinter.Label(self, textvariable=self.fileName, bd=0, width=0, height=1, padx=10, pady=10)
		browseLabel.grid(column=11,row=1,columnspan=2,sticky='EW')
		self.fileName.set("Select File")

		bBrowse = Button(self, text="Select", command=self.loadFile)
		bBrowse.grid(column=11,row=2,columnspan=2 ,sticky='EW')

		self.alg = StringVar(self)
		optM = OptionMenu(self, self.alg, "BF", "BT", "FC-MRV")
		optM.grid(column=11,row=5,columnspan=2 ,sticky='EW')

		bRun = Button(self, text="Run", command=self.run)
		bRun.grid(column=11,row=6,columnspan=2 ,sticky='EW')

		self.resizable(True,False)
		self.update()
		self.geometry(self.geometry())

	def setCell(self, x, y, val):
		self.list[x][y].set(val)

	def loadFile(self):
		fname = askopenfilename(parent=self)
		self.fileName.set(fname.split('/')[-1])
		f = open(fname, "r")
		lines = []
		for line in f:
			lines.append(map(int, line.strip().split(' ')))
		f.close()
		self.puzzle.load(lines)

	def run(self):
		self.algs[self.alg.get()]()

class Puzzle:
	"""docstring for Puzzle"""
	def __init__(self):
		self.initgrid = None
		self.grid = None

	def resetPuzzle(self):
		for i in range(9):
			for j in range(9):
				self.grid[i][j] = self.initgrid[i][j]
				self.gui.setCell(i,j,self.initgrid[i][j])
		self.update_gui()

	def setGUI(self, gui):
		self.gui = gui

	def setCell(self, x, y, val):
		self.grid[x][y] = val
		self.gui.setCell(x,y,val)
		self.update_gui()

	def update_gui(self):
		self.gui.update_idletasks()

	def load(self, data):
		self.initgrid = deepcopy(data)
		self.grid = data
		for i in range(9):
			for j in range(9):
				self.setCell(i,j, self.grid[i][j])

	def isFull(self):
		for item in self.grid:
			if 0 in item:
				return False
		return True

	def isSolved(self):
		for i in self.grid:
			if len(i) > len(set(i)) and 0 not in i:
				return False
		for i in zip(*self.grid):
			if len(i) > len(set(i)) and 0 not in i:
				return False
		for i in [1, 4, 7]:
			for j in [1, 4, 7]:
				tmp =   [ self.grid[i-1][j-1], self.grid[i][j-1], self.grid[i+1][j-1],
						  self.grid[i-1][j],  self.grid[i][j],  self.grid[i+1][j],
						  self.grid[i-1][j+1], self.grid[i][j+1], self.grid[i+1][j+1]]
				if len(tmp) > len(set(tmp)) and 0 not in tmp:
					return False
		return True

	def BF(self):
		remaining_list = []
		for i in range(9):
			for j in range(9):
				if self.grid[i][j] == 0:
					remaining_list.append((i, j))

		def bf_helper(remaining_list):
			if not remaining_list:
				if self.isSolved():
					return True
				else:
					return False
			for i in range(1, 10):
				self.setCell(remaining_list[0][0], remaining_list[0][1], i)
				tmp = bf_helper(remaining_list[1:])
				if tmp:
					return True
				self.setCell(remaining_list[0][0], remaining_list[0][1], 0)
			return False

		bf_helper(remaining_list)

	def BT(self):
		self.resetPuzzle()
		remaining_list = []
		for i in range(9):
			for j in range(9):
				if self.grid[i][j] == 0:
					remaining_list.append((i, j))

		def isValidMove(coord, val):
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

		def bt_helper(remaining_list):
			if not remaining_list:
				return True
			for i in range(1, 10):
				if isValidMove(remaining_list[0], i):
					self.setCell(remaining_list[0][0], remaining_list[0][1], i)
					tmp = bt_helper(remaining_list[1:])
					if tmp:
						return True
					self.setCell(remaining_list[0][0], remaining_list[0][1], 0)
			return False

		bt_helper(remaining_list)

	def FCMRV(self):
		self.resetPuzzle()
		pass

if __name__ == "__main__":
	puzzle = Puzzle()
	app = simpleapp_tk(None, puzzle)
	app.title('Sudoku')
	app.mainloop()
