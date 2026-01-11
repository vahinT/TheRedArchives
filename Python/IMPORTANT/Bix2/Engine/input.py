import pygame


class InputState:
    def __init__(self):
        # movement axes
        self.forward = 0.0   # -1 back, +1 forward
        self.turn = 0.0      # -1 left, +1 right

        self.quit = False

        pygame.init()
        pygame.display.set_mode((1, 1))  # hidden dummy window

    def update(self):
        self.forward = 0.0
        self.turn = 0.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit = True

        keys = pygame.key.get_pressed()

        # forward / backward
        if keys[pygame.K_w]:
            self.forward += 1.0
        if keys[pygame.K_s]:
            self.forward -= 1.0

        # turn left / right
        if keys[pygame.K_a]:
            self.turn -= 1.0
        if keys[pygame.K_d]:
            self.turn += 1.0
