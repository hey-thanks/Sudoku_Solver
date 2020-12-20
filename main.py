import wx
from random import randrange


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
print('Playing Game #{}'.format(index))


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
    valid_set = {'1', '2', '3', '4', '5', '6', '7', '8', '9'}
    for row in board:
        if set(row) != valid_set:
            return False
    return True


# Used during the backtracking algorithm.
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
            print('Win!')
            return 9, 9
    else:
        if j > 0:
            j -= 1
        elif i > 0:
            i -= 1
            j = 8
        else:
            print('No solution!')
            return 9, 9
    return i, j

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
    new_board = []
    for i in range(0, len(board), 3):
        for j in range(0, len(board[i]), 3):
            new_board.append([])
            new_board[-1].extend(board[j][i:i+3])
            new_board[-1].extend(board[j+1][i:i+3])
            new_board[-1].extend(board[j+2][i:i+3])
    return new_board

def check_violations(board):
    """
    Ensure that no row, column, or subgrid contains any duplicate
    values. Returns True if there are no violations.

    """
    subgrid_board = create_subgrids_to_rows_board(board)
    subgrid_board = [[elem for elem in row if elem != ' '] for row in subgrid_board]
    status = check_row_violations(subgrid_board)
    if status:
        rotated_board = create_rotated_board(board)
        rotated_board = [[elem for elem in row if elem != ' '] for row in rotated_board]
        status = check_row_violations(rotated_board)
    return status

def check_row_violations(board):
    """
    Ensure that each row of the given board does not contain any
    duplicate values. Returns True if there are no violations.

    """
    for row in board:
        if len(set(row)) != len(row):
            return False
    return True

def print_board(board):
    """Print the Sudoku board."""
    for row in board:
        print(row)

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

        self.button_list = []
        row_offset = 0
        for i in range(self.NUM_GRID_ROWS):
            self.button_list.append([])
            col_offset = 0
            for j in range(self.NUM_GRID_COLS):
                button = wx.Button(self.panel, id=i*9 + j, label=str(board[i][j]), style=wx.BU_EXACTFIT)
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

        # Add the 'Solve' button.
        self.solve_button = wx.Button(self.panel, label='Solve!')
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
        """
        Solve the Sudoku based on the values that are present on the
        board.

        """
        not_tried = dict()
        my_board = []
        for i, row in enumerate(self.button_list):
            my_board.append([])
            for j, button in enumerate(row):
                button_label = button.GetLabel()
                my_board[i].append(button_label)
                if button_label == ' ':
                    not_tried[(i, j)] = {'1', '2', '3', '4', '5', '6', '7', '8', '9'}
                else:
                    not_tried[(i, j)] = None

        i = 0
        j = 0
        while i < self.NUM_GRID_ROWS and j < self.NUM_GRID_COLS:
            i, j = self.fill_cell(i, j, my_board, not_tried)

        for row in self.button_list:
            for button in row:
                button.SetBackgroundColour(wx.NullColour)

        if check_solution(my_board):
            print('Solution is valid!')

    def fill_cell(self, i, j, my_board, not_tried):
        """
        Fill the cell and keep moving forward if a valid value can be
        found. Otherwise, keep the cell empty and move backwards. If
        the cell was 'given', move over it without altering its value.

        """
        global direction

        # This cell was 'given'. Just move over it.
        if not_tried[(i, j)] is None:
            return move(i, j)

        else:
            # Try to find a number that works.
            numbers_in_row = set(my_board[i])
            while not_tried[(i, j)] - numbers_in_row:
                my_board[i][j] = min(not_tried[(i, j)] - numbers_in_row)
                wx.CallAfter(self.update_cell, i, j, my_board[i][j])
                wx.SafeYield()
                not_tried[(i, j)].remove(my_board[i][j])
                status = check_violations(my_board)

                # A number that works was found. Move forward.
                if status:
                    direction = 'f'
                    return move(i, j)

            # We only make it to here if there is no number that works
            # in that cell. Reset the cell and move backward.
            not_tried[(i, j)] = {'1', '2', '3', '4', '5', '6', '7', '8', '9'}
            my_board[i][j] = ' '
            wx.CallAfter(self.update_cell, i, j, my_board[i][j])
            wx.SafeYield()
            direction = 'b'
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
