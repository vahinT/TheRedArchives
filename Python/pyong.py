import pygame

# Initialize Pygame
pygame.init()

# Set screen dimensions
screen_width = 800
screen_height = 600
screen = pygame.display.set_mode((screen_width, screen_height))

# Set caption and icon
pygame.display.set_caption("Pong")
#icon = pygame.image('C:\Users\Akhila Agencies\Desktop\ ball.png')  # Replace with your desired icon path
#pygame.display.set_icon(icon)

# Colors
white = (255, 255, 255)
black = (0, 0, 0)

# Player paddles
paddle_width = 10
paddle_height = 5
paddle_speed = 5

player1_x = 20
player1_y = screen_height // 2 - paddle_height // 2
player2_x = screen_width - 30
player2_y = screen_height // 2 - paddle_height // 2

# Ball
ball_radius = 10
ball_speed = 5
ball_x = screen_width // 2
ball_y = screen_height // 2
ball_dx = ball_speed
ball_dy = ball_speed

# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Player movement
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w]:
        player1_y -= paddle_speed
    if keys[pygame.K_s]:
        player1_y += paddle_speed
    if keys[pygame.K_UP]:
        player2_y -= paddle_speed
    if keys[pygame.K_DOWN]:
        player2_y += paddle_speed

    # Ball movement
    ball_x += ball_dx
    ball_y += ball_dy

    # Ball collision with walls
    if ball_y <= 0 or ball_y >= screen_height - ball_radius:
        ball_dy = -ball_dy

    # Ball collision with paddles
    if ball_x <= player1_x + paddle_width and ball_y >= player1_y and ball_y <= player1_y + paddle_height:
        ball_dx = -ball_dx
    if ball_x >= player2_x - paddle_width and ball_y >= player2_y and ball_y <= player2_y + paddle_height:
        ball_dx = -ball_dx

    # Check for game over
    if ball_x <= 0 or ball_x >= screen_width:
        # Display game over message and reset game
        font = pygame.font.Font(None, 36)
        if ball_x <= 0:
            text = font.render("Player 2 wins!", True, white)
        else:
            text = font.render("Player 1 wins!", True, white)
        text_rect = text.get_rect(center=(screen_width // 2, screen_height // 2))
        screen.fill(black)
        screen.blit(text, text_rect)
        pygame.display.flip()
        pygame.time.wait(2000)  # Wait for 2 seconds
        running = False
        # Reset game state if desired

    # Draw objects
    screen.fill(black)
    pygame.draw.rect(screen, white, (player1_x, player1_y, paddle_width, paddle_height))
    pygame.draw.rect(screen, white, (player2_x, player2_y, paddle_width, paddle_height))
    pygame.draw.circle(screen, white, (ball_x, ball_y), ball_radius)
    pygame.display.flip()

# Quit Pygame
pygame.quit()
quit()
