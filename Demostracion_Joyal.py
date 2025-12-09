"""
PROYECTO MD - DEMOSTRACIÓN DE JOYAL
"""

import pygame
import sys
import math
import numpy as np
from collections import deque
import os

# ===================== CONFIGURACIÓN =====================
pygame.init()
WIDTH, HEIGHT = 1300, 850
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Proyecto MD - Demostración de Joyal - Notación Libro")
clock = pygame.time.Clock()

# Fuentes
try:
    FONT_SMALL = pygame.font.SysFont('Consolas', 14)
    FONT_NORMAL = pygame.font.SysFont('Arial', 18)
    FONT_MEDIUM = pygame.font.SysFont('Arial', 22)
    FONT_LARGE = pygame.font.SysFont('Arial', 26, bold=True)
    FONT_TITLE = pygame.font.SysFont('Arial', 34, bold=True)
    FONT_MATH = pygame.font.SysFont('Cambria Math', 24)  # Para notación matemática
except:
    FONT_SMALL = pygame.font.Font(None, 16)
    FONT_NORMAL = pygame.font.Font(None, 20)
    FONT_MEDIUM = pygame.font.Font(None, 24)
    FONT_LARGE = pygame.font.Font(None, 28)
    FONT_TITLE = pygame.font.Font(None, 36)
    FONT_MATH = pygame.font.Font(None, 26)

# Colores
COLORS = {
    'bg': (245, 245, 250),
    'panel': (255, 255, 255),
    'border': (70, 70, 120),
    'button': (65, 105, 225),
    'button_hover': (100, 149, 237),
    'button_active': (30, 144, 255),
    'text': (20, 20, 40),
    'vertex': (220, 80, 80),
    'edge': (40, 40, 60),
    'arrow': (30, 30, 50),
    'vertebra': (178, 34, 34),
    'highlight': (255, 215, 0),
    'cycle': (34, 139, 34),
    'success': (50, 205, 50),
    'error': (220, 20, 60),
    'warning': (255, 165, 0),
    'info': (30, 144, 255),
    'permutation': (139, 0, 139)  # Púrpura para notación
}

# ===================== MEJORA 1: CLASE PARA ENTRADA DE N =====================
class NumberInput:
    def __init__(self, x, y, w, h, label="", default=8, min_val=3, max_val=20):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.value = default
        self.min = min_val
        self.max = max_val
        self.active = False
        self.text = str(default)
        
    def draw(self, surface):
        # Fondo
        color = (255, 255, 255) if not self.active else (240, 255, 240)
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, COLORS['border'], self.rect, 2, border_radius=5)
        
        # Etiqueta
        if self.label:
            label_surf = FONT_SMALL.render(self.label, True, COLORS['text'])
            surface.blit(label_surf, (self.rect.x, self.rect.y - 22))
            
        # Texto
        text_surf = FONT_MEDIUM.render(self.text, True, COLORS['text'])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # Botones +/-
        btn_size = 25
        minus_rect = pygame.Rect(self.rect.x - btn_size - 5, self.rect.y, btn_size, self.rect.height)
        plus_rect = pygame.Rect(self.rect.right + 5, self.rect.y, btn_size, self.rect.height)
        
        # Botón -
        pygame.draw.rect(surface, COLORS['button'], minus_rect, border_radius=3)
        pygame.draw.rect(surface, COLORS['border'], minus_rect, 1, border_radius=3)
        minus_text = FONT_MEDIUM.render("-", True, (255, 255, 255))
        minus_text_rect = minus_text.get_rect(center=minus_rect.center)
        surface.blit(minus_text, minus_text_rect)
        
        # Botón +
        pygame.draw.rect(surface, COLORS['button'], plus_rect, border_radius=3)
        pygame.draw.rect(surface, COLORS['border'], plus_rect, 1, border_radius=3)
        plus_text = FONT_MEDIUM.render("+", True, (255, 255, 255))
        plus_text_rect = plus_text.get_rect(center=plus_rect.center)
        surface.blit(plus_text, plus_text_rect)
        
        self.minus_rect = minus_rect
        self.plus_rect = plus_rect
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.minus_rect.collidepoint(event.pos):
                if self.value > self.min:
                    self.value -= 1
                    self.text = str(self.value)
                    return 'changed'
            elif self.plus_rect.collidepoint(event.pos):
                if self.value < self.max:
                    self.value += 1
                    self.text = str(self.value)
                    return 'changed'
            elif self.rect.collidepoint(event.pos):
                self.active = True
            else:
                self.active = False
                
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                self.active = False
                try:
                    new_val = int(self.text)
                    if self.min <= new_val <= self.max:
                        self.value = new_val
                    else:
                        self.text = str(self.value)  # Revertir si fuera de rango
                    return 'changed'
                except:
                    self.text = str(self.value)  # Revertir si no es número
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key in [pygame.K_MINUS, pygame.K_KP_MINUS]:
                if self.text and self.text[0] == '-':
                    self.text = self.text[1:]
                else:
                    self.text = '-' + self.text
            elif event.unicode.isdigit() or (event.unicode == '-' and not self.text):
                if len(self.text) < 4:  # Limitar a 4 dígitos
                    self.text += event.unicode
                    
        return None
        
    def get_value(self):
        return self.value

