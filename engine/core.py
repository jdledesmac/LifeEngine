import pygame
from .input import InputManager

class Engine:
    def __init__(self, width=800, height=600, title="Python Graphics Engine"):
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        self.running = True
        self.input_manager = InputManager()
        self.objects = []

    def add_object(self, obj):
        self.objects.append(obj)

    def run(self):
        while self.running:
            # Calcular Delta Time (dt)
            dt = self.clock.tick(60) / 1000.0
            
            # Input
            self.input_manager.update()
            if self.input_manager.quit_requested:
                self.running = False
            
            # Update
            for obj in self.objects:
                obj.update(dt)
            
            # Draw
            self.screen.fill((0, 0, 0)) # Limpiar pantalla con negro
            for obj in self.objects:
                obj.draw(self.screen)
            
            pygame.display.flip()

        pygame.quit()
