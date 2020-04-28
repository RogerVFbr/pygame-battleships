import random
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


class BattleshipsAIAgent:

    ANSI = {
        'yellow': '\u001b[33m',
        'red': '\u001b[31m',
        'bg_blue': '\u001b[44m',
        'bg_red': '\u001b[41m',
        'bg_white': '\u001b[47m',
        'bg_magenta': '\u001b[45m',
        'bg_cyan': '\u001b[46m',
        'bg_yellow': '\u001b[43m',
        'default': '\u001b[0m'
    }

    def __init__(self, size, hits, misses, ships, player_b=False):
        self.board = self.build_board(size, hits, misses)
        self.size = size
        self.ships = ships
        self.player_b = player_b
        self.candidates = []
        self.priority_candidates = []
        # self.print_board()

    def build_board(self, size, hits, misses, player_b=False):
        board = [['.' for _ in range(size)] for _ in range(size)]
        for x in range(size):
            for y in range(size):
                position = (x, y)
                if position in hits:
                    board[y][x] = 'H'
                elif position in misses:
                    board[y][x] = 'o'
        return board

    def get_coordinates(self):
        coords = self.get_target_coordinates()
        if coords is not None:
            return coords[1], coords[0]
        # return self.get_hunt_coords_by_parity()
        return self.get_hunt_coords_by_probability()

    def get_target_coordinates(self):

        for lin in range(self.size):
            for col in range(self.size):
                if self.board[lin][col] == 'H':
                    self.get_target_candidates_inner(lin, col)
                    self.get_target_candidates_vertical_extremes(lin, col)
                    self.get_target_candidates_horizontal_extremes(lin, col)

        if self.priority_candidates:
            choice = random.choice(self.priority_candidates)
        elif self.candidates:
            choice = random.choice(self.candidates)
        else:
            choice = None

        if choice is not None:
            self.print_choices(choice, target_mode=True)

        return choice

    def get_target_candidates_inner(self, lin, col):

        if 0 < lin < self.size - 1 and 0 < col < self.size - 1:

            if self.board[lin + 1][col] == 'H' and self.board[lin - 1][col] == '.':
                self.priority_candidates.append((lin - 1, col))

            if self.board[lin - 1][col] == 'H' and self.board[lin + 1][col] == '.':
                self.priority_candidates.append((lin + 1, col))

            if self.board[lin][col + 1] == 'H' and self.board[lin][col - 1] == '.':
                self.priority_candidates.append((lin, col - 1))

            if self.board[lin][col - 1] == 'H' and self.board[lin][col + 1] == '.':
                self.priority_candidates.append((lin, col + 1))

            if self.board[lin - 1][col] == '.': self.candidates.append((lin - 1, col))
            if self.board[lin + 1][col] == '.': self.candidates.append((lin + 1, col))
            if self.board[lin][col - 1] == '.': self.candidates.append((lin, col - 1))
            if self.board[lin][col + 1] == '.': self.candidates.append((lin, col + 1))

    def get_target_candidates_vertical_extremes(self, lin, col):

        if lin == 0 or lin == self.size - 1:

            if lin == 0 and self.board[lin + 1][col] == '.':
                self.candidates.append((lin + 1, col))

            elif lin == self.size - 1 and self.board[lin - 1][col] == '.':
                self.candidates.append((lin - 1, col))

            if 0 < col < self.size - 1:

                if self.board[lin][col + 1] == 'H' and self.board[lin][col - 1] == '.':
                    self.priority_candidates.append((lin, col - 1))

                if self.board[lin][col - 1] == 'H' and self.board[lin][col + 1] == '.':
                    self.priority_candidates.append((lin, col + 1))

                if self.board[lin][col - 1] == '.': self.candidates.append((lin, col - 1))
                if self.board[lin][col + 1] == '.': self.candidates.append((lin, col + 1))

    def get_target_candidates_horizontal_extremes(self, lin, col):
        if col == 0 or col == self.size - 1:

            if col == 0 and self.board[lin][col + 1] == '.':
                self.candidates.append((lin, col + 1))

            elif col == self.size - 1 and self.board[lin][col - 1] == '.':
                self.candidates.append((lin, col - 1))

            if 0 < lin < self.size - 1:

                if self.board[lin - 1][col] == 'H' and self.board[lin + 1][col] == '.':
                    self.priority_candidates.append((lin + 1, col))

                if self.board[lin + 1][col] == 'H' and self.board[lin - 1][col] == '.':
                    self.priority_candidates.append((lin - 1, col))

                if self.board[lin + 1][col] == '.': self.candidates.append((lin + 1, col))
                if self.board[lin - 1][col] == '.': self.candidates.append((lin - 1, col))

    def get_hunt_coords_by_parity(self):

        self.get_hunt_coords_by_probability()

        for x in range(self.size):
            for y in range(self.size):
                if x%2 == 0 and y%2 == 0: continue
                if x%2 != 0 and y%2 != 0: continue
                if self.board[x][y] == '.':
                    self.candidates.append((x, y))

        choice = random.choice(self.candidates)
        self.print_choices(choice)
        return choice[1], choice[0]

    def get_hunt_coords_by_probability(self):
        matrix = [[0 for _ in range(self.size)] for _ in range(self.size)]

        for x in range(self.size):
            for y in range(self.size):
                for ship in self.ships:
                    if self.size-1-x >= ship and all(self.board[x+s][y] == '.' for s in range(ship)):
                        for s in range(ship):
                            matrix[x+s][y] += 1
                    if self.size-1-y >= ship and all(self.board[x][y+s] == '.' for s in range(ship)):
                        for s in range(ship):
                            matrix[x][y+s] += 1

        results = []
        for x in range(self.size):
            for y in range(self.size):
                results.append({
                    'x': x,
                    'y': y,
                    'value': matrix[x][y]
                })

        results = sorted(results, key=lambda i: i['value'], reverse=True)
        highest_value = results[0]['value']
        self.candidates = [(x['x'], x['y']) for x in results if x['value'] == highest_value and x['value'] != 0]

        df = pd.DataFrame(matrix)
        if not self.player_b:
            sns.heatmap(df, cmap="Blues")
        else:
            sns.heatmap(df, cmap="Greens")
        plt.show()

        choice = random.choice(self.candidates)
        self.print_choices(choice)
        return choice[1], choice[0]

    def print_board(self):
        print()
        print('BOARD SITUATION')
        for row in self.board:
            for col in row:
                if col == '.':
                    print(f"{self.ANSI['bg_white']}   {self.ANSI['default']}", end='')
                elif col == 'H':
                    print(f"{self.ANSI['bg_red']}   {self.ANSI['default']}", end='')
                elif col == 'o':
                    print(f"{self.ANSI['bg_blue']}   {self.ANSI['default']}", end='')
            print()

    def print_choices(self, choice, target_mode=False):

        board = self.board
        for x, y in self.candidates:
            board[x][y] = 'c'
        for x, y in self.priority_candidates:
            board[x][y] = 'C'

        print()
        spacing = '            ' if not self.player_b else ''
        if target_mode:
            print(f"{spacing}{self.ANSI['red']}TARGET MODE. REMAINING: {self.ships}{self.ANSI['default']}")
        else:
            print(f"{spacing}{self.ANSI['yellow']}HUNT MODE. REMAINING: {self.ships}{self.ANSI['default']}")
        for x in range(self.size):
            print(f"{spacing}", end='')
            for y in range(self.size):
                val = self.board[x][y]
                ch = '*' if (x == choice[0] and y == choice[1]) else ' '
                if val == '.':
                    print(f"{self.ANSI['bg_white']}   {self.ANSI['default']}", end='')
                elif val == 'H':
                    print(f"{self.ANSI['bg_red']}   {self.ANSI['default']}", end='')
                elif val == 'o':
                    print(f"{self.ANSI['bg_blue']}   {self.ANSI['default']}", end='')
                elif val == 'C':
                    print(f"{self.ANSI['bg_cyan']} {ch} {self.ANSI['default']}", end='')
                elif val == 'c':
                    print(f"{self.ANSI['bg_magenta']} {ch} {self.ANSI['default']}", end='')

            print()