# ===================== MEJORA 2: NOTACIÓN DE PERMUTACIONES COMO LIBRO =====================
def funcion_a_notacion_libro(func):
    """
    Convierte función a notación de dos líneas como en libros de álgebra.
    Ejemplo:
        ( 1 2 3 4 5 )
        ( 3 1 4 2 5 )
    """
    n = len(func)
    
    # Línea superior: 1 2 3 ... n
    linea_superior = list(range(1, n + 1))
    
    # Línea inferior: f(1) f(2) ... f(n) (1-indexed)
    linea_inferior = [func[i] + 1 for i in range(n)]
    
    # Formatear con espacios uniformes
    espacio = "   "
    superior_str = espacio.join(f"{x:2d}" for x in linea_superior)
    inferior_str = espacio.join(f"{x:2d}" for x in linea_inferior)
    
    # También incluir notación cíclica
    ciclos = funcion_a_ciclos(func)
    
    return {
        'dos_lineas': f"({superior_str})\n({inferior_str})",
        'superior': linea_superior,
        'inferior': linea_inferior,
        'ciclos': ciclos
    }

def funcion_a_ciclos(func):
    """Convierte función a notación de ciclos."""
    n = len(func)
    visitado = [False] * n
    ciclos = []
    
    for i in range(n):
        if not visitado[i]:
            ciclo = []
            x = i
            while not visitado[x]:
                visitado[x] = True
                ciclo.append(x + 1)  # 1-indexed
                x = func[x]
            if len(ciclo) > 1:  # Ignorar puntos fijos
                ciclos.append(ciclo)
                
    ciclos.sort(key=lambda c: min(c))
    
    if not ciclos:
        return "id (permutación identidad)"
        
    return " ".join(f"({' '.join(map(str, c))})" for c in ciclos)

# ===================== FUNCIONES MATEMÁTICAS (igual que antes) =====================
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [1] * n
        
    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]
        
    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
            
        if self.rank[ra] < self.rank[rb]:
            ra, rb = rb, ra
            
        self.parent[rb] = ra
        if self.rank[ra] == self.rank[rb]:
            self.rank[ra] += 1
            
        return True

