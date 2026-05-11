import pygame
from .base_block import BaseBlock

class Mirror(BaseBlock):
    def __init__(self, x, y, orientation=0, size=100):
        super().__init__(x, y, size)
        # orientation 0: \ , orientation 1: /
        self.orientation = orientation 

    def draw(self, surface):
        super().draw(surface)
        
        # Pokročilá Tech základna (Grid / chlazení)
        bg_rect = self.rect.inflate(-15, -15)
        pygame.draw.rect(surface, (20, 20, 25), bg_rect, border_radius=8)
        pygame.draw.rect(surface, (50, 50, 70), bg_rect, 2, border_radius=8)
        for i in range(1, 6):
            pygame.draw.line(surface, (30, 30, 40), (bg_rect.left, bg_rect.top + i*15), (bg_rect.right, bg_rect.top + i*15), 3)

        mirror_color = (150, 220, 255)
        frame_color = (100, 100, 120)
        
        # Obrovský odrazový plát roztažený přes celou šířku
        offset = 12 
        if self.orientation == 0: # \
            start, end = (self.rect.left + offset, self.rect.top + offset), (self.rect.right - offset, self.rect.bottom - offset)
        else:
            start, end = (self.rect.left + offset, self.rect.bottom - offset), (self.rect.right - offset, self.rect.top + offset)
            
        # Mechanické ukotvení a stín
        pygame.draw.line(surface, (15, 15, 20), start, end, 44)
        pygame.draw.line(surface, frame_color, start, end, 36)
        
        # Vlastní sklo (holografické/zářivé)
        pygame.draw.line(surface, mirror_color, start, end, 18)
        pygame.draw.line(surface, (255, 255, 255), start, end, 6)
        
        # Centrální rotační kloub
        pygame.draw.circle(surface, (25, 25, 30), self.rect.center, 22)
        pygame.draw.circle(surface, frame_color, self.rect.center, 22, 4)
        pygame.draw.circle(surface, mirror_color, self.rect.center, 10)

    def on_click(self):
        # Při kliknutí na zrcadlo se přepne orientace (natočí se o 90°)
        self.orientation = (self.orientation + 1) % 2

    def interact_with_beam(self, beam_dir, color):
        # beam_dir: 0: UP, 1: RIGHT, 2: DOWN, 3: LEFT
        
        if self.orientation == 0: # \
            if beam_dir == 0: return 3
            if beam_dir == 1: return 2
            if beam_dir == 2: return 1
            if beam_dir == 3: return 0
        else:                     # /
            if beam_dir == 0: return 1
            if beam_dir == 1: return 0
            if beam_dir == 2: return 3
            if beam_dir == 3: return 2
            
        return None