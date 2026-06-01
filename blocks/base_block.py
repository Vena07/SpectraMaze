import pygame
import math

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

    def get_breathing_pulse(self, cycle_time=3000, intensity=0.1):
        """Vrací subtle breathing pulse (0 to intensity) pro elegantní animace"""
        time_ms = pygame.time.get_ticks()
        pulse = (math.sin(time_ms / cycle_time * 2 * math.pi) + 1) / 2.0  # 0-1 range
        return pulse * intensity

    def on_click(self):
        # Zástupná metoda pro interakci myší
        pass