import pygame
from .base_block import BaseBlock

class Filter(BaseBlock):
    def __init__(self, x, y, color, size=100):
        super().__init__(x, y, size)
        self.filter_color = color

    def draw(self, surface):
        super().draw(surface)
        
        bg_rect = self.rect.inflate(-15, -15)
        pygame.draw.rect(surface, (20, 20, 25), bg_rect, border_radius=8)
        pygame.draw.rect(surface, (100, 100, 120), bg_rect, 4, border_radius=8)
        
        glass_rect = self.rect.inflate(-35, -35)
        
        # Skleněná barevná výplň filtru
        pygame.draw.rect(surface, (int(self.filter_color[0]*0.4), int(self.filter_color[1]*0.4), int(self.filter_color[2]*0.4)), glass_rect)
        pygame.draw.rect(surface, self.filter_color, glass_rect, 3)
        
        # Odlesk skla
        pygame.draw.line(surface, (255, 255, 255), (glass_rect.left + 5, glass_rect.bottom - 5), (glass_rect.right - 5, glass_rect.top + 5), 2)

    def interact_with_beam(self, beam_dir, color):
        # Propustí dál jen tu část světla, která odpovídá barvě filtru.
        r = min(color[0], self.filter_color[0])
        g = min(color[1], self.filter_color[1])
        b = min(color[2], self.filter_color[2])
        
        if r < 100 and g < 100 and b < 100: return None # Pokud filtr sežral vše, paprsek končí
            
        return (beam_dir, (r, g, b))