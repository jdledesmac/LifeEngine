import pygame

class InputManager:
    def __init__(self):
        self.keys = pygame.key.get_pressed()
        self.quit_requested = False

    def update(self):
        # Actualizamos el estado de las teclas
        self.keys = pygame.key.get_pressed()
        
        # Procesamos eventos de la cola
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit_requested = True
    
    def is_key_pressed(self, key_code):
        if key_code < len(self.keys):
            return self.keys[key_code]
        return False
