import pygame

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)

ROWS = 6
COLS = 7
WIN = 4

WINDOW_WIDTH = 650
WINDOW_HEIGHT = 600
MARGIN = 10

DISC_SIZE = 80
DISC_GAP = 10

BOARD_X = MARGIN
BOARD_Y = WINDOW_HEIGHT - (ROWS * (DISC_SIZE + DISC_GAP) + MARGIN)
BOARD_WIDTH = COLS * (DISC_SIZE + DISC_GAP) + MARGIN
BOARD_HEIGHT = ROWS * (DISC_SIZE + DISC_GAP) + MARGIN

HUMAN = 1
AI = -1
EMPTY = 0

INFINITY = float('inf')
ALPHA = -INFINITY
BETA = INFINITY

pygame.init()
window = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption('Connect Four')
clock = pygame.time.Clock()

font = pygame.font.SysFont('Arial', 32)

board = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]

current_player = HUMAN

game_state = 'running'

game_result = None

def draw_board():
    window.fill(BLACK)

    pygame.draw.rect(window, WHITE, (BOARD_X, BOARD_Y, BOARD_WIDTH, BOARD_HEIGHT))

    for row in range(ROWS):
        for col in range(COLS):
            x = BOARD_X + MARGIN + col * (DISC_SIZE + DISC_GAP) + DISC_SIZE // 2
            y = BOARD_Y + MARGIN + row * (DISC_SIZE + DISC_GAP) + DISC_SIZE // 2
            r = DISC_SIZE // 2 - DISC_GAP // 2

            pygame.draw.circle(window, BLACK, (x, y), r)

            if board[row][col] == HUMAN:
                pygame.draw.circle(window, RED, (x, y), r)
            elif board[row][col] == AI:
                pygame.draw.circle(window, BLUE, (x, y), r)

    if game_state == 'over':
        if game_result == 'win':
            text = font.render('You win!', True, YELLOW)
        elif game_result == 'lose':
            text = font.render('You lose!', True, YELLOW)
        elif game_result == 'draw':
            text = font.render('Draw!', True, YELLOW)

        text_rect = text.get_rect()
        text_rect.center = (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)

        window.blit(text, text_rect)

def is_full():
    for col in range(COLS):
        if board[0][col] == EMPTY:
            return False

    return True

def is_winner(player):
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] == player:
                if col + WIN <= COLS:
                    h_count = 0
                    for i in range(WIN):
                        if board[row][col + i] == player:
                            h_count += 1

                    if h_count == WIN:
                        return True

                if row + WIN <= ROWS:
                    v_count = 0
                    for i in range(WIN):
                        if board[row + i][col] == player:
                            v_count += 1

                    if v_count == WIN:
                        return True

                if row + WIN <= ROWS and col + WIN <= COLS:
                    d_count = 0
                    for i in range(WIN):
                        if board[row + i][col + i] == player:
                            d_count += 1

                    if d_count == WIN:
                        return True

                if row - WIN >= -1 and col + WIN <= COLS:
                    d_count = 0
                    for i in range(WIN):
                        if board[row - i][col + i] == player:
                            d_count += 1

                    if d_count == WIN:
                        return True

    return False

def generate_moves(board, player):
    moves = []
    for col in range(COLS):
        if board[0][col] == EMPTY:
            for row in range(ROWS - 1, -1, -1):
                if board[row][col] == EMPTY:
                    new_board = [row[:] for row in board]
                    new_board[row][col] = player
                    moves.append((col, new_board))
                    break

    return moves

