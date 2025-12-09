# Mejoras de interfaz - Demostración de Joyal (UI arreglada para evitar solapamientos)
# - Reorganiza áreas: header, info panel (izq), graph area (derecha), footer de botones (abajo)
# - Dibuja el gráfico en una superficie separada (clipping) para que nada lo tape
# - Control de padding y zonas reservadas para que textos y cuadros no se superpongan
# - Función simple de 'wrap' para mensajes largos

import pygame
import math
import numpy as np
from collections import deque
import sys

pygame.init()

# Pantalla
WIDTH, HEIGHT = 1280, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Demostración de Joyal - Interfaz mejorada")

# Fuentes
FONT_TITLE = pygame.font.Font(None, 48)
FONT_SUBTITLE = pygame.font.Font(None, 28)
FONT_BOLD = pygame.font.Font(None, 28)
FONT_REGULAR = pygame.font.Font(None, 22)
FONT_SMALL = pygame.font.Font(None, 18)
FONT_TINY = pygame.font.Font(None, 14)

# Paleta
COLORS = {
    'background': (245, 248, 250),
    'header': (30, 60, 114),
    'accent': (41, 128, 185),
    'success': (46, 204, 113),
    'warning': (241, 196, 15),
    'danger': (231, 76, 60),
    'info': (52, 152, 219),
    'dark': (44, 62, 80),
    'light': (236, 240, 241),
    'white': (255, 255, 255),
    'gray': (149, 165, 166),
    'vertex': (52, 152, 219),
    'edge': (149, 165, 166),
    'spine': (231, 76, 60),
    'arrow': (41, 128, 185),
    'highlight': (241, 196, 15)
}

# Layout global y padding reservado
HEADER_H = 110
LEFT_PANEL_W = 360
FOOTER_H = 180
CONTENT_PADDING = 20

# Variables del grafo
n = 6
vertice_pos = []
vertice_rad = 24
aristas = []
grafo = []
parent = []

# Utility: text wrap
def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    cur = ''
    for w in words:
        test = cur + (' ' if cur else '') + w
        if font.size(test)[0] <= max_width:
            cur = test
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines

