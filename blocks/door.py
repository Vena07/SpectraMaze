import pygame
import math
from .base_block import BaseBlock

class Door(BaseBlock):
    def __init__(self, x, y, size=100):
        super().__init__(x, y, size)
        self.is_open = False
        self.id = 0

    def draw(self, surface):
        super().draw(surface)
        
        bg_rect = self.rect.inflate(-10, -10)
        time_ms = pygame.time.get_ticks()
        
        # Sci-fi podlaha pod dveřmi
        pygame.draw.rect(surface, (20, 20, 25), bg_rect, border_radius=6)
        pygame.draw.line(surface, (35, 35, 45), bg_rect.topleft, bg_rect.bottomright, 2)
        pygame.draw.line(surface, (35, 35, 45), bg_rect.bottomleft, bg_rect.topright, 2)
        pygame.draw.circle(surface, (35, 35, 45), bg_rect.center, 12, 2)
        
    def draw_overlay(self, surface):
        bg_rect = self.rect.inflate(-10, -10)
        time_ms = pygame.time.get_ticks()
        
        # 4 rohové masivní sloupky (aby dveře fungovaly pohledově ze všech 4 stran)
        cw = 18 # Šířka rohového bloku
        corners = [
            pygame.Rect(bg_rect.left, bg_rect.top, cw, cw),
            pygame.Rect(bg_rect.right - cw, bg_rect.top, cw, cw),
            pygame.Rect(bg_rect.left, bg_rect.bottom - cw, cw, cw),
            pygame.Rect(bg_rect.right - cw, bg_rect.bottom - cw, cw, cw)
        ]
        
        for corner in corners:
            pygame.draw.rect(surface, (40, 40, 50), corner, border_radius=4)
            pygame.draw.rect(surface, (100, 100, 120), corner, 2, border_radius=4)
            
        # Pulzující chlazení rohů
        pulse = abs(math.sin(time_ms * 0.005))
        for corner in corners:
            pygame.draw.rect(surface, (0, 200, 255, int(100 * pulse)), corner.inflate(-8, -8))
        
        if not self.is_open:
            # Pokročilý sci-fi štít chránící střed ze všech stran
            shield_rect = bg_rect.inflate(-10, -10)
            shield_w, shield_h = shield_rect.width, shield_rect.height
            shield_surf = pygame.Surface((shield_w, shield_h), pygame.SRCALPHA)
            shield_surf.fill((150, 20, 20, 80)) # Základní červený glow
            
            # Animované skenovací linky do mřížky (vertikální i horizontální)
            offset = (time_ms * 0.03) % 20
            for i in range(int(offset) - 20, max(shield_w, shield_h), 20):
                if 0 <= i <= shield_h:
                    pygame.draw.line(shield_surf, (255, 50, 50, 180), (0, i), (shield_w, i), 2)
                if 0 <= i <= shield_w:
                    pygame.draw.line(shield_surf, (255, 50, 50, 180), (i, 0), (i, shield_h), 2)
            
            # Jiskření na okrajích
            edge_glow = int(155 + 100 * abs(math.sin(time_ms * 0.01)))
            pygame.draw.rect(shield_surf, (255, 100, 100, edge_glow), (0, 0, shield_w, shield_h), 3)
            
            # Silný varovný kříž
            pygame.draw.line(shield_surf, (255, 40, 40, 200), (0, 0), (shield_w, shield_h), 4)
            pygame.draw.line(shield_surf, (255, 40, 40, 200), (0, shield_h), (shield_w, 0), 4)
            
            # Centrální varovný uzel
            cx, cy = shield_w // 2, shield_h // 2
            pygame.draw.circle(shield_surf, (255, 50, 50, 220), (cx, cy), 12, 2)
            pygame.draw.circle(shield_surf, (255, 255, 255, 255), (cx, cy), 5)

            surface.blit(shield_surf, (shield_rect.left, shield_rect.top))
        else:
            # Otevřený stav - zasunuté písty a uvolněná dráha ve všech 4 směrech
            cx, cy = bg_rect.centerx, bg_rect.centery
            pygame.draw.line(surface, (50, 255, 100), (bg_rect.left + cw, cy), (bg_rect.left + cw + 6, cy), 4)
            pygame.draw.line(surface, (50, 255, 100), (bg_rect.right - cw, cy), (bg_rect.right - cw - 6, cy), 4)
            pygame.draw.line(surface, (50, 255, 100), (cx, bg_rect.top + cw), (cx, bg_rect.top + cw + 6), 4)
            pygame.draw.line(surface, (50, 255, 100), (cx, bg_rect.bottom - cw), (cx, bg_rect.bottom - cw - 6), 4)
            
            pygame.draw.rect(surface, (10, 80, 30), (cx - 10, cy - 10, 20, 20), border_radius=3)
            pygame.draw.rect(surface, (50, 255, 100), (cx - 10, cy - 10, 20, 20), 2, border_radius=3)

    def interact_with_beam(self, beam_dir, color):
        if self.is_open:
            return beam_dir
        return None