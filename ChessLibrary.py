import json

"""
Functions
"""


class functions:
	@staticmethod
	def indexToCoordinate(index):
		"""Return a board coordinate (e.g. e4) from index (e.g. [4, 4])"""
		return ("a", "b", "c", "d", "e", "f", "g", "h")[index[1]] + str(abs(index[0] - 8))

	@staticmethod
	def coordinateToIndex(coordinate):
		"""Return a raw index (e.g [4, 4]) from board coordinate (e.g. e4)"""
		return [abs(int(coordinate[1]) - 8), ("a", "b", "c", "d", "e", "f", "g", "h").index(coordinate[0])]

	@staticmethod
	def coordinateValid(coordinate):
		"""Returns if the coordinate is valid (e.g. e4 -> True, 4e -> False)"""
		return coordinate[0] in ["a", "b", "c", "d", "e", "f", "g", "h"] and coordinate[1] in ["1", "2", "3", "4", "5", "6", "7", "8"]

	@staticmethod
	def toSAN(move, game):
		"""Return the move in standard algebraic notation (e.g. e2e4 -> e4, g1f3 -> Nf3, e4 -> e4)"""
		extra_characters = ""  # Stores extra characters (e.g +, #, =Q, =Q+...)
		if move.endswith("+"):  # If a "+" is found
			extra_characters = "+"
			move = move[:-1]
		if move.endswith("#"):  # If a "#" is found
			extra_characters = "#"
			move = move[:-1]
		if len(move) > 1:  # Check for "=N/B/R/Q"
			if move[-2] == "=" and move[-1] in ["N", "B", "R", "Q"]:
				extra_characters = move[-2:] + extra_characters
				move = move[:-2]
		if len(move) == 5:
			# Remove the hyphen if one is present (e2-e4 -> e2e4)
			if move[2] == "-":
				move = move[:2] + move[3:]
			# Check if the move is a capture (e.g. e4xd5)
			# If the middle character (move[2]) is "x", and the first two (move[:2]) and last two (move[3:])
			# characters are coordinates
			if move[2] == "x" and coordinateValid(move[:2].lower()) and coordinateValid(move[3:].lower()):
				if game.pieceAt(move[:2].lower()) is None:  # If the piece is not found, return move
					return move + extra_characters
				if game.pieceAt(move[:2].lower()).piece_type[0] == "pawn":  # If the piece is a pawn
					return move[0] + "x" + move[3:] + extra_characters
				else:
					return {"knight": "N", "bishop": "B", "rook": "R", "queen": "Q", "king": "K"}[game.pieceAt(move[:2].lower()).piece_type[0]] + "x" + move[3:] + extra_characters
		if len(move) == 4:  # Check if the move is not a capture (e.g. e2e4)
			# If the first two (move[:2]) and last two (move[2:]) characters are coordinates
			if coordinateValid(move[:2].lower()) and coordinateValid(move[2:].lower()):
				if game.pieceAt(move[:2].lower()) is None:  # If the piece is not found, return move
					return move + extra_characters
				if game.pieceAt(move[:2].lower()).piece_type[0] == "pawn":  # If the piece is a pawn
					return move[2:] + extra_characters
				else:  # Otherwise
					return {"knight": "N", "bishop": "B", "rook": "R", "queen": "Q", "king": "K"}[game.pieceAt(move[:2].lower()).piece_type[0]] + move[2:] + extra_characters
	
		return move + extra_characters


"""
Error Classes
"""


class errors:
	class MoveNotPossible(Exception):
		def __init__(self, move):
			super().__init__("Move '" + str(move) + "' is not possible")

	class InvalidMove(Exception):
		def __init__(self, move):
			super().__init__("Move '" + str(move) + "' is invalid")

	class UndefinedColor(Exception):
		def __init__(self, color):
			if color.lower() == "w":
				super().__init__("Color 'w' is invalid. Maybe you meant 'white'?")
			elif color.lower() == "b":
				super().__init__("Color 'b' is invalid. Maybe you meant 'black'?")
			else:
				super().__init__("Color '" + str(color) + "' is invalid")

	class UndefinedPiece(Exception):
		def __init__(self, piece):
			super().__init__("Piece '" + str(piece) + "' is invalid")


"""
Type Enumerations
"""


