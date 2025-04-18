import tkinter as tk
from tkinter import messagebox
import random
import math
from copy import deepcopy

# Game Logic Class
class TicTacToe:
    def _init_(self):
        self.board = [' '] * 9
        self.current_player = 'X'

    def get_valid_moves(self):
        return [i for i in range(9) if self.board[i] == ' ']

    def make_move(self, move):
        if self.board[move] == ' ':
            self.board[move] = self.current_player
            self.current_player = 'O' if self.current_player == 'X' else 'X'
            return True
        return False

    def is_game_over(self):
        return self.get_winner() is not None or not self.get_valid_moves()

    def get_winner(self):
        winning_combos = [
            [0,1,2],[3,4,5],[6,7,8],
            [0,3,6],[1,4,7],[2,5,8],
            [0,4,8],[2,4,6]
        ]
        for combo in winning_combos:
            a, b, c = combo
            if self.board[a] == self.board[b] == self.board[c] != ' ':
                return self.board[a]
        return None

    def clone(self):
        clone = TicTacToe()
        clone.board = self.board[:]
        clone.current_player = self.current_player
        return clone

# MCTS Classes
class Node:
    def _init_(self, state, parent=None):
        self.state = state
        self.parent = parent
        self.children = {}
        self.wins = 0
        self.visits = 0

    def expand(self):
        for move in self.state.get_valid_moves():
            if move not in self.children:
                next_state = self.state.clone()
                next_state.make_move(move)
                self.children[move] = Node(next_state, self)

    def is_fully_expanded(self):
        return len(self.children) == len(self.state.get_valid_moves())

    def best_child(self, c_param=1.41):
        best_score = float('-inf')
        best_move = None
        for move, child in self.children.items():
            if child.visits == 0:
                score = float('inf')  # Encourage unvisited nodes
            else:
                exploitation = child.wins / child.visits
                exploration = c_param * math.sqrt(math.log(self.visits) / child.visits)
                score = exploitation + exploration
            if score > best_score:
                best_score = score
                best_move = move
        return best_move


    def simulate(self):
        sim_state = self.state.clone()
        while not sim_state.is_game_over():
            move = random.choice(sim_state.get_valid_moves())
            sim_state.make_move(move)
        return sim_state.get_winner()

    def backpropagate(self, result, player):
        self.visits += 1
        if result == player:
            self.wins += 1
        elif result is None:
            self.wins += 0.5
        if self.parent:
            self.parent.backpropagate(result, player)

def mcts(root_state, iterations=500):
    root_node = Node(root_state)
    for _ in range(iterations):
        node = root_node
        # Selection
        while node.is_fully_expanded() and node.children:
            move = node.best_child()
            node = node.children[move]
        # Expansion
        if not node.state.is_game_over():
            node.expand()
            if node.children:
                move = random.choice(list(node.children.keys()))
                node = node.children[move]
        # Simulation
        result = node.simulate()
        # Backpropagation
        node.backpropagate(result, root_state.current_player)
    # Return best move
    return max(root_node.children.items(), key=lambda item: item[1].visits)[0]

# GUI Class
class TicTacToeGUI:
    def _init_(self, root):
        self.root = root
        self.root.title("Tic Tac Toe - MCTS AI")
        self.buttons = []
        self.game = TicTacToe()
        self.human = 'X'
        self.ai = 'O'
        self.build_gui()

    def build_gui(self):
        for i in range(9):
            btn = tk.Button(self.root, text=' ', font=('Arial', 24), width=5, height=2,
                            command=lambda i=i: self.player_move(i))
            btn.grid(row=i//3, column=i%3)
            self.buttons.append(btn)

    def player_move(self, idx):
        if self.game.board[idx] == ' ' and not self.game.is_game_over():
            self.game.make_move(idx)
            self.buttons[idx]['text'] = self.human
            self.buttons[idx]['state'] = 'disabled'
            if self.check_end(): return
            self.root.after(500, self.ai_move)

    def ai_move(self):
        move = mcts(self.game.clone(), iterations=700)
        self.game.make_move(move)
        self.buttons[move]['text'] = self.ai
        self.buttons[move]['state'] = 'disabled'
        self.check_end()

    def check_end(self):
        winner = self.game.get_winner()
        if winner:
            messagebox.showinfo("Game Over", f"{winner} wins!")
            self.disable_all()
            return True
        elif not self.game.get_valid_moves():
            messagebox.showinfo("Game Over", "It's a draw!")
            self.disable_all()
            return True
        return False

    def disable_all(self):
        for btn in self.buttons:
            btn['state'] = 'disabled'

# Run GUI
if name == "main":
    root = tk.Tk()
    app = TicTacToeGUI(root)
    root.mainloop()
