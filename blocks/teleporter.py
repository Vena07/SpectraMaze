import pygame
import math
from .base_block import BaseBlock

class Teleporter(BaseBlock):
    def __init__(self, x, y, size=100):
        super().__init__(x, y, size)
        self.channel = 0
        self.linked_teleporter = None

    def draw(self, surface):
        super().draw(surface)
        
        # Masivní kruhová tech-obruba pro teleportační desku
        bg_rect = self.rect.inflate(-20, -20)
        pygame.draw.rect(surface, (30, 30, 40), bg_rect, border_radius=self.size//2)
        pygame.draw.rect(surface, (80, 80, 100), bg_rect, 3, border_radius=self.size//2)
        
        # Temná propast - laser sem doletí
        pygame.draw.circle(surface, (10, 10, 15), self.rect.center, self.size // 4)

    def draw_overlay(self, surface):
        center = self.rect.center
        time_ms = pygame.time.get_ticks()

        # Rotující magický portálový efekt
        angle = time_ms * 0.002
        radius1 = self.size // 3 - 2
        radius2 = self.size // 4 - 2

        # Vnější rotující prstenec
        pygame.draw.circle(surface, (150, 0, 255), center, radius1, 3)
        x1 = center[0] + math.cos(angle) * radius1
        y1 = center[1] + math.sin(angle) * radius1
        pygame.draw.circle(surface, (200, 100, 255), (int(x1), int(y1)), 6)

        # Vnitřní prstenec (rotuje na druhou stranu)
        pygame.draw.circle(surface, (100, 0, 255), center, radius2, 2)
        x2 = center[0] + math.cos(-angle * 1.5) * radius2
        y2 = center[1] + math.sin(-angle * 1.5) * radius2
        pygame.draw.circle(surface, (255, 150, 255), (int(x2), int(y2)), 4)

        # Jemný pulzující závoj s dýcháním, pod kterým prosvítá projíždějící laser
        breathing = self.get_breathing_pulse(cycle_time=4000, intensity=4)
        glow_intensity = int(12 + breathing)
        glow = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
        pygame.draw.circle(glow, (100, 0, 255, 80), (self.size//2, self.size//2), glow_intensity)
        surface.blit(glow, self.rect.topleft)

    def interact_with_beam(self, beam_dir, color):
        if self.linked_teleporter:
            # Vracíme enginu speciální signál pro okamžitý přeskok na jiné souřadnice
            return ("TELEPORT", self.linked_teleporter.x, self.linked_teleporter.y, beam_dir, color)
        return None