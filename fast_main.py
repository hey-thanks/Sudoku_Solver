import wx
import time
from random import randrange


SET_1_TO_9 = {'1', '2', '3', '4', '5', '6', '7', '8', '9'}


def create_rotated_board(board):
    """
    Generate the rotated Sudoku board. This is used to easily check if
    the columns contain any duplicates.

    """
    rotated_board = [[-1]*9 for _ in range(9)]
    for i in range(len(board)):
        for j in range(len(board[i])):
            rotated_board[i][j] = board[j][i]
    return rotated_board

def create_subgrids_to_rows_board(board):
    """
    Generate the subgridded Sudoku board, which maps 3x3 subgrids to
    rows. This is used to easily check if the subgrids contain any
    duplicates.

    """
    subgrid_board = []
    for i in range(0, len(board), 3):
        for j in range(0, len(board[i]), 3):
            subgrid_board.append([])
            subgrid_board[-1].extend(board[j][i:i+3])
            subgrid_board[-1].extend(board[j+1][i:i+3])
            subgrid_board[-1].extend(board[j+2][i:i+3])
    return subgrid_board

def check_solution(board):
    """Verify that each row, column, and 3x3 subgird contains 1-9."""
    status = check_rows(board)
    if status:
        rotated_board = create_rotated_board(board)
        status = check_rows(rotated_board)
    if status:
        subgrid_board = create_subgrids_to_rows_board(board)
        status = check_rows(subgrid_board)
    return status

def check_rows(board):
    """Verify that each row of the given board contains 1-9."""
    valid_set = SET_1_TO_9
    for row in board:
        if set(row) != valid_set:
            return False
    return True

class Sudoku():
    """
    A class that will hold three copies of a Sudoku board: the
    original, a rotated one, and one that maps the 3x3 subgrids to
    rows. These are used to very quickly determine what numbers are
    valid for a certain cell.

    """
    def __init__(self):
        # Initialize a game board.
        game_list = []
        num_boards = 0
        with open('puzzles.txt', 'r') as f_in:
            for line in f_in:
                if line.startswith('G'):
                    board = []
                    num_boards += 1
                else:
                    line = line.strip()
                    line = line.replace('0', ' ')
                    board.append(list(line))

                if len(board) == 9:
                    game_list.append(board)

        index = randrange(num_boards)
        board = game_list[index]
        print("Playing Game #{}".format(index))

        self.game_board = board
        self.rotated_board = [[' ' for _ in range(9)] for _ in range(9)]
        self.subgrid_board = [[' ' for _ in range(9)] for _ in range(9)]
        self.initialize_secondary_boards()
        self.numbers_tried = dict()
        self.initialize_numbers_tried()

    def initialize_numbers_tried(self):
        """Initialize the numbers_tried dict based on the board."""
        for i, row in enumerate(self.game_board):
            for j, val in enumerate(row):
                if val == ' ':
                    self.numbers_tried[(i, j)] = set()
                else:
                    self.numbers_tried[(i, j)] = None

    def initialize_secondary_boards(self):
        """
        Initialize the rotated and subgridded Sudoku boards. These are
        used to easily check if the columns and 3x3 subgrids contain any
        duplicates.
        
        """
        for i, row in enumerate(self.game_board):
            for j, val in enumerate(row):
                self.rotated_board[j][i] = self.game_board[i][j]
                self.subgrid_insert(i, j, val)
                
    def cell_value(self, i, j):
        """Return the cell value at the given location."""
        return self.game_board[i][j]

    def check(self, i, j):
        """Return a list of a numbers that are valid for a given cell."""
        valid_numbers = SET_1_TO_9 - set(
            self.game_board[i]
        ).union(self.rotated_board[j]
        ).union(self.subgrid_board_get_row(i, j)
        ).union(self.numbers_tried[(i, j)])

        return valid_numbers

    def reset_cell(self, i, j):
        """Reset the numbers_tried dict and game board cells."""
        if self.numbers_tried[(i, j)] is not None:
            self.numbers_tried[(i, j)] = set()
            self.game_board[i][j] = ' '
            self.rotated_board[j][i] = ' '
            self.subgrid_insert(i, j, ' ')

    def insert(self, i, j, val):
        """
        Insert the given value into the given cell and add the value to the
        numbers_tried dict.

        """
        self.game_board[i][j] = val
        self.rotated_board[j][i] = val
        self.subgrid_insert(i, j, val)
        if val != ' ':
            self.numbers_tried[(i, j)].add(val)

    def subgrid_insert(self, i, j, val):
        """
        Insert the given value to the appropriate location in the subgrid
        board based on its location in the original game board.

        """
        if j < 3:
            j = j + ((i%3) * 3)
            i = i - (i%3)
            self.subgrid_board[i][j] = val
            return
        elif 3 <= j < 6:
            if i%3 == 0:
                i += 1
                j -= 3
            elif i%3 == 2:
                i -= 1
                j += 3
            else:
                i = i
                j = j
            self.subgrid_board[i][j] = val
            return
        else:
            if i%3 == 0:
                i += 2
                j -= 6
            elif i%3 == 1:
                i += 1
                j -= 3
            else:
                i = i
                j = j
            self.subgrid_board[i][j] = val
            return

    def subgrid_board_get_row(self, i, j):
        """
        Return the current row of the subgrid board based on the cell
        location.
        
        """
        if j < 3:
            i = i - (i%3)
            return self.subgrid_board[i]
        elif 3 <= j < 6:
            if i%3 == 0:
                i += 1
            elif i%3 == 2:
                i -= 1
            else:
                i = i
            return self.subgrid_board[i]
        else:
            if i%3 == 0:
                i += 2
            elif i%3 == 1:
                i += 1
            else:
                i = i
            return self.subgrid_board[i]

    def print_board(self, board):
        """Print the Sudoku board."""        
        print('\n')
        for row in board:
            print(row)


