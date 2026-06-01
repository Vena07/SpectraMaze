import pygame
import math
from .base_block import BaseBlock

class Bulb(BaseBlock):
    def __init__(self, x, y, target_color, size=100):
        super().__init__(x, y, size)
        self.target_color = target_color
        self.is_lit = False

    def draw(self, surface):
        super().draw(surface)

        time_ms = pygame.time.get_ticks()

        # Zaoblená Tech základna reaktoru
        bg_rect = self.rect.inflate(-20, -20)
        pygame.draw.rect(surface, (30, 30, 40), bg_rect, border_radius=20)
        pygame.draw.rect(surface, (60, 60, 80), bg_rect, 2, border_radius=20)

        # Vykreslení tech sítě v pozadí
        pygame.draw.circle(surface, (20, 20, 25), self.rect.center, self.size // 3)

        bulb_color = self.target_color if self.is_lit else (40, 40, 50)

        # Rotující segmentovaný vnější prstenec (pixel vibe a high-tech vzhled)
        angle_offset = time_ms * 0.002 if self.is_lit else 0
        for i in range(12):
            ang = angle_offset + i * (math.pi / 6)
            dist = self.size // 3
            px = self.rect.centerx + math.cos(ang) * dist
            py = self.rect.centery + math.sin(ang) * dist
            r = 4 if i % 3 == 0 else 2
            pygame.draw.circle(surface, self.target_color, (int(px), int(py)), r)

        # Masivní jádro reaktoru s jemným dýcháním když je vypnutá
        core_radius = self.size // 4
        if not self.is_lit:
            breathing = self.get_breathing_pulse(cycle_time=3000, intensity=2)
            core_radius = int(core_radius + breathing)

        pygame.draw.circle(surface, (20, 20, 25), self.rect.center, core_radius)
        pygame.draw.circle(surface, bulb_color, self.rect.center, core_radius - 2)

        if self.is_lit:
            # Pulzující meltdown a záře v cíli
            pulse = abs(math.sin(time_ms * 0.01)) * 4
            pygame.draw.circle(surface, (255, 255, 255), self.rect.center, int(self.size // 8 + pulse))
            glow_surf = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(glow_surf, (*self.target_color, 120), (self.size // 2, self.size // 2), self.size // 3 + int(pulse*2))
            surface.blit(glow_surf, self.rect.topleft, special_flags=pygame.BLEND_RGBA_ADD)

    def interact_with_beam(self, beam_dir, color):
        # Rozsvícení při správné barvě
        if color == self.target_color:
            self.is_lit = True
        return None # Žárovka paprsek nepustí dál