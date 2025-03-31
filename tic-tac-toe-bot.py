import random, time
import numpy as np
import math
import copy

import ox


class MCTSBot:	

	class Node:
		def __init__(self, state: ox.Board, parent=None):
			self.state = state
			self.parent = parent
			self.children = []
			self.visits = 0
			self.score = 0

			self.exploration = math.sqrt(2)

		def generate_children(self):
			aviable_actions = self.state.get_actions()

			for action in aviable_actions:
				s_ = self.state.clone()
				s_.apply_action(action)
				child = MCTSBot.Node(s_, self)
				self.children.append((action, child))

		def select_child(self):
			max_ucb = float('-inf')
			selected_child = None
			for action, child in self.children:
				if child.visits == 0:
					ucb = float('inf')
				else:
					ucb = child.score / child.visits + self.exploration * math.sqrt(math.log(self.visits) / child.visits)
				if ucb > max_ucb:
					selected_child = (action, child)
					max_ucb = ucb

			return selected_child
		
		def min_center_distance(self):
			center = self.state.size / 2
			size = self.state.size

			legal_actions = self.state.get_actions()
			min_distance = 1000
			best_action = None
			for action in legal_actions:
				distance = abs(center - action / size) + abs(center - action % size)
				if distance < min_distance:
					min_distance = distance
					best_action = action

			return best_action

	def winning_action(self, board: ox.Board):
		av_ac = board.get_actions()
		for action in av_ac:
			state_tmp = board.clone()
			state_tmp.apply_action(action)
			if state_tmp.get_rewards() != [0, 0]:
				return action
		return None
	
	def get_winning_or_defense_action(self, board: ox.Board):
		# check if player can play winning action - play it if its possible
		win_ac = self.winning_action(board)
		if win_ac != None:
			return win_ac
		
		# check if opponent can play winning action - if they do, play it to prevent their victory
		opponent_board = board.clone()
		if opponent_board.current_player() == 0:
			opponent_board.player = 1
		else:
			opponent_board.player = 0
		win_ac = self.winning_action(board)
		if win_ac != None:
			return win_ac
		
		return None

	def __init__(self, play_as: int, time_limit: float):
		self.play_as = play_as
		self.time_limit = time_limit * 0.9

	def get_simulation_action(self, state: ox.Board):
			#action = self.get_winning_or_defense_action()
			#action = self.min_center_distance()
			action = None
			if action == None:
				action = random.choice( list(state.get_actions()) )

			return action
 
	def play_action(self, board: ox.Board):

		start_time = time.time()

		root = self.Node(board)
		win_def_action = self.get_winning_or_defense_action(board)
		if win_def_action != None:
			return win_def_action

		iterations = 0

		#print("before while", time.time() - start_time)

		while (time.time() - start_time) < self.time_limit:
			iterations+=1
			# SELECTION
			current_node = root
			while len(current_node.children) > 0:
				a, current_node = current_node.select_child()

			# EXPANSION
			if current_node.visits > 0 and not current_node.state.is_terminal():
				current_node.generate_children()
				a, current_node = random.choice(current_node.children)

			# SIMULATION
			simulation_state = current_node.state.clone()
			while not simulation_state.is_terminal():
				simulation_state.apply_action(random.choice( list(simulation_state.get_actions()) ))

			rewards = simulation_state.get_rewards()
			reward = rewards[board.player]

			# BACKPROPAGATION
			while True:
				current_node.visits += 1
				current_node.score += reward
				if current_node.parent == None:
					break
				current_node = current_node.parent
 
		#print("iterations", iterations)

		max_avg_score = float('-inf')
		best_action = None
		for action, child in root.children:
			if child.visits == 0:
				avg_score = 0
			else:
				avg_score = child.score / child.visits
			if avg_score > max_avg_score:
				max_avg_score = avg_score
				best_action = action

		return best_action
        
if __name__ == '__main__':
	

	#print(board)

	# try your bot against itself
	for i in range(1):
		board = ox.Board(8)  # 8x8
		bots = [MCTSBot(0, 0.1), MCTSBot(1, 1.0)]
		#bots = [MCTSBot(0, 0.1), MCTSBot(1, 0.1)]
		while not board.is_terminal():
			current_player = board.current_player()
			current_player_mark = ox.MARKS_AS_CHAR[ ox.PLAYER_TO_MARK[current_player] ]

			current_bot = bots[current_player]
			a = current_bot.play_action(board)
			board.apply_action(a)

			print(f"{current_player_mark}: {a} -> \n{board}\n")