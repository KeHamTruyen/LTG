import pygame, random, math, os
from dataclasses import dataclass

# ---------- config ----------
WIDTH, HEIGHT = 960, 540
FPS = 60

BLACK=(0,0,0); WHITE=(255,255,255); GRAY=(60,60,60)
DARK=(35,35,35); GREEN=(60,160,60); DARK_GREEN=(30,110,30)
RED=(200,60,60); YELLOW=(235,200,90); BROWN=(100,70,50)

# assets (có thể đổi tên file ở đây)
ASSET_PATHS = {
    "zombie": "zombieN.png",
    "grave": "graveN.png", 
    "background": "background.jpg",
    "hit_sound": "hit.mp3",
    "bgm": "bgmusic.mp3",
    "heart_full": "heart_full.png",
    "heart_empty": "heart_empty.png",
}

pygame.init()
try:
    pygame.mixer.init()
    MIXER_OK = True
except Exception:
    MIXER_OK = False

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Zombie Whack")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 28)
font_big = pygame.font.SysFont(None, 48)
font_title = pygame.font.SysFont(None, 72)

# ---------- load assets (optional) ----------
def load_img(path_key):
    p = ASSET_PATHS[path_key]
    if os.path.exists(p):
        try:
            return pygame.image.load(p).convert_alpha()
        except Exception:
            return None
    return None

IMG_ZOMBIE = load_img("zombie")
IMG_GRAVE = load_img("grave")
IMG_BG = load_img("background")

# Load heart images
IMG_HEART_FULL = load_img("heart_full") 
IMG_HEART_EMPTY = load_img("heart_empty")

# Scale heart images if loaded successfully
if IMG_HEART_FULL:
    IMG_HEART_FULL = pygame.transform.smoothscale(IMG_HEART_FULL, (38, 38))
if IMG_HEART_EMPTY:
    IMG_HEART_EMPTY = pygame.transform.smoothscale(IMG_HEART_EMPTY, (38, 38))

HIT_SOUND = None
if MIXER_OK and os.path.exists(ASSET_PATHS["hit_sound"]):
    try:
        HIT_SOUND = pygame.mixer.Sound(ASSET_PATHS["hit_sound"])
    except Exception:
        HIT_SOUND = None

if MIXER_OK and os.path.exists(ASSET_PATHS["bgm"]):
    try:
        pygame.mixer.music.load(ASSET_PATHS["bgm"])
        pygame.mixer.music.set_volume(0.35)
        pygame.mixer.music.play(-1)
    except Exception:
        pass

# ---------- holes ----------
def make_holes(cols=5, rows=3, margin_x=120, margin_y=90):
    holes=[]
    grid_w=(WIDTH-2*margin_x); grid_h=(HEIGHT-2*margin_y)
    step_x=grid_w//(cols-1); step_y=grid_h//(rows-1)
    for r in range(rows):
        for c in range(cols):
            x = margin_x + c*step_x
            y = margin_y + r*step_y + (10 if r%2 else 0)
            holes.append((x,y))
    return holes
HOLES = make_holes()

# ---------- particles ----------
@dataclass
class Particle:
    x: float; y: float; vx: float; vy: float; life: float; radius: float
    def update(self, dt):
        self.x += self.vx*dt; self.y += self.vy*dt
        self.vy += 900*dt*0.3
        self.life -= dt
        self.radius = max(0, self.radius - 35*dt)
    def draw(self, surf):
        # Blood effect removed - using only image assets
        pass

# ---------- helpers ----------
def blit_center(surf, img, center_xy, scale=None):
    if img is None: return
    if scale:
        img = pygame.transform.smoothscale(img, scale)
    rect = img.get_rect(center=center_xy)
    surf.blit(img, rect.topleft)

