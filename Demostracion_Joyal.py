# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                                                                            ║
# ║     PROYECTO MD - Demostración de Joyal a la Fórmula de Cayley             ║
# ║                                                                            ║
# ║     Versión Mejorada - Interfaz Profesional                                ║
# ║                                                                            ║
# ╠════════════════════════════════════════════════════════════════════════════╣
# ║                                                                            ║
# ║     MEJORAS IMPLEMENTADAS:                                                 ║
# ║         1. Selector profesional de n (cualquier número ≥ 2)                ║
# ║         2. Interfaz moderna con gradientes y sombras                       ║
# ║         3. Selección de vértices funcional en modo 1                       ║
# ║         4. Visualización destacada de vértebras                            ║
# ║         5. Panel de control informativo con iconos                         ║
# ║         6. Notación de permutaciones mejorada                              ║
# ║         7. Cifrado Hill con explicación detallada                          ║
# ║                                                                            ║
# ╠════════════════════════════════════════════════════════════════════════════╣
# ║                                                                            ║
# ║     AUTORES:                                                               ║
# ║         • Martin Lora Cano                                                 ║
# ║         • Cristian Andrés Diaz Ortega                                      ║
# ║         • Jhon Edison Prieto Artunduaga                                    ║
# ║                                                                            ║
# ╠════════════════════════════════════════════════════════════════════════════╣
# ║                                                                            ║
# ║     DESCRIPCIÓN:                                                           ║
# ║         Demostración visual e interactiva de la biyección de Joyal         ║
# ║         para la fórmula de Cayley: n^(n-2) árboles etiquetados             ║
# ║                                                                            ║
# ╚════════════════════════════════════════════════════════════════════════════╝

import pygame
import math
import numpy as np
from collections import deque
import sys

# ==============================================================================
# CONFIGURACIÓN INICIAL
# ==============================================================================

pygame.init()

# Dimensiones de la ventana
WIDTH, HEIGHT = 1200, 900

# Crear la ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Demostración de Joyal - Fórmula de Cayley")

# Fuentes
FONT = pygame.font.SysFont('Arial', 26)
FONT_BOLD = pygame.font.SysFont('Arial', 24, bold=True)
FONT_SMALL = pygame.font.SysFont('Arial', 22)
FONT_TITLE = pygame.font.SysFont('Arial', 36, bold=True)
FONT_LARGE = pygame.font.SysFont('Arial', 42, bold=True)

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 60, 60)
GREEN = (60, 180, 75)
BLUE = (70, 130, 180)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GRAY = (245, 245, 245)
DARK_GRAY = (100, 100, 100)
YELLOW = (255, 200, 50)
ORANGE = (255, 140, 50)
PURPLE = (160, 100, 220)
CYAN = (0, 180, 180)
BACKGROUND = (240, 245, 250)
HEADER_BG = (40, 80, 150)

# ==============================================================================
# CLASE PARA BOTONES MEJORADOS
# ==============================================================================

