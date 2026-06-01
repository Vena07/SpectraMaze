import pygame
import os
import math
import random
from blocks.crystal import Crystal
from blocks.bulb import Bulb
from blocks.mirror import Mirror
from blocks.splitter import Splitter
from blocks.color_switch import ColorSwitch
from blocks.mixer import Mixer
from blocks.crossover import Crossover
from blocks.door import Door
from blocks.teleporter import Teleporter

class UIManager:
    def __init__(self, screen_width, screen_height):
        self.state = "MAIN_MENU" # Stavy: MAIN_MENU, TUTORIAL_SELECT, COMMUNITY_PLAY, AI_MENU, PLAY, SETTINGS, VICTORY, LOADING, LEVEL_PREVIEW
        self.current_level = 1
        self.current_map_title = ""
        self.current_map_author = ""
        self.font = self.get_font(36)
        self.small_font = self.get_font(24)
        self.big_font = self.get_font(60)
        self.screen_w = screen_width
        self.screen_h = screen_height

        self.moves_made = 0
        self.play_start_time = 0
        self.play_time_str = "00:00"

        self.music_vol = 0.5
        self.sfx_vol = 0.5

        # Transition system
        self.prev_state = "MAIN_MENU"
        self.transition_time = 0.0
        self.transition_duration = 0.4  # 400ms transitions
        self.transition_active = False
        
        # Načtení loga (pokud existuje)
        try:
            possible_paths = [
                os.path.join("img", "logo.png"),
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "img", "logo.png")
            ]
            img = None
            for p in possible_paths:
                if os.path.exists(p):
                    img = pygame.image.load(p).convert_alpha()
                    break
            if img:
                if img.get_width() > 450: # Zmenšení loga pro lepší vzhled
                    scale = 450 / img.get_width()
                    img = pygame.transform.scale(img, (450, int(img.get_height() * scale)))
                self.logo = img
            else:
                self.logo = None
        except Exception:
            self.logo = None

        # Tlačítka pro hlavní menu
        btn_w, btn_h = 300, 60
        center_x = screen_width // 2
        self.btn_play = pygame.Rect(center_x - btn_w//2, 260, btn_w, btn_h) # Posunuto o 60px dolů
        self.btn_ai = pygame.Rect(center_x - btn_w//2, 340, btn_w, btn_h)
        self.btn_tutorial = pygame.Rect(center_x - btn_w//2, 420, btn_w, btn_h)
        self.btn_settings = pygame.Rect(center_x - btn_w//2, 500, btn_w, btn_h)
        self.btn_exit = pygame.Rect(center_x - btn_w//2, 580, btn_w, btn_h)
        self.btn_login = pygame.Rect(center_x - 175, screen_height - 120, 350, 50)
        
        # Tlačítka pro nastavení
        self.btn_mus_down = pygame.Rect(center_x - 150, 200, 60, 50)
        self.btn_mus_up = pygame.Rect(center_x + 90, 200, 60, 50)
        self.btn_sfx_down = pygame.Rect(center_x - 150, 300, 60, 50)
        self.btn_sfx_up = pygame.Rect(center_x + 90, 300, 60, 50)
        self.btn_style_down = pygame.Rect(center_x - 150, 400, 60, 50)
        self.btn_style_up = pygame.Rect(center_x + 90, 400, 60, 50)
        
        self.laser_styles = ["Neon", "Plasma", "Focused", "Helix", "Quantum"]
        self.laser_style_idx = 0
        self.laser_style = self.laser_styles[self.laser_style_idx]
        
        # Tlačítka pro AI Menu
        self.btn_easy = pygame.Rect(center_x - btn_w//2, 250, btn_w, btn_h)
        self.btn_med = pygame.Rect(center_x - btn_w//2, 350, btn_w, btn_h)
        self.btn_hard = pygame.Rect(center_x - btn_w//2, 450, btn_w, btn_h)
        self.last_ai_difficulty = "easy"
        
        self.community_levels = []
        self.community_btns = []
        self.scroll_offset = 0

        # Prvky pro obrazovku s náhledem mapy
        self.preview_blocks = []
        self.preview_level_info = {}
        self.preview_start_btn = pygame.Rect(center_x - 150, self.screen_h - 180, 300, 60)
        self.preview_back_btn = pygame.Rect(10, 10, 110, 40)
        self.preview_author_btn = pygame.Rect(center_x - 100, 140, 200, 40)

        # Seznam tutoriálů (Knihovna bloků)
        self.tutorial_blocks = [
            ("Crystal", "Krystal"), ("Bulb", "Žárovka"), ("Mirror", "Zrcadlo"),
            ("Splitter", "Rozdvojník"), ("ColorSwitch", "Měnič"),
            ("Mixer", "Mixér"), ("Crossover", "Křižovatka"), ("ButtonDoor", "Dveře"),
            ("Teleporter", "Teleport"), ("Explosion", "Exploze")
        ]
        
        # Živé modely bloků, které ukážeme na tlačítku
        self.tutorial_blocks_instances = {
            "Crystal": Crystal(0,0,1,(255,0,0),50),
            "Bulb": Bulb(0,0,(0,255,0),50),
            "Mirror": Mirror(0,0,0,50),
            "Splitter": Splitter(0,0,0,50),
            "ColorSwitch": ColorSwitch(0,0,(0,255,0),50),
            "Mixer": Mixer(0,0,2,50),
            "Crossover": Crossover(0,0,50),
            "ButtonDoor": Door(0,0,50),
            "Teleporter": Teleporter(0,0,50)
        }
        
        self.tutorial_btns = []
        total_w = 4 * 210
        start_x = center_x - (total_w // 2)
        start_y = 180
        for i, (key, label) in enumerate(self.tutorial_blocks):
            row = i // 4
            col = i % 4
            x = start_x + col * 210
            y = start_y + row * 100
            self.tutorial_btns.append({"id": key, "label": label, "rect": pygame.Rect(x, y, 195, 75)})

    def get_font(self, size):
        try:
            font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pixel.ttf")
            return pygame.font.Font(font_path, size)
        except:
            return pygame.font.SysFont("couriernew,consolas,lucidaconsole,monospace", size, bold=True)

    def ease_out(self, t):
        """Ease-out cubic interpolation"""
        t = min(1.0, max(0.0, t))
        return 1 - (1 - t) ** 3

    def update_transition(self, dt):
        """Update transition state"""
        if self.transition_active:
            self.transition_time += dt
            if self.transition_time >= self.transition_duration:
                self.transition_active = False
                self.transition_time = 0.0
                self.prev_state = self.state
        return self.ease_out(self.transition_time / self.transition_duration) if self.transition_active else 1.0

    def trigger_transition(self):
        """Trigger a smooth transition to new state"""
        if self.prev_state != self.state:
            self.transition_active = True
            self.transition_time = 0.0

    def draw_neon_btn(self, surface, rect, text, color, font=None, outline_only=False, mouse_pos=None):
        if font is None: font = self.font
        is_hovered = mouse_pos and rect.collidepoint(mouse_pos)
        
        if is_hovered:
            color = (min(255, color[0] + 60), min(255, color[1] + 60), min(255, color[2] + 60))
            bg_color = (35, 40, 50) if not outline_only else (25, 30, 40)
            border_w = 3
        else:
            bg_color = (20, 25, 30) if not outline_only else (15, 18, 25)
            border_w = 2

        pygame.draw.rect(surface, bg_color, rect, border_radius=10)
        pygame.draw.rect(surface, color, rect, border_w, border_radius=10)
        
        txt_surf = font.render(text, True, color)
        surface.blit(txt_surf, (rect.centerx - txt_surf.get_width()//2, rect.centery - txt_surf.get_height()//2))

    def set_community_levels(self, levels):
        self.community_levels = levels
        self.community_btns = []
        center_x = self.screen_w // 2
        start_y = 200
        # Mřížka - 2 sloupce, bez omezení na pouhých 6 map
        for i, lvl in enumerate(levels):
            row = i // 2
            col = i % 2
            x_pos = center_x - 420 if col == 0 else center_x + 20
            btn_rect = pygame.Rect(x_pos, start_y + row * 100, 400, 80)
            
            # API nyní vrací 'title' a 'author'
            map_title = lvl.get("title", lvl.get("name", "Neznámá mapa"))
            map_author = lvl.get("author") or "Neznámý autor"
            self.community_btns.append({"id": lvl.get("id"), "name": map_title, "author": map_author, "rect": btn_rect})
    
    def set_preview_data(self, blocks, level_info):
        self.preview_blocks = blocks
        self.preview_level_info = level_info

    def handle_event(self, event):
        # Posouvání kolečkem myši v seznamu komunitních map
        if event.type == pygame.MOUSEWHEEL and self.state == "COMMUNITY_PLAY":
            self.scroll_offset -= event.y * 40
            rows = math.ceil(len(self.community_btns) / 2)
            max_scroll = max(0, rows * 100 - (self.screen_h - 300))
            self.scroll_offset = max(0, min(self.scroll_offset, max_scroll))

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            x, y = event.pos
            if self.state == "MAIN_MENU":
                if self.btn_play.collidepoint(x, y):
                    self.state = "COMMUNITY_PLAY"
                    self.trigger_transition()
                    return {"action": "open_community_menu"}
                elif self.btn_ai.collidepoint(x, y):
                    self.state = "AI_MENU"
                    self.trigger_transition()
                    return {"action": "click"}
                elif self.btn_tutorial.collidepoint(x, y):
                    self.state = "TUTORIAL_SELECT"
                    self.trigger_transition()
                    return {"action": "click"}
                elif self.btn_settings.collidepoint(x, y):
                    self.state = "SETTINGS"
                    self.trigger_transition()
                    return {"action": "click"}
                elif self.btn_exit.collidepoint(x, y):
                    return {"action": "quit"}
                elif self.btn_login.collidepoint(x, y):
                    return {"action": "open_url", "url": "https://spectra-maze-web.vercel.app/"}
            elif self.state == "SETTINGS":
                if self.btn_mus_down.collidepoint(x, y):
                    self.music_vol = max(0.0, self.music_vol - 0.1)
                elif self.btn_mus_up.collidepoint(x, y):
                    self.music_vol = min(1.0, self.music_vol + 0.1)
                elif self.btn_sfx_down.collidepoint(x, y):
                    self.sfx_vol = max(0.0, self.sfx_vol - 0.1)
                elif self.btn_sfx_up.collidepoint(x, y):
                    self.sfx_vol = min(1.0, self.sfx_vol + 0.1)
                elif self.btn_style_down.collidepoint(x, y):
                    self.laser_style_idx = (self.laser_style_idx - 1) % len(self.laser_styles)
                    self.laser_style = self.laser_styles[self.laser_style_idx]
                elif self.btn_style_up.collidepoint(x, y):
                    self.laser_style_idx = (self.laser_style_idx + 1) % len(self.laser_styles)
                    self.laser_style = self.laser_styles[self.laser_style_idx]
                # Zpět do menu
                if 10 <= x <= 120 and 10 <= y <= 50:
                    self.state = "MAIN_MENU"
                    self.trigger_transition()
                    return {"action": "click"}
            elif self.state == "TUTORIAL_SELECT":
                for btn in self.tutorial_btns:
                    if btn["rect"].collidepoint(x, y):
                        self.state = "PLAY"
                        self.trigger_transition()
                        self.current_level = btn["id"]
                        return {"action": "load_tutorial", "level": btn["id"]}
                # Tlačítko zpět
                if 10 <= x <= 120 and 10 <= y <= 50:
                    self.state = "MAIN_MENU"
                    self.trigger_transition()
            elif self.state == "AI_MENU":
                if self.btn_easy.collidepoint(x, y):
                    self.state = "PLAY"
                    self.trigger_transition()
                    self.current_level = "AI"
                    self.last_ai_difficulty = "easy"
                    return {"action": "generate_ai", "difficulty": "easy"}
                elif self.btn_med.collidepoint(x, y):
                    self.state = "PLAY"
                    self.trigger_transition()
                    self.current_level = "AI"
                    self.last_ai_difficulty = "medium"
                    return {"action": "generate_ai", "difficulty": "medium"}
                elif self.btn_hard.collidepoint(x, y):
                    self.state = "PLAY"
                    self.trigger_transition()
                    self.current_level = "AI"
                    self.last_ai_difficulty = "hard"
                    return {"action": "generate_ai", "difficulty": "hard"}

                # Tlačítko zpět
                if 10 <= x <= 120 and 10 <= y <= 50:
                    self.state = "MAIN_MENU"
                    self.trigger_transition()
                    return {"action": "click"}
            elif self.state == "COMMUNITY_PLAY":
                for btn in self.community_btns:
                    # Musíme přepočítat pozici tlačítka kvůli scrollování
                    real_rect = btn["rect"].move(0, -self.scroll_offset)
                    if real_rect.collidepoint(x, y):
                        return {"action": "preview_community_level", "level_id": btn["id"], "title": btn["name"], "author": btn["author"]}
                # Tlačítko zpět
                if 10 <= x <= 120 and 10 <= y <= 50:
                    self.state = "MAIN_MENU"
                    self.trigger_transition()
                    return {"action": "click"}
            elif self.state == "LEVEL_PREVIEW":
                if self.preview_start_btn.collidepoint(x, y):
                    return {"action": "start_game"}
                if self.preview_back_btn.collidepoint(x, y):
                    self.state = "COMMUNITY_PLAY"
                    self.trigger_transition()
                    return {"action": "open_community_menu"}
                if self.preview_author_btn.collidepoint(x, y):
                    author = self.preview_level_info.get("author", "")
                    if author:
                        return {"action": "open_url", "url": f"https://spectra-maze-web.vercel.app/profile/{author}"}
            elif self.state == "PLAY":
                # Tlačítko zpět a rychlý restart
                back_txt = "Komunita" if str(self.current_level).startswith("COMMUNITY_") else ("AI Menu" if self.current_level == "AI" else "Knihovna")
                back_w = max(110, self.small_font.size(back_txt)[0] + 20)
                if 10 <= x <= 10 + back_w and 10 <= y <= 50:
                    if self.current_level == "AI":
                        self.state = "AI_MENU"
                    elif str(self.current_level).startswith("COMMUNITY_"):
                        self.state = "COMMUNITY_PLAY"
                    else:
                        self.state = "TUTORIAL_SELECT"
                    self.trigger_transition()
                    return {"action": "click"}
                elif 10 + back_w + 10 <= x <= 10 + back_w + 10 + 150 and 10 <= y <= 50:
                    return {"action": "reset_level"}
            elif self.state == "VICTORY":
                victory_center_x = self.screen_w // 2
                # Tlačítka z obrazovky výhry
                if victory_center_x - 150 <= x <= victory_center_x + 150 and 400 <= y <= 460:
                    if self.current_level == "AI":
                        self.state = "PLAY"
                        self.trigger_transition()
                        return {"action": "generate_ai", "difficulty": self.last_ai_difficulty}
                    elif str(self.current_level).startswith("COMMUNITY_"):
                        self.state = "COMMUNITY_PLAY"
                        self.trigger_transition()
                        return {"action": "open_community_menu"}
                    else:
                        self.state = "MAIN_MENU"
                        self.trigger_transition()
                        return {"action": "click"}
                elif victory_center_x - 150 <= x <= victory_center_x + 150 and 500 <= y <= 560:
                    if str(self.current_level).startswith("COMMUNITY_"):
                        self.state = "COMMUNITY_PLAY"
                        self.trigger_transition()
                        return {"action": "open_community_menu"}
                    else:
                        self.state = "AI_MENU"
                        self.trigger_transition()
                        return {"action": "click"}
        return None

    def draw(self, surface):
        center_x = self.screen_w // 2
        mouse_pos = pygame.mouse.get_pos()

        # Poloprůhledný overlay pro menu (umožní prosvítání hvězdných částic z main.py)
        if self.state in ["MAIN_MENU", "TUTORIAL_SELECT", "SETTINGS", "COMMUNITY_PLAY", "AI_MENU", "LEVEL_PREVIEW", "LOADING"]:
            overlay = pygame.Surface((self.screen_w, self.screen_h), pygame.SRCALPHA)
            overlay_alpha = 180
            if self.transition_active:
                t = self.transition_time / self.transition_duration
                overlay_alpha = int(180 * self.ease_out(t))
            overlay.fill((10, 12, 18, overlay_alpha))
            surface.blit(overlay, (0, 0))

        if self.state == "MAIN_MENU":
            if self.logo:
                logo_rect = self.logo.get_rect(center=(center_x, 120))
                surface.blit(self.logo, logo_rect)
            else:
                title = self.big_font.render("SpectraMaze", True, (0, 200, 220))
                surface.blit(title, (center_x - title.get_width()//2, 120))

            self.draw_neon_btn(surface, self.btn_play, "HRÁT", (0, 200, 220), mouse_pos=mouse_pos)
            self.draw_neon_btn(surface, self.btn_ai, "AI MAPY", (200, 100, 220), mouse_pos=mouse_pos)
            self.draw_neon_btn(surface, self.btn_tutorial, "KNIHOVNA", (100, 180, 240), mouse_pos=mouse_pos)
            self.draw_neon_btn(surface, self.btn_settings, "NASTAVENÍ", (180, 180, 255), mouse_pos=mouse_pos)
            self.draw_neon_btn(surface, self.btn_exit, "UKONČIT", (180, 80, 80), mouse_pos=mouse_pos)

            self.draw_neon_btn(surface, self.btn_login, "Vytvořit mapu na webu", (150, 180, 240), font=self.small_font, mouse_pos=mouse_pos)

        elif self.state == "SETTINGS":
            title = self.big_font.render("Nastavení", True, (0, 200, 220))
            surface.blit(title, (center_x - title.get_width()//2, 80))

            # Ovládání hudby
            txt_mus = self.font.render(f"Hlasitost hudby: {int(self.music_vol * 100)}%", True, (255, 255, 255))
            surface.blit(txt_mus, (center_x - txt_mus.get_width()//2, 160))

            # Vizuální ukazatel hlasitosti
            bar_mus = pygame.Rect(center_x - 70, 215, 140, 20)
            pygame.draw.rect(surface, (30, 35, 45), bar_mus, border_radius=10)
            if self.music_vol > 0:
                fill_mus = pygame.Rect(center_x - 70, 215, int(140 * self.music_vol), 20)
                pygame.draw.rect(surface, (0, 200, 220), fill_mus, border_radius=10)

            self.draw_neon_btn(surface, self.btn_mus_down, "-", (180, 80, 80), mouse_pos=mouse_pos)
            self.draw_neon_btn(surface, self.btn_mus_up, "+", (0, 200, 220), mouse_pos=mouse_pos)

            # Ovládání zvuků
            txt_sfx = self.font.render(f"Hlasitost zvuků: {int(self.sfx_vol * 100)}%", True, (255, 255, 255))
            surface.blit(txt_sfx, (center_x - txt_sfx.get_width()//2, 260))

            bar_sfx = pygame.Rect(center_x - 70, 315, 140, 20)
            pygame.draw.rect(surface, (30, 35, 45), bar_sfx, border_radius=10)
            if self.sfx_vol > 0:
                fill_sfx = pygame.Rect(center_x - 70, 315, int(140 * self.sfx_vol), 20)
                pygame.draw.rect(surface, (0, 200, 220), fill_sfx, border_radius=10)

            self.draw_neon_btn(surface, self.btn_sfx_down, "-", (180, 80, 80), mouse_pos=mouse_pos)
            self.draw_neon_btn(surface, self.btn_sfx_up, "+", (0, 200, 220), mouse_pos=mouse_pos)

            # Styl Laseru
            txt_style = self.font.render("Styl laseru", True, (255, 255, 255))
            surface.blit(txt_style, (center_x - txt_style.get_width()//2, 360))

            style_rect = pygame.Rect(center_x - 70, 400, 140, 50)
            pygame.draw.rect(surface, (20, 25, 30), style_rect, border_radius=10)
            pygame.draw.rect(surface, (180, 180, 255), style_rect, 2, border_radius=10)
            txt_s = self.small_font.render(self.laser_style, True, (180, 180, 255))
            surface.blit(txt_s, (style_rect.centerx - txt_s.get_width()//2, style_rect.centery - txt_s.get_height()//2))

            self.draw_neon_btn(surface, self.btn_style_down, "<", (180, 180, 255), mouse_pos=mouse_pos)
            self.draw_neon_btn(surface, self.btn_style_up, ">", (180, 180, 255), mouse_pos=mouse_pos)
            
            # --- Vizuální animovaný náhled laseru ---
            preview_rect = pygame.Rect(center_x - 150, 480, 300, 60)
            pygame.draw.rect(surface, (15, 18, 25), preview_rect, border_radius=10)
            pygame.draw.rect(surface, (50, 60, 80), preview_rect, 2, border_radius=10)
            
            time_ms = pygame.time.get_ticks()
            pulse = (math.sin(time_ms / 100.0) + 1) / 2.0
            glow_w = int(pulse * 6)
            start_pos = (preview_rect.left + 30, preview_rect.centery)
            end_pos = (preview_rect.right - 30, preview_rect.centery)
            color = (0, 255, 200) # Ukázková azurově-zelená barva
            r, g, b_col = color
            
            for layer_idx in range(5):
                width = 0
                l_color = (0, 0, 0)
                if self.laser_style == "Plasma":
                    wobble = int((math.sin(time_ms / 40.0) + 1) * 4)
                    if layer_idx == 0: width, l_color = 18, (10, 12, 18)
                    elif layer_idx == 1: width, l_color = 14 + wobble, (int(r*0.3), int(g*0.3), int(b_col*0.3))
                    elif layer_idx == 2: width, l_color = 10 + wobble//2, (int(r*0.7), int(g*0.7), int(b_col*0.7))
                    elif layer_idx == 3: width, l_color = 6, color
                    elif layer_idx == 4: width, l_color = 3, (min(255, r+100), min(255, g+100), min(255, b_col+100))
                elif self.laser_style == "Focused":
                    if layer_idx == 0: width, l_color = 10, (10, 12, 18)
                    elif layer_idx == 1: width, l_color = 6, (int(r*0.4), int(g*0.4), int(b_col*0.4))
                    elif layer_idx == 2: width, l_color = 3, color
                    elif layer_idx == 3: width, l_color = 1, (255, 255, 255)
                elif self.laser_style == "Helix":
                    if layer_idx == 0: width, l_color = 12, (10, 12, 18)
                    elif layer_idx == 1: width, l_color = 8 + glow_w//2, (int(r*0.3), int(g*0.3), int(b_col*0.3))
                    elif layer_idx == 2: width, l_color = 4, color
                elif self.laser_style == "Quantum":
                    if layer_idx == 0: width, l_color = 14, (10, 12, 18)
                    elif layer_idx == 1: width, l_color = 10 + glow_w, (int(r*0.2), int(g*0.2), int(b_col*0.2))
                    elif layer_idx == 2: width, l_color = 6, color
                    elif layer_idx == 3: width, l_color = 2, (255, 255, 255)
                else: # Neon
                    if layer_idx == 0: width, l_color = 16, (10, 12, 18)
                    elif layer_idx == 1: width, l_color = 12 + glow_w, (int(r*0.2), int(g*0.2), int(b_col*0.2))
                    elif layer_idx == 2: width, l_color = 8 + glow_w//2, (int(r*0.6), int(g*0.6), int(b_col*0.6))
                    elif layer_idx == 3: width, l_color = 4, color
                    elif layer_idx == 4: width, l_color = 2, (255, 255, 255)
                    
                if width > 0:
                    pygame.draw.line(surface, l_color, start_pos, end_pos, width)
                    radius = width // 2
                    if radius > 0:
                        pygame.draw.circle(surface, l_color, (int(start_pos[0]), int(start_pos[1])), radius)
                        pygame.draw.circle(surface, l_color, (int(end_pos[0]), int(end_pos[1])), radius)
            
            # Kreslení ozdobných tvarů do náhledu
            length = math.hypot(end_pos[0] - start_pos[0], end_pos[1] - start_pos[1])
            if length > 0:
                ux, uy = (end_pos[0] - start_pos[0]) / length, (end_pos[1] - start_pos[1]) / length
                vx, vy = -uy, ux
                
                if self.laser_style == "Helix":
                    pts1, pts2 = [], []
                    for i in range(0, int(length) + 1, 5):
                        px, py = start_pos[0] + ux * i, start_pos[1] + uy * i
                        t = (px + py) * 0.02 - time_ms / 150.0
                        offset = math.sin(t) * 10
                        pts1.append((px + vx * offset, py + vy * offset))
                        pts2.append((px - vx * offset, py - vy * offset))
                    if len(pts1) > 1: pygame.draw.lines(surface, color, False, pts1, 2); pygame.draw.lines(surface, (255, 255, 255), False, pts1, 1)
                    if len(pts2) > 1: pygame.draw.lines(surface, color, False, pts2, 2); pygame.draw.lines(surface, (255, 255, 255), False, pts2, 1)
                
                elif self.laser_style == "Quantum":
                    offset_val = (time_ms * 0.1) % 20
                    for travel in range(int(offset_val), int(length), 20):
                        px, py = start_pos[0] + ux * travel, start_pos[1] + uy * travel
                        t_val = (px + py) * 0.02 + time_ms * 0.005
                        offset = math.sin(t_val) * 12
                        s = 4 + math.sin(t_val * 2) * 3
                        rect = pygame.Rect(px + vx * offset - s/2, py + vy * offset - s/2, s, s)
                        pygame.draw.rect(surface, color, rect)
                        pygame.draw.rect(surface, (255, 255, 255), rect, 1)

                elif self.laser_style == "Plasma":
                    if random.random() < 0.5:
                        pts = []
                        for i in range(0, int(length) + 1, 10):
                            offset = random.uniform(-8, 8)
                            pts.append((start_pos[0] + ux * i + vx * offset, start_pos[1] + uy * i + vy * offset))
                        if len(pts) > 1: pygame.draw.lines(surface, (255, 255, 255), False, pts, 1)

                elif self.laser_style == "Focused":
                    offset_val = (time_ms * 0.2) % 25
                    for travel in range(int(offset_val), int(length), 25):
                        px, py = start_pos[0] + ux * travel, start_pos[1] + uy * travel
                        pygame.draw.circle(surface, color, (int(px), int(py)), 6, 1)
                        pygame.draw.circle(surface, (255, 255, 255), (int(px), int(py)), 3)
            # ----------------------------------------------
            
            self.draw_neon_btn(surface, pygame.Rect(10, 10, 110, 40), "Zpět", (180, 80, 80), font=self.small_font, mouse_pos=mouse_pos)

        elif self.state == "TUTORIAL_SELECT":
            title = self.big_font.render("Knihovna bloků", True, (255, 255, 255))
            surface.blit(title, (center_x - title.get_width()//2, 80))
            for btn in self.tutorial_btns:
                self.draw_neon_btn(surface, btn["rect"], "", (100, 200, 255), mouse_pos=mouse_pos)
                
                # Zobrazení ikony bloku
                icon_size = 50
                b_id = btn["id"]
                if b_id in self.tutorial_blocks_instances:
                    block_inst = self.tutorial_blocks_instances[b_id]
                    icon_surf = pygame.Surface((icon_size, icon_size), pygame.SRCALPHA)
                    block_inst.rect = pygame.Rect(0, 0, icon_size, icon_size)
                    block_inst.size = icon_size
                    block_inst.x = 0
                    block_inst.y = 0
                    block_inst.draw(icon_surf)
                    if hasattr(block_inst, 'draw_overlay'):
                        block_inst.draw_overlay(icon_surf)
                    surface.blit(icon_surf, (btn["rect"].x + 10, btn["rect"].centery - icon_size//2))
                elif b_id == "Explosion":
                    pygame.draw.circle(surface, (255, 50, 0), (btn["rect"].x + 35, btn["rect"].centery), 15, 3)
                    pygame.draw.circle(surface, (255, 150, 0), (btn["rect"].x + 35, btn["rect"].centery), 6)
                
                txt_surf = self.small_font.render(btn["label"], True, (100, 200, 255))
                surface.blit(txt_surf, (btn["rect"].x + 70, btn["rect"].centery - txt_surf.get_height()//2))
                
            self.draw_neon_btn(surface, pygame.Rect(10, 10, 110, 40), "Zpět", (180, 80, 80), font=self.small_font, mouse_pos=mouse_pos)

        elif self.state == "AI_MENU":
            title = self.big_font.render("Generátor AI map", True, (255, 255, 255))
            surface.blit(title, (center_x - title.get_width()//2, 100))

            self.draw_neon_btn(surface, self.btn_easy, "LEHKÁ", (0, 200, 220), mouse_pos=mouse_pos)
            self.draw_neon_btn(surface, self.btn_med, "STŘEDNÍ", (200, 180, 100), mouse_pos=mouse_pos)
            self.draw_neon_btn(surface, self.btn_hard, "TĚŽKÁ", (180, 80, 80), mouse_pos=mouse_pos)

            self.draw_neon_btn(surface, pygame.Rect(10, 10, 110, 40), "Zpět", (180, 80, 80), font=self.small_font, mouse_pos=mouse_pos)

        elif self.state == "COMMUNITY_PLAY":
            title = self.big_font.render("Komunitní mapy", True, (255, 255, 255))
            surface.blit(title, (center_x - title.get_width()//2, 100))
            
            if not self.community_levels:
                info = self.small_font.render("Načítání... nebo žádné mapy nenalezeny.", True, (150, 150, 150))
                surface.blit(info, (center_x - info.get_width()//2, 300))
            else:
                for i, btn in enumerate(self.community_btns):
                    # Reálná pozice tlačítka po započtení scrollu
                    real_rect = btn["rect"].move(0, -self.scroll_offset)

                    # Vykreslíme jen viditelná tlačítka
                    if real_rect.bottom > 180 and real_rect.top < self.screen_h:
                        # Neonový design pro komunitní mapy
                        self.draw_neon_btn(surface, real_rect, "", (100, 200, 255), outline_only=True, mouse_pos=mouse_pos)
                        
                        # Zobrazení názvu mapy vlevo a jména autora vpravo
                        txt_title = self.small_font.render(btn["name"], True, (100, 200, 255))
                        txt_author = self.get_font(18).render(f"od: {btn['author']}", True, (200, 200, 200))
                        surface.blit(txt_title, (real_rect.x + 20, real_rect.centery - txt_title.get_height()//2))
                        surface.blit(txt_author, (real_rect.right - txt_author.get_width() - 20, real_rect.centery - txt_author.get_height()//2))
                
                # Vykreslení posuvníku (scrollbaru)
                max_scroll = max(0, len(self.community_btns) * 80 - (self.screen_h - 300))
                if max_scroll > 0:
                    scrollbar_h = 400
                    scrollbar_y = 200
                    handle_h = max(30, scrollbar_h * (self.screen_h - 250) / (len(self.community_btns) * 80))
                    handle_y = scrollbar_y + (self.scroll_offset / max_scroll) * (scrollbar_h - handle_h)
                    
                    pygame.draw.rect(surface, (30, 30, 40), (self.screen_w - 25, scrollbar_y, 15, scrollbar_h), border_radius=8)
                    pygame.draw.rect(surface, (100, 150, 200), (self.screen_w - 25, handle_y, 15, handle_h), border_radius=8)

            self.draw_neon_btn(surface, pygame.Rect(10, 10, 110, 40), "Zpět", (180, 80, 80), font=self.small_font, mouse_pos=mouse_pos)

        elif self.state == "LOADING":
            title = self.big_font.render("Načítání...", True, (255, 255, 255))
            surface.blit(title, (center_x - title.get_width()//2, self.screen_h // 2 - title.get_height() // 2))

        elif self.state == "LEVEL_PREVIEW":
            title = self.font.render(self.preview_level_info.get("title", ""), True, (255, 255, 255))
            author = self.small_font.render(f"od {self.preview_level_info.get('author', '')}", True, (200, 200, 200))
            surface.blit(title, (center_x - title.get_width()//2, 50))
            surface.blit(author, (center_x - author.get_width()//2, 90))

            self.preview_author_btn.top = 130
            self.draw_neon_btn(surface, self.preview_author_btn, "Profil autora", (150, 200, 255), font=self.small_font, outline_only=True, mouse_pos=mouse_pos)

            # Vylepšený vizuál mapy
            if self.preview_blocks:
                b_size = self.preview_blocks[0].size
                max_x = max([b.x for b in self.preview_blocks] + [0])
                max_y = max([b.y for b in self.preview_blocks] + [0])
                map_px_w = (max_x + 1) * b_size
                map_px_h = (max_y + 1) * b_size
                
                # Výpočet zmenšení pro náhled
                preview_scale = 0.6
                max_preview_h = self.screen_h - 400
                max_preview_w = self.screen_w - 100
                if map_px_h * preview_scale > max_preview_h:
                    preview_scale = max_preview_h / map_px_h
                if map_px_w * preview_scale > max_preview_w:
                    preview_scale = min(preview_scale, max_preview_w / map_px_w)

                preview_px_w = int(map_px_w * preview_scale)
                preview_px_h = int(map_px_h * preview_scale)

                map_surface = pygame.Surface((map_px_w, map_px_h), pygame.SRCALPHA)
                pygame.draw.rect(map_surface, (8, 10, 18, 255), (0, 0, map_px_w, map_px_h), border_radius=15)
                
                for gx in range(max_x + 1):
                    for gy in range(max_y + 1):
                        r = pygame.Rect(gx * b_size, gy * b_size, b_size, b_size)
                        pygame.draw.rect(map_surface, (30, 40, 60), r, 1)
                        pygame.draw.circle(map_surface, (60, 150, 255), r.topleft, 2)
                        
                pygame.draw.rect(map_surface, (0, 180, 255, 100), (0, 0, map_px_w, map_px_h), 3, border_radius=15)
                        
                for block in self.preview_blocks:
                    block.draw(map_surface)
                    if hasattr(block, 'draw_overlay'):
                        block.draw_overlay(map_surface)
                        
                if preview_scale != 1.0:
                    preview_surf = pygame.transform.smoothscale(map_surface, (preview_px_w, preview_px_h))
                else:
                    preview_surf = map_surface

                preview_rect = preview_surf.get_rect(center=(center_x, self.screen_h // 2 + 20))
                
                frame_rect = preview_rect.inflate(20, 20)
                pygame.draw.rect(surface, (15, 18, 25), frame_rect, border_radius=15)
                pygame.draw.rect(surface, (0, 255, 200), frame_rect, 3, border_radius=15)
                
                surface.blit(preview_surf, preview_rect)

            # Tlačítka
            self.draw_neon_btn(surface, self.preview_start_btn, "SPUSTIT", (0, 255, 150), mouse_pos=mouse_pos)

            self.draw_neon_btn(surface, self.preview_back_btn, "Zpět", (255, 100, 100), font=self.small_font, mouse_pos=mouse_pos)

        elif self.state == "PLAY":
            back_txt = "Komunita" if str(self.current_level).startswith("COMMUNITY_") else ("AI Menu" if self.current_level == "AI" else "Knihovna")
            back_w = max(110, self.small_font.size(back_txt)[0] + 20)
            self.draw_neon_btn(surface, pygame.Rect(10, 10, back_w, 40), back_txt, (180, 80, 80), font=self.small_font, mouse_pos=mouse_pos)
            self.draw_neon_btn(surface, pygame.Rect(10 + back_w + 10, 10, 150, 40), "RESTARTOVAT", (200, 180, 100), font=self.small_font, mouse_pos=mouse_pos)
                    
        elif self.state == "VICTORY":
            victory_w, victory_h = 400, 400
            victory_rect = pygame.Rect(center_x - victory_w//2, 200, victory_w, victory_h)

            # Poloprůhledné překrytí by vyžadovalo surface s alfa kanálem, tak uděláme čisté okno
            pygame.draw.rect(surface, (10, 10, 15), victory_rect, border_radius=20)
            pygame.draw.rect(surface, (0, 255, 0), victory_rect, 5, border_radius=20)
            
            txt = self.font.render("ÚROVEŇ DOKONČENA!", True, (0, 255, 0))
            surface.blit(txt, (center_x - txt.get_width()//2, 240))
            
            stats_txt = self.small_font.render(f"Čas: {self.play_time_str}  |  Tahy: {self.moves_made}", True, (150, 255, 200))
            surface.blit(stats_txt, (center_x - stats_txt.get_width()//2, 310))
            
            play_again_txt = "Další AI Mapa" if self.current_level == "AI" else "Další Mapy"
            self.draw_neon_btn(surface, pygame.Rect(center_x - 150, 400, 300, 60), play_again_txt, (0, 255, 150), font=self.small_font, mouse_pos=mouse_pos)
            
            back_victory_txt = "Zpět do AI Menu" if self.current_level == "AI" else "Zpět ke komunitě"
            self.draw_neon_btn(surface, pygame.Rect(center_x - 150, 500, 300, 60), back_victory_txt, (255, 100, 100), font=self.small_font, mouse_pos=mouse_pos)