# ---------- zombie ----------
class Zombie:
    def __init__(self, pos, timer_mode=True):
        self.x,self.y = pos
        self.base_radius = 46
        self.state = "appearing"     # appearing -> alive -> disappearing -> dead
        self.t_appear = 0.2
        self.t_disappear = 0.18
        self.t_alive = random.uniform(0.9,1.6)
        self.timer_mode = timer_mode
        self.time_in_state = 0.0
        self.hit_flag=False
        self.dead=False

    def update(self, dt):
        self.time_in_state += dt
        if self.state=="appearing":
            if self.time_in_state>=self.t_appear:
                self.state="alive"; self.time_in_state=0.0
        elif self.state=="alive":
            if self.timer_mode and self.time_in_state>=self.t_alive:
                self.state="disappearing"; self.time_in_state=0.0
                return "escaped"
        elif self.state=="disappearing":
            if self.time_in_state>=self.t_disappear:
                self.dead=True
        return None

    def is_hittable(self):
        return self.state in ("appearing","alive")

    def hit_test(self, mx,my):
        r=self.current_radius()
        zombie_y = self.y + 50 
        dx,dy=mx-self.x, my-zombie_y
        return dx*dx+dy*dy <= r*r

    def current_radius(self):
        if self.state=="appearing":
            k=min(1.0, self.time_in_state/self.t_appear)
            s=1-(1-k)**3
            return max(5, int(self.base_radius*s))
        elif self.state=="alive":
            return self.base_radius
        elif self.state=="disappearing":
            k=min(1.0, self.time_in_state/self.t_disappear)
            s=(1-k)**2
            return max(1, int(self.base_radius*s))
        return 0

    def on_hit(self):
        if self.is_hittable():
            self.hit_flag=True
            self.state="disappearing"; self.time_in_state=0.0
            return True
        return False

    def draw(self, surf):
        r=self.current_radius()
        if r<=0: return

        zombie_y = self.y + 50  
        if IMG_ZOMBIE:
            sz = int(r*2)
            blit_center(surf, IMG_ZOMBIE, (self.x, zombie_y), (sz, sz))
            # Draw hit effect (if needed)