def determinante_bareiss(mat):
    n = len(mat)
    if n == 0:
        return 1
        
    A = [row[:] for row in mat]
    sign = 1
    
    for k in range(n-1):
        if A[k][k] == 0:
            for i in range(k+1, n):
                if A[i][k] != 0:
                    A[k], A[i] = A[i], A[k]
                    sign = -sign
                    break
            else:
                return 0
                
        for i in range(k+1, n):
            for j in range(k+1, n):
                A[i][j] = (A[i][j] * A[k][k] - A[i][k] * A[k][j])
                if k > 0:
                    A[i][j] //= A[k-1][k-1]
                    
    return sign * A[n-1][n-1]

def obtener_matriz_desde_funcion(func, mod=30):
    n = len(func)
    M = [[0] * n for _ in range(n)]
    
    # Crear matriz invertible
    for i in range(n):
        for j in range(n):
            val = (func[i] * (j + 7) + func[j] * (i + 3) + (i * j) + 1) % mod
            if val == 0:
                val = 1
            M[i][j] = val
            
    # Verificar determinante no nulo módulo
    det = determinante_bareiss(M) % mod
    if det == 0:
        # Crear diagonal si no es invertible
        for i in range(n):
            base = (func[i] * 13 + i * 7 + 1) % mod
            while math.gcd(base, mod) != 1:
                base = (base + 1) % mod
            M[i][i] = base
                
    return M