class enums:
	class Color:
		white, black = "white", "black"
	
		@staticmethod
		def invert(color):
			if color in ["white", "w"]:
				return "black"
			elif color in ["black", "b"]:
				return "white"
			else:
				raise errors.UndefinedColor(color)
			
	class Piece:
		pawn, knight, bishop, rook = "pawn", "knight", "bishop", "rook"
		queen, king = "queen", "king"
		unicode_dictionary = {"whiteking": "♔", "blackking": "♚", "whitequeen": "♕", "blackqueen": "♛", "whiterook": "♖", "blackrook": "♜", "whitebishop": "♗", "blackbishop": "♝", "whiteknight": "♘", "blackknight": "♞", "whitepawn": "♙", "blackpawn": "♟"}
		
		@staticmethod
		def unicode(piece, color="white"):
			if piece not in ["pawn", "knight", "bishop", "rook", "queen", "king"]:
				raise errors.UndefinedPiece(piece)
			if color not in ["white", "black"]:
				raise errors.UndefinedColor(color)
			return {"whiteking": "♔", "blackking": "♚", "whitequeen": "♕", "blackqueen": "♛", "whiterook": "♖", "blackrook": "♜", "whitebishop": "♗", "blackbishop": "♝", "whiteknight": "♘", "blackknight": "♞", "whitepawn": "♙", "blackpawn": "♟"}[color + piece]
		
		@staticmethod
		def value(piece):
			if piece in ["pawn", "knight", "bishop", "rook", "queen", "king"]:
				return {"pawn": 1, "knight": 3, "bishop": 3, "rook": 5, "queen": 9, "king": float("inf")}[piece]
			raise errors.UndefinedPiece(piece)
	
	class Move:
		def __init__(self, name, old_position, new_position, piece, is_capture=False):
			self.piece = piece
			self.name = name
			self.old_position, self.new_position = old_position, new_position
			self.is_capture = is_capture
			if is_capture:
				self.captured_piece = self.piece.board.pieceAt(new_position)
			else:
				self.captured_piece = None


"""Main Script"""


class Square:
	def __init__(self, position, board):
		self.position = functions.indexToCoordinate(position)
		self.board = board
		if ((position[0] + position[1]) & 1) == 0:
			self.color = enums.Color.white
		else:
			self.color = enums.Color.black

	def __str__(self):
		return self.color.title() + " square from " + str(self.board)

	def __repr__(self):
		return self.color.title() + " square from " + str(self.board)

	def __lt__(self, other):
		raise ArithmeticError("Cannot compare squares")

	def __add__(self, _):
		raise ArithmeticError("Cannot add pieces")

	def __sub__(self, _):
		raise ArithmeticError("Cannot subtract pieces")

	def __mul__(self, _):
		raise ArithmeticError("Cannot multiply pieces")

	def __mod__(self, _):
		raise ArithmeticError("Cannot modulo pieces")

	def __floordiv__(self, _):
		raise ArithmeticError("Cannot divide pieces")

	def __divmod__(self, _):
		raise ArithmeticError("Cannot divide pieces")

	def __truediv__(self, _):
		raise ArithmeticError("Cannot divide pieces")

	def __floor__(self):
		raise ArithmeticError("Cannot floor")