# ---------- UI Button ----------
class Button:
    def __init__(self, rect, text, on_click):
        self.rect=pygame.Rect(rect)
        self.text=text
        self.on_click=on_click
        self.hover=False
    def draw(self, surf):
        label=font_big.render(self.text, True, WHITE)
        surf.blit(label, (self.rect.centerx-label.get_width()//2, self.rect.centery-label.get_height()//2))
    def handle(self, event):
        if event.type==pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if self.rect.collidepoint(event.pos):
                self.on_click()

# ---------- Game ----------
class Game:
    def __init__(self):
        # states: menu | playing | paused | gameover
        self.state="menu"
        self.timer_mode = True         
        self.round_time = 60           
        self.time_left = self.round_time

        self.lives_max = 3
        self.lives = self.lives_max

        self.zombie=None
        self.spawn_delay=(0.4,0.8)
        self.next_spawn_in=0.6
        self.particles=[]
        self.hits=0; self.miss_clicks=0; self.escaped=0

        self.background=self.build_background()

        # menu buttons
        btn_w, btn_h = 260, 56
        self.btn_start = Button(((WIDTH-btn_w)//2, 260, btn_w, btn_h), "Start Game", self.start_game)
        self.btn_timer_toggle = Button(((WIDTH-btn_w)//2, 330, btn_w, btn_h),
                                 "Timer: ON", self.toggle_zombie_timer)

        # time adjust buttons
        self.btn_time_minus = Button((WIDTH//2 - 200, 200, 90, 48), "-30s", self.dec_round_time)
        self.btn_time_plus  = Button((WIDTH//2 + 110, 200, 90, 48), "+30s", self.inc_round_time)

        self.btn_quit = Button(((WIDTH-btn_w)//2, 400, btn_w, btn_h), "Quit", self.quit_game)

        # gameover buttons
        self.btn_again = Button(((WIDTH-btn_w)//2, 370, btn_w, btn_h), "Play Again", self.play_again)
        self.btn_backmenu = Button(((WIDTH-btn_w)//2, 440, btn_w, btn_h), "Back to Menu", self.back_to_menu)

        # pause buttons
        self.btn_resume = Button(((WIDTH-btn_w)//2, 320, btn_w, btn_h), "Resume", self.resume_game)
        self.btn_pause_menu = Button(((WIDTH-btn_w)//2, 390, btn_w, btn_h), "Main Menu", self.back_to_menu)

    # ---------- background ----------
    def build_background(self):
        if IMG_BG:
            return pygame.transform.smoothscale(IMG_BG, (WIDTH, HEIGHT))
        bg=pygame.Surface((WIDTH,HEIGHT))
        bg.fill((20,25,28))
        return bg

    # ---------- menu actions ----------
    def start_game(self):
        self.reset_all()
        self.state="playing"
    def toggle_zombie_timer(self):
        self.timer_mode = not self.timer_mode
        self.btn_timer_toggle.text = f"Timer: {'ON' if self.timer_mode else 'OFF'}"
    def quit_game(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))
    def dec_round_time(self):
        self.round_time = max(30, self.round_time - 30)
    def inc_round_time(self):
        self.round_time = min(300, self.round_time + 30)

    # ---------- game over actions ----------
    def play_again(self):
        self.reset_all()
        self.state="playing"
    def back_to_menu(self):
        self.state="menu"

    # ---------- pause actions ----------
    def pause_game(self):
        self.state="paused"
    def resume_game(self):
        self.state="playing"

    # ---------- core gameplay ----------
    def spawn_zombie(self):
        self.zombie = Zombie(random.choice(HOLES), timer_mode=self.timer_mode)

    def update_particles(self, dt):
        for p in self.particles: p.update(dt)
        self.particles=[p for p in self.particles if p.life>0 and p.radius>0]

    def add_hit_particles(self, x,y):
        for _ in range(12):
            ang=random.uniform(0, math.tau); spd=random.uniform(140,260)
            vx=math.cos(ang)*spd; vy=math.sin(ang)*spd-50
            self.particles.append(Particle(x,y,vx,vy,life=0.5,radius=random.uniform(6,10)))

    def on_click(self, mx,my):
        if self.state!="playing": return
        hit=False
        if self.zombie and self.zombie.is_hittable() and self.zombie.hit_test(mx,my):
            if self.zombie.on_hit():
                hit=True; self.hits+=1; 
                self.add_hit_particles(self.zombie.x, self.zombie.y + 50)
                if HIT_SOUND:
                    try: HIT_SOUND.play()
                    except Exception: pass
        if not hit:
            self.miss_clicks+=1
            self.lives = max(0, self.lives-1)
            if self.lives==0:
                self.state="gameover"

    def update(self, dt):
        if self.state=="playing":
            if self.timer_mode:
                self.time_left -= dt
                if self.time_left <= 0:
                    self.time_left = 0
                    self.state="gameover"

            # zombie lifecycle
            if self.zombie:
                escaped=self.zombie.update(dt)
                if escaped=="escaped": self.escaped+=1
                if self.zombie.dead:
                    self.zombie=None; self.next_spawn_in=random.uniform(*self.spawn_delay)
            if self.zombie is None:
                self.next_spawn_in-=dt
                if self.next_spawn_in<=0: self.spawn_zombie()

            self.update_particles(dt)
        elif self.state=="paused":
            self.update_particles(dt)

    # ---------- drawing ----------
    def draw_timer(self, surf):
        if not self.timer_mode:
            return  
        t = int(self.time_left)
        mm = t//60; ss=t%60
        txt = font_big.render(f"TIME {mm:02d}:{ss:02d}", True, YELLOW)
        surf.blit(txt, (WIDTH-220, 10))

    def draw_lives(self, surf):
        for i in range(self.lives_max):
            img = IMG_HEART_FULL if i < self.lives else IMG_HEART_EMPTY
            surf.blit(img, (20 + i*44, 12))

    def draw_hud(self, surf):
        total = max(1, self.hits + self.miss_clicks)
        acc = 100.0 * self.hits / total
        bar=pygame.Surface((WIDTH,70), pygame.SRCALPHA); bar.fill((0,0,0,80)); surf.blit(bar,(0,0))
        # left: lives
        self.draw_lives(surf)
        # center: title
        title=font_big.render("ZOMBIE WHACK", True, YELLOW)
        surf.blit(title,(WIDTH//2 - title.get_width()//2, 12))
        # right: timer
        self.draw_timer(surf)

        # row 2
        t_hits=font.render(f"Hits: {self.hits}", True, WHITE)
        t_miss=font.render(f"Miss: {self.miss_clicks}", True, WHITE)
        t_esc =font.render(f"Escaped: {self.escaped}", True, WHITE)
        t_acc =font.render(f"Accuracy: {acc:.1f}%", True, WHITE)
        x=20; surf.blit(t_hits,(x,46)); x+=110
        surf.blit(t_miss,(x,46)); x+=120
        surf.blit(t_esc,(x,46)); x+=140
        surf.blit(t_acc,(x,46))

    def draw_menu(self, surf):
        surf.blit(self.background,(0,0))
        overlay=pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,120)); surf.blit(overlay,(0,0))
        title=font_title.render("ZOMBIE WHACK", True, YELLOW)
        surf.blit(title, (WIDTH//2 - title.get_width()//2, 90))
        label=font_big.render("Round Time:", True, WHITE)
        surf.blit(label, (WIDTH//2 - label.get_width()//2, 160))
        mm = self.round_time//60; ss=self.round_time%60
        cur=font_big.render(f"{mm:02d}:{ss:02d}", True, YELLOW)
        surf.blit(cur, (WIDTH//2 - cur.get_width()//2, 205))

        for btn in (self.btn_time_minus, self.btn_time_plus, self.btn_start, self.btn_timer_toggle, self.btn_quit):
            btn.draw(surf)
        help1=font.render("Controls: Left Click: Whack | ESC: Quit", True, (180,180,180))
        surf.blit(help1, (WIDTH//2 - help1.get_width()//2, HEIGHT-30))

    def draw_gameover(self, surf):
        surf.blit(self.background,(0,0))
        overlay=pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,160)); surf.blit(overlay,(0,0))
        title=font_title.render("GAME OVER", True, YELLOW)
        surf.blit(title, (WIDTH//2 - title.get_width()//2, 90))

        total = max(1, self.hits + self.miss_clicks)
        acc = 100.0 * self.hits / total
        lines = [
            f"Hits: {self.hits}",
            f"Miss: {self.miss_clicks}",
            f"Escaped: {self.escaped}",
            f"Accuracy: {acc:.1f}%",
        ]
        y=180
        for s in lines:
            t=font_big.render(s, True, WHITE)
            surf.blit(t, (WIDTH//2 - t.get_width()//2, y)); y+=44

        for btn in (self.btn_again, self.btn_backmenu):
            btn.draw(surf)

    def draw_pause(self, surf):
        overlay=pygame.Surface((WIDTH,HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,180)); surf.blit(overlay,(0,0))
        
        title=font_title.render("PAUSED", True, YELLOW)
        surf.blit(title, (WIDTH//2 - title.get_width()//2, 150))
        
        # hiển thị stats hiện tại
        total = max(1, self.hits + self.miss_clicks)
        acc = 100.0 * self.hits / total
        lines = [
            f"Current Stats:",
            f"Hits: {self.hits}",
            f"Miss: {self.miss_clicks}", 
            f"Escaped: {self.escaped}",
            f"Accuracy: {acc:.1f}%",
        ]
        y=200
        for s in lines:
            color = YELLOW if s.startswith("Current") else WHITE
            t=font.render(s, True, color)  # dùng font nhỏ hơn
            surf.blit(t, (WIDTH//2 - t.get_width()//2, y)); y+=25

        for btn in (self.btn_resume, self.btn_pause_menu):
            btn.draw(surf)

    def draw_graves(self, surf):
        for (x,y) in HOLES:
            if IMG_GRAVE:
                # scale grave 
                gw = int(46*2.6); gh = int(46*2.2)  # dùng base_radius = 46
                grave_scaled = pygame.transform.smoothscale(IMG_GRAVE, (gw, gh))
                # mộ vẽ ở vị trí thấp hơn để tạo lỗ
                grave_rect = grave_scaled.get_rect(center=(x, y+50))  
                surf.blit(grave_scaled, grave_rect.topleft)

    def draw(self, surf):
        surf.blit(self.background,(0,0))
        self.draw_graves(surf)
        
        if self.state=="menu":
            self.draw_menu(surf); return
        if self.state=="gameover":
            self.draw_gameover(surf); return
        if self.state=="paused":
            if self.zombie: self.zombie.draw(surf)
            for p in self.particles: p.draw(surf)
            self.draw_hud(surf)
            self.draw_pause(surf); return

        if self.zombie: self.zombie.draw(surf)
        for p in self.particles: p.draw(surf)
        self.draw_hud(surf)

    # ---------- resets ----------
    def reset_scores_only(self):
        self.hits=self.miss_clicks=self.escaped=0

    def reset_all(self):
        self.reset_scores_only()
        self.lives=self.lives_max
        self.time_left=float(self.round_time)
        self.zombie=None; self.particles.clear(); self.next_spawn_in=0.4

# ---------- main loop ----------
def main():
    game=Game(); running=True
    while running:
        dt=clock.tick(FPS)/1000.0
        for event in pygame.event.get():
            if event.type==pygame.QUIT: running=False
            elif game.state=="menu":
                for btn in (game.btn_time_minus, game.btn_time_plus, game.btn_start, game.btn_timer_toggle, game.btn_quit):
                    btn.handle(event)
            elif game.state=="gameover":
                for btn in (game.btn_again, game.btn_backmenu):
                    btn.handle(event)
            elif game.state=="paused":
                for btn in (game.btn_resume, game.btn_pause_menu):
                    btn.handle(event)
            elif event.type==pygame.KEYDOWN and game.state=="playing":
                if event.key==pygame.K_ESCAPE: 
                    game.pause_game()  # pause thay vì quit
                elif event.key==pygame.K_r: game.reset_scores_only()
                elif event.key==pygame.K_t:
                    game.timer_mode = not game.timer_mode
                    if game.zombie: game.zombie.timer_mode = game.timer_mode
            elif event.type==pygame.KEYDOWN and game.state=="paused":
                if event.key==pygame.K_ESCAPE:
                    game.resume_game()  # ESC để resume
            elif event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
                if game.state=="playing":
                    mx,my=pygame.mouse.get_pos(); game.on_click(mx,my)

        # hover effects
        if game.state=="menu":
            mx,my=pygame.mouse.get_pos()
            for btn in (game.btn_time_minus, game.btn_time_plus, game.btn_start, game.btn_timer_toggle, game.btn_quit):
                btn.hover = btn.rect.collidepoint((mx,my))
        elif game.state=="gameover":
            mx,my=pygame.mouse.get_pos()
            for btn in (game.btn_again, game.btn_backmenu):
                btn.hover = btn.rect.collidepoint((mx,my))
        elif game.state=="paused":
            mx,my=pygame.mouse.get_pos()
            for btn in (game.btn_resume, game.btn_pause_menu):
                btn.hover = btn.rect.collidepoint((mx,my))

        game.update(dt)
        game.draw(screen)
        pygame.display.flip()
    pygame.quit()

if __name__=="__main__":
    main()