def evaluate(board):
    score = 0
    for row in range(ROWS):
        for col in range(COLS):
            if board[row][col] != EMPTY:
                if col + WIN <= COLS:
                    red_count = 0
                    blue_count = 0
                    for i in range(WIN):
                        if board[row][col + i] == HUMAN:
                            red_count += 1
                        elif board[row][col + i] == AI:
                            blue_count += 1

                    if red_count == 0 and blue_count > 0:
                        line_value = 10 ** (blue_count - 1)
                    elif red_count > 0 and blue_count == 0:
                        line_value = -10 ** (red_count - 1)
                    else:
                        line_value = 0

                    score += line_value

                if row + WIN <= ROWS:
                    red_count = 0
                    blue_count = 0
                    for i in range(WIN):
                        if board[row + i][col] == HUMAN:
                            red_count += 1
                        elif board[row + i][col] == AI:
                            blue_count += 1

                    if red_count == 0 and blue_count > 0:
                        line_value = 10 ** (blue_count - 1)
                    elif red_count > 0 and blue_count == 0:
                        line_value = -10 ** (red_count - 1)
                    else:
                        line_value = 0

                    score += line_value

                if row + WIN <= ROWS and col + WIN <= COLS:
                    red_count = 0
                    blue_count = 0
                    for i in range(WIN):
                        if board[row + i][col + i] == HUMAN:
                            red_count += 1
                        elif board[row + i][col + i] == AI:
                            blue_count += 1

                    if red_count == 0 and blue_count > 0:
                        line_value = 10 ** (blue_count - 1)
                    elif red_count > 0 and blue_count == 0:
                        line_value = -10 ** (red_count - 1)
                    else:
                        line_value = 0

                    score += line_value

                if row - WIN >= -1 and col + WIN <= COLS:
                    red_count = 0
                    blue_count = 0
                    for i in range(WIN):
                        if board[row - i][col + i] == HUMAN:
                            red_count += 1
                        elif board[row - i][col + i] == AI:
                            blue_count += 1

                    if red_count == 0 and blue_count > 0:
                        line_value = 10 ** (blue_count - 1)
                    elif red_count > 0 and blue_count == 0:
                        line_value = -10 ** (red_count - 1)
                    else:
                        line_value = 0

                    score += line_value

    return score

def alpha_beta(board, depth, alpha, beta, player):
    if is_winner(HUMAN) or is_winner(AI) or is_full() or depth == 0:
        return (evaluate(board), None)

    if player == AI:
        best_score = -INFINITY
        best_move = None
        moves = generate_moves(board, AI)
        for move in moves:
            col, new_board = move
            score, _ = alpha_beta(new_board, depth - 1, alpha, beta, HUMAN)
            if score > best_score:
                best_score = score
                best_move = col

            alpha = max(alpha, best_score)
            if alpha >= beta:
                break

        return (best_score, best_move)

    elif player == HUMAN:
        best_score = INFINITY
        best_move = None
        moves = generate_moves(board, HUMAN)
        for move in moves:
            col, new_board = move
            score, _ = alpha_beta(new_board, depth - 1, alpha, beta, AI)
            if score < best_score:
                best_score = score
                best_move = col

            beta = min(beta, best_score)
            if alpha >= beta:
                break

        return (best_score, best_move)

running = True

while running:

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if game_state == 'running' and current_player == HUMAN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if BOARD_X <= mouse_x <= BOARD_X + BOARD_WIDTH and BOARD_Y <= mouse_y <= BOARD_Y + BOARD_HEIGHT:
                    col = (mouse_x - BOARD_X) // (DISC_SIZE + DISC_GAP)
                    if board[0][col] == EMPTY:
                        for row in range(ROWS - 1, -1, -1):
                            if board[row][col] == EMPTY:
                                board[row][col] = HUMAN
                                current_player = AI
                                break

    if game_state == 'running':
        if is_winner(HUMAN):
            game_state = 'over'
            game_result = 'win'
        elif is_winner(AI):
            game_state = 'over'
            game_result = 'lose'
        elif is_full():
            game_state = 'over'
            game_result = 'draw'
        else:
            if current_player == AI:
                difficulty =  5
                _, best_move = alpha_beta(board, difficulty, ALPHA, BETA, AI)
                if best_move is not None:
                    for row in range(ROWS - 1, -1, -1):
                        if board[row][best_move] == EMPTY:
                            board[row][best_move] = AI
                            current_player = HUMAN
                            break
                        
    draw_board()

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