direction = 'f'
def move(i, j):
    """Move forward or backward by one cell."""
    global direction
    if direction == 'f':
        if j < 8:
            j += 1
        elif i < 8:
            j = 0
            i += 1
        else:
            print("Win!")
            return 9, 9
    else:
        if j > 0:
            j -= 1
        elif i > 0:
            i -= 1
            j = 8
        else:
            print("No solution!")
            return 9, 9
    return i, j


class MyFrame(wx.Frame):
    """Create the GUI and all associated functionality."""
    def __init__(self):
        super().__init__(parent=None, title='Sudoku', size=(485,485))
        self.highlighted_button = None
        self.NUM_GRID_ROWS = 9
        self.NUM_GRID_COLS = 9
        
        self.panel = wx.Panel(self)

        self.master_sizer = wx.BoxSizer(wx.VERTICAL)

        self.main_grid = wx.GridBagSizer(2, 2)
        self.master_sizer.Add(self.main_grid, 0, wx.ALL|wx.EXPAND, 5)

        self.sudoku_board = Sudoku()
        self.button_list = []
        row_offset = 0
        for i in range(self.NUM_GRID_ROWS):
            self.button_list.append([])
            col_offset = 0
            for j in range(self.NUM_GRID_COLS):
                button = wx.Button(self.panel, id=i*9 + j, label=self.sudoku_board.cell_value(i, j), style=wx.BU_EXACTFIT)
                button.Bind(wx.EVT_BUTTON, self.on_grid_click)
                self.main_grid.Add(button, pos=(i+row_offset, j+col_offset), flag=wx.ALL|wx.EXPAND, border=0)
                self.button_list[i].append(button)
                # Add separators to make it look more like a sudoku
                # board.
                if j % 3 == 2 and j != 8:
                    col_offset += 1
                    if i % 3 == 0:
                        self.main_grid.Add(wx.StaticLine(self.panel, style=wx.LI_VERTICAL),
                                           pos=(i+row_offset, j+col_offset),
                                           span=(3, 0))

                if i % 3 == 2 and j == 8:
                    row_offset += 1
                    self.main_grid.Add(wx.StaticLine(self.panel, style=wx.LI_HORIZONTAL),
                                       pos=(i+row_offset, j+col_offset),
                                       span=(0, 11))

        # Add a separator between the Sudoku grid and the controls.
        grid_control_separator = wx.StaticLine(self.panel, style=wx.LI_HORIZONTAL)
        self.master_sizer.Add(grid_control_separator, 0, wx.ALL|wx.EXPAND, 5)

        # Add the controls grid (row of buttons).
        self.selection_button_grid = wx.GridSizer(10, 1, 0)
        self.master_sizer.Add(self.selection_button_grid, 0, wx.ALL|wx.EXPAND, 0)

        self.selection_button_list = []
        control_buttons = ['1', '2', '3', '4', '5', '6', '7', '8', '9', ' ']
        for i, label in enumerate(control_buttons):
            button = wx.Button(self.panel, id=100+i, label=label, style=wx.BU_EXACTFIT)
            button.Bind(wx.EVT_BUTTON, self.select_number)
            self.selection_button_grid.Add(button, 0, wx.ALL|wx.EXPAND, 5)
            self.selection_button_list.append(button)

        # Add the "Solve" button.
        self.solve_button = wx.Button(self.panel, label="Solve!")
        self.solve_button.Bind(wx.EVT_BUTTON, self.on_solve)
        self.master_sizer.Add(self.solve_button, 0, wx.ALL|wx.CENTER, 5)

        self.panel.SetSizer(self.master_sizer)

        self.Show()

    def select_number(self, event):
        """
        Update the highlighted grid cell based on the control button that
        was clicked.

        """
        if self.highlighted_button is not None:
            if event.Id != 109:
                self.highlighted_button.SetLabel(str(event.Id - 99))
            else:
                self.highlighted_button.SetLabel(' ')

    def on_grid_click(self, event):
        """Highlight/unhighlight the grid cell that was clicked."""
        if self.highlighted_button is None:
            self.highlighted_button = self.button_list[event.Id // 9][event.Id % 9]
            self.highlighted_button.SetBackgroundColour(wx.Colour(0, 130, 0))
        elif self.highlighted_button is self.button_list[event.Id // 9][event.Id % 9]:
            self.highlighted_button.SetBackgroundColour(wx.NullColour)
            self.highlighted_button = None
        else:
            self.highlighted_button.SetBackgroundColour(wx.NullColour)
            self.highlighted_button = self.button_list[event.Id // 9][event.Id % 9]
            self.highlighted_button.SetBackgroundColour(wx.Colour(0, 130, 0))

    def on_solve(self, event):
        """Solve the Sudoku based on the original values given."""
        my_board = self.sudoku_board

        # Go through the board and fill the cells whose only option is
        # a single valid number.
        keep_going = True
        while keep_going:
            keep_going = False
            for i in range(9):
                for j in range(9):
                    if my_board.numbers_tried[(i, j)] is not None and len(my_board.check(i, j)) == 1:
                        my_board.insert(i, j, my_board.check(i, j).pop())
                        my_board.numbers_tried[(i, j)] = None
                        wx.CallAfter(self.update_cell, i, j, my_board.cell_value(i, j))
                        wx.SafeYield()
                        keep_going = True

        i = 0
        j = 0
        while i < self.NUM_GRID_ROWS and j < self.NUM_GRID_COLS:
            i, j = self.fill_cell(i, j, my_board)

        for row in self.button_list:
            for button in row:
                button.SetBackgroundColour(wx.NullColour)

        if check_solution(my_board.game_board):
            print("Solution is valid!")

    def fill_cell(self, i, j, my_board):
        """
        Fill the cell and keep moving forward if a valid value can be
        found. Otherwise, keep the cell empty and move backwards. If
        the cell was 'given', move over it without altering its value.

        """
        global direction
        
        # This cell was 'given'. Just move over it.
        if my_board.numbers_tried[(i, j)] is None:
            return move(i, j)

        else:
            # Try to find a number that works.
            valid_numbers = my_board.check(i, j)
            if valid_numbers:
                my_board.insert(i, j, valid_numbers.pop())
                wx.CallAfter(self.update_cell, i, j, my_board.cell_value(i, j))
                wx.SafeYield()
                direction = 'f'
                return move(i, j)

            else:
                direction = 'b'
                my_board.reset_cell(i, j)
                wx.CallAfter(self.update_cell, i, j, my_board.cell_value(i, j))
                wx.SafeYield()
                return move(i, j)

    def update_cell(self, i, j, num):
        """
        Update the number in the cell and the color of the cell as the
        algorithm progresses.

        """
        self.button_list[i][j].SetLabel(str(num))
        if str(num) == ' ':
            self.button_list[i][j].SetBackgroundColour(wx.Colour(130, 0, 0))
        else:
            self.button_list[i][j].SetBackgroundColour(wx.Colour(0, 130, 0))

if __name__ == '__main__':
    app = wx.App()
    frame = MyFrame()
    app.MainLoop()



