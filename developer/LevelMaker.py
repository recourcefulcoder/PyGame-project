import pygame
from os.path import exists


class Board:
    # создание поля
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.board = [["black"] * width for _ in range(height)]
        self.left = 0
        self.top = 0
        self.chosen_object = 'black'
        self.colors = {"black": (0, 0, 0), "red": (255, 0, 0), "grey": (128, 128, 128),
                       "brown": (94, 47, 13), "blue": (66, 170, 255), "white": (255, 255, 255),
                       "golden": (255, 215, 0)}
        self.cell_size = 30
        self.font = pygame.font.Font(None, 24)

    def set_view(self, left, top, cell_size):
        self.left = left
        self.top = top
        self.cell_size = cell_size

    def render(self, screen):
        for i in range(self.height):
            for j in range(self.width):
                pygame.draw.rect(screen, pygame.Color(255, 255, 255),
                                 ((j * self.cell_size + self.left, i * self.cell_size + self.top),
                                  (self.cell_size, self.cell_size)), width=1)
                if self.board[i][j] in self.colors.keys():
                    pygame.draw.rect(screen, pygame.Color(*self.colors[self.board[i][j]]),
                                     ((j * self.cell_size + self.left + 1, i * self.cell_size + self.top + 1),
                                      (self.cell_size - 2, self.cell_size - 2)))
                else:
                    screen.blit(self.font.render(self.board[i][j], True, (80, 200, 120)),
                                (j * self.cell_size + self.left + 1, i * self.cell_size + self.top + 1))

    def get_cell(self, mouse_pos):
        x = mouse_pos[0] - self.left
        y = mouse_pos[1] - self.top
        if 0 <= x <= self.cell_size * self.width and 0 <= y <= self.cell_size * self.height:
            column = x // self.cell_size
            row = y // self.cell_size
            return row, column
        return None

    def on_click(self, cell_coords):
        self.board[cell_coords[0]][cell_coords[1]] = self.chosen_object

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell is not None:
            self.on_click(cell)

    def change_field_size(self, width, height):
        self.width = width
        self.height = height

    def change_cell_size(self, cell_size):
        self.cell_size = cell_size


class ColorBoard(Board):
    def __init__(self, win_width):
        super().__init__(3, 3)
        self.board[0][0] = "black"
        self.board[0][1] = "red"
        self.board[0][2] = "grey"
        self.board[1][0] = "brown"
        self.board[1][1] = "blue"
        self.board[1][2] = "white"
        self.board[2][0] = "golden"
        self.board[2][1] = "1"
        self.current_checkpoint = 1
        self.cell_size = 20
        self.left = win_width - self.cell_size * 3

    def on_click(self, cell_coords):
        if cell_coords is not None:
            value = self.board[cell_coords[0]][cell_coords[1]]
            return value
        return None

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        return self.on_click(cell)


class ChangingCheckpoint(Board):
    def __init__(self):
        super().__init__(1, 2)
        self.board[0][0] = "Add"
        self.board[1][0] = "Del"
        self.set_view(35 * board.cell_size + 30, color_board.cell_size * 4, 30)
        self.font = pygame.font.Font(None, 16)

    def get_click(self, mouse_pos):
        cell = self.get_cell(mouse_pos)
        if cell is not None:
            return self.board[cell[0]][cell[1]]
        return None


if __name__ == '__main__':
    level = input("Введите номер уровня (1, 2 или 3): ")
    while not (level == '1' or level == '2' or level == '3'):
        level = input("Неверный формат ввода. Введите 1, 2 или 3: ")
    if level == '1':
        level = "first_level.txt"
    elif level == '2':
        level = "second_level.txt"
    else:
        level = "third_level.txt"
    level = "../data/levels/" + level
    pygame.init()
    pygame.display.set_caption("LevelMaker")
    size = width, height = 800, 610
    screen = pygame.display.set_mode(size)
    color_board = ColorBoard(width)
    board = Board(35, 30)
    board.cell_size = 20

    changing_checkpoint = ChangingCheckpoint()

    if exists(level):
        with open(level, mode='r') as level_file:
            value = level_file.readline()
            global_cnt = -1
            while value:
                global_cnt += 1
                cnt = 0
                for elem in value.split():
                    board.board[global_cnt][cnt] = elem
                    cnt += 1
                value = level_file.readline()
    pygame.display.flip()
    running = True
    mouse_pressed = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                with open(level, mode='w') as level_file:
                    for elem in board.board:
                        for elem1 in elem:
                            level_file.write(elem1 + ' ')
                        level_file.write('\n')
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pressed = True
                color = color_board.get_click(event.pos)
                board.get_click(event.pos)
                if color is not None:
                    board.chosen_object = color
                value = changing_checkpoint.get_click(event.pos)
                if value == "Add":
                    if board.chosen_object == color_board.board[2][1]:
                        board.chosen_object = str(int(color_board.board[2][1]) + 1)
                    color_board.board[2][1] = str(int(color_board.board[2][1]) + 1)

                elif value == "Del":
                    if color_board.board[2][1] > "1":
                        if board.chosen_object == color_board.board[2][1]:
                            board.chosen_object = str(int(color_board.board[2][1]) - 1)
                        color_board.board[2][1] = str(int(color_board.board[2][1]) - 1)
            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pressed = False
            if event.type == pygame.MOUSEMOTION:
                if mouse_pressed:
                    board.get_click(event.pos)
        screen.fill((0, 0, 0))
        board.render(screen)
        color_board.render(screen)
        changing_checkpoint.render(screen)
        pygame.display.flip()
