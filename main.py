import pygame
import sys
import math
import random
from ui import UIManager
import webbrowser
from level_manager import LevelManager
from engine import LaserEngine

def create_synth_beep(freq_start, freq_end, duration, vol=0.2, wave_type='sine'):
    try:
        import array
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        buf = array.array('h', [0] * (n_samples * 2))
        for i in range(n_samples):
            t = float(i) / sample_rate
            
            # Obálka: rychlý náběh (attack) a plynulé utlumení (decay)
            attack_samples = int(sample_rate * 0.02)
            if i < attack_samples:
                env = i / attack_samples
            else:
                env = 1.0 - ((i - attack_samples) / (n_samples - attack_samples))
                
            # Změna výšky tónu (Pitch bend) pro sci-fi efekt
            freq = freq_start + (freq_end - freq_start) * (i / n_samples)
            phase = 2 * math.pi * freq * t
            
            # Různé typy zvukových vln
            if wave_type == 'sine': s = math.sin(phase)
            elif wave_type == 'square': s = 1.0 if math.sin(phase) > 0 else -1.0
            elif wave_type == 'saw': s = 2.0 * (t * freq - math.floor(0.5 + t * freq))
            elif wave_type == 'noise': s = random.uniform(-1.0, 1.0)
            else: s = math.sin(phase)
                
            val = int(vol * 32767 * env * s)
            buf[i*2] = val
            buf[i*2+1] = val
        return pygame.mixer.Sound(buffer=buf)
    except Exception:
        return None

