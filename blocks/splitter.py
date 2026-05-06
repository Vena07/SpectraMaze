import pygame
from .base_block import BaseBlock

class Splitter(BaseBlock):
    def __init__(self, x, y, orientation=0, size=100):
        super().__init__(x, y, size)
        # 0: štěpí do vertikály (Nahoru/Dolů), 1: štěpí do horizontály (Doleva/Doprava)
        self.orientation = orientation % 2

    def on_click(self):
        self.orientation = (self.orientation + 1) % 2

    def draw(self, surface):
        super().draw(surface)
        
        # Tech základna
        bg_rect = self.rect.inflate(-20, -20)
        pygame.draw.rect(surface, (30, 30, 40), bg_rect, border_radius=12)
        pygame.draw.rect(surface, (60, 60, 80), bg_rect, 2, border_radius=12)
        
        color = (255, 200, 100) # Zlatavá barva pro odlišení od modrých zrcadel
        
        center = self.rect.center
        c_size = self.size // 3
        pts = [
            (center[0], center[1] - c_size), (center[0] + c_size, center[1]),
            (center[0], center[1] + c_size), (center[0] - c_size, center[1])
        ]
        
        pygame.draw.polygon(surface, (40, 30, 20), pts)
        pygame.draw.polygon(surface, color, pts, 3)
        
        # Výstupní kanály (značky štěpení z jádra)
        offset = self.size // 2 - 5
        if self.orientation == 0: # Štěpí Nahoru a Dolů
            pygame.draw.line(surface, color, (center[0], center[1] - 15), (center[0], center[1] - offset), 6)
            pygame.draw.line(surface, color, (center[0], center[1] + 15), (center[0], center[1] + offset), 6)
            pygame.draw.circle(surface, (255, 255, 255), (center[0], center[1] - offset), 4)
            pygame.draw.circle(surface, (255, 255, 255), (center[0], center[1] + offset), 4)
        else: # Štěpí Doleva a Doprava
            pygame.draw.line(surface, color, (center[0] - 15, center[1]), (center[0] - offset, center[1]), 6)
            pygame.draw.line(surface, color, (center[0] + 15, center[1]), (center[0] + offset, center[1]), 6)
            pygame.draw.circle(surface, (255, 255, 255), (center[0] - offset, center[1]), 4)
            pygame.draw.circle(surface, (255, 255, 255), (center[0] + offset, center[1]), 4)

    def interact_with_beam(self, beam_dir, color):
        # Štěpí paprsek pouze na 2 strany kolmo na směr letu (rovně už nepropouští)
        if self.orientation == 0:
            if beam_dir in (1, 3): return [0, 2] # Jde zleva/zprava -> štěpí nahoru a dolů
            return None
        else:
            if beam_dir in (0, 2): return [1, 3] # Jde shora/zdola -> štěpí doleva a doprava
            return None