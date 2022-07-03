import math


def get_best_move(state):
    best_score = -math.inf
    best_move = None
    for move in state.possible_moves():
        state.board[move[0]][move[1]] = -1
        score = minimax(state, 9, True)
        state.board[move[0]][move[1]] = 0
        if score > best_score:
            best_score = score
            best_move = move
    return best_move

def evaluation_function(state):
    for row in state.board:
        if abs(sum(row)) == 3:
            return -1 if sum(row) > 0 else 1
    for col in zip(*state.board):
        if abs(sum(col)) == 3:
            return -1 if sum(col) > 0 else 1

    diagonal_1 = [state.board[0][0], state.board[1][1], state.board[2][2]]
    diagonal_2 = [state.board[0][2], state.board[1][1], state.board[2][0]]

    if abs(sum(diagonal_1)) == 3:
        return -1 if sum(diagonal_1) > 0 else 1
    if abs(sum(diagonal_2)) == 3:
        return -1 if sum(diagonal_2) > 0 else 1
    return 0

def minimax(state, max_depth, is_player_maximizer):
    if max_depth == 0 or state.is_end_state():
        # We're at the end. Time to evaluate the state we're in
        return evaluation_function(state)

    # Is the current player the maximizer?
    if is_player_maximizer:
        value = -math.inf
        for move in state.possible_moves():
            state.board[move[0]][move[1]] = -1
            evaluation = minimax(state, max_depth - 1, False)
            state.board[move[0]][move[1]] = 0
            value = max(value, evaluation)
        return value

    # Or the minimizer?
    else:
        value = math.inf
        for move in state.possible_moves():
            state.board[move[0]][move[1]] = 1
            evaluation = minimax(state, max_depth - 1, True)
            state.board[move[0]][move[1]] = 0
            value = min(value, evaluation)
        return value



class TicTacToe():
    def __init__(self):
        self.board = [
            [0, 0, 0],
            [0, 0, 0],
            [0, 0, 0]
        ]
        self.turn = -1

    def is_end_state(self):
        for row in self.board:
            if abs(sum(row)) == 3:
                return True
        for col in zip(*self.board):
            if abs(sum(col)) == 3:
                return True

        diagonal_1 = [self.board[0][0], self.board[1][1], self.board[2][2]]
        diagonal_2 = [self.board[0][2], self.board[1][1], self.board[2][0]]

        if abs(sum(diagonal_1)) == 3:
            return True
        if abs(sum(diagonal_2)) == 3:
            return True
        
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == 0:
                    return False
        return True

    def possible_moves(self):
        available_moves = []
        for i in range(3):
            for j in range(3):
                if self.board[i][j] == 0:
                    available_moves.append((i, j))
        return available_moves

    def show(self):
        for row in self.board:
            print(row)
        print()

    def play(self, x, y):
        self.board[x][y] = self.turn
        self.turn *= -1



if __name__ == '__main__':
    tictac = TicTacToe()
    tictac.show()
    while (not tictac.is_end_state()):
        ai_get_move = get_best_move(tictac)
        tictac.play(ai_get_move[0], ai_get_move[1])
        tictac.show()

        input_x, input_y = input("Enter data: ").split(',')
        input_x, input_y = int(input_x), int(input_y)
        tictac.play(input_x, input_y)
        tictac.show()
        
    