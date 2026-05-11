import pygame
import math
from .base_block import BaseBlock

class Crystal(BaseBlock):
    def __init__(self, x, y, direction, color, size=100):
        super().__init__(x, y, size)
        self.direction = direction
        self.color = color

    def on_click(self):
        # Otočení směru krystalu o 90 stupňů
        self.direction = (self.direction + 1) % 4

    def draw(self, surface):
        super().draw(surface)
        
        # Tech základna
        bg_rect = self.rect.inflate(-15, -15)
        pygame.draw.rect(surface, (30, 30, 40), bg_rect, border_radius=12)
        pygame.draw.rect(surface, (60, 60, 80), bg_rect, 2, border_radius=12)
        
        # Zářivá pulzující aura krystalu
        time_ms = pygame.time.get_ticks() 
        pulse_alpha = int((math.sin(time_ms / 150.0) + 1) * 30 + 20) # 20-80 alpha
        
        # Vnější pulzující aura
        aura_radius = int(self.size / 2.2)
        glow_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*self.color, pulse_alpha), (self.size // 2, self.size // 2), aura_radius)
        surface.blit(glow_surf, self.rect.topleft, special_flags=pygame.BLEND_RGBA_ADD)
        
        # Extrémně masivní Tech Kanón (hlaveň)
        barrel_len = self.size // 2 - 2
        b_w = 26 # Širší hlaveň
        center = self.rect.center
        
        if self.direction == 0:   b_rect = pygame.Rect(center[0] - b_w//2, center[1] - barrel_len, b_w, barrel_len)
        elif self.direction == 1: b_rect = pygame.Rect(center[0], center[1] - b_w//2, barrel_len, b_w)
        elif self.direction == 2: b_rect = pygame.Rect(center[0] - b_w//2, center[1], b_w, barrel_len)
        elif self.direction == 3: b_rect = pygame.Rect(center[0] - barrel_len, center[1] - b_w//2, barrel_len, b_w)
        
        pygame.draw.rect(surface, (35, 35, 45), b_rect, border_radius=4)
        pygame.draw.rect(surface, (80, 80, 100), b_rect, 3, border_radius=4)
        
        charge_pulse = abs(math.sin(time_ms * 0.01)) * 0.5 + 0.5
        inner_b = b_rect.inflate(-8, -8)
        pygame.draw.rect(surface, (int(self.color[0]*charge_pulse), int(self.color[1]*charge_pulse), int(self.color[2]*charge_pulse)), inner_b, border_radius=2)

        # Mohutné Hexagonální jádro
        w, h = 18, 22
        hex_pts = [(center[0], center[1]-h), (center[0]+w, center[1]-h//2), (center[0]+w, center[1]+h//2), 
                   (center[0], center[1]+h), (center[0]-w, center[1]+h//2), (center[0]-w, center[1]-h//2)]
        
        pygame.draw.polygon(surface, (max(0, self.color[0]-150), max(0, self.color[1]-150), max(0, self.color[2]-150)), hex_pts)
        pygame.draw.polygon(surface, self.color, hex_pts, 4)
        
        # Vnitřní ostrá svítící faza
        pygame.draw.line(surface, (255, 255, 255), (center[0], center[1]-h+4), (center[0], center[1]+h-4), 4)
        pygame.draw.circle(surface, (255, 255, 255), center, 6)
        
        # Žhnoucí ústí hlavně
        if self.direction == 0:   tip = (center[0], center[1] - barrel_len)
        elif self.direction == 1: tip = (center[0] + barrel_len, center[1])
        elif self.direction == 2: tip = (center[0], center[1] + barrel_len)
        elif self.direction == 3: tip = (center[0] - barrel_len, center[1])
        pygame.draw.circle(surface, (255, 255, 255), tip, 5)
        pygame.draw.circle(surface, self.color, tip, 8, 2)