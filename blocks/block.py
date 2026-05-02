import pygame
from .base_block import BaseBlock

class Wall(BaseBlock):
    def __init__(self, x, y, size=100):
        super().__init__(x, y, size)

    def draw(self, surface):
        super().draw(surface)
        
        # Moderní high-tech vzhled zdi
        wall_rect = self.rect.inflate(-20, -20)
        
        # Stín / Základna bloku
        pygame.draw.rect(surface, (20, 20, 25), self.rect.inflate(-10, -10), border_radius=8)
        
        # Hlavní tělo s moderním tmavým tónem
        pygame.draw.rect(surface, (45, 45, 55), wall_rect, border_radius=8)
        
        # Vnější tech-rámeček
        pygame.draw.rect(surface, (80, 80, 100), wall_rect, 2, border_radius=8)
        
        # Vnitřní design překážky (např. diagonální chlazení / varovný kříž)
        pygame.draw.line(surface, (60, 60, 75), wall_rect.topleft, wall_rect.bottomright, 4)
        pygame.draw.line(surface, (60, 60, 75), wall_rect.topright, wall_rect.bottomleft, 4)
        
        # Středový uzel překážky
        pygame.draw.circle(surface, (80, 80, 100), wall_rect.center, 8)
        pygame.draw.circle(surface, (30, 30, 40), wall_rect.center, 4)

    def interact_with_beam(self, beam_dir, color):
        # Zeď paprsek nepustí dál, vrací None a paprsek na zdi zanikne
        return None