# Componentes: botón simplificado (mantiene estilo profesional)
class ProfessionalButton:
    def __init__(self, x, y, w, h, text, color=COLORS['accent']):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover = False
        self.pressed = False
        self.radius = 8

    def draw(self, surf):
        # Sombra
        s = pygame.Surface((self.rect.w + 6, self.rect.h + 6), pygame.SRCALPHA)
        pygame.draw.rect(s, (0,0,0,40), pygame.Rect(3,3,self.rect.w,self.rect.h), border_radius=self.radius)
        surf.blit(s, (self.rect.x - 3, self.rect.y - 3))

        # Fondo
        bg = self.color if not self.hover else tuple(min(255, c+20) for c in self.color)
        pygame.draw.rect(surf, bg, self.rect, border_radius=self.radius)
        pygame.draw.rect(surf, COLORS['white'], self.rect, 2, border_radius=self.radius)

        # Texto (centrado y con posibilidad de varias líneas)
        lines = self.text.split('\n')
        total_h = sum(FONT_BOLD.size(line)[1] for line in lines)
        y = self.rect.y + (self.rect.h - total_h)//2
        for line in lines:
            ts = FONT_BOLD.render(line, True, COLORS['white'])
            surf.blit(ts, (self.rect.centerx - ts.get_width()//2, y))
            y += ts.get_height()

    def update(self, mouse_pos):
        self.hover = self.rect.collidepoint(mouse_pos)
        return self.hover

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.hover:
            self.pressed = True
            return True
        return False

class InputField:
    def __init__(self, x, y, w, h, label='', placeholder=''):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.placeholder = placeholder
        self.text = ''
        self.active = False
        self.cursor_visible = True
        self.cursor_tm = 0

    def draw(self, surf):
        if self.label:
            lab = FONT_SMALL.render(self.label, True, COLORS['dark'])
            surf.blit(lab, (self.rect.x, self.rect.y - lab.get_height() - 6))

        bg = COLORS['white'] if not self.active else (250,250,255)
        pygame.draw.rect(surf, bg, self.rect, border_radius=6)
        pygame.draw.rect(surf, COLORS['accent'] if self.active else COLORS['gray'], self.rect, 2, border_radius=6)

        display = self.text if self.text else self.placeholder
        color = COLORS['dark'] if self.text else COLORS['gray']

        # Truncar con wrap si es demasiado largo horizontalmente
        max_w = self.rect.w - 12
        txtsurf = FONT_REGULAR.render(display, True, color)
        if txtsurf.get_width() > max_w:
            # recortar y añadir '...'
            s = display
            while FONT_REGULAR.size(s + '...')[0] > max_w and len(s) > 0:
                s = s[:-1]
            display = s + '...'
            txtsurf = FONT_REGULAR.render(display, True, color)

        surf.blit(txtsurf, (self.rect.x + 6, self.rect.y + (self.rect.h - txtsurf.get_height())//2))

        # Cursor
        if self.active and self.cursor_visible:
            cursor_x = self.rect.x + 6 + txtsurf.get_width()
            y1 = self.rect.y + 6
            y2 = self.rect.y + self.rect.h - 6
            pygame.draw.line(surf, COLORS['accent'], (cursor_x, y1), (cursor_x, y2), 2)

    def update(self, dt):
        self.cursor_tm += dt
        if self.cursor_tm > 500:
            self.cursor_visible = not self.cursor_visible
            self.cursor_tm = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                return True
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_ESCAPE:
                self.active = False
            else:
                if event.unicode.isprintable() and len(self.text) < 200:
                    self.text += event.unicode
        return False

# Layout-aware screen: garantiza que los paneles no se superpongan
class MainLayout:
    def __init__(self):
        # elementos comunes
        self.header_rect = pygame.Rect(0, 0, WIDTH, HEADER_H)
        self.left_panel = pygame.Rect(CONTENT_PADDING, HEADER_H + CONTENT_PADDING, LEFT_PANEL_W - 2*CONTENT_PADDING, HEIGHT - HEADER_H - FOOTER_H - 2*CONTENT_PADDING)
        self.graph_area = pygame.Rect(LEFT_PANEL_W + CONTENT_PADDING, HEADER_H + CONTENT_PADDING, WIDTH - LEFT_PANEL_W - 2*CONTENT_PADDING, HEIGHT - HEADER_H - FOOTER_H - 2*CONTENT_PADDING)
        self.footer_rect = pygame.Rect(0, HEIGHT - FOOTER_H, WIDTH, FOOTER_H)

    def draw_header(self, surf, title, subtitle=''):
        pygame.draw.rect(surf, COLORS['header'], self.header_rect)
        t = FONT_TITLE.render(title, True, COLORS['white'])
        surf.blit(t, (24, 20))
        if subtitle:
            s = FONT_SUBTITLE.render(subtitle, True, COLORS['light'])
            surf.blit(s, (24, 20 + t.get_height() + 6))

    def draw_left_panel_bg(self, surf):
        pygame.draw.rect(surf, COLORS['white'], self.left_panel, border_radius=12)
        pygame.draw.rect(surf, COLORS['accent'], self.left_panel, 2, border_radius=12)

    def get_graph_surface(self):
        # Surface separada para el grafo (evita solapamientos con otros elementos de la UI)
        surf = pygame.Surface((self.graph_area.w, self.graph_area.h))
        surf.fill(COLORS['background'])
        return surf

layout = MainLayout()

# Inicialización de estructuras del grafo

def calcular_posiciones_vertices(n_vertices):
    global vertice_pos
    vertice_pos = []
    centro_x = layout.graph_area.x + layout.graph_area.w // 2
    centro_y = layout.graph_area.y + layout.graph_area.h // 2
    radio = min(220, 70 + n_vertices * 10)
    for i in range(n_vertices):
        ang = 2*math.pi*i/n_vertices - math.pi/2
        x = int(centro_x + radio*math.cos(ang))
        y = int(centro_y + radio*math.sin(ang))
        vertice_pos.append((x,y))
    return vertice_pos


def inicializar_estructuras(n_vertices):
    global n, grafo, parent, aristas, vertice_rad
    n = n_vertices
    aristas = []
    grafo = [[] for _ in range(n)]
    parent = list(range(n))
    vertice_rad = max(14, min(30, 180 // n))
    calcular_posiciones_vertices(n)


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

# Pantalla de selección de n (ejemplo simplificado)
class NSelectionScreen:
    def __init__(self):
        self.title = 'CONFIGURACIÓN INICIAL'
        self.n_input = InputField(layout.left_panel.x + 12, layout.left_panel.y + 40, layout.left_panel.w - 24, 44, 'NÚMERO DE VÉRTICES (n ≥ 2)', 'Ej: 6')
        self.cont_btn = ProfessionalButton(layout.left_panel.x + 12, layout.left_panel.y + 100, 140, 44, 'CONTINUAR', COLORS['success'])
        self.error = ''

    def draw(self, surf):
        surf.fill(COLORS['background'])
        layout.draw_header(surf, 'Demostración de Joyal', 'Fórmula de Cayley: n^(n-2)')
        layout.draw_left_panel_bg(surf)

        # contenido del panel izquierdo
        x = layout.left_panel.x + 20
        y = layout.left_panel.y + 12
        title = FONT_BOLD.render('Configuración', True, COLORS['accent'])
        surf.blit(title, (x, y))

        self.n_input.draw(surf)
        self.cont_btn.draw(surf)

        # Mensaje de ayuda dentro del panel (envuelto)
        help_text = 'Ingrese el número de vértices del árbol. Recomendado: 3 a 15 para visualización.'
        lines = wrap_text(help_text, FONT_REGULAR, layout.left_panel.w - 36)
        yy = self.n_input.rect.y + self.n_input.rect.h + 12
        for line in lines:
            surf.blit(FONT_REGULAR.render(line, True, COLORS['dark']), (x, yy))
            yy += FONT_REGULAR.get_height() + 4

        if self.error:
            err_rect = pygame.Rect(layout.left_panel.x + 12, yy + 8, layout.left_panel.w - 24, 56)
            pygame.draw.rect(surf, (255,235,235), err_rect, border_radius=8)
            pygame.draw.rect(surf, COLORS['danger'], err_rect, 2, border_radius=8)
            err_lines = wrap_text(self.error, FONT_SMALL, err_rect.w - 12)
            ty = err_rect.y + 8
            for l in err_lines:
                surf.blit(FONT_SMALL.render(l, True, COLORS['danger']), (err_rect.x + 8, ty))
                ty += FONT_SMALL.get_height() + 2

        # Nota: el grafo se muestra en una superficie separada para evitar solapamientos
        graph_surf = layout.get_graph_surface()
        # Dibujar un placeholder elegante
        ph = FONT_REGULAR.render('Área de visualización del grafo', True, COLORS['gray'])
        graph_surf.blit(ph, (layout.graph_area.w//2 - ph.get_width()//2, layout.graph_area.h//2 - ph.get_height()//2))
        surf.blit(graph_surf, (layout.graph_area.x, layout.graph_area.y))

    def update(self, mouse_pos, dt):
        self.cont_btn.update(mouse_pos)
        self.n_input.update(dt)

    def handle_event(self, event):
        if self.n_input.handle_event(event):
            return self.validate()
        if self.cont_btn.handle_event(event):
            return self.validate()
        return None

    def validate(self):
        try:
            val = int(self.n_input.text or '0')
            if val < 2:
                self.error = 'El número debe ser al menos 2'
                return None
            if val > 40:
                self.error = 'Para mejor rendimiento, use n ≤ 40'
                return None
            self.error = ''
            inicializar_estructuras(val)
            return 'OK'
        except ValueError:
            self.error = 'Ingrese un número válido'
            return None

# Modo simplificado Tree -> Function (solo UI/reservas, lógica principal tomada del original)
class TreeToFunctionMode:
    def __init__(self):
        self.title = 'MODO 1: ÁRBOL → FUNCIÓN'
        self.info_panel = pygame.Rect(layout.left_panel.x, layout.left_panel.y, layout.left_panel.w, layout.left_panel.h)
        # botones en footer (centrados y con separación garantizada)
        btn_w = 140
        gap = 24
        base_x = WIDTH//2 - (btn_w*3 + gap*2)//2
        y = HEIGHT - FOOTER_H + 30
        self.btn_back = ProfessionalButton(base_x, y, btn_w, 46, '← MENÚ', COLORS['gray'])
        self.btn_reset = ProfessionalButton(base_x + (btn_w + gap), y, btn_w, 46, 'REINICIAR', COLORS['warning'])
        self.btn_next = ProfessionalButton(base_x + 2*(btn_w + gap), y, btn_w, 46, 'CONTINUAR', COLORS['success'])

        # Botones para seleccionar vértices (se colocan en el footer sin sobreponer el step indicator)
        self.vertex_buttons = []
        self.create_vertex_buttons()

        # estado
        self.step = 0
        self.selected_vertex = None
        self.start_vertex = None
        self.end_vertex = None
        self.function = [None]*n

    def create_vertex_buttons(self):
        self.vertex_buttons.clear()
        per_row = min(n, 10)
        total_w = per_row * 52 + (per_row - 1) * 8
        start_x = WIDTH//2 - total_w//2
        y = HEIGHT - 90
        for i in range(n):
            col = i % per_row
            row = i // per_row
            x = start_x + col * 60
            yy = y + row * 44
            btn = ProfessionalButton(x, yy, 52, 40, str(i+1), COLORS['vertex'])
            self.vertex_buttons.append(btn)

    def draw(self, surf):
        surf.fill(COLORS['background'])
        layout.draw_header(surf, self.title)
        layout.draw_left_panel_bg(surf)

        # Draw info panel content
        self.draw_info_panel(surf)

        # Graph surface (separate)
        gsurf = layout.get_graph_surface()
        # draw edges on gsurf
        for v1, v2 in aristas:
            p1 = (vertice_pos[v1][0] - layout.graph_area.x, vertice_pos[v1][1] - layout.graph_area.y)
            p2 = (vertice_pos[v2][0] - layout.graph_area.x, vertice_pos[v2][1] - layout.graph_area.y)
            pygame.draw.line(gsurf, COLORS['edge'], p1, p2, 3)

        # vertices
        for i, pos in enumerate(vertice_pos):
            px = pos[0] - layout.graph_area.x
            py = pos[1] - layout.graph_area.y
            pygame.draw.circle(gsurf, COLORS['vertex'], (px, py), vertice_rad)
            pygame.draw.circle(gsurf, COLORS['white'], (px, py), vertice_rad, 2)
            ns = FONT_BOLD.render(str(i+1), True, COLORS['white'])
            gsurf.blit(ns, (px - ns.get_width()//2, py - ns.get_height()//2))

        # blit graph surface
        surf.blit(gsurf, (layout.graph_area.x, layout.graph_area.y))

        # footer buttons and vertex buttons (drawn last so they appear on top and never overlap content)
        for vb in self.vertex_buttons:
            vb.draw(surf)

        self.btn_back.draw(surf)
        self.btn_reset.draw(surf)
        self.btn_next.draw(surf)

        # step indicator (positioned above footer to avoid overlap)
        self.draw_step_indicator(surf)

    def draw_info_panel(self, surf):
        x, y = self.info_panel.x + 12, self.info_panel.y + 12
        title = FONT_BOLD.render('INFORMACIÓN DEL ÁRBOL', True, COLORS['accent'])
        surf.blit(title, (x, y))
        y += title.get_height() + 8
        lines = [f'Vértices: {n}', f'Aristas: {len(aristas)}/{n-1}', f'Conectado: {"Sí" if self.is_connected() else "No"}']
        for line in lines:
            surf.blit(FONT_SMALL.render(line, True, COLORS['dark']), (x, y))
            y += FONT_SMALL.get_height() + 6

    def draw_step_indicator(self, surf):
        steps = ['1. Construir', '2. Inicio', '3. Fin', '4. Completado']
        w = 520
        sx = WIDTH//2 - w//2
        sy = HEIGHT - FOOTER_H - 58
        for i, s in enumerate(steps):
            rect = pygame.Rect(sx + i*130, sy, 120, 40)
            color = COLORS['success'] if i < self.step else (COLORS['info'] if i == self.step else COLORS['gray'])
            pygame.draw.rect(surf, color, rect, border_radius=8)
            pygame.draw.rect(surf, COLORS['white'], rect, 2, border_radius=8)
            surf.blit(FONT_SMALL.render(s, True, COLORS['white']), (rect.centerx - 40, rect.centery - 8))

    def update(self, mouse_pos, dt):
        self.btn_back.update(mouse_pos)
        self.btn_reset.update(mouse_pos)
        self.btn_next.update(mouse_pos)
        for vb in self.vertex_buttons:
            vb.update(mouse_pos)

    def handle_event(self, event):
        if self.btn_back.handle_event(event):
            return 'BACK'
        if self.btn_reset.handle_event(event):
            self.reset()
        if self.btn_next.handle_event(event):
            if self.step < 3:
                self.step += 1
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, vb in enumerate(self.vertex_buttons):
                if vb.rect.collidepoint(event.pos):
                    self.handle_vertex_click(i)
        return None

    def handle_vertex_click(self, idx):
        # lógica tomada y simplificada del original: aquí solo actualizamos estado y evitamos solapamientos
        if self.step == 0:
            if self.selected_vertex is None:
                self.selected_vertex = idx
            else:
                if idx != self.selected_vertex:
                    if (self.selected_vertex, idx) not in aristas and (idx, self.selected_vertex) not in aristas:
                        if find(self.selected_vertex) != find(idx):
                            aristas.append((self.selected_vertex, idx))
                            union(self.selected_vertex, idx)
                            grafo[self.selected_vertex].append(idx)
                            grafo[idx].append(self.selected_vertex)
                self.selected_vertex = None
                if len(aristas) == n - 1 and self.is_connected():
                    self.step = 1
        elif self.step == 1:
            self.start_vertex = idx
            self.step = 2
        elif self.step == 2:
            if idx != self.start_vertex:
                self.end_vertex = idx
                # calc función placeholder
                self.function = [None]*n
                path = self.find_path(self.start_vertex, self.end_vertex)
                if path:
                    for i in range(len(path)-1):
                        a,b = path[i], path[i+1]
                        # marcar como vértebra de forma simple
                    self.step = 3

    def find_path(self, a, b):
        visited = [False]*n
        q = deque([a])
        parent_ = [-1]*n
        visited[a] = True
        while q:
            cur = q.popleft()
            if cur == b:
                path = []
                while cur != -1:
                    path.append(cur)
                    cur = parent_[cur]
                return list(reversed(path))
            for nb in grafo[cur]:
                if not visited[nb]:
                    visited[nb] = True
                    parent_[nb] = cur
                    q.append(nb)
        return None

    def is_connected(self):
        if n == 0:
            return False
        r = find(0)
        return all(find(i) == r for i in range(n))

    def reset(self):
        global aristas, grafo, parent
        aristas.clear()
        grafo = [[] for _ in range(n)]
        parent = list(range(n))
        self.step = 0
        self.selected_vertex = None
        self.start_vertex = None
        self.end_vertex = None
        self.function = [None]*n

# Aplicación principal (simplificada para enfoque en UI)
class JoyalApp:
    def __init__(self):
        self.screen = 'SELECT_N'
        self.clock = pygame.time.Clock()
        self.n_screen = NSelectionScreen()
        self.tree_screen = TreeToFunctionMode()
        inicializar_estructuras(6)

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60)
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if self.screen == 'SELECT_N':
                    res = self.n_screen.handle_event(event)
                    if res == 'OK':
                        self.screen = 'TREE'
                elif self.screen == 'TREE':
                    res = self.tree_screen.handle_event(event)
                    if res == 'BACK':
                        self.screen = 'SELECT_N'

            if self.screen == 'SELECT_N':
                self.n_screen.update(mouse_pos, dt)
                self.n_screen.draw(screen)
            elif self.screen == 'TREE':
                self.tree_screen.update(mouse_pos, dt)
                self.tree_screen.draw(screen)

            pygame.display.flip()
        pygame.quit()

if __name__ == '__main__':
    app = JoyalApp()
    app.run()
