# ==============================CS-199==================================
# FILE:			MyAI.py
#
# AUTHOR: 		Justin Chung
#
# DESCRIPTION:	This file contains the MyAI class. You will implement your
#				agent in this file. You will write the 'getAction' function,
#				the constructor, and any additional helper functions.
#
# NOTES: 		- MyAI inherits from the abstract AI class in AI.py.
#
#				- DO NOT MAKE CHANGES TO THIS FILE.
# ==============================CS-199==================================

from AI import AI
from Action import Action


class MyAI( AI ):

	class Tile():
		coords = tuple()
		covered = True
		flag = False
		num = -1
	
		def __init__(self, x, y):
			self.coords = (x,y)

	class VTile(Tile):
		def __init__(self, x, y):
			self.coords = (x,y)
			self.vValue = -1
			self.vNeighbors = []

	class CTile(Tile):
		def __init__(self, x, y, n):
			self.coords = (x,y)
			self.cNeighbors = []
			self.num = n


	def __init__(self, rowDimension, colDimension, totalMines, startX, startY):

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		self.rowDimension = rowDimension
		self.colDimension = colDimension
		self.totalMines = totalMines
		self.board = [[self.Tile(j,i) for i in range(rowDimension)] for j in range(colDimension)]
		self.board[startX][startY].covered = False
		self.board[startX][startY].num = 0
		self.parentTile = (startX, startY)
		self.childTile = None
		self.actionsLeft = rowDimension * colDimension
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

	# debugging
	def printTileInfo(self, c: int, r: int):
		if not self.board[c][r].covered:
			print(str(self.board[c][r].num) + ' ', end=" ")
		elif self.board[c][r].flag:
			print('? ', end=" ")
		elif self.board[c][r].covered:
			print('. ', end=" ")

	def printBoard(self):
		board_as_string = ""
		print("", end=" ")
		for r in range(self.rowDimension - 1, -1, -1):
			print(str(r+1).ljust(2) + '|', end=" ")
			for c in range(self.colDimension):
				self.printTileInfo(c, r)
			if (r != 0):
				print('\n', end=" ")
		
		column_label = "     "
		column_border = "   "
		for c in range(1, self.colDimension+1):
			column_border += "---"
			column_label += str(c).ljust(3)
		print(board_as_string)
		print(column_border)
		print(column_label)

	# get covered and unmarked neighbor count
	def getCUN(self, x: int, y: int):
		count = 0
		for i in [-1,0,1]:
			for j in [-1,0,1]:
				if x + i >= 0 and x + i < self.colDimension and y + j >= 0 and y + j < self.rowDimension and not (i == 0 and j == 0):
					tile = self.board[x + i][y + j]
					if tile.covered and not tile.flag:
						count += 1
		return count
	
	# get covered and marked neighbor count
	def getCMN(self, x: int, y: int):
		count = 0
		for i in [-1,0,1]:
			for j in [-1,0,1]:
				if x + i >= 0 and x + i < self.colDimension and y + j >= 0 and y + j < self.rowDimension and not (i == 0 and j == 0):
					tile = self.board[x + i][y + j]
					if tile.covered and tile.flag:
						count += 1
		return count
	
	def getUN(self, x: int, y: int):
		count = 0
		for i in [-1,0,1]:
			for j in [-1,0,1]:
				if x + i >= 0 and x + i < self.colDimension and y + j >= 0 and y + j < self.rowDimension and not (i == 0 and j == 0):
					tile = self.board[x + i][y + j]
					if not tile.covered:
						count += 1
		return count
	
	# choose valid neighbor and return coords
	def chooseVN(self, x: int, y: int):
		for i in [-1,0,1]:
			for j in [-1,0,1]:
				if x + i >= 0 and x + i < self.colDimension and y + j >= 0 and y + j < self.rowDimension and not (i == 0 and j == 0):
					tile = self.board[x + i][y + j]
					if tile.covered and not tile.flag:
						return (x+i, y+j)
					
	# loop through board and return new parent and child
	def newPandC(self):
		for i in range(self.colDimension):
			for j in range(self.rowDimension):
				number = self.board[i][j].num
				cun = self.getCUN(i,j)
				cmn = self.getCMN(i,j)
				if cun > 0 and (number == 0 or number == cmn):
					return (i, j), self.chooseVN(i, j), False
				elif number > 0 and number == cun + cmn and not number == cmn:
					return (i, j), self.chooseVN(i, j), True
		return None, None, None
	
	# loop through board and guess new parent and child based on probability
	def guessNewPandC(self):
		parent, child = None, None
		for i in range(self.colDimension):
			for j in range(self.rowDimension):
				number = self.board[i][j].num
				cun = self.getCUN(i,j)
				cmn = self.getCMN(i,j)
				if (self.board[i][j].covered == False and cun > 0):
					bombProb = (number - cmn) / cun
					if parent != None:
						parentNumber = self.board[parent[0]][parent[1]].num
						parentCUN = self.getCUN(parent[0], parent[1])
						parentCMN = self.getCMN(parent[0], parent[1])
						parentBombProb = (parentNumber - parentCMN) / parentCUN
					if parent == None or bombProb < parentBombProb:
						parent = (i,j)
						child = self.chooseVN(i,j)
		return parent, child
	
	# loop through board and initialize frontier lists
	def updateFrontier(self, frontierC: list, frontierV: list):
		for i in range(self.colDimension):
			for j in range(self.rowDimension):
				if not self.board[i][j].covered and self.getCUN(i,j) > 0:
					n = self.board[i][j].num
					frontierC.append(self.CTile(i,j, n))
				elif self.board[i][j].covered and not self.board[i][j].flag and self.getUN(i,j) > 0:
					frontierV.append(self.VTile(i,j))


	def checkVarAssignment(self, vtile: VTile):
		# self.printBoard()
		for c in vtile.vNeighbors:
			u = 0
			mines = 0
			for v in c.cNeighbors:
				if v.vValue == -1:
					u += 1
				elif v.vValue == 1:
					mines += 1
			el = c.num - self.getCMN(c.coords[0], c.coords[1])
			# print(c.coords, el)
			# print(el, mines, u, c.coords)
			if (mines > (c.num - self.getCMN(c.coords[0], c.coords[1]))) or ((c.num - self.getCMN(c.coords[0], c.coords[1])) > (mines + u)):
				return False
		return True


	def getAction(self, number: int) -> "Action Object":

		########################################################################
		#							YOUR CODE BEGINS						   #
		########################################################################
		#self.printBoard()

		if (self.actionsLeft == 1):
			return Action(AI.Action.LEAVE)
		self.actionsLeft -= 1

		try:
			px, py = self.parentTile[0], self.parentTile[1]
		except:
			return Action(AI.Action.LEAVE)
		pnum = self.board[px][py].num
		cun = self.getCUN(px,py)
		cmn = self.getCMN(px,py)

		if (self.childTile != None):
			self.board[self.childTile[0]][self.childTile[1]].num = number

		if cun == 0 or (pnum != cmn and pnum != cun + cmn):
			self.parentTile, self.childTile, flag = self.newPandC()
			if flag == None:	# ambiguous case
				frontierC = []
				frontierV = []
				self.updateFrontier(frontierC, frontierV)
				for v in frontierV:
					for c in frontierC:
						if c.coords[0] in range(v.coords[0]-1, v.coords[0]+2) and c.coords[1] in range(v.coords[1]-1, v.coords[1]+2):
							v.vNeighbors.append(c)
							c.cNeighbors.append(v)

				solutions = []
				poppedFrontierV = []
				# print("model checking")
				while True:
					# print([x.vValue for x in frontierV], [x.vValue for x in poppedFrontierV])
					if len(frontierV) == 0:
						solution = [v.vValue for v in reversed(poppedFrontierV)]
						solutions.append(solution)
						# print("SOLUTION", solution)
						# for i in range(0, len(solutions)):
						# 	solutions[i] += solution[i]
						frontierV.append(poppedFrontierV.pop())						
					
					getOut = False
					vtile = frontierV[-1]
					if vtile.vValue == 1:
						while vtile.vValue == 1:
							vtile.vValue = -1
							if len(poppedFrontierV) == 0:
								getOut = True
								break
							frontierV.append(poppedFrontierV.pop())
							vtile = frontierV[-1]
					else:
						vtile.vValue += 1
						if self.checkVarAssignment(vtile):
							poppedV = frontierV.pop()
							poppedFrontierV.append(poppedV)

					if getOut:
						break

				final = [0 for x in solutions[0]]
				for inner in solutions:
					for i in range(0, len(inner)):
						final[i] += inner[i]

				tile = frontierV[final.index(min(final))]
				self.parentTile = tile.vNeighbors[0].coords
				self.childTile = tile.coords
				self.board[self.childTile[0]][self.childTile[1]].covered = False
		
				return Action(AI.Action.UNCOVER, self.childTile[0], self.childTile[1])
				
				# self.parentTile, self.childTile = self.guessNewPandC()
				# if self.parentTile == None:		# game is done, no more tiles left to uncover
				# 	return Action(AI.Action.LEAVE)
				# self.board[self.childTile[0]][self.childTile[1]].covered = False
				# return Action(AI.Action.UNCOVER, self.childTile[0], self.childTile[1])
			if flag: 
				self.board[self.childTile[0]][self.childTile[1]].flag = True 
				return Action(AI.Action.FLAG, self.childTile[0], self.childTile[1])
			else: 
				self.board[self.childTile[0]][self.childTile[1]].covered = False
				return Action(AI.Action.UNCOVER, self.childTile[0], self.childTile[1])

		if pnum == 0 or pnum == cmn:
			self.childTile = self.chooseVN(px,py)
			self.board[self.childTile[0]][self.childTile[1]].covered = False
			return Action(AI.Action.UNCOVER, self.childTile[0], self.childTile[1])
		
		if pnum == cun + cmn:
			self.childTile = self.chooseVN(px,py)
			self.board[self.childTile[0]][self.childTile[1]].flag = True
			return Action(AI.Action.FLAG, self.childTile[0], self.childTile[1])
		
		return Action(AI.Action.LEAVE)
		########################################################################
		#							YOUR CODE ENDS							   #
		########################################################################

		# module load python/3.5.2
		# python3 Minesweeper_Python/bin/Main.pyc -f WorldGenerator/Problems/