class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_BLUE, hover_color=(200, 220, 255), text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.current_color = color
        self.clicked = False
        self.shadow = False
        
    def draw(self, surface):
        # Sombra sutil
        if self.shadow:
            shadow_rect = pygame.Rect(self.rect.x + 3, self.rect.y + 3, self.rect.width, self.rect.height)
            pygame.draw.rect(surface, (200, 200, 200, 100), shadow_rect, border_radius=10)
        
        # Botón principal
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (100, 100, 100), self.rect, 2, border_radius=10)
        
        # Renderizar texto centrado
        lines = self.text.split('\n')
        total_height = len(lines) * 25
        
        for i, line in enumerate(lines):
            text_surf = FONT.render(line, True, self.text_color)
            text_rect = text_surf.get_rect(center=(self.rect.centerx, 
                                                   self.rect.centroid[1] - total_height//2 + 25 + i * 25))
            surface.blit(text_surf, text_rect)
        
    def check_hover(self, pos):
        if self.rect.collidepoint(pos):
            self.current_color = self.hover_color
            return True
        else:
            self.current_color = self.color
            return False
            
    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.clicked = True
            pygame.time.delay(150)  # Pequeña pausa para feedback táctil
            return True
        return False

# ==============================================================================
# CLASE PARA CAMPOS DE TEXTO MEJORADOS
# ==============================================================================

class InputBox:
    def __init__(self, x, y, width, height, text='', label='', placeholder=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.label = label
        self.placeholder = placeholder
        self.active = False
        self.max_length = 100
        
    def draw(self, surface):
        # Dibujar label
        if self.label:
            label_surf = FONT_SMALL.render(self.label, True, (80, 80, 80))
            surface.blit(label_surf, (self.rect.x, self.rect.y - 30))
            
        # Dibujar caja con efecto de profundidad
        color = BLUE if self.active else (150, 150, 150)
        
        # Sombra
        shadow_rect = pygame.Rect(self.rect.x + 2, self.rect.y + 2, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, (220, 220, 220), shadow_rect, border_radius=8)
        
        # Caja principal
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=8)
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=8)
        
        # Dibujar texto o placeholder
        display_text = self.text if self.text else self.placeholder
        text_color = BLACK if self.text else (180, 180, 180)
        
        text_surf = FONT.render(display_text, True, text_color)
        
        # Recortar texto si es muy largo
        if text_surf.get_width() > self.rect.width - 20:
            # Crear texto con "..." al final
            truncated = display_text
            while FONT.render(truncated + "...", True, text_color).get_width() > self.rect.width - 20 and len(truncated) > 1:
                truncated = truncated[:-1]
            text_surf = FONT.render(truncated + "...", True, text_color)
        
        surface.blit(text_surf, (self.rect.x + 10, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))
        
        # Cursor si está activo
        if self.active:
            cursor_x = self.rect.x + 10 + text_surf.get_width()
            pygame.draw.line(surface, BLUE, 
                           (cursor_x, self.rect.y + 5),
                           (cursor_x, self.rect.y + self.rect.height - 5), 2)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                elif event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    # Pegar desde portapapeles
                    try:
                        self.text += pygame.scrap.get(pygame.SCRAP_TEXT).decode('utf-8')
                    except:
                        pass
                else:
                    if len(self.text) < self.max_length and event.unicode.isprintable():
                        self.text += event.unicode
        return False
        
    def get_text(self):
        return self.text.strip()

# ==============================================================================
# SELECTOR DE N - VERSIÓN PROFESIONAL
# ==============================================================================

class NSelector:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 500, 400)
        self.n = 6  # Valor por defecto
        self.selected = False
        self.input_box = InputBox(x + 150, y + 180, 200, 50, "6", 
                                 "NÚMERO DE VÉRTICES (n ≥ 2):",
                                 "Ej: 6")
        self.confirm_btn = Button(x + 200, y + 280, 100, 50, "CONTINUAR", GREEN, (50, 200, 50), WHITE)
        self.confirm_btn.shadow = True
        self.error_msg = ""
        
    def draw(self, surface):
        # Fondo con gradiente
        for i in range(self.rect.height):
            color_val = 245 + int(10 * (i / self.rect.height))
            pygame.draw.line(surface, (color_val, color_val, color_val), 
                           (self.rect.x, self.rect.y + i), 
                           (self.rect.x + self.rect.width, self.rect.y + i))
        
        # Borde principal
        pygame.draw.rect(surface, (240, 245, 250), self.rect, border_radius=20)
        pygame.draw.rect(surface, (70, 130, 180), self.rect, 4, border_radius=20)
        
        # Sombra exterior
        shadow_rect = pygame.Rect(self.rect.x + 5, self.rect.y + 5, self.rect.width, self.rect.height)
        pygame.draw.rect(surface, (200, 200, 200, 50), shadow_rect, border_radius=20)
        
        # Título centrado con sombra
        title = FONT_LARGE.render("CONFIGURACIÓN INICIAL", True, (30, 80, 150))
        title_shadow = FONT_LARGE.render("CONFIGURACIÓN INICIAL", True, (100, 100, 150))
        surface.blit(title_shadow, (self.rect.centerx - title.get_width()//2 + 3, self.rect.y + 33))
        surface.blit(title, (self.rect.centerx - title.get_width()//2, self.rect.y + 30))
        
        # Línea decorativa
        pygame.draw.line(surface, (70, 130, 180), 
                        (self.rect.x + 50, self.rect.y + 80),
                        (self.rect.x + self.rect.width - 50, self.rect.y + 80), 3)
        
        # Subtítulo
        subtitle = FONT_BOLD.render("Fórmula de Cayley: n^(n-2) árboles etiquetados", True, (50, 50, 50))
        surface.blit(subtitle, (self.rect.centerx - subtitle.get_width()//2, self.rect.y + 100))
        
        # Instrucción
        instr = FONT.render("Ingrese cualquier número entero n ≥ 2:", True, (80, 80, 80))
        surface.blit(instr, (self.rect.centerx - instr.get_width()//2, self.rect.y + 150))
        
        # Caja de entrada
        self.input_box.draw(surface)
        
        # Mensaje de error
        if self.error_msg:
            error_bg = pygame.Rect(self.rect.centerx - 180, self.rect.y + 240, 360, 40)
            pygame.draw.rect(surface, (255, 230, 230), error_bg, border_radius=8)
            pygame.draw.rect(surface, RED, error_bg, 2, border_radius=8)
            
            error = FONT_SMALL.render(self.error_msg, True, RED)
            surface.blit(error, (self.rect.centerx - error.get_width()//2, self.rect.y + 250))
        
        # Botón continuar
        self.confirm_btn.draw(surface)
        
        # Ejemplo de fórmula
        if 2 <= self.n <= 20:
            formula = FONT_BOLD.render(f"Con n = {self.n}: {self.n}^({self.n}-2) = {self.n**(self.n-2):,} árboles", True, GREEN)
            surface.blit(formula, (self.rect.centerx - formula.get_width()//2, self.rect.y + 350))
        elif self.n > 20:
            formula = FONT_BOLD.render(f"Con n = {self.n}: {self.n}^({self.n}-2) árboles (número muy grande)", True, GREEN)
            surface.blit(formula, (self.rect.centerx - formula.get_width()//2, self.rect.y + 350))
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            if self.confirm_btn.check_click(pos):
                try:
                    n_val = int(self.input_box.get_text())
                    if n_val >= 2:
                        if n_val > 20:
                            # Preguntar confirmación para números grandes
                            self.error_msg = f"¿Seguro? n={n_val} generará {n_val**(n_val-2):e} árboles"
                            return False
                        self.n = n_val
                        self.selected = True
                        self.error_msg = ""
                        return True
                    else:
                        self.error_msg = "n debe ser ≥ 2"
                except ValueError:
                    self.error_msg = "Ingrese un número válido"
                    
        # Manejar entrada de texto
        self.input_box.handle_event(event)
        
        # Actualizar n en tiempo real
        try:
            temp_n = int(self.input_box.get_text())
            if 2 <= temp_n <= 100:  # Permitir hasta 100
                self.n = temp_n
        except:
            pass
            
        return False

# ==============================================================================
# VARIABLES GLOBALES
# ==============================================================================

n = 6
vertice_pos = []
vertice_rad = 25
aristas = []
grafo = []
parent = []

# ==============================================================================
# FUNCIONES MATEMÁTICAS Y DE GRAFOS
# ==============================================================================

def calcular_posiciones_vertices(n_vertices):
    """Calcula posiciones para n vértices en un círculo"""
    global vertice_pos
    vertice_pos = []
    centro_x, centro_y = WIDTH // 2, 400
    radio = min(250, 150 + n_vertices * 10)
    
    for i in range(n_vertices):
        angulo = 2 * math.pi * i / n_vertices - math.pi/2
        x = centro_x + radio * math.cos(angulo)
        y = centro_y + radio * math.sin(angulo)
        vertice_pos.append((int(x), int(y)))
    
    return vertice_pos

def inicializar_estructuras(n_vertices):
    """Inicializa las estructuras de datos para n vértices"""
    global n, grafo, parent, aristas
    n = n_vertices
    aristas = []
    grafo = [[] for _ in range(n)]
    parent = list(range(n))
    calcular_posiciones_vertices(n)

def find(x):
    """Union-Find: encontrar raíz con compresión de caminos"""
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]

def union(a, b):
    """Union-Find: unir dos conjuntos"""
    rootA = find(a)
    rootB = find(b)
    if rootA != rootB:
        parent[rootB] = rootA
        return True
    return False

def grafoconexo():
    """Verifica si el grafo es conexo"""
    if n == 0:
        return False
    root0 = find(0)
    return all(find(i) == root0 for i in range(n))

def distancia(a, b):
    """Distancia euclidiana entre dos puntos"""
    return math.hypot(a[0] - b[0], a[1] - b[1])

def draw_vertices():
    """Dibuja todos los vértices con estilo mejorado"""
    for i, pos in enumerate(vertice_pos):
        # Sombra del vértice
        shadow_pos = (pos[0] + 2, pos[1] + 2)
        pygame.draw.circle(screen, (150, 150, 150, 100), shadow_pos, vertice_rad)
        
        # Círculo del vértice con gradiente
        for r in range(vertice_rad, 0, -1):
            color_val = 200 - int(50 * (r / vertice_rad))
            color = (color_val, color_val, 255)
            pygame.draw.circle(screen, color, pos, r)
        
        # Borde
        pygame.draw.circle(screen, BLUE, pos, vertice_rad, 3)
        
        # Número (1-indexado)
        vertice_num = FONT_BOLD.render(str(i + 1), True, WHITE)
        num_shadow = FONT_BOLD.render(str(i + 1), True, (50, 50, 100))
        screen.blit(num_shadow, (pos[0] - 7, pos[1] - 7))
        screen.blit(vertice_num, (pos[0] - 8, pos[1] - 8))

def draw_dirigido(surface, a_pos, b_pos, color=BLUE, width=3, head_size=12):
    """Dibuja una flecha dirigida de a a b"""
    ax, ay = a_pos
    bx, by = b_pos
    total = math.hypot(bx-ax, by-ay)
    
    if total == 0:
        return
        
    # Ajustar para que comience y termine en el borde del círculo
    sx = ax + (vertice_rad/total) * (bx-ax)
    sy = ay + (vertice_rad/total) * (by-ay)
    ex = bx - (vertice_rad/total) * (bx-ax)
    ey = by - (vertice_rad/total) * (by-ay)
    
    # Línea principal con sombra
    pygame.draw.line(surface, (50, 50, 50), (sx+1, sy+1), (ex+1, ey+1), width)
    pygame.draw.line(surface, color, (sx, sy), (ex, ey), width)
    
    # Punta de flecha
    angle = math.atan2(ey - sy, ex - sx)
    left = (ex - head_size * math.cos(angle - math.pi/6),
            ey - head_size * math.sin(angle - math.pi/6))
    right = (ex - head_size * math.cos(angle + math.pi/6),
             ey - head_size * math.sin(angle + math.pi/6))
    pygame.draw.polygon(surface, color, [(ex, ey), left, right])

def draw_vertebra_destacada(surface, camino_vertebra, vertices_pos):
    """Dibuja la vértebra de forma destacada"""
    if not camino_vertebra or len(camino_vertebra) < 2:
        return
    
    # Dibujar vértebra como línea gruesa con efecto 3D
    for i in range(len(camino_vertebra) - 1):
        v1 = camino_vertebra[i]
        v2 = camino_vertebra[i + 1]
        p1 = vertices_pos[v1]
        p2 = vertices_pos[v2]
        
        # Línea de sombra
        pygame.draw.line(surface, (150, 50, 50), 
                        (p1[0] + 2, p1[1] + 2), 
                        (p2[0] + 2, p2[1] + 2), 8)
        
        # Línea principal
        pygame.draw.line(surface, RED, p1, p2, 6)
        
        # Línea de resalte
        pygame.draw.line(surface, (255, 180, 180), p1, p2, 2)
        
        # Flecha de dirección solo en el inicio
        if i == 0:
            draw_dirigido(surface, p1, p2, RED, 4, 14)
    
    # Resaltar vértices de la vértebra
    for v in camino_vertebra:
        pos = vertices_pos[v]
        pygame.draw.circle(surface, RED, pos, vertice_rad + 4, 3)
        pygame.draw.circle(surface, (255, 200, 200), pos, vertice_rad + 6, 1)
        
    # Etiquetar inicio y fin
    if len(camino_vertebra) >= 2:
        inicio = camino_vertebra[0]
        fin = camino_vertebra[-1]
        
        # Fondo para etiquetas
        inicio_bg = pygame.Rect(vertices_pos[inicio][0] - 40, vertices_pos[inicio][1] - 50, 80, 25)
        fin_bg = pygame.Rect(vertices_pos[fin][0] - 30, vertices_pos[fin][1] - 50, 60, 25)
        
        pygame.draw.rect(surface, (255, 240, 240), inicio_bg, border_radius=5)
        pygame.draw.rect(surface, RED, inicio_bg, 2, border_radius=5)
        pygame.draw.rect(surface, (255, 240, 240), fin_bg, border_radius=5)
        pygame.draw.rect(surface, RED, fin_bg, 2, border_radius=5)
        
        # Texto de etiquetas
        inicio_label = FONT_BOLD.render("INICIO", True, RED)
        fin_label = FONT_BOLD.render("FIN", True, RED)
        
        screen.blit(inicio_label, (vertices_pos[inicio][0] - inicio_label.get_width()//2, 
                                   vertices_pos[inicio][1] - 45))
        screen.blit(fin_label, (vertices_pos[fin][0] - fin_label.get_width()//2, 
                                vertices_pos[fin][1] - 45))

def draw_bucle(surface, pos, radius=20, color=BLUE, width=3):
    """Dibuja un bucle (arista de un vértice a sí mismo)"""
    x, y = pos
    centro = (x + 6, y - radius + 2)
    rx, ry = 22, 16
    
    rect = pygame.Rect(0, 0, rx * 2, ry * 2)
    rect.center = centro
    
    start_angle = math.radians(200)
    end_angle = math.radians(520)
    pygame.draw.arc(surface, color, rect, start_angle, end_angle, width)
    
    tip_angle = math.radians(200)
    tip_x = centro[0] + rx * math.cos(tip_angle)
    tip_y = centro[1] + ry * math.sin(tip_angle)
    ah = 10
    left = (tip_x - ah * math.cos(tip_angle - math.pi/6),
            tip_y - ah * math.sin(tip_angle - math.pi/6))
    right = (tip_x - ah * math.cos(tip_angle + math.pi/6),
             tip_y - ah * math.sin(tip_angle + math.pi/6))
    pygame.draw.polygon(surface, color, [(tip_x, tip_y), left, right])

def depthfirstsearch(graph, start, end, path=None, visited=None):
    """DFS para encontrar camino entre vértices"""
    if path is None:
        path = []
    if visited is None:
        visited = set()
        
    path = path + [start]
    visited.add(start)
    
    if start == end:
        return path
        
    for neighbor in graph[start]:
        if neighbor not in visited:
            newpath = depthfirstsearch(graph, neighbor, end, path, visited)
            if newpath:
                return newpath
                
    return None

def vertices_en_ciclo(aristas_dir):
    """Encuentra vértices que están en ciclos"""
    grafo_local = {}
    for u, v in aristas_dir:
        grafo_local.setdefault(u, []).append(v)
        grafo_local.setdefault(v, [])
        
    vertices_cic = set()
    
    for u, vecinos in grafo_local.items():
        for v in vecinos:
            grafo_local[u].remove(v)
            camino = depthfirstsearch(grafo_local, v, u)
            grafo_local[u].append(v)
            
            if camino:
                vertices_cic.add(u)
                vertices_cic.add(v)
                
    return sorted(vertices_cic)

def dirigir_vertices(grafo, aristas, aristas_vert, vertice_fin):
    """Orienta aristas hacia la vértebra"""
    dist = [-1] * len(grafo)
    queue = deque([vertice_fin])
    dist[vertice_fin] = 0
    
    while queue:
        v = queue.popleft()
        for ady in grafo[v]:
            if dist[ady] == -1:
                dist[ady] = dist[v] + 1
                queue.append(ady)
                
    aristas_dir = []
    for v1, v2 in aristas:
        en_vert = False
        for a, b in aristas_vert:
            if (v1 == a and v2 == b) or (v1 == b and v2 == a):
                en_vert = True
                break
                
        if not en_vert:
            if dist[v1] > dist[v2]:
                aristas_dir.append((v1, v2))
            else:
                aristas_dir.append((v2, v1))
                
    return aristas_dir

# ==============================================================================
# SISTEMA DE ENCRIPTACIÓN HILL
# ==============================================================================

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZÑ,. '
CHAR_TO_NUM = {ch: i for i, ch in enumerate(ALPHABET)}
NUM_TO_CHAR = {i: ch for i, ch in enumerate(ALPHABET)}
MOD = len(ALPHABET)

def char_a_num(ch):
    """Convierte carácter a número"""
    ch = ch.upper()
    return CHAR_TO_NUM.get(ch, CHAR_TO_NUM[' '])

def num_a_char(n):
    """Convierte número a carácter"""
    n = n % MOD
    return NUM_TO_CHAR.get(n, ' ')

def determinante_bareiss(mat):
    """Calcula determinante con algoritmo de Bareiss"""
    n = len(mat)
    if n == 0:
        return 1
        
    A = [list(map(int, row)) for row in mat]
    prev = 1
    sign = 1
    
    for k in range(n - 1):
        if A[k][k] == 0:
            swap_row = None
            for r in range(k + 1, n):
                if A[r][k] != 0:
                    swap_row = r
                    break
            if swap_row is None:
                return 0
            A[k], A[swap_row] = A[swap_row], A[k]
            sign *= -1
            
        pivot = A[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * pivot - A[i][k] * A[k][j]) // prev
        prev = pivot
        
    return sign * A[n - 1][n - 1]

def matriz_adjunta(M, MOD=30):
    """Calcula matriz adjunta"""
    n = len(M)
    adj = [[0] * n for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            minor = [[M[r][c] for c in range(n) if c != j] 
                    for r in range(n) if r != i]
            det_minor = determinante_bareiss(minor)
            cofactor = ((-1) ** (i + j)) * det_minor
            adj[j][i] = cofactor % MOD
            
    return adj

def egcd(a, b):
    """Algoritmo extendido de Euclides"""
    if b == 0:
        return (a, 1, 0)
    else:
        g, x1, y1 = egcd(b, a % b)
        return (g, y1, x1 - (a // b) * y1)

def inversa_modular_matriz(M, MOD=30):
    """Calcula inversa modular de matriz"""
    n = len(M)
    
    detM = determinante_bareiss(M)
    det_mod = detM % MOD
    
    g, x, y = egcd(det_mod, MOD)
    if g != 1:
        return None
        
    det_inv = x % MOD
    
    adj = matriz_adjunta(M, MOD)
    
    inv = [[(det_inv * adj[i][j]) % MOD for j in range(n)] for i in range(n)]
    return inv

def multiplicar_matriz_vector(M, vec, MOD=30):
    """Multiplica matriz por vector modularmente"""
    n = len(vec)
    out = [0] * n
    for i in range(n):
        s = 0
        row = M[i]
        for j in range(n):
            s += row[j] * vec[j]
        out[i] = s % MOD
    return out

def es_invertible_mod(mat, mod):
    """Verifica si matriz es invertible módulo mod"""
    det = int(round(np.linalg.det(mat)))
    return math.gcd(det, mod) == 1

def generar_matriz_desde_funcion(funcion, n_vertices):
    """Genera matriz invertible n×n desde función"""
    clean = [(0 if v is None else int(v)) for v in funcion]
    func = [clean[i % len(clean)] for i in range(n_vertices)]
    
    arr = []
    for i in range(n_vertices):
        row = []
        for j in range(n_vertices):
            row.append((func[i] * (j + 1) + (func[j] + 1)) % MOD)
        arr.append(row)
    
    mat = np.array(arr, dtype=int)
    
    if es_invertible_mod(mat, MOD):
        return mat
    
    I = np.eye(n_vertices, dtype=int)
    for i in range(n_vertices):
        v = 3 * (func[i] + 1) + 1
        v %= MOD
        while math.gcd(v, MOD) != 1:
            v = (v + 1) % MOD
        I[i][i] = v
        
    return I

def cifrar_hill(texto, clave):
    """Cifra texto usando cifrado Hill"""
    nums = [char_a_num(ch) for ch in texto]
    n_size = len(clave)
    
    while len(nums) % n_size != 0:
        nums.append(char_a_num(' '))
    
    cifrado = []
    for i in range(0, len(nums), n_size):
        bloque = nums[i:i + n_size]
        cifrado_bloque = multiplicar_matriz_vector(clave, bloque, MOD)
        cifrado.extend(cifrado_bloque)
    
    return ''.join(num_a_char(n) for n in cifrado)

def descifrar_hill(texto_cifrado, clave):
    """Descifra texto usando cifrado Hill"""
    nums = [char_a_num(ch) for ch in texto_cifrado]
    n_size = len(clave)
    
    clave_inv = inversa_modular_matriz(clave, MOD)
    if clave_inv is None:
        raise ValueError("Clave no invertible")
    
    descifrado = []
    for i in range(0, len(nums), n_size):
        bloque = nums[i:i + n_size]
        descifrado_bloque = multiplicar_matriz_vector(clave_inv, bloque, MOD)
        descifrado.extend(descifrado_bloque)
    
    return ''.join(num_a_char(n) for n in descifrado)

# ==============================================================================
# NOTACIÓN DE PERMUTACIONES
# ==============================================================================

def funcion_a_notacion_permutacion(funcion, n_vertices):
    """Convierte función a notación de permutaciones (ciclos)"""
    if any(v is None for v in funcion):
        return "Función incompleta"
    
    mapa = {i: funcion[i] for i in range(n_vertices)}
    visitados = set()
    ciclos = []
    
    for i in range(n_vertices):
        if i not in visitados:
            ciclo = []
            actual = i
            
            while actual not in visitados:
                visitados.add(actual)
                ciclo.append(actual + 1)
                actual = mapa[actual]
                
                if actual == i:
                    break
                    
            if len(ciclo) > 1:
                ciclos.append(ciclo)
    
    if not ciclos:
        return "Id (permutación identidad)"
    
    ciclo_strs = []
    for ciclo in ciclos:
        ciclo_strs.append("(" + " ".join(str(v) for v in ciclo) + ")")
    
    puntos_fijos = []
    for i in range(n_vertices):
        if mapa[i] == i and i+1 not in [v for ciclo in ciclos for v in ciclo]:
            puntos_fijos.append(str(i+1))
    
    resultado = " ".join(ciclo_strs)
    if puntos_fijos:
        resultado += " donde {" + ", ".join(puntos_fijos) + "} son puntos fijos"
    
    return resultado

def funcion_a_notacion_dos_lineas(funcion, n_vertices):
    """Representa función en notación de dos líneas"""
    if any(v is None for v in funcion):
        return "Función incompleta"
    
    linea1 = " ".join(str(i+1) for i in range(n_vertices))
    linea2 = " ".join(str(funcion[i]+1 if funcion[i] is not None else "?") 
                     for i in range(n_vertices))
    
    return f"({linea1})\n({linea2})"

# ==============================================================================
# CLASE PRINCIPAL DE LA APLICACIÓN
# ==============================================================================

class JoyalApp:
    def __init__(self):
        # Estados
        self.STATE_SELECT_N = 0
        self.STATE_MENU = 1
        self.STATE_TREE_MODE = 2
        self.STATE_FUNC_MODE = 3
        
        self.state = self.STATE_SELECT_N
        self.n_selector = NSelector(WIDTH//2 - 250, HEIGHT//2 - 200)
        
        # Variables de árbol
        self.mode = None
        self.vertice_1 = None
        self.vertice_ini = None
        self.vertice_fin = None
        self.funcion = []
        self.aristas_vert = []
        self.aristas_dir = []
        self.camino_vertebra = None
        self.camino_orden = None
        self.camino_inv = []
        self.estado = 0
        self.show_tables = False
        self.error_fun = 0
        
        # Variables de cifrado
        self.texto_cifrado = ""
        self.texto_descifrado = ""
        self.explicacion_cifrado = ""
        
        # Campos de entrada
        self.func_input = InputBox(50, 650, 500, 45, 
                                  label="FUNCIÓN f (ej: 1,2,3,6,6,6,7,8,9)",
                                  placeholder="Ingrese valores separados por comas")
        self.crypto_input = InputBox(50, 750, 500, 45, 
                                    label="TEXTO PARA CIFRAR/DESCIFRAR",
                                    placeholder="Escriba su mensaje aquí")
        
        # Botones principales
        self.btn_mode1 = Button(50, 550, 250, 80, "MODO 1\nÁrbol → Función", 
                               (180, 220, 255), (200, 230, 255))
        self.btn_mode1.shadow = True
        
        self.btn_mode2 = Button(330, 550, 250, 80, "MODO 2\nFunción → Árbol", 
                               (180, 255, 220), (200, 255, 230))
        self.btn_mode2.shadow = True
        
        self.btn_reset = Button(610, 550, 150, 80, "REINICIAR\nSistema", 
                               (255, 180, 180), (255, 200, 200), RED)
        self.btn_reset.shadow = True
        
        # Botones de acción
        self.btn_submit_func = Button(570, 650, 200, 45, "ENVIAR FUNCIÓN", GREEN, (70, 200, 70), WHITE)
        self.btn_build_tree = Button(570, 700, 200, 45, "CONSTRUIR ÁRBOL", ORANGE, (255, 160, 60), WHITE)
        self.btn_encrypt = Button(570, 750, 200, 45, "CIFRAR TEXTO", PURPLE, (180, 120, 240), WHITE)
        self.btn_decrypt = Button(790, 650, 200, 45, "DESCIFRAR TEXTO", BLUE, (90, 150, 220), WHITE)
        self.btn_back = Button(790, 700, 200, 45, "VOLVER AL MENÚ", DARK_GRAY, (120, 120, 120), WHITE)
        
        # Botones de vértices
        self.vertex_buttons = []
        
    def crear_botones_vertices(self):
        """Crea botones para los n vértices organizados"""
        self.vertex_buttons = []
        buttons_per_row = min(n, 12)
        total_width = buttons_per_row * 60
        start_x = (WIDTH - total_width) // 2
        
        for i in range(n):
            row = i // buttons_per_row
            col = i % buttons_per_row
            
            x = start_x + col * 60
            y = 520 + row * 45
            
            # Color según el estado
            color = ORANGE
            if self.mode == 1:
                if i == self.vertice_1:
                    color = GREEN
                elif i in [self.vertice_ini, self.vertice_fin]:
                    color = RED
                elif self.estado >= 4 and i in self.funcion and self.funcion[i] is not None:
                    color = BLUE
            
            btn = Button(x, y, 55, 40, f"V{i+1}", color)
            self.vertex_buttons.append(btn)
    
    def dibujar_fondo_titulo(self):
        """Dibuja el fondo y título de la aplicación"""
        # Fondo con gradiente sutil
        for y in range(0, HEIGHT, 2):
            color_val = 240 + int(15 * (y / HEIGHT))
            pygame.draw.line(screen, (color_val, color_val, color_val), (0, y), (WIDTH, y))
        
        # Encabezado con degradado
        header_rect = pygame.Rect(0, 0, WIDTH, 120)
        for y in range(header_rect.height):
            color_val = 40 + int(40 * (y / header_rect.height))
            pygame.draw.line(screen, (color_val, 80, 150), 
                           (0, y), (WIDTH, y))
        
        # Borde del encabezado
        pygame.draw.rect(screen, (100, 150, 220), header_rect, 2)
        
        # Título principal con sombra
        title = FONT_LARGE.render("DEMOSTRACIÓN VISUAL - BIYECCIÓN DE JOYAL", True, WHITE)
        title_shadow = FONT_LARGE.render("DEMOSTRACIÓN VISUAL - BIYECCIÓN DE JOYAL", True, (20, 50, 100))
        screen.blit(title_shadow, (WIDTH//2 - title.get_width()//2 + 3, 33))
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 30))
        
        # Subtítulo
        subt = FONT_BOLD.render("Fórmula de Cayley: n^(n-2) árboles etiquetados", True, (220, 220, 255))
        screen.blit(subt, (WIDTH//2 - subt.get_width()//2, 80))
        
        # Info actual
        if self.state != self.STATE_SELECT_N:
            info = FONT.render(f"n = {n} vértices | {n}^({n}-2) = {n**(n-2):,} árboles etiquetados", True, (50, 50, 50))
            screen.blit(info, (WIDTH//2 - info.get_width()//2, 110))
    
    def dibujar_instrucciones_modo1(self):
        """Dibuja instrucciones para el modo 1"""
        instrucciones = [
            ("PASO 1: CONSTRUYE EL ÁRBOL", "Haz clic en dos vértices para conectarlos"),
            ("PASO 2: SELECCIONA VÉRTICES", "Elige inicio y fin de la vértebra"),
            ("PASO 3: OBTÉN LA FUNCIÓN", "El sistema calculará f automáticamente")
        ]
        
        y_pos = 140
        for i, (titulo, desc) in enumerate(instrucciones):
            # Fondo para cada paso
            step_rect = pygame.Rect(20, y_pos, WIDTH - 40, 60)
            
            # Color según el paso actual
            if (self.estado < 2 and i == 0) or (self.estado == 2 and i == 1) or (self.estado >= 3 and i == 2):
                bg_color = (235, 245, 255)
                border_color = BLUE
            else:
                bg_color = (245, 245, 245)
                border_color = (200, 200, 200)
            
            pygame.draw.rect(screen, bg_color, step_rect, border_radius=10)
            pygame.draw.rect(screen, border_color, step_rect, 2, border_radius=10)
            
            # Número del paso
            num_circle = pygame.Rect(35, y_pos + 15, 30, 30)
            pygame.draw.circle(screen, BLUE, num_circle.center, 15)
            num_text = FONT_BOLD.render(str(i+1), True, WHITE)
            screen.blit(num_text, (num_circle.centerx - num_text.get_width()//2, 
                                  num_circle.centery - num_text.get_height()//2))
            
            # Título del paso
            tit_surf = FONT_BOLD.render(titulo, True, (40, 100, 180))
            screen.blit(tit_surf, (80, y_pos + 10))
            
            # Descripción
            desc_surf = FONT_SMALL.render(desc, True, (80, 80, 80))
            screen.blit(desc_surf, (80, y_pos + 35))
            
            y_pos += 70
    
    def dibujar_panel_informacion(self):
        """Dibuja panel lateral con información"""
        panel_x = 800
        panel_y = 140
        panel_w = 380
        panel_h = 380
        
        # Fondo del panel con sombra
        shadow_rect = pygame.Rect(panel_x + 4, panel_y + 4, panel_w, panel_h)
        pygame.draw.rect(screen, (200, 200, 200, 100), shadow_rect, border_radius=12)
        
        pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_w, panel_h), border_radius=12)
        pygame.draw.rect(screen, (70, 130, 180), (panel_x, panel_y, panel_w, panel_h), 3, border_radius=12)
        
        # Título del panel
        panel_title = FONT_TITLE.render("📊 PANEL DE CONTROL", True, (40, 80, 150))
        screen.blit(panel_title, (panel_x + 20, panel_y + 15))
        
        # Línea decorativa
        pygame.draw.line(screen, (70, 130, 180), 
                        (panel_x + 20, panel_y + 55),
                        (panel_x + panel_w - 20, panel_y + 55), 2)
        
        # Contenido del panel
        info_y = panel_y + 70
        
        if self.mode == 1:  # Modo árbol → función
            status_messages = {
                0: ("⏳ Construyendo árbol", (200, 150, 0)),
                1: ("❌ ¡Ciclo detectado!", RED),
                2: ("✅ Árbol completo", GREEN),
                3: ("🎯 Seleccione INICIO", BLUE),
                4: ("🎯 Seleccione FIN", BLUE),
                5: ("✅ Función generada", GREEN)
            }
            
            status_text, status_color = status_messages.get(self.estado, ("", BLACK))
            
            textos = [
                ("MODO:", "Árbol → Función"),
                ("ESTADO:", status_text),
                ("ARISTAS:", f"{len(aristas)}/{n-1}"),
                ("CONEXO:", "✅ Sí" if grafoconexo() else "❌ No")
            ]
            
            if self.vertice_1 is not None:
                textos.append(("SELECCIONADO:", f"V{self.vertice_1 + 1}"))
            if self.vertice_ini is not None:
                textos.append(("INICIO:", f"V{self.vertice_ini + 1}"))
            if self.vertice_fin is not None:
                textos.append(("FIN:", f"V{self.vertice_fin + 1}"))
                
        else:  # Modo función → árbol
            textos = [
                ("MODO:", "Función → Árbol"),
                ("FUNCIÓN:", str([f+1 if f is not None else '?' for f in self.funcion])),
                ("CICLOS:", str(len(self.camino_orden)) if self.camino_orden else "0"),
                ("VÉRTEBRA:", "→".join(str(v+1) for v in self.camino_vertebra) if self.camino_vertebra else "-")
            ]
        
        # Dibujar textos
        for i, (label, value) in enumerate(textos):
            label_surf = FONT_BOLD.render(label, True, (80, 80, 80))
            value_surf = FONT_BOLD.render(value, True, (40, 40, 40))
            screen.blit(label_surf, (panel_x + 30, info_y + i * 35))
            screen.blit(value_surf, (panel_x + 150, info_y + i * 35))
        
        # Información del cifrado Hill
        if self.funcion and all(f is not None for f in self.funcion):
            crypto_y = panel_y + panel_h - 120
            
            crypto_header = FONT_BOLD.render("🔐 CIFRADO HILL", True, (0, 150, 100))
            screen.blit(crypto_header, (panel_x + 30, crypto_y))
            
            try:
                matriz = generar_matriz_desde_funcion(self.funcion, n)
                det = int(round(np.linalg.det(matriz)))
                invertible = es_invertible_mod(matriz, MOD)
                
                matrix_info = FONT_SMALL.render(f"Matriz {n}×{n} | Modular {MOD}", True, (0, 120, 80))
                det_text = FONT_SMALL.render(f"Determinante: {det} (mod {MOD})", True, (0, 120, 80))
                inv_text = FONT_SMALL.render(f"Invertible: {'✅ Sí' if invertible else '❌ No'}", 
                                           True, GREEN if invertible else RED)
                
                screen.blit(matrix_info, (panel_x + 30, crypto_y + 30))
                screen.blit(det_text, (panel_x + 30, crypto_y + 55))
                screen.blit(inv_text, (panel_x + 30, crypto_y + 80))
            except:
                pass
    
    def dibujar_notacion_permutacion(self):
        """Dibuja la notación de permutaciones de la función"""
        if not self.funcion or all(v is None for v in self.funcion):
            return
            
        y_pos = 820 if n <= 8 else 800
        
        # Notación en ciclos
        notacion_ciclos = funcion_a_notacion_permutacion(self.funcion, n)
        
        # Fondo para la notación
        notacion_bg = pygame.Rect(50, y_pos - 10, 700, 60)
        pygame.draw.rect(screen, (245, 250, 255), notacion_bg, border_radius=8)
        pygame.draw.rect(screen, PURPLE, notacion_bg, 2, border_radius=8)
        
        # Título
        title_surf = FONT_BOLD.render("Notación cíclica: ", True, PURPLE)
        screen.blit(title_surf, (60, y_pos))
        
        # Notación
        notacion_surf = FONT.render(notacion_ciclos, True, (100, 50, 150))
        
        # Ajustar si es muy largo
        if notacion_surf.get_width() > 650:
            palabras = notacion_ciclos.split()
            lineas = []
            linea_actual = ""
            
            for palabra in palabras:
                if len(linea_actual + " " + palabra) < 50:
                    linea_actual += " " + palabra if linea_actual else palabra
                else:
                    lineas.append(linea_actual)
                    linea_actual = palabra
            if linea_actual:
                lineas.append(linea_actual)
            
            for i, linea in enumerate(lineas[:2]):  # Máximo 2 líneas
                line_surf = FONT_SMALL.render(linea, True, (100, 50, 150))
                screen.blit(line_surf, (60, y_pos + 30 + i * 25))
        else:
            screen.blit(notacion_surf, (60 + title_surf.get_width(), y_pos))
    
    def dibujar_tablas(self):
        """Dibuja tablas de correspondencia V → f(V)"""
        if not self.camino_orden or not self.show_tables:
            return
            
        base_y = 400
        
        # Tabla 1: Vértebra
        if self.camino_orden and self.camino_inv:
            f1t1 = [v + 1 for v in self.camino_orden]
            f2t1 = [v + 1 for v in self.camino_inv]
            
            # Etiqueta de vértebra
            recorrido = " → ".join(str(v + 1) for v in self.camino_vertebra) if self.camino_vertebra else "—"
            recorrido_bg = pygame.Rect(50, base_y - 40, 300, 30)
            pygame.draw.rect(screen, (255, 240, 240), recorrido_bg, border_radius=5)
            pygame.draw.rect(screen, RED, recorrido_bg, 2, border_radius=5)
            
            recorrido_msg = FONT_BOLD.render("VÉRTEBRA: " + recorrido, True, RED)
            screen.blit(recorrido_msg, (60, base_y - 35))
            
            # Dibujar tabla
            self.dibujar_tabla_individual(50, base_y, f1t1, f2t1, "Vértebra")
        
        # Tabla 2: Aristas orientadas
        if self.aristas_dir:
            f1t2 = [a + 1 for a, b in self.aristas_dir]
            f2t2 = [b + 1 for a, b in self.aristas_dir]
            
            dir_bg = pygame.Rect(350, base_y - 40, 300, 30)
            pygame.draw.rect(screen, (240, 245, 255), dir_bg, border_radius=5)
            pygame.draw.rect(screen, BLUE, dir_bg, 2, border_radius=5)
            
            dir_msg = FONT_BOLD.render("Aristas orientadas:", True, BLUE)
            screen.blit(dir_msg, (360, base_y - 35))
            
            self.dibujar_tabla_individual(350, base_y, f1t2, f2t2, "f(V)")
    
    def dibujar_tabla_individual(self, x, y, fila1, fila2, titulo):
        """Dibuja una tabla individual"""
        columnas = max(len(fila1), len(fila2))
        ancho, alto = 50, 35
        
        # Fondo de la tabla
        tabla_bg = pygame.Rect(x - 5, y - 5, columnas*ancho + 10, 2*alto + 10)
        pygame.draw.rect(screen, (250, 255, 255), tabla_bg, border_radius=8)
        pygame.draw.rect(screen, (150, 150, 150), tabla_bg, 2, border_radius=8)
        
        # Borde interior
        pygame.draw.rect(screen, BLACK, (x, y, columnas*ancho, 2*alto), 2)
        
        # Línea horizontal
        pygame.draw.line(screen, BLACK, (x, y+alto), (x + columnas*ancho, y+alto), 1)
        
        # Líneas verticales
        for c in range(1, columnas):
            pygame.draw.line(screen, BLACK, (x + c*ancho, y), (x + c*ancho, y + 2*alto), 1)
        
        # Etiquetas
        label_v = FONT_BOLD.render("V", True, RED)
        label_f = FONT_BOLD.render("f(V)", True, BLUE)
        screen.blit(label_v, (x - 25, y + alto//2 - label_v.get_height()//2))
        screen.blit(label_f, (x - 35, y + alto + alto//2 - label_f.get_height()//2))
        
        # Valores
        for c in range(columnas):
            val1 = fila1[c] if c < len(fila1) else "-"
            val2 = fila2[c] if c < len(fila2) else "-"
            
            t1 = FONT_BOLD.render(str(val1), True, RED if val1 != "-" else DARK_GRAY)
            t2 = FONT_BOLD.render(str(val2), True, BLUE if val2 != "-" else DARK_GRAY)
            
            # Centrar
            screen.blit(t1, (x + c*ancho + (ancho-t1.get_width())//2, y + (alto-t1.get_height())//2))
            screen.blit(t2, (x + c*ancho + (ancho-t2.get_width())//2, y + alto + (alto-t2.get_height())//2))
    
    def manejar_evento_vertice(self, vertice_idx):
        """Maneja clic en un vértice"""
        if self.mode == 1:  # Modo árbol → función
            if not grafoconexo():
                # Fase de construcción del árbol
                if self.vertice_1 is None:
                    self.vertice_1 = vertice_idx
                    self.estado = 0
                else:
                    if vertice_idx != self.vertice_1:
                        v1, v2 = self.vertice_1, vertice_idx
                        
                        # Verificar si ya existe la arista
                        if (v1, v2) in aristas or (v2, v1) in aristas:
                            self.estado = 1
                        elif find(v1) == find(v2):
                            self.estado = 1
                        else:
                            self.estado = 0
                            aristas.append((v1, v2))
                            union(v1, v2)
                            grafo[v1].append(v2)
                            grafo[v2].append(v1)
                            
                            # Verificar si el árbol está completo
                            if grafoconexo() and len(aristas) == n - 1:
                                self.estado = 2
                                self.funcion = [None] * n
                    
                    self.vertice_1 = None
                    
            elif None in self.funcion:
                # Fase de selección de vértices inicial y final
                if self.vertice_ini is None:
                    self.vertice_ini = vertice_idx
                    self.estado = 3
                elif self.vertice_fin is None and vertice_idx != self.vertice_ini:
                    self.vertice_fin = vertice_idx
                    self.estado = 4
                    
                    # Calcular vértebra y función
                    self.calcular_vertebra_y_funcion()
    
    def calcular_vertebra_y_funcion(self):
        """Calcula la vértebra y función completa"""
        if self.vertice_ini == self.vertice_fin:
            self.aristas_vert = []
            self.funcion[self.vertice_ini] = self.vertice_fin
            self.camino_vertebra = self.camino_inv = self.camino_orden = [self.vertice_fin]
        else:
            self.camino_vertebra = depthfirstsearch(grafo, self.vertice_ini, self.vertice_fin)
            if not self.camino_vertebra:
                # Búsqueda alternativa
                self.camino_vertebra = self.encontrar_camino_dfs(self.vertice_ini, self.vertice_fin)
            
            self.aristas_vert = [(self.camino_vertebra[i], self.camino_vertebra[i + 1])
                               for i in range(len(self.camino_vertebra) - 1)]
            self.camino_orden = sorted(self.camino_vertebra)
            self.camino_inv = list(reversed(self.camino_vertebra))
            
            for i in range(len(self.camino_orden)):
                self.funcion[self.camino_orden[i]] = self.camino_inv[i]
        
        # Orientar aristas restantes
        self.aristas_dir = dirigir_vertices(grafo, aristas, self.aristas_vert, self.vertice_fin)
        for a, b in self.aristas_dir:
            self.funcion[a] = b
        
        self.show_tables = True
        self.generar_explicacion_cifrado()
        self.crear_botones_vertices()  # Actualizar colores de botones
    
    def encontrar_camino_dfs(self, inicio, fin):
        """Encuentra camino usando DFS"""
        stack = [(inicio, [inicio])]
        visited = set()
        
        while stack:
            vertex, path = stack.pop()
            if vertex == fin:
                return path
            if vertex not in visited:
                visited.add(vertex)
                for neighbor in grafo[vertex]:
                    stack.append((neighbor, path + [neighbor]))
        
        return [inicio]
    
    def procesar_funcion_usuario(self):
        """Procesa la función ingresada por el usuario"""
        texto = self.func_input.get_text()
        try:
            vals = list(map(int, texto.split(',')))
            
            if len(vals) == n and all(1 <= x <= n for x in vals):
                self.funcion = [v - 1 for v in vals]
                self.error_fun = 0
                
                self.camino_orden = vertices_en_ciclo(list(enumerate(self.funcion)))
                self.camino_inv = []
                for i in range(len(self.camino_orden)):
                    self.camino_inv.append(self.funcion[self.camino_orden[i]])
                self.camino_vertebra = list(reversed(self.camino_inv))
                
                if len(self.camino_vertebra) > 1:
                    self.aristas_vert = [(self.camino_vertebra[i], self.camino_vertebra[i + 1])
                                      for i in range(len(self.camino_vertebra) - 1)]
                else:
                    self.aristas_vert = []
                
                self.aristas_dir = []
                for i in range(n):
                    en_vert = i in self.camino_orden
                    if not en_vert:
                        self.aristas_dir.append((i, self.funcion[i]))
                
                self.show_tables = True
                self.generar_explicacion_cifrado()
                
            elif len(vals) != n:
                self.error_fun = 1
            else:
                self.error_fun = 2
        except:
            self.error_fun = 3
    
    def generar_explicacion_cifrado(self):
        """Genera explicación del sistema de cifrado Hill"""
        if not self.funcion or any(v is None for v in self.funcion):
            return
            
        self.explicacion_cifrado = f"Cifrado Hill {n}×{n} - Matriz generada desde f(V) - Modular {MOD}"
    
    def cifrar_texto(self):
        """Cifra texto usando Hill"""
        texto = self.crypto_input.get_text()
        if texto and self.funcion and all(f is not None for f in self.funcion):
            try:
                matriz_clave = generar_matriz_desde_funcion(self.funcion, n)
                self.texto_cifrado = cifrar_hill(texto, matriz_clave)
                self.texto_descifrado = ""
            except Exception as e:
                self.texto_cifrado = f"Error: {str(e)}"
    
    def descifrar_texto(self):
        """Descifra texto usando Hill"""
        texto = self.crypto_input.get_text()
        if texto and self.funcion and all(f is not None for f in self.funcion):
            try:
                matriz_clave = generar_matriz_desde_funcion(self.funcion, n)
                self.texto_descifrado = descifrar_hill(texto, matriz_clave)
                self.texto_cifrado = ""
            except Exception as e:
                self.texto_descifrado = f"Error: {str(e)}"
    
    def reiniciar(self):
        """Reinicia la aplicación al estado inicial"""
        global aristas, grafo, parent
        aristas = []
        grafo = [[] for _ in range(n)]
        parent = list(range(n))
        
        self.mode = None
        self.vertice_1 = None
        self.vertice_ini = None
        self.vertice_fin = None
        self.funcion = [None] * n
        self.aristas_vert = []
        self.aristas_dir = []
        self.camino_vertebra = None
        self.camino_orden = None
        self.camino_inv = []
        self.estado = 0
        self.show_tables = False
        self.error_fun = 0
        self.texto_cifrado = ""
        self.texto_descifrado = ""
        self.explicacion_cifrado = ""
        
        self.func_input.text = ""
        self.crypto_input.text = ""
        self.crear_botones_vertices()
    
    def dibujar(self):
        """Dibuja toda la interfaz"""
        if self.state == self.STATE_SELECT_N:
            self.n_selector.draw(screen)
            return
            
        self.dibujar_fondo_titulo()
        
        if self.state == self.STATE_MENU:
            # Menú principal
            menu_title = FONT_TITLE.render("SELECCIONE UN MODO DE OPERACIÓN", True, (40, 80, 150))
            screen.blit(menu_title, (WIDTH//2 - menu_title.get_width()//2, 200))
            
            self.btn_mode1.draw(screen)
            self.btn_mode2.draw(screen)
            self.btn_reset.draw(screen)
            
            # Dibujar vértices
            draw_vertices()
            
        elif self.state == self.STATE_TREE_MODE:
            # Modo árbol → función
            if self.estado < 4:
                # Árbol en construcción
                for v1, v2 in aristas:
                    pygame.draw.line(screen, BLACK, vertice_pos[v1], vertice_pos[v2], 4)
            else:
                # Árbol completo con direcciones
                for v1, v2 in self.aristas_dir:
                    pygame.draw.line(screen, (100, 100, 100), vertice_pos[v1], vertice_pos[v2], 4)
                    draw_dirigido(screen, vertice_pos[v1], vertice_pos[v2], BLUE, 3, 10)
                
                # Dibujar vértebra destacada
                if self.camino_vertebra:
                    draw_vertebra_destacada(screen, self.camino_vertebra, vertice_pos)
            
            draw_vertices()
            
            # Instrucciones paso a paso
            self.dibujar_instrucciones_modo1()
            
            # Mostrar vértice seleccionado
            if self.vertice_1 is not None:
                sel_bg = pygame.Rect(WIDTH//2 - 150, 340, 300, 40)
                pygame.draw.rect(screen, (230, 255, 230), sel_bg, border_radius=8)
                pygame.draw.rect(screen, GREEN, sel_bg, 2, border_radius=8)
                
                sel_msg = FONT_BOLD.render(f"Vértice seleccionado: V{self.vertice_1 + 1}", True, GREEN)
                screen.blit(sel_msg, (WIDTH//2 - sel_msg.get_width()//2, 350))
            
            # Dibujar botones y controles
            for btn in self.vertex_buttons:
                btn.draw(screen)
            
            self.crypto_input.draw(screen)
            self.btn_decrypt.draw(screen)
            self.btn_back.draw(screen)
            
            # Mostrar resultados de descifrado
            if self.texto_descifrado:
                resultado_bg = pygame.Rect(50, 810, 700, 40)
                pygame.draw.rect(screen, (230, 255, 230), resultado_bg, border_radius=8)
                pygame.draw.rect(screen, GREEN, resultado_bg, 2, border_radius=8)
                
                resultado = FONT_BOLD.render(f"Descifrado: {self.texto_descifrado[:60]}", True, GREEN)
                screen.blit(resultado, (60, 820))
            
            self.dibujar_tablas()
            self.dibujar_notacion_permutacion()
            
        elif self.state == self.STATE_FUNC_MODE:
            # Modo función → árbol
            # Dibujar función como flechas
            for i, f in enumerate(self.funcion):
                if f is not None:
                    if i != f:
                        draw_dirigido(screen, vertice_pos[i], vertice_pos[f], BLUE, 3, 10)
                    else:
                        draw_bucle(screen, vertice_pos[i])
            
            # Dibujar vértebra si existe
            if self.camino_vertebra:
                draw_vertebra_destacada(screen, self.camino_vertebra, vertice_pos)
            
            draw_vertices()
            
            # Mostrar información de ciclos
            if self.camino_orden:
                ciclos_bg = pygame.Rect(WIDTH//2 - 200, 120, 400, 40)
                pygame.draw.rect(screen, (230, 230, 255), ciclos_bg, border_radius=8)
                pygame.draw.rect(screen, BLUE, ciclos_bg, 2, border_radius=8)
                
                ciclos_msg = FONT_BOLD.render(f"Vértices en ciclos: {[v+1 for v in self.camino_orden]}", True, BLUE)
                screen.blit(ciclos_msg, (WIDTH//2 - ciclos_msg.get_width()//2, 130))
            
            # Dibujar controles
            self.func_input.draw(screen)
            self.crypto_input.draw(screen)
            self.btn_submit_func.draw(screen)
            self.btn_build_tree.draw(screen)
            self.btn_encrypt.draw(screen)
            self.btn_back.draw(screen)
            
            # Mostrar mensajes de error
            if self.error_fun > 0:
                errores = {
                    1: f"Error: Debe ingresar exactamente {n} valores",
                    2: f"Error: Valores deben estar entre 1 y {n}",
                    3: "Error: Formato inválido (use números separados por comas)"
                }
                error_bg = pygame.Rect(WIDTH//2 - 250, 620, 500, 40)
                pygame.draw.rect(screen, (255, 230, 230), error_bg, border_radius=8)
                pygame.draw.rect(screen, RED, error_bg, 2, border_radius=8)
                
                error_msg = FONT_BOLD.render(errores.get(self.error_fun, ""), True, RED)
                screen.blit(error_msg, (WIDTH//2 - error_msg.get_width()//2, 630))
            
            # Mostrar resultados de cifrado
            if self.texto_cifrado:
                resultado_bg = pygame.Rect(50, 810, 700, 40)
                pygame.draw.rect(screen, (230, 230, 255), resultado_bg, border_radius=8)
                pygame.draw.rect(screen, PURPLE, resultado_bg, 2, border_radius=8)
                
                resultado = FONT_BOLD.render(f"Cifrado: {self.texto_cifrado[:60]}", True, PURPLE)
                screen.blit(resultado, (60, 820))
            
            self.dibujar_tablas()
            self.dibujar_notacion_permutacion()
        
        # Dibujar panel de información
        self.dibujar_panel_informacion()
    
    def manejar_eventos(self, event):
        """Maneja eventos de pygame"""
        if self.state == self.STATE_SELECT_N:
            if self.n_selector.handle_event(event):
                inicializar_estructuras(self.n_selector.n)
                self.crear_botones_vertices()
                self.state = self.STATE_MENU
                self.reiniciar()
            return
            
        # Verificar clics en botones
        pos = pygame.mouse.get_pos()
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == self.STATE_MENU:
                if self.btn_mode1.check_click(pos):
                    self.mode = 1
                    self.state = self.STATE_TREE_MODE
                    self.reiniciar()
                elif self.btn_mode2.check_click(pos):
                    self.mode = 2
                    self.state = self.STATE_FUNC_MODE
                    self.reiniciar()
                elif self.btn_reset.check_click(pos):
                    self.state = self.STATE_SELECT_N
                    
            elif self.state == self.STATE_TREE_MODE:
                # Botones de vértices
                for i, btn in enumerate(self.vertex_buttons):
                    if btn.check_click(pos):
                        self.manejar_evento_vertice(i)
                        
                # Otros botones
                if self.btn_decrypt.check_click(pos):
                    self.descifrar_texto()
                elif self.btn_back.check_click(pos):
                    self.state = self.STATE_MENU
                    
            elif self.state == self.STATE_FUNC_MODE:
                if self.btn_submit_func.check_click(pos):
                    self.procesar_funcion_usuario()
                elif self.btn_build_tree.check_click(pos):
                    # Mostrar mensaje informativo
                    if self.funcion and all(f is not None for f in self.funcion):
                        self.error_fun = 0
                elif self.btn_encrypt.check_click(pos):
                    self.cifrar_texto()
                elif self.btn_back.check_click(pos):
                    self.state = self.STATE_MENU
        
        # Manejar campos de entrada
        if self.state == self.STATE_FUNC_MODE:
            if self.func_input.handle_event(event):
                self.procesar_funcion_usuario()
            self.crypto_input.handle_event(event)
        elif self.state == self.STATE_TREE_MODE:
            self.crypto_input.handle_event(event)
    
    def ejecutar(self):
        """Bucle principal de la aplicación"""
        clock = pygame.time.Clock()
        running = True
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_F1:
                        # Ayuda rápida
                        print("F1: Mostrar ayuda")
                    elif event.key == pygame.K_r and pygame.key.get_mods() & pygame.KMOD_CTRL:
                        self.reiniciar()
                
                self.manejar_eventos(event)
            
            # Actualizar botones (hover)
            pos = pygame.mouse.get_pos()
            
            if self.state == self.STATE_MENU:
                self.btn_mode1.check_hover(pos)
                self.btn_mode2.check_hover(pos)
                self.btn_reset.check_hover(pos)
            elif self.state == self.STATE_TREE_MODE:
                for btn in self.vertex_buttons:
                    btn.check_hover(pos)
                self.btn_decrypt.check_hover(pos)
                self.btn_back.check_hover(pos)
            elif self.state == self.STATE_FUNC_MODE:
                self.btn_submit_func.check_hover(pos)
                self.btn_build_tree.check_hover(pos)
                self.btn_encrypt.check_hover(pos)
                self.btn_back.check_hover(pos)
            
            # Dibujar
            self.dibujar()
            
            # Actualizar pantalla
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()

# ==============================================================================
# EJECUCIÓN PRINCIPAL
# ==============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  PROYECTO MD - Demostración de Joyal a la Fórmula de Cayley")
    print("  Versión Mejorada - Interfaz Profesional")
    print("=" * 70)
    print("  Mejoras implementadas:")
    print("    1. Selector profesional de n (cualquier número ≥ 2)")
    print("    2. Interfaz moderna con gradientes y sombras")
    print("    3. Selección de vértices funcional en modo 1")
    print("    4. Visualización destacada de vértebras")
    print("    5. Panel de control informativo con iconos")
    print("=" * 70)
    print("  Autores:")
    print("    • Martin Lora Cano")
    print("    • Cristian Andrés Diaz Ortega")
    print("    • Jhon Edison Prieto Artunduaga")
    print("=" * 70)
    print("\n  Iniciando aplicación...")
    
    app = JoyalApp()
    app.ejecutar()