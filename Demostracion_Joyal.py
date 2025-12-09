# Demostracion_Joyal_final.py
# Interfaz limpia y profesional para la demostración de Joyal (Modo 1 y Modo 2)
# Guarda esto y ejecútalo con: python Demostracion_Joyal_final.py
# Requiere: pygame

import pygame
import math
import re
from collections import deque

pygame.init()

# -------------------------
# Configuración ventana
# -------------------------
WIDTH, HEIGHT = 1280, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Demostración de Joyal — UI Final")
clock = pygame.time.Clock()

# -------------------------
# Paleta y fuentes
# -------------------------
COL_BG = (245, 247, 250)
COL_HEADER = (18, 56, 120)
COL_PANEL = (255, 255, 255)
COL_ACCENT = (29, 131, 212)
COL_ACCENT_D = (20, 90, 170)
COL_TEXT = (36, 40, 44)
COL_GRAY = (150, 155, 160)
COL_SUCCESS = (46, 204, 113)
COL_DANGER = (231, 76, 60)
COL_VERTEX = (52, 152, 219)
COL_VERTEX_TEXT = (255, 255, 255)
COL_EDGE = (156, 163, 175)
COL_SPINE = (200, 60, 60)

FONT_TITLE = pygame.font.Font(None, 54)
FONT_SUB = pygame.font.Font(None, 26)
FONT_REG = pygame.font.Font(None, 22)
FONT_BOLD = pygame.font.Font(None, 26)
FONT_SMALL = pygame.font.Font(None, 18)
FONT_NUM = pygame.font.Font(None, 24)

# -------------------------
# Helpers UI
# -------------------------
def draw_text(surf, txt, font, color, x, y):
    surf.blit(font.render(txt, True, color), (x, y))