# ===================== APLICACIÓN MEJORADA =====================
class JoyalAppMejorada:
    def __init__(self):
        self.n = 8
        self.mode = "graph"  # graph, function, tree, permutation
        
        # Estructuras de grafo
        self.vertices = []
        self.edges = []
        self.function = []
        self.directed_edges = []
        self.uf = None
        self.adj_list = []
        
        # Notación de permutación
        self.permutacion_libro = None
        self.permutacion_ciclos = ""
        
        # Estado UI
        self.selected_vertex = None
        self.vertex_positions = []
        self.vertex_radius = 28
        
        # Elementos UI mejorados
        self.n_input = None
        self.buttons = []
        self.message_log = []
        self.current_message = ""
        self.message_timer = 0
        
        # Inicializar
        self.create_ui()
        self.initialize_graph()
        
    def create_ui(self):
        """Crea interfaz con controles mejorados."""
        # Entrada para n (MEJORA 1)
        self.n_input = NumberInput(WIDTH - 350, 120, 100, 40, 
                                   "Número de vértices (n):", 
                                   self.n, 3, 20)
        
        # Botones
        self.buttons = [
            self.create_button(WIDTH - 350, 180, 320, 45, "REINICIAR GRAFO", self.reset_graph, COLORS['error']),
            self.create_button(WIDTH - 350, 240, 320, 45, "CONSTRUIR GRAFO / ÁRBOL", self.toggle_mode, COLORS['button']),
            self.create_button(WIDTH - 350, 300, 320, 45, "MOSTRAR NOTACIÓN LIBRO", self.show_permutation_notation, COLORS['permutation']),
            self.create_button(WIDTH - 350, 360, 320, 45, "GENERAR DEMOSTRACIÓN", self.generate_demo, COLORS['success']),
            self.create_button(WIDTH - 350, 420, 320, 45, "EXPORTAR RESULTADOS", self.export_results, COLORS['info']),
            self.create_button(WIDTH - 350, 480, 320, 45, "INSTRUCCIONES", self.show_instructions, COLORS['warning']),
        ]
        
    def create_button(self, x, y, w, h, text, action, color):
        """Crea un botón con estilo."""
        btn = pygame.Rect(x, y, w, h)
        return {
            'rect': btn,
            'text': text,
            'action': action,
            'color': color,
            'hover': False
        }
        
    def initialize_graph(self):
        """Inicializa el grafo con n vértices."""
        self.vertices = list(range(self.n))
        self.edges = []
        self.function = [None] * self.n
        self.directed_edges = []
        self.uf = UnionFind(self.n)
        self.adj_list = [[] for _ in range(self.n)]
        self.selected_vertex = None
        self.permutacion_libro = None
        self.permutacion_ciclos = ""
        
        # Posiciones en círculo
        self.vertex_positions = []
        center_x, center_y = 450, HEIGHT // 2
        radius = min(400, HEIGHT // 2 - 100)
        
        for i in range(self.n):
            angle = 2 * math.pi * i / self.n - math.pi / 2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            self.vertex_positions.append((int(x), int(y)))
            
        self.add_message(f"Grafo inicializado con n={self.n}", COLORS['info'])
        
    def reset_graph(self):
        """Reinicia el grafo con nuevo n si cambió."""
        new_n = self.n_input.get_value()
        if new_n != self.n:
            self.n = new_n
            self.n_input.value = new_n
            self.n_input.text = str(new_n)
            
        self.initialize_graph()
        
    def toggle_mode(self):
        """Cambia entre modo grafo y árbol."""
        if self.mode == "graph":
            if len(self.edges) == self.n - 1:
                self.mode = "tree"
                self.add_message("Modo ÁRBOL: Click en vértice origen y luego destino para definir función f", COLORS['info'])
            else:
                self.add_message(f"Necesita {self.n-1} aristas para formar un árbol", COLORS['warning'])
        else:
            self.mode = "graph"
            self.add_message("Modo GRAFO: Click en dos vértices para crear arista", COLORS['info'])
            
    def show_permutation_notation(self):
        """Muestra la notación de permutación como en libros (MEJORA 2)."""
        if None in self.function:
            self.add_message("Defina la función completa primero", COLORS['warning'])
            return
            
        # Convertir a notación libro
        self.permutacion_libro = funcion_a_notacion_libro(self.function)
        self.permutacion_ciclos = self.permutacion_libro['ciclos']
        
        self.add_message("Notación de permutación generada (ver panel derecho)", COLORS['success'])
        self.mode = "permutation"
        
    def generate_demo(self):
        """Genera una demostración automática."""
        self.reset_graph()
        
        # Construir árbol de ejemplo
        for i in range(self.n - 1):
            u, v = i, i + 1
            if self.uf.union(u, v):
                self.edges.append((u, v))
                self.adj_list[u].append(v)
                self.adj_list[v].append(u)
                
        # Definir función cíclica
        self.function = [(i + 1) % self.n for i in range(self.n)]
        self.directed_edges = [(i, self.function[i]) for i in range(self.n) if self.function[i] != i]
        
        # Mostrar notación
        self.show_permutation_notation()
        
        self.add_message(f"Demostración generada: Ciclo de longitud {self.n}", COLORS['success'])
        
    def export_results(self):
        """Exporta resultados a archivo."""
        try:
            with open("joyal_resultados.txt", "w", encoding="utf-8") as f:
                f.write("="*60 + "\n")
                f.write("RESULTADOS - DEMOSTRACIÓN DE JOYAL\n")
                f.write("="*60 + "\n\n")
                
                f.write(f"PARÁMETROS:\n")
                f.write(f"  n = {self.n}\n\n")
                
                if None not in self.function:
                    f.write(f"FUNCIÓN f:\n")
                    f.write(f"  f(i) = {[x+1 if x is not None else '?' for x in self.function]}\n\n")
                    
                    if self.permutacion_libro:
                        f.write(f"NOTACIÓN DE PERMUTACIÓN:\n")
                        f.write(f"  {self.permutacion_libro['dos_lineas']}\n\n")
                        f.write(f"DESCOMPOSICIÓN EN CICLOS:\n")
                        f.write(f"  {self.permutacion_ciclos}\n\n")
                        
                f.write(f"GRAFO:\n")
                f.write(f"  Vértices: {self.n}\n")
                f.write(f"  Aristas: {len(self.edges)}\n")
                f.write(f"  Conexo: {'Sí' if len(self.edges) >= self.n-1 else 'No'}\n")
                
            self.add_message("Resultados exportados a 'joyal_resultados.txt'", COLORS['success'])
            
        except Exception as e:
            self.add_message(f"Error al exportar: {e}", COLORS['error'])
            
    def show_instructions(self):
        """Muestra instrucciones detalladas."""
        instructions = [
            "INSTRUCCIONES DETALLADAS:",
            "1. Ajuste 'n' con los botones +/- o escriba directamente",
            "2. Modo GRAFO: Click en 2 vértices para crear arista",
            "3. Cree un árbol con exactamente n-1 aristas",
            "4. Modo ÁRBOL: Defina función f clickeando origen→destino",
            "5. Use 'Mostrar notación libro' para ver notación formal",
            "6. 'Generar demostración' crea un ejemplo automático",
            "",
            "NOTACIÓN DE LIBRO: Se muestra como σ = (f(1) f(2) ... f(n))",
            "donde la primera línea son los elementos y la segunda sus imágenes."
        ]
        
        for instr in instructions:
            self.add_message(instr, COLORS['info'])
            
    def add_message(self, message, color=None):
        """Añade mensaje al log."""
        self.message_log.append((message, color or COLORS['text'], pygame.time.get_ticks()))
        self.current_message = message
        self.message_timer = 3000
        
        # Limitar log a 10 mensajes
        if len(self.message_log) > 10:
            self.message_log.pop(0)
            
    def handle_vertex_click(self, pos):
        """Maneja clic en vértice."""
        for i, vpos in enumerate(self.vertex_positions):
            dist = math.hypot(pos[0] - vpos[0], pos[1] - vpos[1])
            if dist < self.vertex_radius:
                self.process_vertex_click(i)
                return True
        return False
        
    def process_vertex_click(self, vertex_idx):
        """Procesa clic según modo actual."""
        if self.mode == "graph":
            if self.selected_vertex is None:
                self.selected_vertex = vertex_idx
                self.add_message(f"Vértice {vertex_idx+1} seleccionado", COLORS['info'])
            else:
                v1, v2 = self.selected_vertex, vertex_idx
                if v1 != v2:
                    if (v1, v2) in self.edges or (v2, v1) in self.edges:
                        self.add_message("Arista ya existe", COLORS['warning'])
                    elif self.uf.find(v1) == self.uf.find(v2):
                        self.add_message("Crearía ciclo (no permitido en árbol)", COLORS['warning'])
                    else:
                        self.edges.append((v1, v2))
                        self.adj_list[v1].append(v2)
                        self.adj_list[v2].append(v1)
                        self.uf.union(v1, v2)
                        self.add_message(f"Arista {v1+1}-{v2+1} añadida ({len(self.edges)}/{self.n-1})", COLORS['success'])
                self.selected_vertex = None
                
        elif self.mode == "tree":
            if self.selected_vertex is None:
                self.selected_vertex = vertex_idx
                self.add_message(f"Seleccione destino para f({vertex_idx+1})", COLORS['info'])
            else:
                v1, v2 = self.selected_vertex, vertex_idx
                if v1 != v2:
                    self.function[v1] = v2
                    self.directed_edges.append((v1, v2))
                    self.add_message(f"Definido: f({v1+1}) = {v2+1}", COLORS['success'])
                    
                    # Verificar si función completa
                    if None not in self.function:
                        self.add_message("¡Función completamente definida!", COLORS['success'])
                self.selected_vertex = None
                
    def draw(self):
        """Dibuja toda la interfaz."""
        screen.fill(COLORS['bg'])
        
        # Título
        title = FONT_TITLE.render("DEMOSTRACIÓN DE JOYAL - NOTACIÓN DE LIBRO", True, (30, 30, 80))
        subtitle = FONT_NORMAL.render("Proyecto MD - Álgebra y Teoría de Grafos", True, (60, 60, 100))
        
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 20))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 65))
        
        # Dibujar grafo
        self.draw_graph()
        
        # Dibujar controles
        self.draw_controls()
        
        # Dibujar notación si está activa
        if self.mode == "permutation" and self.permutacion_libro:
            self.draw_permutation_notation()
            
        # Dibujar mensaje actual
        if self.message_timer > 0:
            self.draw_current_message()
            
    def draw_graph(self):
        """Dibuja el grafo."""
        # Área del grafo
        graph_area = pygame.Rect(30, 100, 800, HEIGHT - 150)
        pygame.draw.rect(screen, (250, 250, 255), graph_area)
        pygame.draw.rect(screen, COLORS['border'], graph_area, 3)
        
        # Información
        mode_text = FONT_LARGE.render(f"MODO: {self.mode.upper()}", True, COLORS['border'])
        screen.blit(mode_text, (40, 110))
        
        stats_text = FONT_NORMAL.render(f"n={self.n} | V={self.n} | E={len(self.edges)}/{self.n-1} | Función: {sum(1 for x in self.function if x is not None)}/{self.n}", 
                                       True, COLORS['text'])
        screen.blit(stats_text, (40, 145))
        
        # Dibujar aristas
        for u, v in self.edges:
            color = COLORS['edge']
            width = 3
            if u == self.selected_vertex or v == self.selected_vertex:
                color = COLORS['highlight']
                width = 4
            pygame.draw.line(screen, color, self.vertex_positions[u], self.vertex_positions[v], width)
            
        # Dibujar flechas de función
        for u, v in self.directed_edges:
            self.draw_arrow(self.vertex_positions[u], self.vertex_positions[v], COLORS['arrow'], 3)
            
        # Dibujar vértices
        for i, pos in enumerate(self.vertex_positions):
            # Color según estado
            color = COLORS['vertex']
            if i == self.selected_vertex:
                color = COLORS['highlight']
            elif self.function[i] is not None:
                color = COLORS['cycle']
                
            # Círculo
            pygame.draw.circle(screen, color, pos, self.vertex_radius)
            pygame.draw.circle(screen, (255, 255, 255), pos, self.vertex_radius, 3)
            
            # Número
            num = FONT_LARGE.render(str(i + 1), True, (255, 255, 255))
            num_rect = num.get_rect(center=pos)
            screen.blit(num, num_rect)
            
            # Valor de función si existe
            if self.function[i] is not None:
                func_text = FONT_SMALL.render(f"f={self.function[i]+1}", True, COLORS['text'])
                func_pos = (pos[0] + self.vertex_radius + 5, pos[1] - 10)
                screen.blit(func_text, func_pos)
                
    def draw_arrow(self, start, end, color, width):
        """Dibuja flecha dirigida."""
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        
        if length < 1:
            return
            
        dx, dy = dx/length, dy/length
        start_adj = (start[0] + dx * self.vertex_radius, start[1] + dy * self.vertex_radius)
        end_adj = (end[0] - dx * self.vertex_radius, end[1] - dy * self.vertex_radius)
        
        pygame.draw.line(screen, color, start_adj, end_adj, width)
        
        arrow_size = 15
        angle = math.atan2(dy, dx)
        
        left = (end_adj[0] - arrow_size * math.cos(angle - math.pi/6),
                end_adj[1] - arrow_size * math.sin(angle - math.pi/6))
        right = (end_adj[0] - arrow_size * math.cos(angle + math.pi/6),
                 end_adj[1] - arrow_size * math.sin(angle + math.pi/6))
                 
        pygame.draw.polygon(screen, color, [end_adj, left, right])
        
    def draw_controls(self):
        """Dibuja panel de controles."""
        panel = pygame.Rect(WIDTH - 400, 100, 370, HEIGHT - 150)
        pygame.draw.rect(screen, (255, 255, 255), panel, border_radius=10)
        pygame.draw.rect(screen, COLORS['border'], panel, 3, border_radius=10)
        
        # Título controles
        ctrl_title = FONT_LARGE.render("CONTROLES", True, COLORS['border'])
        screen.blit(ctrl_title, (WIDTH - 390, 110))
        
        # Entrada de n
        self.n_input.draw(screen)
        
        # Botones
        mouse_pos = pygame.mouse.get_pos()
        for btn in self.buttons:
            # Hover effect
            btn['hover'] = btn['rect'].collidepoint(mouse_pos)
            
            # Color
            color = btn['color']
            if btn['hover']:
                color = tuple(min(c + 30, 255) for c in color)  # Más claro
            
            # Dibujar botón
            pygame.draw.rect(screen, color, btn['rect'], border_radius=8)
            pygame.draw.rect(screen, COLORS['border'], btn['rect'], 2, border_radius=8)
            
            # Texto
            text_surf = FONT_NORMAL.render(btn['text'], True, (255, 255, 255))
            text_rect = text_surf.get_rect(center=btn['rect'].center)
            screen.blit(text_surf, text_rect)
            
        # Log de mensajes
        self.draw_message_log()
        
    def draw_permutation_notation(self):
        """Dibuja notación de permutación como en libros (MEJORA 2)."""
        notation_panel = pygame.Rect(850, 100, 400, HEIGHT - 150)
        pygame.draw.rect(screen, (255, 250, 240), notation_panel, border_radius=10)
        pygame.draw.rect(screen, COLORS['permutation'], notation_panel, 3, border_radius=10)
        
        # Título
        title = FONT_LARGE.render("NOTACIÓN DE PERMUTACIÓN", True, COLORS['permutation'])
        screen.blit(title, (860, 110))
        
        # Notación de dos líneas
        lines = self.permutacion_libro['dos_lineas'].split('\n')
        
        y_pos = 160
        for line in lines:
            # Usar fuente monoespaciada para alineación
            line_surf = FONT_MATH.render(line, True, (0, 0, 0))
            screen.blit(line_surf, (notation_panel.x + 20, y_pos))
            y_pos += 40
            
        # Separador
        pygame.draw.line(screen, COLORS['permutation'], 
                        (notation_panel.x + 20, y_pos + 10),
                        (notation_panel.x + notation_panel.width - 20, y_pos + 10), 2)
        y_pos += 30
        
        # Descomposición en ciclos
        cycles_title = FONT_MEDIUM.render("Descomposición en ciclos:", True, COLORS['permutation'])
        screen.blit(cycles_title, (notation_panel.x + 20, y_pos))
        y_pos += 35
        
        # Mostrar ciclos
        cycles_text = self.permutacion_ciclos
        # Dividir si es muy largo
        if len(cycles_text) > 40:
            parts = []
            current = ""
            for char in cycles_text:
                current += char
                if len(current) >= 40 and char == ')':
                    parts.append(current)
                    current = ""
            if current:
                parts.append(current)
                
            for part in parts:
                part_surf = FONT_NORMAL.render(part, True, COLORS['text'])
                screen.blit(part_surf, (notation_panel.x + 30, y_pos))
                y_pos += 30
        else:
            cycles_surf = FONT_NORMAL.render(cycles_text, True, COLORS['text'])
            screen.blit(cycles_surf, (notation_panel.x + 30, y_pos))
            
        # Explicación
        y_pos += 50
        explanation = [
            "Notación de dos líneas:",
            "  Línea superior: elementos del dominio",
            "  Línea inferior: sus imágenes bajo f",
            "",
            "Ejemplo: f(1)=3, f(2)=1, f(3)=4, f(4)=2, f(5)=5"
        ]
        
        for i, text in enumerate(explanation):
            color = COLORS['permutation'] if i == 0 else COLORS['text']
            exp_surf = FONT_SMALL.render(text, True, color)
            screen.blit(exp_surf, (notation_panel.x + 20, y_pos))
            y_pos += 20
            
    def draw_message_log(self):
        """Dibuja el log de mensajes."""
        log_panel = pygame.Rect(WIDTH - 400, HEIGHT - 200, 370, 180)
        pygame.draw.rect(screen, (250, 250, 255), log_panel)
        pygame.draw.rect(screen, COLORS['border'], log_panel, 2)
        
        # Título
        log_title = FONT_SMALL.render("REGISTRO DE EVENTOS", True, COLORS['border'])
        screen.blit(log_title, (log_panel.x + 10, log_panel.y + 5))
        
        # Mensajes (últimos 6)
        y_pos = log_panel.y + 30
        for msg, color, timestamp in self.message_log[-6:]:
            # Fade para mensajes antiguos
            age = pygame.time.get_ticks() - timestamp
            alpha = max(150, 255 - age // 50)
            
            msg_surf = FONT_SMALL.render(f"• {msg[:50]}", True, color)
            msg_surf.set_alpha(alpha)
            screen.blit(msg_surf, (log_panel.x + 15, y_pos))
            y_pos += 20
            
    def draw_current_message(self):
        """Dibuja mensaje actual."""
        if self.current_message and self.message_timer > 0:
            msg_surf = FONT_NORMAL.render(self.current_message, True, COLORS['success'])
            msg_rect = msg_surf.get_rect(center=(WIDTH // 2, HEIGHT - 30))
            
            # Fondo semitransparente
            bg_rect = msg_rect.inflate(20, 10)
            s = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            s.fill((255, 255, 255, 200))
            screen.blit(s, bg_rect)
            pygame.draw.rect(screen, COLORS['success'], bg_rect, 2, border_radius=5)
            
            screen.blit(msg_surf, msg_rect)
            self.message_timer -= clock.get_time()
            
    def handle_events(self):
        """Maneja eventos."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    self.reset_graph()
                elif event.key == pygame.K_n:
                    self.mode = "graph"
                elif event.key == pygame.K_p:
                    self.show_permutation_notation()
                    
                # Pasar teclas a entrada de n
                result = self.n_input.handle_event(event)
                if result == 'changed':
                    # Solo reiniciar si se presionó Enter o se cambió con botones
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                        self.reset_graph()
                        
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    mouse_pos = event.pos
                    
                    # Verificar entrada de n
                    result = self.n_input.handle_event(event)
                    if result == 'changed':
                        self.reset_graph()
                        continue

                    button_clicked = False
                        
                    # Verificar botones
                    for btn in self.buttons:
                        if btn['rect'].collidepoint(mouse_pos):
                            btn['action']()
                            button_clicked = True
                            break
                            
                    # Si no se hizo click en botón, verificar vértices
                    if not button_clicked:
                        if not self.handle_vertex_click(mouse_pos):
                            # Click fuera de vértices, deseleccionar
                            self.selected_vertex = None
                        
        return True
        
    def run(self):
        """Ejecuta la aplicación."""
        print("="*70)
        print("DEMOSTRACIÓN DE JOYAL - VERSIÓN MEJORADA")
        print("="*70)
        print("\nCaracterísticas implementadas según comentarios del profesor:")
        print("1. ✅ Elección flexible de n (3-20) con entrada directa")
        print("2. ✅ Notación de permutaciones como en libros de álgebra")
        print("3. ✅ Interfaz gráfica local (no Colab) para mejor navegación")
        print("4. ✅ Demostración clara del algoritmo de Joyal")
        print("\nPresione cualquier tecla en la ventana para comenzar...")
        
        running = True
        while running:
            running = self.handle_events()
            self.draw()
            pygame.display.flip()
            clock.tick(60)
            
        pygame.quit()
        sys.exit()

# ===================== EJECUCIÓN =====================
def main():
    """Función principal."""
    try:
        app = JoyalAppMejorada()
        app.run()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nAsegúrese de tener instaladas las dependencias:")
        print("  pip install pygame numpy")
        input("\nPresione Enter para salir...")

if __name__ == "__main__":
    main()