def main():
    pygame.init()
    pygame.mixer.init()
    # Spuštění hry v bezokrajovém okně (Borderless Window) pro snazší pořizování screenshotů
    screen = pygame.display.set_mode((0, 0), pygame.NOFRAME)
    screen_w = screen.get_width()
    screen_h = screen.get_height()
    pygame.display.set_caption("SpectraMaze")
    clock = pygame.time.Clock()

    # Temný ambientní drone zvuk pro atmosféru
    snd_ambient = create_synth_beep(80, 80, 2.0, 0.05, 'sine')
    
    # Hudba v pozadí
    try:
        pygame.mixer.music.load("sound/soundtrack.mp3") # Můžeš nahradit .wav, nebo .ogg
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    except:
        pass # Pokud soubor neexistuje, hra nespadne

    snd_click = create_synth_beep(800, 1200, 0.05, 0.1, 'sine')
    snd_block = create_synth_beep(600, 400, 0.08, 0.2, 'square')
    snd_victory = create_synth_beep(400, 800, 0.6, 0.3, 'sine')
    snd_crystal = create_synth_beep(800, 2400, 0.15, 0.25, 'sine')     # Rychlé nabití krystalu
    snd_mirror = create_synth_beep(2500, 3500, 0.05, 0.2, 'saw')       # Ostré skleněné cinknutí
    snd_mixer = create_synth_beep(300, 900, 0.2, 0.2, 'square')        # Hutné "vrrrm" míchání
    snd_splitter = create_synth_beep(2000, 1000, 0.15, 0.25, 'sine')   # Rozštěpení (klesavý ping)
    snd_switch = create_synth_beep(1000, 2000, 0.1, 0.2, 'square')     # Digitální glitch/změna
    snd_door = create_synth_beep(150, 80, 0.25, 0.3, 'saw')            # Těžký kovový doraz
    snd_button = create_synth_beep(1200, 1400, 0.05, 0.2, 'square')    # Jasný mechanický klik
    snd_crossover = create_synth_beep(1200, 800, 0.1, 0.2, 'sine')     # Hladké proklouznutí (zhoupnutí)
    snd_bulb = create_synth_beep(400, 2500, 0.3, 0.3, 'sine')          # Uspokojivé najetí energie
    snd_explosion = create_synth_beep(200, 50, 0.8, 0.6, 'noise')      # Masivní dlouhá exploze
    snd_teleporter = create_synth_beep(3000, 300, 0.3, 0.25, 'saw')    # Agresivní vtáhnutí portálem
    snd_wall = create_synth_beep(100, 50, 0.15, 0.4, 'noise')          # Tupý náraz do zdi
    
    snd_laser_on = create_synth_beep(1500, 200, 0.4, 0.3, 'saw')       # ZAP! Sci-fi výstřel
    snd_door_open = create_synth_beep(200, 600, 0.4, 0.35, 'square')   # Otevření masivních dveří
    snd_bulb_hit = create_synth_beep(2000, 3000, 0.2, 0.25, 'sine')    # Cinknutí úspěšného zásahu
    snd_hit = create_synth_beep(200, 100, 0.1, 0.2, 'noise')           # Zapsknutí při nárazu laseru

    block_sounds = {
        "Crystal": snd_crystal,
        "Mirror": snd_mirror,
        "Mixer": snd_mixer,
        "Splitter": snd_splitter,
        "ColorSwitch": snd_switch,
        "Door": snd_door,
        "Button": snd_button,
        "Crossover": snd_crossover,
        "Bulb": snd_bulb,
        "Teleporter": snd_teleporter,
        "Wall": snd_wall
    }

    ui_manager = UIManager(screen_w, screen_h)
    level_manager = LevelManager(screen_w, screen_h)
    engine = LaserEngine()
    blocks = []
    
    shake_frames = 0

    while True:
        # Aktualizace hlasitosti z nastavení
        pygame.mixer.music.set_volume(ui_manager.music_vol)
        if snd_ambient: snd_ambient.set_volume(ui_manager.music_vol * 0.2)
        for snd in block_sounds.values():
            if snd: snd.set_volume(ui_manager.sfx_vol)
        if snd_click: snd_click.set_volume(ui_manager.sfx_vol)
        if snd_victory: snd_victory.set_volume(ui_manager.sfx_vol)
        if snd_explosion: snd_explosion.set_volume(ui_manager.sfx_vol)
        if snd_laser_on: snd_laser_on.set_volume(ui_manager.sfx_vol)
        if snd_door_open: snd_door_open.set_volume(ui_manager.sfx_vol)
        if snd_bulb_hit: snd_bulb_hit.set_volume(ui_manager.sfx_vol)
        if snd_hit: snd_hit.set_volume(ui_manager.sfx_vol)
        
        # Aktualizace zvoleného stylu laseru
        engine.laser_style = ui_manager.laser_style
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
                
            # Tajná zkratka pro export grafiky všech bloků do .png
            if event.type == pygame.KEYDOWN and event.key == pygame.K_F12:
                import os
                from blocks.crystal import Crystal
                from blocks.bulb import Bulb
                from blocks.mirror import Mirror
                from blocks.splitter import Splitter
                from blocks.color_switch import ColorSwitch
                from blocks.mixer import Mixer
                from blocks.crossover import Crossover
                from blocks.door import Door
                from blocks.teleporter import Teleporter
                from blocks.button import Button
                from blocks.block import Wall
                from blocks.prism import Prism
                from blocks.filter import Filter
                
                if not os.path.exists("exports"):
                    os.makedirs("exports")
                    
                ex_size = 200 # Rozlišení exportovaných obrázků (můžeš zvětšit)
                blocks_to_export = {
                    "Crystal": Crystal(0, 0, 1, (255, 0, 0), ex_size),
                    "Bulb": Bulb(0, 0, (0, 255, 0), ex_size),
                    "Mirror": Mirror(0, 0, 0, ex_size),
                    "Splitter": Splitter(0, 0, 0, ex_size),
                    "ColorSwitch": ColorSwitch(0, 0, (0, 255, 0), ex_size),
                    "Mixer": Mixer(0, 0, 2, ex_size),
                    "Crossover": Crossover(0, 0, ex_size),
                    "Door": Door(0, 0, ex_size),
                    "Teleporter": Teleporter(0, 0, ex_size),
                    "Button": Button(0, 0, ex_size),
                    "Wall": Wall(0, 0, ex_size),
                    "Prism": Prism(0, 0, ex_size),
                    "Filter": Filter(0, 0, (0, 200, 255), ex_size)
                }
                
                for name, b in blocks_to_export.items():
                    surf = pygame.Surface((ex_size, ex_size), pygame.SRCALPHA)
                    # Vyplníme pozadí temnou vesmírnou barvou ze hry, aby správně vynikla neonová záře (ADD blending)
                    surf.fill((8, 10, 18, 255))
                    b.draw(surf)
                    if hasattr(b, 'draw_overlay'):
                        b.draw_overlay(surf)
                    pygame.image.save(surf, f"exports/{name}.png")
                
                print(f"\n[ÚSPĚCH] Vyexportováno {len(blocks_to_export)} high-res bloků do složky 'exports'!\n")

            # Zpracování událostí pro UI
            action = ui_manager.handle_event(event)
            if action:
                action_type = action.get("action")
                if action_type == "load_tutorial":
                    if snd_click: snd_click.play()
                    blocks = level_manager.load_tutorial(action["level"])
                    engine.show_lasers = False
                    ui_manager.moves_made = 0
                    ui_manager.play_start_time = pygame.time.get_ticks()
                elif action_type == "quit":
                    pygame.quit()
                    sys.exit()
                elif action_type == "click":
                    if snd_click: snd_click.play()
                elif action_type == "open_url":
                    if snd_click: snd_click.play()
                    webbrowser.open(action["url"])
                elif action_type == "generate_ai":
                    if snd_click: snd_click.play()
                    blocks = level_manager.generate_ai_level(action["difficulty"])
                    engine.show_lasers = False
                    ui_manager.moves_made = 0
                    ui_manager.play_start_time = pygame.time.get_ticks()
                elif action_type == "open_community_menu":
                    if snd_click: snd_click.play()
                    # Okamžité zobrazení načítací obrazovky před stažením map
                    ui_manager.state = "LOADING"
                    screen.fill((10, 10, 15))
                    ui_manager.draw(screen)
                    pygame.display.flip()

                    # Provede stažení map z databáze a předá je do UI
                    levels = level_manager.search_community_levels()
                    ui_manager.set_community_levels(levels)
                    ui_manager.state = "COMMUNITY_PLAY"
                elif action_type == "preview_community_level":
                    if snd_click: snd_click.play()
                    ui_manager.state = "LOADING"
                    # Vykreslíme načítací obrazovku JEDNOU předtím, než hra "zamrzne"
                    screen.fill((10, 10, 10))
                    ui_manager.draw(screen)
                    pygame.display.flip()

                    # Teď proběhne samotné načítání, které může na chvíli hru zastavit
                    loaded_blocks = level_manager.load_community_level(action["level_id"])
                    if loaded_blocks:
                        ui_manager.set_preview_data(loaded_blocks, action)
                        ui_manager.state = "LEVEL_PREVIEW"
                    else:
                        # Pokud se mapa nenačte, vrátíme se do seznamu
                        ui_manager.state = "COMMUNITY_PLAY"
                elif action_type == "start_game":
                    if snd_click: snd_click.play()
                    blocks = ui_manager.preview_blocks
                    engine.show_lasers = False
                    ui_manager.state = "PLAY"
                    ui_manager.current_level = f"COMMUNITY_{ui_manager.preview_level_info['level_id']}"
                    ui_manager.current_map_title = ui_manager.preview_level_info.get("title", "Komunitní úroveň")
                    ui_manager.current_map_author = ui_manager.preview_level_info.get("author", "Neznámý autor")
                    ui_manager.moves_made = 0
                    ui_manager.play_start_time = pygame.time.get_ticks()
                elif action_type == "rate_map":
                    print(f"HODNOCENÍ: Uživatel dal mapě {action['level_id']} hodnocení {action['rating']} hvězd.")
                    # Zde by se volala funkce pro odeslání na API
                    # level_manager.rate_map(action['level_id'], action['rating'])


            # Zpracování kliknutí do herního pole, pokud hrajeme
            if ui_manager.state == "PLAY" and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                x, y = event.pos
                # Pokud jsme nekliknuli na UI tlačítko (Menu vlevo nahoře)
                if not (10 <= x <= 300 and 10 <= y <= 50):
                    if y >= screen_h - 55:
                        # Kliknutí na tlačítko START/STOP dole
                        if (screen_w // 2 - 125) <= x <= (screen_w // 2 + 125) and (screen_h - 48) <= y <= (screen_h - 8):
                            if snd_click: snd_click.play()
                            if engine.show_lasers:
                                if engine.is_exploded:
                                    # Tvrdý reset mapy po explozi
                                    if not str(ui_manager.current_level).startswith("COMMUNITY_") and ui_manager.current_level != "AI":
                                        blocks = level_manager.load_tutorial(ui_manager.current_level)
                                    elif str(ui_manager.current_level).startswith("COMMUNITY_"):
                                        level_id = str(ui_manager.current_level).split("_")[1]
                                        blocks = level_manager.load_community_level(level_id)
                                    engine.is_exploded = False
                                engine.show_lasers = False
                                for b in blocks:
                                    if hasattr(b, 'reset') and not type(b).__name__ == "Door": b.reset()
                                    if type(b).__name__ == "Bulb": b.is_lit = False
                                    if type(b).__name__ == "Button": b.is_pressed = False
                                    if type(b).__name__ == "Door": b.is_open = False
                            else:
                                engine.show_lasers = True
                                if snd_laser_on: snd_laser_on.play() # Zvuk startu paprsku
                                engine.is_animating = True
                                engine.explosion_played = False
                                engine.anim_frame = 0
                                engine.block_size = level_manager.block_size
                                engine.calculate_beams(blocks, level_manager.grid_w, level_manager.grid_h)
                    else:
                        # Kliknutí do herního pole (s dynamickým offsetem)
                        grid_px_w = level_manager.grid_w * level_manager.block_size
                        grid_px_h = level_manager.grid_h * level_manager.block_size
                        actual_offset_x = (screen_w - grid_px_w) // 2
                        is_tutorial = not str(ui_manager.current_level).startswith("COMMUNITY_") and ui_manager.current_level != "AI"
                        if is_tutorial:
                            actual_offset_y = 160 + (screen_h - 220 - grid_px_h) // 2
                        else:
                            actual_offset_y = max(80, (screen_h - 60 - grid_px_h) // 2)
                            
                        game_area_rect = pygame.Rect(actual_offset_x, actual_offset_y, grid_px_w, grid_px_h)
                        
                        if engine.show_lasers:
                            # Kliknutím kamkoliv do pole se lasery vypnou
                            engine.show_lasers = False
                            for b in blocks:
                                if hasattr(b, 'reset') and not type(b).__name__ == "Door": b.reset()
                                if type(b).__name__ == "Bulb": b.is_lit = False
                                if type(b).__name__ == "Button": b.is_pressed = False
                                if type(b).__name__ == "Door": b.is_open = False
                        else:
                            if game_area_rect.collidepoint(x, y):
                                grid_x = (x - actual_offset_x) // level_manager.block_size
                                grid_y = (y - actual_offset_y) // level_manager.block_size
                                for b in blocks:
                                    if b.x == grid_x and b.y == grid_y:
                                        # Počítání tahů a otočení
                                        if hasattr(b, 'on_click'):
                                            b.on_click()
                                            if getattr(b, 'movable', True): # Neměnné bloky by se neměly počítat, ale pro jistotu
                                                ui_manager.moves_made += 1
                                        snd = block_sounds.get(type(b).__name__, snd_block)
                                        if snd: snd.play()
                                        break

        # Vykreslení scény
        screen.fill((4, 4, 8)) # Hluboký vesmír
        mouse_pos = pygame.mouse.get_pos()

        # --- ANIMOVANÉ POZADÍ CELÉ HRY (VESMÍR) ---
        time_ms = pygame.time.get_ticks()
        
        # Jemný mlhovinový efekt (ambientní záře v pozadí)
        nebula_pulse = (math.sin(time_ms * 0.0005) + 1) / 2.0
        pygame.draw.circle(screen, (20, 10, 40), (screen_w // 4, screen_h // 3), int(300 + nebula_pulse * 50))
        pygame.draw.circle(screen, (10, 20, 40), (screen_w * 3 // 4, screen_h * 2 // 3), int(400 - nebula_pulse * 50))
        
        for i in range(200):
            layer = (i % 3) + 1 # 3 vrstvy pro paralaxní 3D efekt
            speed = 0.01 * layer
            px = (i * 137) % screen_w
            py = (screen_h - ((i * 251 + time_ms * speed) % screen_h)) % screen_h
            size = layer if i % 2 == 0 else layer - 1
            
            # Zbarvení hvězd (modré, fialové, čistě bílé)
            if i % 5 == 0: color = (150, 200, 255)
            elif i % 4 == 0: color = (255, 180, 255)
            else: color = (255, 255, 255)
            
            brightness = int((math.sin(time_ms * 0.002 + i) + 1) * 80) + 40
            f_color = (min(255, int(color[0] * brightness / 255)), 
                       min(255, int(color[1] * brightness / 255)), 
                       min(255, int(color[2] * brightness / 255)))
            pygame.draw.circle(screen, f_color, (int(px), int(py)), max(1, size))
        # ---------------------------------

        if ui_manager.state == "PLAY" or (ui_manager.state == "LEVEL_PREVIEW" and not ui_manager.preview_blocks):
            # Vykreslení herního pole na samostatný povrch (dynamická velikost)
            grid_px_w = level_manager.grid_w * level_manager.block_size
            grid_px_h = level_manager.grid_h * level_manager.block_size
            actual_offset_x = (screen_w - grid_px_w) // 2
            
            is_tutorial = not str(ui_manager.current_level).startswith("COMMUNITY_") and ui_manager.current_level != "AI"
            if is_tutorial:
                actual_offset_y = 160 + (screen_h - 220 - grid_px_h) // 2
            else:
                actual_offset_y = max(80, (screen_h - 60 - grid_px_h) // 2) # Odsazení kvůli top HUDu
            
            # Plochá zabarvená herní plocha (vesmírné sklo s odrazem)
            game_surface = pygame.Surface((grid_px_w, grid_px_h), pygame.SRCALPHA)
            pygame.draw.rect(game_surface, (8, 10, 18, 180), (0, 0, grid_px_w, grid_px_h), border_radius=15)
            
            pulse_grid = (math.sin(time_ms / 500.0) + 1) / 2.0
            grid_color = (30 + int(20 * pulse_grid), 40 + int(30 * pulse_grid), 60 + int(40 * pulse_grid))
            
            for grid_x in range(level_manager.grid_w):
                for grid_y in range(level_manager.grid_h):
                    rect = pygame.Rect(grid_x * level_manager.block_size, grid_y * level_manager.block_size, level_manager.block_size, level_manager.block_size)
                    # Subtilní, pulzující sci-fi mřížka
                    pygame.draw.rect(game_surface, grid_color, rect, 1)
                    # Zvýrazněné rohy (technologický uzel)
                    pygame.draw.circle(game_surface, (60, 150, 255), rect.topleft, 2)
                    
            # Vnější High-tech rámeček
            pygame.draw.rect(game_surface, (0, 180, 255, 60), (0, 0, grid_px_w, grid_px_h), 2, border_radius=15)
            
            # Zaměřovací rohy HUDu (HUD brackets)
            c_len = min(30, level_manager.block_size // 2)
            for cx, cy in [(0, 0), (grid_px_w-2, 0), (0, grid_px_h-2), (grid_px_w-2, grid_px_h-2)]:
                dir_x = 1 if cx == 0 else -1
                dir_y = 1 if cy == 0 else -1
                pts = [(cx + c_len * dir_x, cy), (cx, cy), (cx, cy + c_len * dir_y)]
                pygame.draw.lines(game_surface, (0, 255, 255), False, pts, 3)
                    
            # Zjištění, nad jakým blokem je myš
            hovered_block = None
            game_area_rect = pygame.Rect(actual_offset_x, actual_offset_y, grid_px_w, grid_px_h)
            if game_area_rect.collidepoint(mouse_pos):
                grid_x = (mouse_pos[0] - actual_offset_x) // level_manager.block_size
                grid_y = (mouse_pos[1] - actual_offset_y) // level_manager.block_size
                hovered_block = (grid_x, grid_y)
                    
            # Nyní kreslíme BLOKY PRVNÍ, takže paprsky budou létat viditelně nad nimi!
            for b in blocks:
                b.draw(game_surface)
                # Vykreslení barevného indikátoru propojení pro Tlačítka, Dveře a Teleporty
                if hasattr(b, 'link_color'):
                    pygame.draw.rect(game_surface, b.link_color, b.rect.inflate(-8, -8), 3, border_radius=8)
                    
                # Vykreslíme svítící hover (najetí myší) efekt nad samotným blokem
                if hovered_block and b.x == hovered_block[0] and b.y == hovered_block[1] and ui_manager.state == "PLAY":
                    hover_surf = pygame.Surface((level_manager.block_size, level_manager.block_size), pygame.SRCALPHA)
                    pygame.draw.rect(hover_surf, (255, 255, 255, 20), (0, 0, level_manager.block_size, level_manager.block_size), border_radius=12)
                    pygame.draw.rect(hover_surf, (255, 255, 255, 60), (0, 0, level_manager.block_size, level_manager.block_size), 2, border_radius=12)
                    game_surface.blit(hover_surf, (b.x * level_manager.block_size, b.y * level_manager.block_size))
                    
            # Lasery se překreslí přes bloky (ideální pro zrcadla a křižovatky)
            engine.update_animation()
            engine.draw(game_surface)
            
            # Přehrávání zvuků paprsku přesně ve chvíli, kdy doletí k cíli
            while getattr(engine, 'sound_queue', []):
                snd_type = engine.sound_queue.pop(0)
                if snd_type == "bulb" and snd_bulb_hit: snd_bulb_hit.play()
                elif snd_type == "door" and snd_door_open: snd_door_open.play()
                elif snd_type == "hit" and snd_hit: snd_hit.play()
            
            # Vykreslení vrchní vrstvy bloků (aby paprsky zajížděly "pod" prstence Teleportu atd.)
            for b in blocks:
                if hasattr(b, 'draw_overlay'):
                    b.draw_overlay(game_surface)
                    
                # Vizuální znázornění zablokování (přišroubování) u logických bloků
                if not getattr(b, 'movable', False) and type(b).__name__ in ["Mirror", "Splitter", "Mixer", "ColorSwitch", "Crossover"]:
                    for ox, oy in [(15, 15), (level_manager.block_size-15, 15), (15, level_manager.block_size-15), (level_manager.block_size-15, level_manager.block_size-15)]:
                        pygame.draw.circle(game_surface, (15, 15, 20), (b.rect.x + ox, b.rect.y + oy), 6)
                        pygame.draw.circle(game_surface, (100, 100, 120), (b.rect.x + ox, b.rect.y + oy), 6, 2)
                        pygame.draw.line(game_surface, (100, 100, 120), (b.rect.x + ox - 3, b.rect.y + oy - 3), (b.rect.x + ox + 3, b.rect.y + oy + 3), 2)
                        pygame.draw.line(game_surface, (100, 100, 120), (b.rect.x + ox - 3, b.rect.y + oy + 3), (b.rect.x + ox + 3, b.rect.y + oy - 3), 2)
            
            if engine.show_lasers and engine.is_exploded:
                if engine.anim_frame >= engine.explosion_dist:
                    if not getattr(engine, 'explosion_played', False):
                        if snd_explosion: snd_explosion.play()
                        engine.explosion_played = True
                        shake_frames = 20 # Spuštění třesu obrazovky!

            # Vykreslení popisků pro Library (Tutoriály)
            is_tutorial = not str(ui_manager.current_level).startswith("COMMUNITY_") and ui_manager.current_level != "AI"
            if is_tutorial and ui_manager.current_level in level_manager.block_tutorials:
                tut_data = level_manager.block_tutorials[ui_manager.current_level]
                title_surf = ui_manager.big_font.render(tut_data["title"], True, (0, 200, 220))
                screen.blit(title_surf, (screen_w // 2 - title_surf.get_width()//2, 10))
                
                # Automatické zalamování dlouhého textu
                words = tut_data["desc"].split(' ')
                lines = []
                current_line = ""
                for word in words:
                    test_line = current_line + word + " "
                    if ui_manager.small_font.size(test_line)[0] > screen_w - 40:
                        lines.append(current_line)
                        current_line = word + " "
                    else:
                        current_line = test_line
                lines.append(current_line)
                
                for i, line in enumerate(lines):
                    desc_surf = ui_manager.small_font.render(line, True, (200, 220, 255))
                    screen.blit(desc_surf, (screen_w // 2 - desc_surf.get_width()//2, 60 + i * 30))
                    
            # Vykreslení horního panelu (Čas a Tahy) pro aktivní hru
            if not is_tutorial and not (engine.is_victory(blocks) and engine.show_lasers):
                time_elapsed = (pygame.time.get_ticks() - ui_manager.play_start_time) // 1000
                ui_manager.play_time_str = f"{time_elapsed//60:02}:{time_elapsed%60:02}"
                
                hud_rect = pygame.Rect(screen_w // 2 - 150, 15, 300, 45)
                pygame.draw.rect(screen, (20, 25, 30), hud_rect, border_radius=12)
                pygame.draw.rect(screen, (0, 200, 220), hud_rect, 2, border_radius=12)
                t_img = ui_manager.small_font.render(f"Čas: {ui_manager.play_time_str}", True, (200, 255, 255))
                m_img = ui_manager.small_font.render(f"Tahy: {ui_manager.moves_made}", True, (200, 255, 255))
                screen.blit(t_img, (hud_rect.left + 20, hud_rect.centery - t_img.get_height()//2))
                screen.blit(m_img, (hud_rect.right - m_img.get_width() - 20, hud_rect.centery - m_img.get_height()//2))

            # Aplikace třesu obrazovky (Screen Shake)
            shake_x, shake_y = 0, 0
            if shake_frames > 0:
                shake_x = random.randint(-6, 6)
                shake_y = random.randint(-6, 6)
                shake_frames -= 1

            screen.blit(game_surface, (actual_offset_x + shake_x, actual_offset_y + shake_y))

            if engine.show_lasers and not engine.is_animating and ui_manager.state == "PLAY":
                if engine.is_victory(blocks) and not engine.is_exploded:
                    if ui_manager.current_level == "AI" or str(ui_manager.current_level).startswith("COMMUNITY_"): # Pro tutoriály výhru neukazujeme
                        ui_manager.state = "VICTORY"
                        if snd_victory: snd_victory.play()

            # Vykreslení spodního řídicího panelu
            if ui_manager.state == "PLAY":
                pygame.draw.rect(screen, (20, 25, 30), (0, screen_h - 55, screen_w, 55))
                pygame.draw.line(screen, (50, 60, 80), (0, screen_h - 55), (screen_w, screen_h - 55), 2) # Tech hrana
                
                btn_color = (0, 200, 220) if not engine.show_lasers else (180, 80, 80)
                if engine.is_exploded: btn_color = (200, 180, 100)  # Výstražná zlatá
                
                btn_rect = pygame.Rect(screen_w // 2 - 125, screen_h - 48, 250, 40)
                is_btn_hovered = btn_rect.collidepoint(mouse_pos)
                
                if is_btn_hovered:
                    btn_color = (min(255, btn_color[0]+50), min(255, btn_color[1]+50), min(255, btn_color[2]+50))
                    pygame.draw.rect(screen, (35, 40, 50), btn_rect, border_radius=10)
                    pygame.draw.rect(screen, btn_color, btn_rect, 3, border_radius=10)
                else:
                    pygame.draw.rect(screen, (15, 18, 25), btn_rect, border_radius=10)
                    pygame.draw.rect(screen, btn_color, btn_rect, 2, border_radius=10)
                
                font = ui_manager.small_font
                txt = "ZASTAVIT (Upravit)" if engine.show_lasers else "SPUSTIT"
                if engine.is_exploded: txt = "RESET (Exploze!)"
                img = font.render(txt, True, btn_color)
                screen.blit(img, img.get_rect(center=btn_rect.center))

                # Zobrazení aktuálního levelu
                level_font = ui_manager.small_font
                if str(ui_manager.current_level).startswith("COMMUNITY_"):
                    level_text = f"{ui_manager.current_map_title} od {ui_manager.current_map_author}"
                else:
                    level_text = "Level: AI Vygenerováno" if ui_manager.current_level == "AI" else "Režim pískoviště"
                level_img = level_font.render(level_text, True, (220, 220, 220))
                screen.blit(level_img, (20, screen_h - 55 + (55 - level_img.get_height()) // 2))

        # Update transitions before drawing
        dt = clock.get_time() / 1000.0  # Delta time in seconds since last frame
        ui_manager.update_transition(dt)

        ui_manager.draw(screen)

        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()