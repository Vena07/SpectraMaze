import pygame

class BaseBlock:
    def __init__(self, x, y, size=100):
        self.x = x
        self.y = y
        self.size = size
        self.rect = pygame.Rect(x * size, y * size, size, size)
        self.movable = False # Výchozí hodnota (přepisuje se při načítání)

    def draw(self, surface):
        # Původní neprůhledné pozadí (čtverec) je odstraněno, 
        # aby pod bloky prosvítala moderní animace částic z main.py!
        pass

    def draw_overlay(self, surface):
        # Vrchní vrstva bloku kreslená AŽ NA lasery (pro 3D efekt)
        pass

    def interact_with_beam(self, beam_dir, color):
        # Standardně blok paprsek pohltí
        return None
        
    def on_click(self):
        # Zástupná metoda pro interakci myší
        pass