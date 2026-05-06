import pygame
import math
from .base_block import BaseBlock

class Button(BaseBlock):
    def __init__(self, x, y, size=100):
        super().__init__(x, y, size)
        self.linked_doors = []
        self.link_id = 0
        self.is_pressed = False

    def draw(self, surface):
        super().draw(surface)
        
        center = self.rect.center
        time_ms = pygame.time.get_ticks()
        
        # Osmiúhelníková sci-fi základna
        b_size = self.size // 2 - 15
        pts = [
            (center[0] - b_size, center[1] - b_size//2), (center[0] - b_size//2, center[1] - b_size),
            (center[0] + b_size//2, center[1] - b_size), (center[0] + b_size, center[1] - b_size//2),
            (center[0] + b_size, center[1] + b_size//2), (center[0] + b_size//2, center[1] + b_size),
            (center[0] - b_size//2, center[1] + b_size), (center[0] - b_size, center[1] + b_size//2),
        ]
        pygame.draw.polygon(surface, (25, 25, 30), pts)
        pygame.draw.polygon(surface, (80, 80, 100), pts, 2)
        
        # Vodivé linky z okrajů do středu
        line_color = (0, 150, 80) if self.is_pressed else (100, 30, 30)
        pygame.draw.line(surface, line_color, (center[0], center[1] - b_size), center, 4)
        pygame.draw.line(surface, line_color, (center[0], center[1] + b_size), center, 4)
        pygame.draw.line(surface, line_color, (center[0] - b_size, center[1]), center, 4)
        pygame.draw.line(surface, line_color, (center[0] + b_size, center[1]), center, 4)
        
        # Pulzující senzorové pole (vnitřní kruh)
        pulse = abs(math.sin(time_ms * 0.005)) * 4 if self.is_pressed else 0
        color = (0, 255, 150) if self.is_pressed else (200, 50, 50)
        pygame.draw.circle(surface, (15, 15, 20), center, self.size // 4)
        pygame.draw.circle(surface, color, center, int(self.size // 4 - 4 + pulse), max(2, int(4 - pulse//2)))
        
        if self.is_pressed:
            # Symbol aktivace
            pygame.draw.rect(surface, (255, 255, 255), (center[0]-6, center[1]-6, 12, 12), 2, border_radius=2)
            pygame.draw.circle(surface, (255, 255, 255), center, 3)
        else:
            # Symbol křížku (neaktivní)
            pygame.draw.line(surface, (255, 100, 100), (center[0]-6, center[1]-6), (center[0]+6, center[1]+6), 3)
            pygame.draw.line(surface, (255, 100, 100), (center[0]-6, center[1]+6), (center[0]+6, center[1]-6), 3)

    def interact_with_beam(self, beam_dir, color):
        self.is_pressed = True
        return beam_dir