class Button:
    def __init__(self, x, y, w, h, text, color=COL_ACCENT):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover = False
    def update(self, mouse):
        self.hover = self.rect.collidepoint(mouse)
    def draw(self, surf):
        bg = tuple(min(255, c+20) for c in self.color) if self.hover else self.color
        # shadow
        shadow = pygame.Surface((self.rect.w, self.rect.h), pygame.SRCALPHA)
        pygame.draw.rect(shadow, (0,0,0,28), shadow.get_rect(), border_radius=10)
        surf.blit(shadow, (self.rect.x+4, self.rect.y+4))
        pygame.draw.rect(surf, bg, self.rect, border_radius=10)
        pygame.draw.rect(surf, (255,255,255), self.rect, 2, border_radius=10)
        t = FONT_BOLD.render(self.text, True, (255,255,255))
        surf.blit(t, (self.rect.centerx - t.get_width()//2, self.rect.centery - t.get_height()//2))
    def clicked(self, event):
        return event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover

class InputBox:
    def __init__(self, x, y, w, h, placeholder=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = ''
        self.placeholder = placeholder
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
    def draw(self, surf):
        pygame.draw.rect(surf, COL_PANEL, self.rect, border_radius=10)
        pygame.draw.rect(surf, COL_ACCENT if self.active else COL_GRAY, self.rect, 2, border_radius=10)
        display = self.text if self.text else self.placeholder
        color = COL_TEXT if self.text else (170,170,170)
        t = FONT_REG.render(display, True, color)
        surf.blit(t, (self.rect.x + 10, self.rect.y + (self.rect.h - t.get_height())//2))
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 10 + t.get_width()
            pygame.draw.line(surf, COL_ACCENT, (cursor_x, self.rect.y + 8), (cursor_x, self.rect.y + self.rect.h - 8), 2)
    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                return True
            else:
                if event.unicode.isprintable():
                    self.text += event.unicode
        return False
    def get(self):
        return self.text.strip()

# -------------------------
# Algoritmos de grafos y utilidades
# -------------------------
n = 6
vertice_pos = []
vertice_radius = 26
edges = []
graph = []
parent = []

def calcular_posiciones(N):
    global vertice_pos, vertice_radius
    vertice_pos = []
    cx, cy = int(WIDTH * 0.62), int(HEIGHT * 0.55)
    R = min(300, 100 + N * 12)
    for i in range(N):
        ang = 2 * math.pi * i / N - math.pi/2
        vertice_pos.append((int(cx + R * math.cos(ang)), int(cy + R * math.sin(ang))))
    vertice_radius = max(16, min(30, 180 // max(3,N)))
    return vertice_pos

def inicializar_estructuras(N):
    global n, edges, graph, parent
    n = N
    edges = []
    graph = [[] for _ in range(n)]
    parent = list(range(n))
    calcular_posiciones(n)

def find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]

def union(a,b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[rb] = ra
        return True
    return False

def bfs_path(a,b):
    if a==b: return [a]
    vis = [False]*n
    prev = [-1]*n
    q = deque([a]); vis[a]=True
    while q:
        u = q.popleft()
        for v in graph[u]:
            if not vis[v]:
                vis[v]=True
                prev[v]=u
                q.append(v)
                if v==b:
                    path=[]
                    cur=v
                    while cur!=-1:
                        path.append(cur)
                        cur=prev[cur]
                    return list(reversed(path))
    return None

# -------------------------
# Parsing robusto para modo 2
# -------------------------
def limpiar_entrada_f(raw):
    txt = raw.lower()
    txt = txt.replace('→','->').replace('=>','->').replace(':','->')
    txt = txt.replace('(', '').replace(')', '').replace('[','').replace(']','').replace('{','').replace('}','')
    txt = txt.replace(' ', '')
    if 'f=' in txt:
        txt = txt.split('f=')[-1]
    return txt

def parsear_funcion(raw, N):
    txt = limpiar_entrada_f(raw)
    if not txt:
        return None, "Entrada vacía."
    partes = re.split(r',|;|\s+', txt)
    pares = []
    for p in partes:
        if not p: continue
        if '->' in p:
            a,b = p.split('->')
            if a.isdigit() and b.isdigit():
                pares.append((int(a), int(b)))
        else:
            nums = re.findall(r'\d+', p)
            if len(nums)==2:
                pares.append((int(nums[0]), int(nums[1])))
    if not pares:
        return None, "No se pudo interpretar la función."
    f = [None]*N
    for a,b in pares:
        if not (1 <= a <= N and 1 <= b <= N):
            return None, f"Valores fuera de rango (1..{N})."
        f[a-1] = b-1
    if any(v is None for v in f):
        return None, "Faltan valores en f; la función debe definir f(i) para cada i."
    return f, "OK"

# -------------------------
# Dibujado del grafo
# -------------------------
def draw_graph(surface, highlight_vertices=None, spine_edges=None, directed_edges=None):
    # edges (simple lines)
    spine_edges = spine_edges or []
    directed_edges = directed_edges or []
    for a,b in edges:
        color = COL_EDGE
        w = 3
        if (a,b) in spine_edges or (b,a) in spine_edges:
            color = COL_SPINE; w = 5
        pygame.draw.line(surface, color, vertice_pos[a], vertice_pos[b], w)
    # vertices
    for i, (x,y) in enumerate(vertice_pos):
        # draw shadow
        pygame.draw.circle(surface, (0,0,0,20), (int(x+2), int(y+2)), vertice_radius)
        col = COL_VERTEX
        if highlight_vertices:
            if i in highlight_vertices.get('selected', []):
                col = (245, 196, 72)
            if i in highlight_vertices.get('start', []):
                col = COL_SUCCESS
            if i in highlight_vertices.get('end', []):
                col = COL_DANGER
        pygame.draw.circle(surface, col, (int(x), int(y)), vertice_radius)
        pygame.draw.circle(surface, (255,255,255), (int(x), int(y)), vertice_radius, 2)
        ns = FONT_NUM.render(str(i+1), True, COL_VERTEX_TEXT)
        surface.blit(ns, (x - ns.get_width()/2, y - ns.get_height()/2))
    # directed edges arrows (optional)
    for v1, v2 in directed_edges:
        draw_arrow(surface, vertice_pos[v1], vertice_pos[v2], COL_ACCENT)

def draw_arrow(surface, start, end, color):
    dx = end[0]-start[0]; dy = end[1]-start[1]
    L = math.hypot(dx, dy)
    if L < 1e-6: return
    sx = start[0] + dx*(vertice_radius)/L
    sy = start[1] + dy*(vertice_radius)/L
    ex = end[0] - dx*(vertice_radius)/L
    ey = end[1] - dy*(vertice_radius)/L
    pygame.draw.line(surface, color, (sx,sy), (ex,ey), 3)
    angle = math.atan2(dy, dx)
    size = 10
    left = (ex - size*math.cos(angle - math.pi/6), ey - size*math.sin(angle - math.pi/6))
    right = (ex - size*math.cos(angle + math.pi/6), ey - size*math.sin(angle + math.pi/6))
    pygame.draw.polygon(surface, color, [(ex,ey), left, right])

# -------------------------
# Modo 1: Árbol -> Función
# -------------------------
class ModeTreeToFunction:
    def __init__(self):
        self.step = 0
        self.selected = None
        self.start = None
        self.end = None
        self.function = [None]*n
        self.spine_path = None
        self.vertex_buttons = []  # not used visually, but kept for event mapping
        # control buttons
        self.btn_back = Button(24,24,120,42, "MENÚ", color=(120,120,120))
        self.btn_reset = Button(WIDTH-150,24,120,42, "REINICIAR", color=(230,180,40))
        self.btn_next = Button(WIDTH-300, HEIGHT-80, 120,42, "SIGUIENTE", color=COL_SUCCESS)
        self.btn_prev = Button(WIDTH-430, HEIGHT-80, 120,42, "ATRÁS", color=(160,160,160))
    def draw(self, surf):
        surf.fill(COL_BG)
        # header
        pygame.draw.rect(surf, COL_HEADER, (0,0,WIDTH,110))
        draw_text(surf, "MODO 1 — ÁRBOL → FUNCIÓN", FONT_TITLE, (255,255,255), 18, 22)
        draw_text(surf, self.get_instruction(), FONT_SUB, (220,220,220), 18, 70)
        # left panel
        left_w = 340
        pygame.draw.rect(surf, COL_PANEL, (18, 130, left_w, HEIGHT-180), border_radius=12)
        pygame.draw.rect(surf, COL_ACCENT, (18,130,left_w, HEIGHT-180), 2, border_radius=12)
        draw_text(surf, "Panel de control", FONT_BOLD, COL_ACCENT, 34, 150)
        # info lines
        lines = [
            f"Vértices: {n}",
            f"Aristas: {len(edges)}/{n-1}",
            f"Conectado: {'Sí' if self.is_connected() else 'No'}",
            f"Paso: {self.step+1}/4"
        ]
        y0 = 190
        for i,l in enumerate(lines):
            draw_text(surf, l, FONT_REG, COL_TEXT, 34, y0 + i*28)
        # show generated function when ready
        if self.step==3:
            draw_text(surf, "Función generada f(v):", FONT_BOLD, COL_SUCCESS, 34, y0 + 4*28 + 12)
            tab_y = y0 + 4*28 + 48
            for i in range(min(n,10)):
                vtxt = FONT_SMALL.render(f"{i+1} -> {self.function[i]+1 if self.function[i] is not None else '?'}", True, COL_TEXT)
                surf.blit(vtxt, (34, tab_y + i*22))
            if n>10:
                draw_text(surf, "...", FONT_SMALL, COL_TEXT, 34, tab_y + 10*22)
        # draw graph area
        pygame.draw.rect(surf, COL_BG, (380,130, WIDTH-400, HEIGHT-260))
        draw_graph(surf, highlight_vertices=self._highlights(), spine_edges=self._spine_edges())
        # buttons
        self.btn_back.update(pygame.mouse.get_pos()); self.btn_back.draw(surf)
        self.btn_reset.update(pygame.mouse.get_pos()); self.btn_reset.draw(surf)
        if self.step>0:
            self.btn_prev.update(pygame.mouse.get_pos()); self.btn_prev.draw(surf)
        if self.step < 3 and (self.step==0 or self.check_step_complete()):
            self.btn_next.update(pygame.mouse.get_pos()); self.btn_next.draw(surf)
    def _highlights(self):
        d = {'selected': [], 'start': [], 'end': []}
        if self.selected is not None: d['selected'].append(self.selected)
        if self.start is not None: d['start'].append(self.start)
        if self.end is not None: d['end'].append(self.end)
        return d
    def _spine_edges(self):
        if self.spine_path and len(self.spine_path)>1:
            return [(self.spine_path[i], self.spine_path[i+1]) for i in range(len(self.spine_path)-1)]
        return []
    def get_instruction(self):
        texts = [
            "Paso 1: Conecta vértices para formar un árbol (clic en dos vértices).",
            "Paso 2: Selecciona el vértice INICIAL de la vértebra.",
            "Paso 3: Selecciona el vértice FINAL de la vértebra.",
            "Listo: función generada - revisa el panel izquierdo."
        ]
        return texts[self.step]
    def handle_event(self, event):
        if self.btn_back.clicked(event): return "BACK"
        if self.btn_reset.clicked(event):
            self.reset(); return None
        if self.btn_prev.clicked(event):
            if self.step>0: self.step-=1; return None
        if self.btn_next.clicked(event) and (self.step==0 and self.check_step_complete() or self.step>0):
            if self.step<3: self.step+=1; return None
        if event.type == pygame.MOUSEBUTTONDOWN and event.button==1:
            mx,my = event.pos
            # check clicks on vertices
            for i,(x,y) in enumerate(vertice_pos):
                if math.hypot(mx-x, my-y) <= vertice_radius+6:
                    self._vertex_clicked(i)
                    break
        return None
    def _vertex_clicked(self, idx):
        if self.step==0:
            if self.selected is None:
                self.selected = idx
            else:
                if idx!=self.selected and (self.selected, idx) not in edges and (idx, self.selected) not in edges:
                    # no cycles: union-find prevents cycles
                    if find(self.selected) != find(idx):
                        edges.append((self.selected, idx))
                        graph[self.selected].append(idx); graph[idx].append(self.selected)
                        union(self.selected, idx)
                self.selected = None
                if len(edges) == n-1 and self.is_connected():
                    self.step = 1
        elif self.step==1:
            self.start = idx
            self.step = 2
        elif self.step==2:
            if idx!=self.start:
                self.end = idx
                self.calculate_function()
                self.step = 3
    def calculate_function(self):
        self.spine_path = bfs_path(self.start, self.end)
        if self.spine_path and len(self.spine_path)>0:
            spine = self.spine_path[:]
            # simplified mapping for demo: assign reversed mapping between sorted & reversed
            ordre = sorted(spine)
            rev = list(reversed(spine))
            for i in range(len(ordre)):
                self.function[ordre[i]] = rev[i]
        # orient other edges toward end
        dist = [-1]*n
        q = deque([self.end]); dist[self.end]=0
        while q:
            u=q.popleft()
            for v in graph[u]:
                if dist[v]==-1:
                    dist[v]=dist[u]+1; q.append(v)
        directed=[]
        for a,b in edges:
            if (a,b) not in self._spine_edges() and (b,a) not in self._spine_edges():
                if dist[a] > dist[b]: directed.append((a,b))
                else: directed.append((b,a))
        for a,b in directed:
            self.function[a]=b
    def is_connected(self):
        if n==0: return False
        r=find(0)
        return all(find(i)==r for i in range(n))
    def check_step_complete(self):
        if self.step==0:
            return (len(edges)==n-1) and self.is_connected()
        if self.step==1:
            return self.start is not None
        if self.step==2:
            return self.end is not None
        return True
    def reset(self):
        global edges, graph, parent
        edges = []
        graph = [[] for _ in range(n)]
        parent = list(range(n))
        self.step=0; self.selected=None; self.start=None; self.end=None
        self.function = [None]*n; self.spine_path=None

# -------------------------
# Modo 2: Función -> Árbol
# -------------------------
class ModeFunctionToTree:
    def __init__(self):
        self.func_box = InputBox(34, 200, 360, 120, placeholder="Ej: 1->2,2->2,3->4,...")
        self.btn_generate = Button(40, 340, 160, 46, "GENERAR")
        self.btn_back = Button(24, 24, 120, 42, "MENÚ", color=(120,120,120))
        self.error = ""
        self.tree_edges = []
        self.spine = []
    def draw(self, surf):
        surf.fill(COL_BG)
        pygame.draw.rect(surf, COL_HEADER, (0,0,WIDTH,110))
        draw_text(surf, "MODO 2 — FUNCIÓN → ÁRBOL", FONT_TITLE, (255,255,255), 18, 20)
        draw_text(surf, "Ingresa f: {1..n} → {1..n} (ej: 1->2,2->2,...)", FONT_SUB, (220,220,220), 18, 68)
        # left panel
        pygame.draw.rect(surf, COL_PANEL, (18, 130, 420, HEIGHT-180), border_radius=12)
        pygame.draw.rect(surf, COL_ACCENT, (18,130,420, HEIGHT-180), 2, border_radius=12)
        draw_text(surf, "Entrada de función f", FONT_BOLD, COL_ACCENT, 34, 150)
        # input and buttons
        self.func_box.draw(surf)
        self.btn_generate.update(pygame.mouse.get_pos()); self.btn_generate.draw(surf)
        self.btn_back.update(pygame.mouse.get_pos()); self.btn_back.draw(surf)
        if self.error:
            draw_text(surf, self.error, FONT_SMALL, COL_DANGER, 36, 420)
        # graph area
        draw_graph(surf, spine_edges=self.spine, directed_edges=[])
        # if tree present, draw edges in right panel info
        if self.tree_edges:
            draw_text(surf, "Árbol generado (ejemplo):", FONT_BOLD, COL_SUCCESS, 34, 460)
            y=500
            for i,(a,b) in enumerate(self.tree_edges[:10]):
                draw_text(surf, f"{i+1}. {a+1} — {b+1}", FONT_SMALL, COL_TEXT, 36, y + i*20)
    def handle_event(self, event):
        if self.btn_back.clicked(event): return "BACK"
        if self.func_box.handle_event(event):
            pass
        if self.btn_generate.clicked(event):
            txt = self.func_box.get()
            f, msg = parsear_funcion(txt, n)
            if f is None:
                self.error = msg
            else:
                self.error = ""
                # build cycles (spine) and edges accordingly (simplified conversion for demo)
                self.build_tree_from_function(f)
        return None
    def build_tree_from_function(self, f):
        # f is list length n with 0-indexed values
        # find cycles
        visited = [False]*n
        cycles = []
        noncycles = []
        for i in range(n):
            if visited[i]: continue
            cur = i; path=[]
            while not visited[cur]:
                visited[cur]=True; path.append(cur); cur=f[cur]
            if cur in path:
                idx = path.index(cur)
                cycle = path[idx:]
                cycles.extend(cycle)
            else:
                noncycles.extend(path)
        self.spine = sorted(list(set(cycles)))
        # tree edges: connect spine in cycle order then attach non-cycle nodes to their f(...)
        self.tree_edges = []
        if len(self.spine) > 1:
            # try to preserve order as they appear following f
            # produce spine in visitation order
            ordered=[]
            start = self.spine[0]
            cur = start
            while True:
                ordered.append(cur)
                cur = f[cur]
                if cur==start or cur in ordered:
                    break
            for i in range(len(ordered)-1):
                self.tree_edges.append((ordered[i], ordered[i+1]))
        # attach others
        for v in range(n):
            if v not in self.spine:
                self.tree_edges.append((v, f[v]))
        # Update global edges/graph for visualization (non-destructive)
        global edges, graph, parent
        edges = list(self.tree_edges)
        graph = [[] for _ in range(n)]
        parent = list(range(n))
        for a,b in edges:
            # undirected tree edges
            graph[a].append(b); graph[b].append(a)
            union(a,b)

# -------------------------
# Pantalla principal (menú)
# -------------------------
class MainMenu:
    def __init__(self):
        self.btn_mode1 = Button(WIDTH//2 - 360, 300, 320, 90, "MODO 1\nÁRBOL → FUNCIÓN")
        self.btn_mode2 = Button(WIDTH//2 + 40, 300, 320, 90, "MODO 2\nFUNCIÓN → ÁRBOL", color=COL_SUCCESS)
        self.btn_choose_n = Button(WIDTH//2 - 110, 420, 220, 56, "CONFIGURAR N")
        self.n_display = n
    def draw(self, surf):
        surf.fill(COL_BG)
        pygame.draw.rect(surf, COL_HEADER, (0,0,WIDTH,160))
        draw_text(surf, "Demostración de Joyal — Fórmula de Cayley", FONT_TITLE, (255,255,255), 28, 30)
        draw_text(surf, f"n = {n}    ➜  n^(n-2) = {n**(n-2):,}", FONT_SUB, (230,230,230), 28, 92)
        # central card
        pygame.draw.rect(surf, COL_PANEL, (WIDTH//2 - 430, 190, 860, 480), border_radius=18)
        pygame.draw.rect(surf, COL_ACCENT, (WIDTH//2 - 430, 190, 860, 480), 2, border_radius=18)
        desc = [
            "Esta aplicación demuestra la biyección de Joyal para la",
            "fórmula de Cayley (n^(n-2)).",
            "",
            "Elige un modo: construir un árbol y obtener la función, o",
            "ingresar una función y reconstruir el árbol."
        ]
        for i,l in enumerate(desc):
            draw_text(surf, l, FONT_REG, COL_TEXT, WIDTH//2 - 380, 220 + i*28)
        self.btn_mode1.update(pygame.mouse.get_pos()); self.btn_mode1.draw(surf)
        self.btn_mode2.update(pygame.mouse.get_pos()); self.btn_mode2.draw(surf)
        self.btn_choose_n.update(pygame.mouse.get_pos()); self.btn_choose_n.draw(surf)
    def handle_event(self, event):
        if self.btn_mode1.clicked(event): return "MODE1"
        if self.btn_mode2.clicked(event): return "MODE2"
        if self.btn_choose_n.clicked(event): return "CHOOSE_N"
        return None

# -------------------------
# Elegir n
# -------------------------
def choose_n_screen():
    box = InputBox(WIDTH//2 - 120, 300, 240, 48, placeholder="Ej: 6")
    btn_ok = Button(WIDTH//2 - 80, 370, 160, 48, "APLICAR")
    err = ""
    while True:
        dt = clock.tick(60)
        mouse = pygame.mouse.get_pos()
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                return None
            if box.handle_event(event):
                pass
            if btn_ok.clicked(event):
                txt = box.get()
                if txt.isdigit() and int(txt) >= 2:
                    val = int(txt)
                    if val > 60:
                        err = "Usa n ≤ 60 para mejor rendimiento."
                    else:
                        inicializar_estructuras(val)
                        return val
                else:
                    err = "Ingrese un número entero válido (≥2)."
        box.update(dt)
        screen.fill(COL_BG)
        pygame.draw.rect(screen, COL_HEADER, (0,0,WIDTH,120))
        draw_text(screen, "Configurar n", FONT_TITLE, (255,255,255), 28, 22)
        pygame.draw.rect(screen, COL_PANEL, (WIDTH//2 - 320, 170, 640, 420), border_radius=14)
        draw_text(screen, "Número de vértices (n)", FONT_BOLD, COL_ACCENT, WIDTH//2 - 120, 240)
        box.draw(screen)
        btn_ok.update(mouse); btn_ok.draw(screen)
        if err:
            draw_text(screen, err, FONT_SMALL, COL_DANGER, WIDTH//2 - 120, 440)
        pygame.display.flip()

# -------------------------
# MAIN APP
# -------------------------
def main():
    inicializar_estructuras(6)  # default
    menu = MainMenu()
    mode1 = ModeTreeToFunction()
    mode2 = ModeFunctionToTree()

    state = "MENU"
    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type==pygame.QUIT:
                running=False
            else:
                if state == "MENU":
                    res = menu.handle_event(event)
                    if res == "MODE1":
                        mode1 = ModeTreeToFunction()
                        state = "MODE1"
                    elif res == "MODE2":
                        mode2 = ModeFunctionToTree()
                        state = "MODE2"
                    elif res == "CHOOSE_N":
                        val = choose_n_screen()
                        if val:
                            inicializar_estructuras(val)
                            menu = MainMenu()
                elif state == "MODE1":
                    res = mode1.handle_event(event)
                    if res == "BACK":
                        state = "MENU"
                elif state == "MODE2":
                    res = mode2.handle_event(event)
                    if res == "BACK":
                        state = "MENU"

        # draw
        if state == "MENU":
            menu.draw(screen)
        elif state == "MODE1":
            mode1.draw(screen)
        elif state == "MODE2":
            mode2.draw(screen)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()
