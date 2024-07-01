import pygame
import sys

ROWS = 6
COLS = 7
WIN = 4

# Defining symbols for players
HUMAN = 1
AI = -1
EMPTY = 0

BLACK = (0, 0, 0)
GREY = (238, 237, 237)
RED = (215, 19, 19)
BLUE = (0, 121, 255)
YELLOW = (240, 222, 54)

DISC_SIZE = 80
DISC_GAP = 5
MARGIN = 2 * DISC_GAP
FONT_SIZE = 60
BOARD_WIDTH = COLS * (DISC_SIZE + DISC_GAP) + MARGIN
BOARD_HEIGHT = ROWS * (DISC_SIZE + DISC_GAP) + MARGIN

# Initializing alpha and beta values
INFINITY = float("inf")
ALPHA = -INFINITY
BETA = INFINITY

pygame.init()
window = pygame.display.set_mode((BOARD_WIDTH, BOARD_HEIGHT))
pygame.display.set_caption("Connect Four")
clock = pygame.time.Clock()

font = pygame.font.SysFont("Calibri", FONT_SIZE)

# Creating and initializing game board with zeros
board = []
for i in range(ROWS):
    row = []
    for j in range(COLS):
        row.append(EMPTY)
    board.append(row)


current_player = HUMAN
game_state = "running"  # Variable to store the game state (running or over)
game_result = None  # Variable to store the game result (win, lose, draw or None)


