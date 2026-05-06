import pygame
from .base_block import BaseBlock

class Crossover(BaseBlock):
    def __init__(self, x, y, size=200):
        super().__init__(x, y, size)

    def draw(self, surface):
        super().draw(surface)
        
        # Moderní pozadí uzlu (křižovatky)
        bg_rect = self.rect.inflate(-30, -30)
        pygame.draw.rect(surface, (30, 30, 40), bg_rect, border_radius=12)
        pygame.draw.rect(surface, (60, 60, 80), bg_rect, 2, border_radius=12)
        
        # Prohloubené vodící kanály pro paprsek - tmavé, aby vynikl letící laser
        channel_color = (15, 15, 20)
        pygame.draw.line(surface, channel_color, (self.rect.centerx, self.rect.top + 15), (self.rect.centerx, self.rect.bottom - 15), 16)
        pygame.draw.line(surface, channel_color, (self.rect.left + 15, self.rect.centery), (self.rect.right - 15, self.rect.centery), 16)
        
    def draw_overlay(self, surface):
        # Centrální přemostění - lasery pod něj zalezou
        pygame.draw.circle(surface, (60, 60, 80), self.rect.center, 14, 3)
        pygame.draw.circle(surface, (20, 25, 35), self.rect.center, 11)
        pygame.draw.circle(surface, (100, 100, 120), self.rect.center, 4)

    def interact_with_beam(self, beam_dir, color):
        # Křižovatka vrací původní směr paprsku, čímž ho propustí dál
        # (LaserEngine pak automaticky zajistí, aby nedošlo ke smíchání barev)
        return beam_dir