class Piece:
	def __init__(self, position, piece_type, color, board):
		self.position = functions.indexToCoordinate(position)
		self.piece_type, self.color, self.board = piece_type, color, board

	def moves(self, show_data=False):
		moves = []
		if self.piece_type == enums.Piece.pawn:  # Pawn moves
			# Straight pawn moves
			# # Check if pawn is blocked
			for i in self.board.pieces:
				if functions.coordinateToIndex(i.position) == [functions.coordinateToIndex(self.position)[0] - (1 if self.color == enums.Color.white else -1), functions.coordinateToIndex(self.position)[1]]:
					break
			else:  # If pawn is not blocked
				if show_data:
					moves.append(enums.Move(name=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - (1 if self.color == enums.Color.white else -1), functions.coordinateToIndex(self.position)[1]]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - (1 if self.color == enums.Color.white else -1), functions.coordinateToIndex(self.position)[1]]), piece=self))  # Append single pawn move
				else:
					moves.append(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - (1 if self.color == enums.Color.white else -1), functions.coordinateToIndex(self.position)[1]]))  # Append single pawn move
				# Check if pawn is on home rank
				if (int(self.position[1]) == 2 and self.color == enums.Color.white) or (int(self.position[1]) == 7 and self.color == enums.Color.black):
					# Check if pawn double move is blocked
					for i in self.board.pieces:
						if functions.coordinateToIndex(i.position) == [functions.coordinateToIndex(self.position)[0] - (2 if self.color == enums.Color.white else -2), functions.coordinateToIndex(self.position)[1]]:
							break
					else:  # If pawn double move is not blocked
						if show_data:
							moves.append(enums.Move(name=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - (2 if self.color == enums.Color.white else -2), functions.coordinateToIndex(self.position)[1]]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - (2 if self.color == enums.Color.white else -2), functions.coordinateToIndex(self.position)[1]]), piece=self))  # Append double pawn move
						else:
							moves.append(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - (2 if self.color == enums.Color.white else -2), functions.coordinateToIndex(self.position)[1]]))  # Append double pawn move
			# Pawn captures
			capture_found = False  # Set default value of the capture_found variable
			if self.color == enums.Color.white:  # For white pawns
				# Check for left diagonal captures (e.g. e4xd5)
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [i - 1 for i in functions.coordinateToIndex(self.position)] and i.color == enums.Color.black:
						capture_found = True  # Make capture_found True
						break
				if capture_found:  # If capture is found
					if show_data:
						moves.append(enums.Move(name=functions.indexToCoordinate(functions.coordinateToIndex(self.position))[0] + "x" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] - 1]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] - 1]), piece=self, is_capture=True))  # Append pawn capture move
					else:
						moves.append(functions.indexToCoordinate(functions.coordinateToIndex(self.position))[0] + "x" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] - 1]))  # Append pawn capture move
				capture_found = False  # Reset capture_found variable
				# Check for right diagonal captures (e.g. e4xf5)
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 1] and i.color == enums.Color.black:
						capture_found = True  # Make capture_found True
						break
				if capture_found:
					if show_data:
						moves.append(enums.Move(name=functions.indexToCoordinate(functions.coordinateToIndex(self.position))[0] + "x" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 1]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 1]), piece=self, is_capture=True))  # Append pawn capture move
					else:
						moves.append(functions.indexToCoordinate(functions.coordinateToIndex(self.position))[0] + "x" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 1]))  # Append pawn capture move
			else:  # For black pawns
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 1] and i.color == enums.Color.white:
						capture_found = True  # Make capture_found True
						break
				if capture_found:
					if show_data:
						moves.append(enums.Move(name=functions.indexToCoordinate(functions.coordinateToIndex(self.position))[0] + "x" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 1]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 1]), piece=self, is_capture=True))  # Append pawn capture move
					else:
						moves.append(functions.indexToCoordinate(functions.coordinateToIndex(self.position))[0] + "x" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 1]))  # Append pawn capture move
				capture_found = False  # Reset capture_found variable
				# Check for right diagonal captures (e.g. exf4)
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [i + 1 for i in functions.coordinateToIndex(self.position)] and i.color == enums.Color.white:
						capture_found = True  # Make capture_found True
						break
				if capture_found:
					if show_data:
						moves.append(enums.Move(name=functions.indexToCoordinate(functions.coordinateToIndex(self.position))[0] + "x" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] + 1]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] + 1]), piece=self, is_capture=True))  # Append pawn capture move
					else:
						moves.append(functions.indexToCoordinate(functions.coordinateToIndex(self.position))[0] + "x" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] + 1]))  # Append pawn capture move
		elif self.piece_type == enums.Piece.knight:  # Knight moves
			found, valid = False, True
			if self.position[1] not in "78" and self.position[0] != "a":
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [functions.coordinateToIndex(self.position)[0] - 2, functions.coordinateToIndex(self.position)[1] - 1]:
						if i.color == self.color:
							valid = False
						found = True
				if valid:
					if show_data:
						moves.append(enums.Move(name="N" + ("x" if found else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 2, functions.coordinateToIndex(self.position)[1] - 1]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 2, functions.coordinateToIndex(self.position)[1] - 1]), piece=self, is_capture=found))
					else:
						moves.append("N" + ("x" if found else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 2, functions.coordinateToIndex(self.position)[1] - 1]))
			found, valid = False, True
			if self.position[1] not in "12" and self.position[0] != "a":
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [functions.coordinateToIndex(self.position)[0] + 2, functions.coordinateToIndex(self.position)[1] - 1]:
						if i.color == self.color:
							valid = False
						found = True
				if valid:
					if show_data:
						moves.append(enums.Move(name="N" + ("x" if found else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 2, functions.coordinateToIndex(self.position)[1] - 1]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 2, functions.coordinateToIndex(self.position)[1] - 1]), piece=self, is_capture=found))
					else:
						moves.append("N" + ("x" if found else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 2, functions.coordinateToIndex(self.position)[1] - 1]))
			found, valid = False, True
			if self.position[1] not in "78" and self.position[0] != "h":
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [functions.coordinateToIndex(self.position)[0] - 2, functions.coordinateToIndex(self.position)[1] + 1]:
						if i.color == self.color:
							valid = False
						found = True
				if valid:
					if show_data:
						moves.append(enums.Move(name="N" + ("x" if found else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 2, functions.coordinateToIndex(self.position)[1] + 1]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 2, functions.coordinateToIndex(self.position)[1] + 1]), piece=self, is_capture=found))
					else:
						moves.append("N" + ("x" if found else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 2, functions.coordinateToIndex(self.position)[1] + 1]))
			found, valid = False, True
			if self.position[1] not in "12" and self.position[0] != "h":
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [functions.coordinateToIndex(self.position)[0] + 2, functions.coordinateToIndex(self.position)[1] + 1]:
						if i.color == self.color:
							valid = False
						found = True
				if valid:
					if show_data:
						moves.append(enums.Move(name="N" + ("x" if found else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 2, functions.coordinateToIndex(self.position)[1] + 1]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 2, functions.coordinateToIndex(self.position)[1] + 1]), piece=self, is_capture=found))
					else:
						moves.append("N" + ("x" if found else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 2, functions.coordinateToIndex(self.position)[1] + 1]))
			found, valid = False, True
			if self.position[1] != "8" and self.position[0] not in "ab":
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] - 2]:
						if i.color == self.color:
							valid = False
						found = True
				if valid:
					if show_data:
						moves.append(enums.Move(name="N" + ("x" if found else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] - 2]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] - 2]), piece=self, is_capture=found))
					else:
						moves.append("N" + ("x" if found else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] - 2]))
			found, valid = False, True
			if self.position[1] != "1" and self.position[0] not in "ab":
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 2]:
						if i.color == self.color:
							valid = False
						found = True
				if valid:
					if show_data:
						moves.append(enums.Move(name="N" + ("x" if found else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 2]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 2]), piece=self, is_capture=found))
					else:
						moves.append("N" + ("x" if found else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 2]))
			found, valid = False, True
			if self.position[1] != "1" and self.position[0] not in "gh":
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] + 2]:
						if i.color == self.color:
							valid = False
						found = True
				if valid:
					if show_data:
						moves.append(enums.Move(name="N" + ("x" if found else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] + 2]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] + 2]), piece=self, is_capture=found))
					else:
						moves.append("N" + ("x" if found else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] + 2]))
			found, valid = False, True
			if self.position[1] != "8" and self.position[0] not in "gh":
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 2]:
						if i.color == self.color:
							valid = False
						found = True
				if valid:
					if show_data:
						moves.append(enums.Move(name="N" + ("x" if found else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 2]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 2]), piece=self, is_capture=found))
					else:
						moves.append("N" + ("x" if found else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 2]))
		elif self.piece_type == enums.Piece.bishop:  # Bishop moves
			capture = False
			pos1, pos2 = functions.coordinateToIndex(self.position)
			while pos1 != 0 and pos2 != 0:
				pos1, pos2 = pos1 - 1, pos2 - 1
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [pos1, pos2]:
						if i.color == self.color:
							break
						capture = True
				else:
					if show_data:
						moves.append(enums.Move(name="B" + ("x" if capture else "") + functions.indexToCoordinate([pos1, pos2]), old_position=self.position, new_position=functions.indexToCoordinate([pos1, pos2]), piece=self, is_capture=capture))
					else:
						moves.append("B" + ("x" if capture else "") + functions.indexToCoordinate([pos1, pos2]))
					if capture:
						break
					continue
				break
			capture = False
			pos1, pos2 = functions.coordinateToIndex(self.position)
			while pos1 != 7 and pos2 != 7:
				pos1, pos2 = pos1 + 1, pos2 + 1
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [pos1, pos2]:
						if i.color == self.color:
							break
						capture = True
				else:
					if show_data:
						moves.append(enums.Move(name="B" + ("x" if capture else "") + functions.indexToCoordinate([pos1, pos2]), old_position=self.position, new_position=functions.indexToCoordinate([pos1, pos2]), piece=self, is_capture=capture))
					else:
						moves.append("B" + ("x" if capture else "") + functions.indexToCoordinate([pos1, pos2]))
					if capture:
						break
					continue
				break
			capture = False
			pos1, pos2 = functions.coordinateToIndex(self.position)
			while pos1 != 0 and pos2 != 7:
				pos1, pos2 = pos1 - 1, pos2 + 1
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [pos1, pos2]:
						if i.color == self.color:
							break
						capture = True
				else:
					if show_data:
						moves.append(enums.Move(name="B" + ("x" if capture else "") + functions.indexToCoordinate([pos1, pos2]), old_position=self.position, new_position=functions.indexToCoordinate([pos1, pos2]), piece=self, is_capture=capture))
					else:
						moves.append("B" + ("x" if capture else "") + functions.indexToCoordinate([pos1, pos2]))
					if capture:
						break
					continue
				break
			capture = False
			pos1, pos2 = functions.coordinateToIndex(self.position)
			while pos1 != 7 and pos2 != 0:
				pos1, pos2 = pos1 + 1, pos2 - 1
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [pos1, pos2]:
						if i.color == self.color:
							break
						capture = True
				else:
					if show_data:
						moves.append(enums.Move(name="B" + ("x" if capture else "") + functions.indexToCoordinate([pos1, pos2]), old_position=self.position, new_position=functions.indexToCoordinate([pos1, pos2]), piece=self, is_capture=capture))
					else:
						moves.append("B" + ("x" if capture else "") + functions.indexToCoordinate([pos1, pos2]))
					if capture:
						break
					continue
				break
		if self.piece_type == enums.Piece.rook:  # Rook moves
			capture = False
			for x in reversed(range(functions.coordinateToIndex(self.position)[0])):
				for y in self.board.pieces:
					if functions.coordinateToIndex(y.position) == [x, functions.coordinateToIndex(self.position)[1]]:
						if y.color == self.color:
							break
						capture = True
				else:
					if show_data:
						moves.append(enums.Move(name="R" + ("x" if capture else "") + functions.indexToCoordinate([x, functions.coordinateToIndex(self.position)[1]]), old_position=self.position, new_position=functions.indexToCoordinate([x, functions.coordinateToIndex(self.position)[1]]), piece=self, is_capture=capture))
					else:
						moves.append("R" + ("x" if capture else "") + functions.indexToCoordinate([x, functions.coordinateToIndex(self.position)[1]]))
					if capture:
						break
					continue
				break
			capture = False
			for x in reversed(range(functions.coordinateToIndex(self.position)[1])):
				for y in self.board.pieces:
					if functions.coordinateToIndex(y.position) == [functions.coordinateToIndex(self.position)[0], x]:
						if y.color == self.color:
							break
						capture = True
				else:
					if show_data:
						moves.append(enums.Move(name="R" + ("x" if capture else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], x]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], x]), piece=self, is_capture=capture))
					else:
						moves.append("R" + ("x" if capture else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], x]))
					if capture:
						break
					continue
				break
			capture = False
			for x in range(functions.coordinateToIndex(self.position)[0] + 1, 8):
				for y in self.board.pieces:
					if functions.coordinateToIndex(y.position) == [x, functions.coordinateToIndex(self.position)[1]]:
						if y.color == self.color:
							break
						capture = True
				else:
					if show_data:
						moves.append(enums.Move(name="R" + ("x" if capture else "") + functions.indexToCoordinate([x, functions.coordinateToIndex(self.position)[1]]), old_position=self.position, new_position=functions.indexToCoordinate([x, functions.coordinateToIndex(self.position)[1]]), piece=self, is_capture=capture))
					else:
						moves.append("R" + ("x" if capture else "") + functions.indexToCoordinate([x, functions.coordinateToIndex(self.position)[1]]))
					if capture:
						break
					continue
				break
			capture = False
			for x in range(functions.coordinateToIndex(self.position)[1] + 1, 8):
				for y in self.board.pieces:
					if functions.coordinateToIndex(y.position) == [functions.coordinateToIndex(self.position)[0], x]:
						if y.color == self.color:
							break
						capture = True
				else:
					if show_data:
						moves.append(enums.Move(name="R" + ("x" if capture else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], x]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], x]), piece=self, is_capture=capture))
					else:
						moves.append("R" + ("x" if capture else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], x]))
					if capture:
						break
					continue
				break
		elif self.piece_type == "queen":  # Queen moves
			capture = False
			pos1, pos2 = functions.coordinateToIndex(self.position)
			while pos1 != 0 and pos2 != 0:
				pos1, pos2 = pos1 - 1, pos2 - 1
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [pos1, pos2]:
						if i.color == self.color:
							break
						capture = True
				else:
					if show_data:
						moves.append(enums.Move(name="Q" + ("x" if capture else "") + functions.indexToCoordinate([pos1, pos2]), old_position=self.position, new_position=functions.indexToCoordinate([pos1, pos2]), piece=self, is_capture=capture))
					else:
						moves.append("Q" + ("x" if capture else "") + functions.indexToCoordinate([pos1, pos2]))
					if capture:
						break
					continue
				break
			capture = False
			pos1, pos2 = functions.coordinateToIndex(self.position)
			while pos1 != 7 and pos2 != 7:
				pos1, pos2 = pos1 + 1, pos2 + 1
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [pos1, pos2]:
						if i.color == self.color:
							break
						capture = True
				else:
					if show_data:
						moves.append(enums.Move(name="Q" + ("x" if capture else "") + functions.indexToCoordinate([pos1, pos2]), old_position=self.position, new_position=functions.indexToCoordinate([pos1, pos2]), piece=self, is_capture=capture))
					else:
						moves.append("Q" + ("x" if capture else "") + functions.indexToCoordinate([pos1, pos2]))
					if capture:
						break
					continue
				break
			capture = False
			pos1, pos2 = functions.coordinateToIndex(self.position)
			while pos1 != 0 and pos2 != 7:
				pos1, pos2 = pos1 - 1, pos2 + 1
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [pos1, pos2]:
						if i.color == self.color:
							break
						capture = True
				else:
					if show_data:
						moves.append(enums.Move(name="Q" + ("x" if capture else "") + functions.indexToCoordinate([pos1, pos2]), old_position=self.position, new_position=functions.indexToCoordinate([pos1, pos2]), piece=self, is_capture=capture))
					else:
						moves.append("Q" + ("x" if capture else "") + functions.indexToCoordinate([pos1, pos2]))
					if capture:
						break
					continue
				break
			capture = False
			pos1, pos2 = functions.coordinateToIndex(self.position)
			while pos1 != 7 and pos2 != 0:
				pos1, pos2 = pos1 + 1, pos2 - 1
				for i in self.board.pieces:
					if functions.coordinateToIndex(i.position) == [pos1, pos2]:
						if i.color == self.color:
							break
						capture = True
				else:
					if show_data:
						moves.append(enums.Move(name="Q" + ("x" if capture else "") + functions.indexToCoordinate([pos1, pos2]), old_position=self.position, new_position=functions.indexToCoordinate([pos1, pos2]), piece=self, is_capture=capture))
					else:
						moves.append("Q" + ("x" if capture else "") + functions.indexToCoordinate([pos1, pos2]))
					if capture:
						break
					continue
				break
			capture = False
			for x in reversed(range(functions.coordinateToIndex(self.position)[0])):
				for y in self.board.pieces:
					if functions.coordinateToIndex(y.position) == [x, functions.coordinateToIndex(self.position)[1]]:
						if y.color == self.color:
							break
						capture = True
				else:
					if show_data:
						moves.append(enums.Move(name="Q" + ("x" if capture else "") + functions.indexToCoordinate([x, functions.coordinateToIndex(self.position)[1]]), old_position=self.position, new_position=functions.indexToCoordinate([x, functions.coordinateToIndex(self.position)[1]]), piece=self, is_capture=capture))
					else:
						moves.append("Q" + ("x" if capture else "") + functions.indexToCoordinate([x, functions.coordinateToIndex(self.position)[1]]))
					if capture:
						break
					continue
				break
			capture = False
			for x in reversed(range(functions.coordinateToIndex(self.position)[1])):
				for y in self.board.pieces:
					if functions.coordinateToIndex(y.position) == [functions.coordinateToIndex(self.position)[0], x]:
						if y.color == self.color:
							break
						capture = True
				else:
					if show_data:
						moves.append(enums.Move(name="Q" + ("x" if capture else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], x]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], x]), piece=self, is_capture=capture))
					else:
						moves.append("Q" + ("x" if capture else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], x]))
					if capture:
						break
					continue
				break
			capture = False
			for x in range(functions.coordinateToIndex(self.position)[0] + 1, 8):
				for y in self.board.pieces:
					if functions.coordinateToIndex(y.position) == [x, functions.coordinateToIndex(self.position)[1]]:
						if y.color == self.color:
							break
						capture = True
				else:
					if show_data:
						moves.append(enums.Move(name="Q" + ("x" if capture else "") + functions.indexToCoordinate([x, functions.coordinateToIndex(self.position)[1]]), old_position=self.position, new_position=functions.indexToCoordinate([x, functions.coordinateToIndex(self.position)[1]]), piece=self, is_capture=capture))
					else:
						moves.append("Q" + ("x" if capture else "") + functions.indexToCoordinate([x, functions.coordinateToIndex(self.position)[1]]))
					if capture:
						break
					continue
				break
			capture = False
			for x in range(functions.coordinateToIndex(self.position)[1] + 1, 8):
				for y in self.board.pieces:
					if functions.coordinateToIndex(y.position) == [functions.coordinateToIndex(self.position)[0], x]:
						if y.color == self.color:
							break
						capture = True
				else:
					if show_data:
						moves.append(enums.Move(name="Q" + ("x" if capture else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], x]), old_position=self.position, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], x]), piece=self, is_capture=capture))
					else:
						moves.append("Q" + ("x" if capture else "") + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], x]))
					if capture:
						break
					continue
				break
		elif self.piece_type == enums.Piece.king:
			if self.position[0] != "h" and self.position[1] != "1":
				if not self.board.attackers(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] + 1]), enums.Color.invert(self.color)):
					if self.board.pieceAt(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] + 1])):
						if self.board.pieceAt(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] + 1])).color != self.color:
							if show_data:
								moves.append(enums.Move(name="Kx" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] + 1]), old_position=self, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] + 1]), piece=self, is_capture=True))
							else:
								moves.append("Kx" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] + 1]))
					else:
						if show_data:
							moves.append(enums.Move(name="K" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] + 1]), old_position=self, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] + 1]), piece=self))
						else:
							moves.append("K" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] + 1]))
			if self.position[0] != "a" and self.position[1] != "8":
				if not self.board.attackers(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] - 1]), enums.Color.invert(self.color)):
					if self.board.pieceAt(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] - 1])):
						if self.board.pieceAt(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] - 1])).color != self.color:
							if show_data:
								moves.append(enums.Move(name="Kx" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] - 1]), old_position=self, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] - 1]), piece=self, is_capture=True))
							else:
								moves.append("Kx" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] - 1]))
					else:
						if show_data:
							moves.append(enums.Move(name="K" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] - 1]), old_position=self, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] - 1]), piece=self))
						else:
							moves.append("K" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] - 1]))
			if self.position[0] != "a" and self.position[1] != "1":
				if not self.board.attackers(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 1]), enums.Color.invert(self.color)):
					if self.board.pieceAt(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 1])):
						if self.board.pieceAt(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 1])).color != self.color:
							if show_data:
								moves.append(enums.Move(name="Kx" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 1]), old_position=self, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 1]), piece=self, is_capture=True))
							else:
								moves.append("Kx" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 1]))
					else:
						if show_data:
							moves.append(enums.Move(name="K" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 1]), old_position=self, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 1]), piece=self))
						else:
							moves.append("K" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1] - 1]))
			if self.position[0] != "h" and self.position[1] != "8":
				if not self.board.attackers(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 1]), enums.Color.invert(self.color)):
					if self.board.pieceAt(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 1])):
						if self.board.pieceAt(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 1])).color != self.color:
							if show_data:
								moves.append(enums.Move(name="Kx" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 1]), old_position=self, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 1]), piece=self, is_capture=True))
							else:
								moves.append("Kx" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 1]))
					else:
						if show_data:
							moves.append(enums.Move(name="K" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 1]), old_position=self, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 1]), piece=self))
						else:
							moves.append("K" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1] + 1]))
			if self.position[0] != "a":
				if not self.board.attackers(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] - 1]), enums.Color.invert(self.color)):
					if self.board.pieceAt(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] - 1])):
						if self.board.pieceAt(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] - 1])).color != self.color:
							if show_data:
								moves.append(enums.Move(name="Kx" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] - 1]), old_position=self, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] - 1]), piece=self, is_capture=True))
							else:
								moves.append("Kx" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] - 1]))
					else:
						if show_data:
							moves.append(enums.Move(name="K" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] - 1]), old_position=self, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] - 1]), piece=self))
						else:
							moves.append("K" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] - 1]))
			if self.position[0] != "h":
				if not self.board.attackers(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] + 1]), enums.Color.invert(self.color)):
					if self.board.pieceAt(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] + 1])):
						if self.board.pieceAt(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] + 1])).color != self.color:
							if show_data:
								moves.append(enums.Move(name="Kx" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] + 1]), old_position=self, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] + 1]), piece=self, is_capture=True))
							else:
								moves.append("Kx" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] + 1]))
					else:
						if show_data:
							moves.append(enums.Move(name="K" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] + 1]), old_position=self, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] + 1]), piece=self))
						else:
							moves.append("K" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0], functions.coordinateToIndex(self.position)[1] + 1]))
			if self.position[1] != "1":
				if not self.board.attackers(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1]]), enums.Color.invert(self.color)):
					if self.board.pieceAt(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1]])):
						if self.board.pieceAt(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1]])).color != self.color:
							if show_data:
								moves.append(enums.Move(name="Kx" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1]]), old_position=self, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1]]), piece=self, is_capture=True))
							else:
								moves.append("Kx" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1]]))
					else:
						if show_data:
							moves.append(enums.Move(name="K" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1]]), old_position=self, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1]]), piece=self))
						else:
							moves.append("K" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] + 1, functions.coordinateToIndex(self.position)[1]]))
			if self.position[1] != "8":
				if not self.board.attackers(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1]]), enums.Color.invert(self.color)):
					if self.board.pieceAt(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1]])):
						if self.board.pieceAt(functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1]])).color != self.color:
							if show_data:
								moves.append(enums.Move(name="Kx" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1]]), old_position=self, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1]]), piece=self, is_capture=True))
							else:
								moves.append("Kx" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1]]))
					else:
						if show_data:
							moves.append(enums.Move(name="K" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1]]), old_position=self, new_position=functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1]]), piece=self))
						else:
							moves.append("K" + functions.indexToCoordinate([functions.coordinateToIndex(self.position)[0] - 1, functions.coordinateToIndex(self.position)[1]]))
		return moves

	def __str__(self):
		return self.color.title() + " " + self.piece_type + " at " + self.position + " from " + repr(self.board)

	def __lt__(self, other):
		return enums.Piece.value(self.piece_type) < enums.Piece.value(other)

	def __add__(self, _):
		raise ArithmeticError("Cannot add pieces")

	def __sub__(self, _):
		raise ArithmeticError("Cannot subtract pieces")

	def __mul__(self, _):
		raise ArithmeticError("Cannot multiply pieces")

	def __mod__(self, _):
		raise ArithmeticError("Cannot modulo pieces")

	def __floordiv__(self, _):
		raise ArithmeticError("Cannot divide pieces")

	def __divmod__(self, _):
		raise ArithmeticError("Cannot divide pieces")

	def __truediv__(self, _):
		raise ArithmeticError("Cannot divide pieces")

	def __floor__(self):
		raise ArithmeticError("Cannot floor")