def draw_board():
    window.fill(GREY)

    pygame.draw.rect(window, BLUE, (0, 0, BOARD_WIDTH, BOARD_HEIGHT))

    # Loop for drawing colored discs on the board
    for row in range(ROWS):
        for col in range(COLS):
            x = MARGIN + col * (DISC_SIZE + DISC_GAP) + DISC_SIZE // 2
            y = MARGIN + row * (DISC_SIZE + DISC_GAP) + DISC_SIZE // 2
            r = DISC_SIZE // 2 - DISC_GAP // 2

            if board[row][col] == HUMAN:
                pygame.draw.circle(window, RED, (x, y), r)
            elif board[row][col] == AI:
                pygame.draw.circle(window, YELLOW, (x, y), r)
            else:
                pygame.draw.circle(window, GREY, (x, y), r)

    # Check the game state and result
    if game_state == "over":
        if game_result == "win":
            text = font.render("You win!", True, BLACK)
        elif game_result == "lose":
            text = font.render("You lose!", True, BLACK)
        elif game_result == "draw":
            text = font.render("Draw!", True, BLACK)

        # Draws the text rectangle and centers it on the window
        text_rect = text.get_rect()
        text_rect.center = (BOARD_WIDTH // 2, BOARD_HEIGHT // 2)
        window.blit(text, text_rect)


def is_full():
    for col in range(COLS):
        if board[0][col] == EMPTY:
            return False
    return True


def is_winner(player):
    for row in range(ROWS):
        for col in range(COLS):
            # Checks if the current slot belongs to the player
            if board[row][col] == player:
                # Check horizontal line
                if col + WIN <= COLS:
                    # Counter to keep track of horizontal discs
                    h_count = 0
                    # Loop through each horizontal slot
                    for i in range(WIN):
                        # Check if the next slot belongs to the player and increment it
                        if board[row][col + i] == player:
                            h_count += 1

                    # Check if the counter is equal to the number of discs required to win
                    if h_count == WIN:
                        return True

                # Checks vertical line
                if row + WIN <= ROWS:
                    # Counter to keep track of vertical discs
                    v_count = 0
                    # Loop through each vertical slot
                    for i in range(WIN):
                        # Check if the next slot belongs to the player and increment it
                        if board[row + i][col] == player:
                            v_count += 1

                    # Check if the counter is equal to the number of discs required to win
                    if v_count == WIN:
                        return True

                # Check diagonal win (positive slope)
                if row + WIN <= ROWS and col + WIN <= COLS:
                    # Initialize a counter for diagonal discs
                    d_count = 0
                    # Loop through each diagonal slot
                    for i in range(WIN):
                        # Check if the slot belongs to the player and increment
                        if board[row + i][col + i] == player:
                            d_count += 1

                    # Check if the counter is equal to the number of discs required to win
                    if d_count == WIN:
                        return True

                # Check diagonal win (negative slope)
                if row - WIN >= -1 and col + WIN <= COLS:
                    # Initialize a counter for diagonal discs
                    d_count = 0
                    # Loop through each diagonal slot
                    for i in range(WIN):
                        # Check if the slot belongs to the player and increment
                        if board[row - i][col + i] == player:
                            d_count += 1

                    # Check if the counter is equal to the number of discs required to win
                    if d_count == WIN:
                        # Return True if there is a diagonal win (negative slope)
                        return True

    # Return False if there is no winner
    return False


# Function to generate all possible moves for a given board state and player


def generate_moves(board, player):
    # Initialize an empty list to store the moves
    moves = []
    # Loop through each column of the board
    for col in range(COLS):
        # Check if the top row of the column is empty
        if board[0][col] == EMPTY:
            # Loop through each row of the column from bottom to top
            for row in reversed(range(ROWS)):
                # Check if the current slot is empty
                if board[row][col] == EMPTY:
                    # Create a copy of the board
                    new_board = [row[:] for row in board]
                    # Drop the player's disc into the empty slot
                    new_board[row][col] = player
                    # Append the move to the list of moves
                    moves.append((col, new_board))
                    # Break the loop as only one disc can be dropped per column
                    break

    # Return the list of moves
    return moves


# Create a function to evaluate how good a board state is for each player using a scoring heuristic


def evaluate(board):
    # Initialize the score to zero
    score = 0
    # Loop through each row and column of the board
    for row in range(ROWS):
        for col in range(COLS):
            # Check if the current slot is not empty
            if board[row][col] != EMPTY:
                # Check horizontal line
                if col + WIN <= COLS:
                    # Initialize counters for red and blue discs
                    red_count = 0
                    yellow_count = 0
                    # Loop through each horizontal slot
                    for i in range(WIN):
                        # Check if the slot is red or blue and increment the corresponding counter
                        if board[row][col + i] == HUMAN:
                            red_count += 1
                        elif board[row][col + i] == AI:
                            yellow_count += 1

                    # Calculate the line value based on the number of discs in the line (more discs = larger value)
                    if red_count == 0 and yellow_count > 0:
                        line_value = 10 ** (yellow_count - 1) + 10
                    elif red_count > 0 and yellow_count == 0:
                        line_value = -(10 ** (red_count - 1)) + 10
                    elif red_count > yellow_count:
                        line_value = 1
                    elif red_count > yellow_count:
                        line_value = -1
                    else:
                        line_value = 0

                    # Add the line value to the score
                    score += line_value

                # Check vertical line
                if row + WIN <= ROWS:
                    # Initialize counters for red and blue discs
                    red_count = 0
                    yellow_count = 0
                    # Loop through each vertical slot
                    for i in range(WIN):
                        # Check if the slot is red or blue and increment the corresponding counter
                        if board[row + i][col] == HUMAN:
                            red_count += 1
                        elif board[row + i][col] == AI:
                            yellow_count += 1

                    # Calculate the line value based on the number of discs in the line (more discs = larger value)
                    if red_count == 0 and yellow_count > 0:
                        line_value = 10 ** (yellow_count - 1) + 10
                    elif red_count > 0 and yellow_count == 0:
                        line_value = -(10 ** (red_count - 1)) + 10
                    elif red_count > yellow_count:
                        line_value = 1
                    elif red_count > yellow_count:
                        line_value = -1
                    else:
                        line_value = 0

                    # Add the line value to the score
                    score += line_value

                # Check diagonal line (positive slope)
                if row + WIN <= ROWS and col + WIN <= COLS:
                    # Initialize counters for red and blue discs
                    red_count = 0
                    yellow_count = 0
                    # Loop through each diagonal slot
                    for i in range(WIN):
                        # Check if the slot is red or blue and increment the corresponding counter
                        if board[row + i][col + i] == HUMAN:
                            red_count += 1
                        elif board[row + i][col + i] == AI:
                            yellow_count += 1

                    # Calculate the line value based on the number of discs in the line (more discs = larger value)
                    if red_count == 0 and yellow_count > 0:
                        line_value = 10 ** (yellow_count - 1) + 10
                    elif red_count > 0 and yellow_count == 0:
                        line_value = -(10 ** (red_count - 1)) + 10
                    elif red_count > yellow_count:
                        line_value = 1
                    elif red_count > yellow_count:
                        line_value = -1
                    else:
                        line_value = 0

                    # Add the line value to the score
                    score += line_value

                # Check diagonal line (negative slope)
                if row - WIN >= -1 and col + WIN <= COLS:
                    # Initialize counters for red and blue discs
                    red_count = 0
                    yellow_count = 0
                    # Loop through each diagonal slot
                    for i in range(WIN):
                        # Check if the slot is red or blue and increment the corresponding counter
                        if board[row - i][col + i] == HUMAN:
                            red_count += 1
                        elif board[row - i][col + i] == AI:
                            yellow_count += 1

                    # Calculate the line value based on the number of discs in the line (more discs = larger value)
                    if red_count == 0 and yellow_count > 0:
                        line_value = 10 ** (yellow_count - 1) + 10
                    elif red_count > 0 and yellow_count == 0:
                        line_value = -(10 ** (red_count - 1)) + 10
                    elif red_count > yellow_count:
                        line_value = 1
                    elif red_count > yellow_count:
                        line_value = -1
                    else:
                        line_value = 0

                    # Add the line value to the score
                    score += line_value

    # Return the score
    return score


# Create a function to implement the alpha beta pruning algorithm to find the best move for the AI player


def alpha_beta(board, depth, alpha, beta, player):
    # Check if the game is over or the depth limit is reached
    if is_winner(HUMAN) or is_winner(AI) or is_full() or depth == 0:
        # Return the score and None as the move
        return (evaluate(board), None)

    # Check if the player is the AI (maximizing player)
    if player == AI:
        # Initialize the best score to negative infinity and the best move to None
        best_score = -INFINITY
        best_move = None
        # Generate all possible moves for the AI player
        moves = generate_moves(board, AI)
        # Loop through each move
        for move in moves:
            # Get the column and the new board state after making the move
            col, new_board = move
            # Recursively call the alpha beta function with the new board state, decreased depth, and switched player
            score, _ = alpha_beta(new_board, depth - 1, alpha, beta, HUMAN)
            # Check if the score is better than the best score
            if score > best_score:
                # Update the best score and the best move
                best_score = score
                best_move = col

            # Update the alpha value with the maximum of alpha and best score
            alpha = max(alpha, best_score)
            # Check if alpha is greater than or equal to beta (pruning condition)
            if alpha >= beta:
                # Break the loop as further exploration is not needed
                break

        # Return the best score and the best move
        return (best_score, best_move)

    # Check if the player is the human (minimizing player)
    elif player == HUMAN:
        # Initialize the best score to positive infinity and the best move to None
        best_score = INFINITY
        best_move = None
        # Generate all possible moves for the human player
        moves = generate_moves(board, HUMAN)
        # Loop through each move
        for move in moves:
            # Get the column and the new board state after making the move
            col, new_board = move
            # Recursively call the alpha beta function with the new board state, decreased depth, and switched player
            score, _ = alpha_beta(new_board, depth - 1, alpha, beta, AI)
            # Check if the score is better than the best score
            if score < best_score:
                # Update the best score and the best move
                best_score = score
                best_move = col

            # Update the beta value with the minimum of beta and best score
            beta = min(beta, best_score)
            # Check if alpha is greater than or equal to beta (pruning condition)
            if alpha >= beta:
                # Break the loop as further exploration is not needed
                break

        # Return the best score and the best move
        return (best_score, best_move)


# Create a main loop to run until the user quits
running = True

while running:

    # Process events (keystrokes, mouse clicks, etc.)
    for event in pygame.event.get():
        # Check if the event is the quit event
        if event.type == pygame.QUIT:
            # exit the game
            sys.exit()

        # Check if the event is a mouse click
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # Check if the game state is running and the current player is human
            if game_state == "running" and current_player == HUMAN:
                # Get the mouse position
                mouse_x, mouse_y = pygame.mouse.get_pos()
                # Check if the mouse position is within the board area
                if mouse_x <= BOARD_WIDTH and mouse_y <= BOARD_HEIGHT:
                    # Calculate the column index based on the mouse position
                    col = (mouse_x) // (DISC_SIZE + DISC_GAP)
                    # Check if the top row of the column is empty
                    if board[0][col] == EMPTY:
                        # Loop through each row of the column from bottom to top
                        for row in range(ROWS - 1, -1, -1):
                            # Check if the current slot is empty
                            if board[row][col] == EMPTY:
                                # Drop the human disc into the empty slot
                                board[row][col] = HUMAN
                                # Switch the current player to AI
                                current_player = AI
                                # Break the loop as only one disc can be dropped per column
                                break

    # Update game logic

    # Check if the game state is running
    if game_state == "running":
        # Check if there is a winner or the board is full
        if is_winner(HUMAN):
            # Set the game state to over and the game result to win
            game_state = "over"
            game_result = "win"
        elif is_winner(AI):
            # Set the game state to over and the game result to lose
            game_state = "over"
            game_result = "lose"
        elif is_full():
            # Set the game state to over and the game result to draw
            game_state = "over"
            game_result = "draw"
        else:
            # Check if the current player is AI
            if current_player == AI:
                # Set a difficulty level as the depth limit for alpha beta pruning (higher = harder)
                difficulty = 6
                # Call the alpha beta function to find the best move for the AI player
                _, best_move = alpha_beta(board, difficulty, ALPHA, BETA, AI)
                # Check if the best move is not None
                if best_move is not None:
                    # Loop through each row of the column from bottom to top
                    for row in reversed(range(ROWS)):
                        # Check if the current slot is empty
                        if board[row][best_move] == EMPTY:
                            # Drop the AI disc into the empty slot
                            board[row][best_move] = AI
                            # Switch the current player to human
                            current_player = HUMAN
                            # Break the loop as only one disc can be dropped per column
                            break

    # Draw everything on the window

    draw_board()

    # Update the window

    pygame.display.flip()

    # Set the frame rate

    clock.tick(60)

# Quit pygame and exit

pygame.quit()
