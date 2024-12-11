import pygame
from simulation import Simulation

def main():
    pygame.init()
    screen = pygame.display.set_mode((1250, 1250))
    pygame.display.set_caption("Virtual Ant Farm")
    clock = pygame.time.Clock()

    simulation = Simulation()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        simulation.update()
        simulation.render(screen)
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
