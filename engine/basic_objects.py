import pygame

class GameObject:
    def __init__(self, x, y, width, height, color=(255, 255, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color

    def update(self, dt):
        """
        Método para actualizar el estado del objeto.
        dt: Delta time en segundos.
        """
        pass

    def draw(self, surface):
        """
        Método para dibujar el objeto en la superficie dada.
        """
        pygame.draw.rect(surface, self.color, self.rect)