class Game:
	def __init__(self, raise_errors=True):
		"""Initialize"""
		self.opening = ""
		self.move_list, self.raw_move_list = "", []
		self.turn = enums.Color.white
		self.squares, self.pieces = [], []
		for x in range(8):
			row = []
			for y in range(8):
				row.append(Square([x, y], self))
				if x in [0, 7]:
					if y in [0, 7]:
						self.pieces.append(Piece([x, y], enums.Piece.rook, enums.Color.black if x == 0 else enums.Color.white, self))
					elif y in [1, 6]:
						self.pieces.append(Piece([x, y], enums.Piece.knight, enums.Color.black if x == 0 else enums.Color.white, self))
					elif y in [2, 5]:
						self.pieces.append(Piece([x, y], enums.Piece.bishop, enums.Color.black if x == 0 else enums.Color.white, self))
					elif y == 3:
						self.pieces.append(Piece([x, y], enums.Piece.queen, enums.Color.black if x == 0 else enums.Color.white, self))
					elif y == 4:
						self.pieces.append(Piece([x, y], enums.Piece.king, enums.Color.black if x == 0 else enums.Color.white, self))
				elif x in [1, 6]:
					self.pieces.append(Piece([x, y], enums.Piece.pawn, enums.Color.black if x == 1 else enums.Color.white, self))
			self.squares.append(row)
		self.raise_errors = raise_errors

	def FEN(self):
		"""Returns the FEN of the game"""
		return "(FEN TEXT)"

	def error(self, error):
		"""Raises an error if allowed"""
		if self.raise_errors:
			raise error

	def move(self, move):
		"""Moves a piece"""
		if isinstance(move, enums.Move):
			move = move.name
		if not isinstance(move, str):
			self.error(errors.InvalidMove(move))
		move = functions.toSAN(move, self)
		if move not in self.legal_moves():
			self.error(errors.MoveNotPossible(move))
		for i in self.legal_moves(True):
			if i.name == move and i.piece.color == self.turn:
				if i.is_capture:
					self.pieces.remove(self.pieceAt(i.new_position))
				i.piece.position = i.new_position
				self.raw_move_list.append(i)
				break
		if self.turn == enums.Color.white:  # Add move to move list
			if self.move_list == "":
				self.move_list += "1. " + move
			else:
				self.move_list += " " + str(int(self.move_list.split(" ")[-3][0]) + 1) + ". " + move
		else:
			self.move_list += " " + move
		self.turn = (enums.Color.white, enums.Color.black)[self.turn == enums.Color.white]
		for i in json.load(open("openings.json", "r+")):
			if i["moves"] == self.move_list:
				self.opening = i["eco"] + " " + i["name"]

	def legal_moves(self, show_data=False):
		"""Returns all legal moves"""
		return [y for x in self.pieces if x.color == self.turn for y in x.moves(show_data)]

	def pieceAt(self, coordinate):
		"""Returns the piece at coordinate if one exists, otherwise return None"""
		return self.pieces[[i.position for i in self.pieces].index(coordinate)] if coordinate in [i.position for i in self.pieces] else None

	def takeback(self):
		"""Take backs one move. To take back multiple moves, call the function multiple times."""
		if not self.raw_move_list:
			return
		if self.raw_move_list[-1].is_capture:
			self.pieces.append(Piece(self.raw_move_list[-1].new_position, self.raw_move_list[-1].captured_piece.piece_type, self.raw_move_list[-1].captured_piece.color, self))
		self.raw_move_list[-1].piece.position = self.raw_move_list[-1].old_position
		self.raw_move_list.pop()
		if self.move_list.split(" ")[-2][-1] == ".":
			self.move_list = " ".join(self.move_list.split(" ")[:-2])
		else:
			self.move_list = " ".join(self.move_list.split(" ")[:-1])
		self.turn = enums.Color.invert(self.turn)
		if self.move_list == "":
			self.opening = ""
		else:
			for i in json.load(open("openings.json", "r+")):
				if i["moves"] == self.move_list:
					self.opening = i["eco"] + " " + i["name"]

	def attackers(self, coordinate, color):
		"""Returns the pieces that attack the coordinate"""
		if color not in [enums.Color.white, enums.Color.black]:
			self.error(errors.UndefinedColor(color))
		attackers = []
		for i in self.pieces:
			if i.color != color:
				continue
			if i.piece_type == enums.Piece.pawn:
				if functions.coordinateToIndex(coordinate) in [[functions.coordinateToIndex(i.position)[0] - (1 if i.color == enums.Color.white else -1), functions.coordinateToIndex(i.position)[1] - 1], [functions.coordinateToIndex(i.position)[0] - (1 if i.color == enums.Color.white else -1), functions.coordinateToIndex(i.position)[1] + 1]]:
					attackers.append(i)
			elif i.piece_type == enums.Piece.king:
				if functions.coordinateToIndex(coordinate) in [[functions.coordinateToIndex(i.position)[0] - 1, functions.coordinateToIndex(i.position)[1] - 1], [functions.coordinateToIndex(i.position)[0] - 1, functions.coordinateToIndex(i.position)[1]], [functions.coordinateToIndex(i.position)[0] - 1, functions.coordinateToIndex(i.position)[1] + 1], [functions.coordinateToIndex(i.position)[0], functions.coordinateToIndex(i.position)[1] - 1], [functions.coordinateToIndex(i.position)[0], functions.coordinateToIndex(i.position)[1] + 1], [functions.coordinateToIndex(i.position)[0] + 1, functions.coordinateToIndex(i.position)[1] - 1], [functions.coordinateToIndex(i.position)[0] + 1, functions.coordinateToIndex(i.position)[1]], [functions.coordinateToIndex(i.position)[0] + 1, functions.coordinateToIndex(i.position)[1] + 1]]:
					attackers.append(i)
			elif any([coordinate in x for x in i.moves()]):
				attackers.append(i)
		return attackers

	def visualized(self, use_unicode=True, empty_squares=" ", separators=True):
		return (("---------------------------------\n| " if use_unicode else "-----------------------------------------\n| ") + (" |\n---------------------------------\n| " if use_unicode else " |\n-----------------------------------------\n| ").join(" | ".join([y + ((empty_squares if use_unicode else empty_squares + " ") if y == "" else "") for y in x]) for x in [["".join([((enums.Piece.unicode(z.piece_type, z.color)) if use_unicode else (z.color[0].upper() + (z.piece_type[0].upper() if z.piece_type != "knight" else "N"))) if functions.coordinateToIndex(z.position) == [x, y] else "" for z in self.pieces]) for y in range(len(self.squares[x]))] for x in range(len(self.squares))]) + (" |\n---------------------------------" if use_unicode else " |\n-----------------------------------------")) if separators else ("\n".join(" ".join([y + ((empty_squares if use_unicode else empty_squares + " ") if y == "" else "") for y in x]) for x in [["".join([((enums.Piece.unicode(z.piece_type, z.color)) if use_unicode else (z.color[0].upper() + (z.piece_type[0].upper() if z.piece_type != "knight" else "N"))) if functions.coordinateToIndex(z.position) == [x, y] else "" for z in self.pieces]) for y in range(len(self.squares[x]))] for x in range(len(self.squares))]))

	def __str__(self):
		return "Chess Game with FEN " + self.FEN()

	def __lt__(self, other):
		return len(self.pieces) < len(other.pieces)

	def __add__(self, _):
		raise ArithmeticError("Cannot add games")

	def __sub__(self, _):
		raise ArithmeticError("Cannot subtract games")

	def __mul__(self, _):
		raise ArithmeticError("Cannot multiply games")

	def __mod__(self, _):
		raise ArithmeticError("Cannot modulo games")

	def __floordiv__(self, _):
		raise ArithmeticError("Cannot divide games")

	def __divmod__(self, _):
		raise ArithmeticError("Cannot divide games")

	def __truediv__(self, _):
		raise ArithmeticError("Cannot divide games")

	def __floor__(self):
		raise ArithmeticError("Cannot floor")

	def __eq__(self, other):
		return self.FEN() == other.FEN()
