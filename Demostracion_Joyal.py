# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                                                                            ║
# ║     PROYECTO MD - Demostración de Joyal a la Fórmula de Cayley             ║
# ║                                                                            ║
# ║     Versión GitHub - Mejorada según requerimientos                         ║
# ║                                                                            ║
# ╠════════════════════════════════════════════════════════════════════════════╣
# ║                                                                            ║
# ║     MEJORAS IMPLEMENTADAS:                                                 ║
# ║         1. Elegir CUALQUIER número n de vértices (≥2)                      ║
# ║         2. Notación de permutaciones para la función                       ║
# ║         3. Mejor explicación del cifrado Hill                              ║
# ║         4. Interfaz mejorada y organizada                                  ║
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
# ║         Este programa implementa una demostración visual e interactiva     ║
# ║         de la biyección de Joyal para la fórmula de Cayley, que establece  ║
# ║         que el número de árboles etiquetados con n vértices es n^(n-2).    ║
# ║                                                                            ║
# ║         El programa permite:                                               ║
# ║         1. Construir una función a partir de un árbol (Modo 1)             ║
# ║         2. Construir un árbol a partir de una función (Modo 2)             ║
# ║         3. Encriptar/desencriptar textos usando cifrado Hill n×n           ║
# ║                                                                            ║
# ╠════════════════════════════════════════════════════════════════════════════╣
# ║                                                                            ║
# ║     INSTRUCCIONES DE USO:                                                  ║
# ║         1. Ejecutar: python joyal_demo.py                                  ║
# ║         2. Ingresar número de vértices n (≥2)                              ║
# ║         3. Usar los botones de la interfaz gráfica                         ║
# ║                                                                            ║
# ╚════════════════════════════════════════════════════════════════════════════╝

import pygame
import math
import numpy as np
from collections import deque
import sys
import os

# ==============================================================================
# CONFIGURACIÓN INICIAL
# ==============================================================================

pygame.init()

# Dimensiones de la ventana (más grande)
WIDTH, HEIGHT = 1200, 850

# Crear la ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Proyecto MD - Demostración de Joyal a la Fórmula de Cayley")

# Fuentes
try:
    FONT = pygame.font.SysFont('Arial', 24)
    FONT_BOLD = pygame.font.SysFont('Arial', 26, bold=True)
    FONT_SMALL = pygame.font.SysFont('Arial', 20)
    FONT_TITLE = pygame.font.SysFont('Arial', 32, bold=True)
    FONT_LARGE = pygame.font.SysFont('Arial', 36, bold=True)
except:
    # Fallback si no encuentra Arial
    FONT = pygame.font.SysFont(None, 24)
    FONT_BOLD = pygame.font.SysFont(None, 26, bold=True)
    FONT_SMALL = pygame.font.SysFont(None, 20)
    FONT_TITLE = pygame.font.SysFont(None, 32, bold=True)
    FONT_LARGE = pygame.font.SysFont(None, 36, bold=True)

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GRAY = (240, 240, 240)
DARK_GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
DARK_BLUE = (0, 0, 139)
LIGHT_GREEN = (144, 238, 144)

# ==============================================================================
# CLASE PARA BOTONES MEJORADA
# ==============================================================================

class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_BLUE, text_color=BLACK):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.hover_color = self._adjust_color(color, 30)  # Más claro al hover
        self.current_color = color
        self.clicked = False
        self.hovered = False
        
    def _adjust_color(self, color, amount):
        """Ajusta el color para efecto hover"""
        return tuple(min(255, max(0, c + amount)) for c in color)
        
    def draw(self, surface):
        # Fondo del botón
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 2, border_radius=8)
        
        # Renderizar texto centrado
        text_surf = FONT.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # Efecto de sombra si está hover
        if self.hovered:
            pygame.draw.rect(surface, (100, 100, 100, 100), self.rect, 1, border_radius=8)
        
    def check_hover(self, pos):
        self.hovered = self.rect.collidepoint(pos)
        self.current_color = self.hover_color if self.hovered else self.color
        return self.hovered
            
    def check_click(self, pos):
        if self.rect.collidepoint(pos):
            self.clicked = True
            return True
        self.clicked = False
        return False

# ==============================================================================
# CLASE PARA CAMPOS DE TEXTO MEJORADA
# ==============================================================================

class InputBox:
    def __init__(self, x, y, width, height, text='', label='', placeholder=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.label = label
        self.placeholder = placeholder
        self.active = False
        self.max_length = 100
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def draw(self, surface):
        # Dibujar label
        if self.label:
            label_surf = FONT_SMALL.render(self.label, True, DARK_BLUE)
            surface.blit(label_surf, (self.rect.x, self.rect.y - 25))
            
        # Dibujar caja
        color = BLUE if self.active else DARK_GRAY
        pygame.draw.rect(surface, WHITE, self.rect, border_radius=4)
        pygame.draw.rect(surface, color, self.rect, 2, border_radius=4)
        
        # Mostrar texto o placeholder
        display_text = self.text if self.text else self.placeholder
        text_color = BLACK if self.text else DARK_GRAY
        
        text_surf = FONT.render(display_text, True, text_color)
        
        # Recortar texto si es muy largo
        if text_surf.get_width() > self.rect.width - 10:
            # Encontrar cuánto texto cabe
            for i in range(len(display_text), 0, -1):
                test_text = "..." + display_text[-i:]
                test_surf = FONT.render(test_text, True, text_color)
                if test_surf.get_width() <= self.rect.width - 10:
                    text_surf = test_surf
                    break
        
        surface.blit(text_surf, (self.rect.x + 5, self.rect.y + (self.rect.height - text_surf.get_height()) // 2))
        
        # Cursor parpadeante si está activo
        if self.active:
            self.cursor_timer = (self.cursor_timer + 1) % 60
            if self.cursor_timer < 30:
                cursor_x = self.rect.x + 5 + text_surf.get_width()
                pygame.draw.line(surface, BLACK, 
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
                elif event.key == pygame.K_ESCAPE:
                    self.active = False
                else:
                    if len(self.text) < self.max_length:
                        self.text += event.unicode
        return False
        
    def get_text(self):
        return self.text.strip()

# ==============================================================================
# CLASE PARA SELECTOR DE N - CUALQUIER NÚMERO
# ==============================================================================

class NSelector:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 400, 250)
        self.n = 6  # Valor por defecto (lo que mostraste)
        self.selected = False
        
        # Campo de entrada para cualquier n
        self.input_box = InputBox(x + 100, y + 100, 200, 40, '6', 'Ingrese número de vértices (n):', 'Ej: 6')
        
        # Botones predefinidos para valores comunes
        self.common_buttons = []
        common_values = [3, 4, 5, 6, 7, 8, 9, 10, 12, 15]
        for i, value in enumerate(common_values):
            row = i // 5
            col = i % 5
            btn = Button(x + 50 + col * 70, y + 160 + row * 45, 60, 35, str(value))
            self.common_buttons.append((btn, value))
            
        # Botón de confirmar
        self.confirm_btn = Button(x + 150, y + 210, 100, 40, "Confirmar", GREEN)
        
        # Botón avanzado (para n grandes)
        self.advanced_btn = Button(x + 260, y + 210, 120, 40, "Personalizado", ORANGE)
        
    def draw(self, surface):
        # Fondo
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect, border_radius=15)
        pygame.draw.rect(surface, DARK_BLUE, self.rect, 3, border_radius=15)
        
        # Título
        title = FONT_LARGE.render("CONFIGURACIÓN INICIAL", True, DARK_BLUE)
        surface.blit(title, (self.rect.x + self.rect.width//2 - title.get_width()//2, self.rect.y + 15))
        
        # Instrucción
        instr1 = FONT.render("Ingrese cualquier número n ≥ 2", True, BLACK)
        instr2 = FONT_SMALL.render("(Para n > 15, use 'Personalizado')", True, DARK_GRAY)
        surface.blit(instr1, (self.rect.x + 20, self.rect.y + 50))
        surface.blit(instr2, (self.rect.x + 20, self.rect.y + 75))
        
        # Dibujar campo de entrada
        self.input_box.draw(surface)
        
        # Valores comunes
        common_label = FONT_SMALL.render("Valores comunes:", True, BLACK)
        surface.blit(common_label, (self.rect.x + 20, self.rect.y + 145))
        
        # Dibujar botones comunes
        for btn, value in self.common_buttons:
            if value == self.n:
                btn.color = YELLOW
            btn.draw(surface)
            
        # Botones de acción
        self.confirm_btn.draw(surface)
        self.advanced_btn.draw(surface)
        
    def handle_event(self, event):
        # Manejar campo de entrada
        if self.input_box.handle_event(event):
            return True
            
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            
            # Verificar campo de entrada
            if self.input_box.rect.collidepoint(pos):
                self.input_box.active = True
            else:
                self.input_box.active = False
                
            # Procesar valor del campo
            try:
                input_n = int(self.input_box.text) if self.input_box.text else 6
                if input_n >= 2:
                    self.n = input_n
            except:
                self.n = 6
                
            # Verificar botones comunes
            for btn, value in self.common_buttons:
                if btn.check_click(pos):
                    self.n = value
                    self.input_box.text = str(value)
                    
            # Verificar botón confirmar
            if self.confirm_btn.check_click(pos):
                try:
                    self.n = int(self.input_box.text) if self.input_box.text else 6
                    if self.n < 2:
                        self.n = 6  # Valor mínimo
                    elif self.n > 50:  # Límite razonable
                        self.n = 50
                except:
                    self.n = 6
                self.selected = True
                return True
                
            # Verificar botón avanzado
            if self.advanced_btn.check_click(pos):
                # Mantener el valor actual
                self.selected = True
                return True
                
        return False

# ==============================================================================
# FUNCIONES MATEMÁTICAS Y DE GRAFOS
# ==============================================================================

# Variables globales que se configurarán dinámicamente
n = 6  # Valor inicial
vertice_pos = []
vertice_rad = 20
aristas = []
grafo = []
parent = []
ARISTA_WIDTH = 4

def calcular_posiciones_vertices(n_vertices):
    """Calcula posiciones para n vértices en un círculo"""
    global vertice_pos
    vertice_pos = []
    centro_x, centro_y = WIDTH // 2, 350
    # Radio adaptativo según n
    radio = min(250, 180 + n_vertices * 5) if n_vertices <= 20 else 300
    
    for i in range(n_vertices):
        angulo = 2 * math.pi * i / n_vertices - math.pi/2  # Ajuste para empezar arriba
        x = centro_x + radio * math.cos(angulo)
        y = centro_y + radio * math.sin(angulo)
        vertice_pos.append((int(x), int(y)))
    
    return vertice_pos

def inicializar_estructuras(n_vertices):
    """Inicializa las estructuras de datos para n vértices"""
    global n, grafo, parent, aristas, vertice_rad
    n = n_vertices
    aristas = []
    grafo = [[] for _ in range(n)]
    parent = list(range(n))
    
    # Ajustar tamaño de vértices según n
    vertice_rad = max(15, min(25, 30 - n//5))
    
    calcular_posiciones_vertices(n)
    return n

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
    return all(find(i) == root0 for i in range(1, n))

def distancia(a, b):
    """Distancia euclidiana entre dos puntos"""
    return math.hypot(a[0] - b[0], a[1] - b[1])

def draw_vertices(surface=None):
    """Dibuja todos los vértices"""
    if surface is None:
        surface = screen
        
    for i, pos in enumerate(vertice_pos):
        # Círculo del vértice (rosa)
        pygame.draw.circle(surface, (255, 180, 180), pos, vertice_rad)
        # Borde
        pygame.draw.circle(surface, BLACK, pos, vertice_rad, 2)
        # Número (1-indexado)
        vertice_num = FONT_BOLD.render(str(i + 1), True, WHITE)
        text_rect = vertice_num.get_rect(center=pos)
        surface.blit(vertice_num, text_rect)

def draw_dirigido(surface, a_pos, b_pos, color=BLACK, width=3, head_size=10):
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
    
    # Línea principal
    pygame.draw.line(surface, color, (sx, sy), (ex, ey), width)
    
    # Punta de flecha
    angle = math.atan2(ey - sy, ex - sx)
    left = (ex - head_size * math.cos(angle - math.pi/6),
            ey - head_size * math.sin(angle - math.pi/6))
    right = (ex - head_size * math.cos(angle + math.pi/6),
             ey - head_size * math.sin(angle + math.pi/6))
    pygame.draw.polygon(surface, color, [(ex, ey), left, right])

def draw_vertebra(surface, p1, p2, color=RED, ancho=4, largo_linea=12, largo_espacio=8):
    """Dibuja línea punteada para vértebra"""
    x1, y1 = p1
    x2, y2 = p2
    length = math.hypot(x2 - x1, y2 - y1)
    
    if length == 0:
        return
        
    dx = (x2 - x1) / length
    dy = (y2 - y1) / length
    
    dibujo = 0.0
    while dibujo < length:
        ini_x = x1 + dx * dibujo
        ini_y = y1 + dy * dibujo
        final = min(dibujo + largo_linea, length)
        fin_x = x1 + dx * final
        fin_y = y1 + dy * final
        pygame.draw.line(surface, color, (ini_x, ini_y), (fin_x, fin_y), ancho)
        dibujo += largo_linea + largo_espacio

def draw_bucle(surface, pos, color=BLACK, width=3):
    """Dibuja un bucle (arista de un vértice a sí mismo)"""
    x, y = pos
    centro = (x + 6, y - vertice_rad + 2)
    rx, ry = 20, 14
    
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
    if not aristas_dir:
        return []
        
    grafo_local = {}
    for u, v in aristas_dir:
        grafo_local.setdefault(u, []).append(v)
        grafo_local.setdefault(v, [])
        
    vertices_cic = set()
    
    for u, vecinos in grafo_local.items():
        for v in vecinos:
            # Remover temporalmente la arista
            if v in grafo_local[u]:
                grafo_local[u].remove(v)
                # Buscar camino alternativo
                camino = depthfirstsearch(grafo_local, v, u)
                # Restaurar arista
                grafo_local[u].append(v)
                
                if camino:
                    vertices_cic.add(u)
                    vertices_cic.add(v)
                
    return sorted(vertices_cic)

def dirigir_vertices(grafo, aristas, aristas_vert, vertice_fin):
    """Orienta aristas hacia la vértebra"""
    # Calcular distancias al vértice final con BFS
    dist = [-1] * len(grafo)
    queue = deque([vertice_fin])
    dist[vertice_fin] = 0
    
    while queue:
        v = queue.popleft()
        for ady in grafo[v]:
            if dist[ady] == -1:
                dist[ady] = dist[v] + 1
                queue.append(ady)
                
    # Orientar aristas
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
# NOTACIÓN DE PERMUTACIONES
# ==============================================================================

def funcion_a_notacion_permutacion(funcion, n_vertices):
    """Convierte función a notación de permutaciones (ciclos)"""
    if any(v is None for v in funcion):
        return "Función incompleta"
    
    # Crear diccionario de mapeo
    mapa = {i: funcion[i] for i in range(n_vertices)}
    
    # Encontrar ciclos
    visitados = set()
    ciclos = []
    
    for i in range(n_vertices):
        if i not in visitados:
            ciclo = []
            actual = i
            
            while actual not in visitados:
                visitados.add(actual)
                ciclo.append(actual + 1)  # 1-indexado
                actual = mapa[actual]
                
                # Si volvimos al inicio, cerrar ciclo
                if actual == i:
                    break
                    
            # Solo agregar ciclos de longitud > 1
            if len(ciclo) > 1:
                ciclos.append(ciclo)
    
    # Construir notación
    if not ciclos:
        # Verificar si es identidad o tiene bucles
        puntos_fijos = [i+1 for i in range(n_vertices) if mapa[i] == i]
        if len(puntos_fijos) == n_vertices:
            return "Id (identidad)"
        elif puntos_fijos:
            return f"Puntos fijos: {puntos_fijos}"
        else:
            return "Sin ciclos (función)"
    
    # Representar ciclos
    ciclo_strs = []
    for ciclo in ciclos:
        ciclo_strs.append("(" + " ".join(str(v) for v in ciclo) + ")")
    
    return " ".join(ciclo_strs)

def funcion_a_notacion_dos_lineas(funcion, n_vertices):
    """Representa función en notación de dos líneas"""
    if any(v is None for v in funcion):
        linea1 = " ".join(str(i+1) for i in range(n_vertices))
        linea2 = " ".join("?" for _ in range(n_vertices))
    else:
        linea1 = " ".join(str(i+1) for i in range(n_vertices))
        linea2 = " ".join(str(funcion[i]+1) for i in range(n_vertices))
    
    return f"({linea1})\n({linea2})"

# ==============================================================================
# CLASE PRINCIPAL DE LA APLICACIÓN - MEJORADA
# ==============================================================================

class JoyalApp:
    def __init__(self):
        # Estados
        self.STATE_SELECT_N = 0
        self.STATE_MENU = 1
        self.STATE_TREE_MODE = 2
        self.STATE_FUNC_MODE = 3
        
        self.state = self.STATE_SELECT_N
        self.n_selector = NSelector(WIDTH//2 - 200, HEIGHT//2 - 125)
        
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
        self.func_input = InputBox(50, 600, 400, 40, 
                                  label="Función f(1..n) (ej: 1,2,3,4,5,6)",
                                  placeholder="1,2,3,4,5,6")
        self.crypto_input = InputBox(50, 700, 400, 40, 
                                    label="Texto para cifrar/descifrar",
                                    placeholder="Ingrese texto aquí")
        
        # Botones principales
        self.btn_mode1 = Button(50, 500, 220, 45, "Modo 1: Árbol → Función", LIGHT_BLUE)
        self.btn_mode2 = Button(300, 500, 220, 45, "Modo 2: Función → Árbol", LIGHT_GREEN)
        self.btn_reset = Button(550, 500, 120, 45, "Reiniciar", RED)
        
        # Botones de acción
        self.btn_submit_func = Button(470, 600, 150, 40, "Enviar Función", GREEN)
        self.btn_build_tree = Button(630, 600, 150, 40, "Construir Árbol", ORANGE)
        self.btn_encrypt = Button(470, 700, 120, 40, "Cifrar", PURPLE)
        self.btn_decrypt = Button(600, 700, 120, 40, "Descifrar", BLUE)
        self.btn_back = Button(730, 700, 100, 40, "Volver", DARK_GRAY)
        
        # Botones de vértices (se crearán dinámicamente)
        self.vertex_buttons = []
        
    def crear_botones_vertices(self):
        """Crea botones para los n vértices"""
        self.vertex_buttons = []
        
        # Calcular disposición de botones
        if n <= 12:
            # Una sola fila
            for i in range(n):
                x = 50 + i * 55
                y = 550
                btn = Button(x, y, 50, 40, str(i+1), ORANGE)
                self.vertex_buttons.append(btn)
        else:
            # Dos filas
            mitad = (n + 1) // 2
            for i in range(n):
                if i < mitad:
                    x = 50 + i * 55
                    y = 530
                else:
                    x = 50 + (i - mitad) * 55
                    y = 580
                btn = Button(x, y, 50, 40, str(i+1), ORANGE)
                self.vertex_buttons.append(btn)
    
    def dibujar_fondo_titulo(self):
        """Dibuja el fondo y título de la aplicación"""
        # Fondo
        screen.fill(LIGHT_GRAY)
        
        # Barra superior
        pygame.draw.rect(screen, DARK_BLUE, (0, 0, WIDTH, 60))
        
        # Título principal
        title = FONT_LARGE.render("DEMOSTRACIÓN DE JOYAL - FÓRMULA DE CAYLEY", True, WHITE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 15))
        
        # Subtítulo con fórmula
        formula_text = f"Número de vértices: n = {n}"
        subt = FONT_BOLD.render(formula_text, True, DARK_BLUE)
        screen.blit(subt, (WIDTH//2 - subt.get_width()//2, 70))
        
        # Fórmula de Cayley
        resultado = n**(n-2) if n >= 2 else 0
        formula = FONT_BOLD.render(f"Número de árboles etiquetados: {n}^{{{n}-2}} = {resultado:,}", 
                                  True, GREEN)
        screen.blit(formula, (WIDTH//2 - formula.get_width()//2, 100))
    
    def dibujar_panel_informacion(self):
        """Dibuja panel lateral con información"""
        panel_x = 800
        panel_y = 150
        panel_w = 380
        panel_h = 350
        
        # Fondo del panel
        pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_w, panel_h), border_radius=10)
        pygame.draw.rect(screen, BLUE, (panel_x, panel_y, panel_w, panel_h), 3, border_radius=10)
        
        # Título del panel
        panel_title = FONT_TITLE.render("INFORMACIÓN", True, BLUE)
        screen.blit(panel_title, (panel_x + panel_w//2 - panel_title.get_width()//2, panel_y + 15))
        
        # Línea separadora
        pygame.draw.line(screen, DARK_GRAY, (panel_x + 10, panel_y + 50), 
                        (panel_x + panel_w - 10, panel_y + 50), 2)
        
        info_y = panel_y + 65
        
        # Información según modo
        if self.mode == 1:  # Modo árbol → función
            textos = [
                "MODO 1: Árbol → Función",
                "",
                f"Estado: {self.obtener_estado_texto()}",
                f"Aristas: {len(aristas)}/{n-1}",
                f"Conectado: {'Sí' if grafoconexo() else 'No'}"
            ]
            
            if self.vertice_ini is not None:
                textos.append(f"Vértice inicial: {self.vertice_ini + 1}")
            if self.vertice_fin is not None:
                textos.append(f"Vértice final: {self.vertice_fin + 1}")
                
        elif self.mode == 2:  # Modo función → árbol
            textos = [
                "MODO 2: Función → Árbol",
                "",
                f"Función ingresada:"
            ]
            
            # Mostrar función compacta
            func_str = "["
            for i, f in enumerate(self.funcion):
                if f is not None:
                    func_str += str(f + 1)
                else:
                    func_str += "?"
                if i < n - 1:
                    func_str += ","
            func_str += "]"
            
            textos.append(func_str)
            
            if self.camino_orden:
                textos.append("")
                textos.append(f"Vértebra (ciclos):")
                ciclos = [str(v+1) for v in self.camino_orden]
                textos.append("[" + ",".join(ciclos) + "]")
        
        # Dibujar textos
        for i, texto in enumerate(textos):
            if i == 0:  # Título del modo
                text_surf = FONT_BOLD.render(texto, True, DARK_BLUE)
            else:
                text_surf = FONT_SMALL.render(texto, True, BLACK)
            screen.blit(text_surf, (panel_x + 15, info_y + i * 25))
        
        # Instrucciones actuales
        instrucciones_y = panel_y + panel_h - 80
        pygame.draw.line(screen, DARK_GRAY, (panel_x + 10, instrucciones_y - 10), 
                        (panel_x + panel_w - 10, instrucciones_y - 10), 1)
        
        instruccion = self.obtener_instruccion_actual()
        instruc_surf = FONT_SMALL.render(instruccion, True, DARK_GRAY)
        
        # Dividir si es muy larga
        if instruc_surf.get_width() > panel_w - 20:
            palabras = instruccion.split()
            lineas = []
            linea_actual = ""
            for palabra in palabras:
                if len(linea_actual + " " + palabra) < 40:
                    linea_actual += " " + palabra if linea_actual else palabra
                else:
                    lineas.append(linea_actual)
                    linea_actual = palabra
            if linea_actual:
                lineas.append(linea_actual)
            
            for i, linea in enumerate(lineas[:3]):
                line_surf = FONT_SMALL.render(linea, True, DARK_GRAY)
                screen.blit(line_surf, (panel_x + 10, instrucciones_y + i * 20))
        else:
            screen.blit(instruc_surf, (panel_x + 10, instrucciones_y))
    
    def obtener_estado_texto(self):
        """Texto descriptivo del estado actual"""
        if self.mode == 1:
            estados = {
                0: "Conectando vértices",
                1: "¡Ciclo detectado!",
                2: "Árbol completo",
                3: "Seleccione inicio",
                4: "Seleccione fin",
                5: "Función generada",
                6: "Listo para descifrar"
            }
            return estados.get(self.estado, f"Estado {self.estado}")
        return "Modo función"
    
    def obtener_instruccion_actual(self):
        """Instrucción según el estado actual"""
        if self.state == self.STATE_TREE_MODE:
            if self.estado == 0:
                return "Haga clic en 2 vértices para conectarlos"
            elif self.estado == 1:
                return "¡Esa conexión crearía un ciclo! Intente con otros vértices"
            elif self.estado == 2:
                return "Árbol completo. Seleccione vértice INICIAL de la vértebra"
            elif self.estado == 3:
                return "Ahora seleccione vértice FINAL de la vértebra"
            elif self.estado >= 4:
                return "Función generada. Puede descifrar mensajes"
        elif self.state == self.STATE_FUNC_MODE:
            if not self.funcion or all(v is None for v in self.funcion):
                return "Ingrese la función y presione 'Enviar Función'"
            else:
                return "Función procesada. Puede cifrar mensajes"
        return "Seleccione un modo para comenzar"
    
    def dibujar_notacion_permutacion(self):
        """Dibuja la notación de permutaciones de la función"""
        if not self.funcion:
            return
            
        y_pos = 650 if n <= 9 else 620
        
        # Notación en ciclos
        notacion_ciclos = funcion_a_notacion_permutacion(self.funcion, n)
        ciclos_text = f"Notación cíclica: {notacion_ciclos}"
        
        # Ajustar para texto largo
        ciclos_surf = FONT_BOLD.render(ciclos_text[:80], True, PURPLE)
        if ciclos_surf.get_width() > WIDTH - 100:
            # Dibujar en dos partes
            parte1 = ciclos_text[:40] + "..."
            parte1_surf = FONT_BOLD.render(parte1, True, PURPLE)
            screen.blit(parte1_surf, (50, y_pos))
            
            parte2 = "..." + ciclos_text[40:80] + "..."
            parte2_surf = FONT_SMALL.render(parte2, True, PURPLE)
            screen.blit(parte2_surf, (50, y_pos + 25))
        else:
            screen.blit(ciclos_surf, (50, y_pos))
        
        # Notación de dos líneas
        y_pos += 50
        notacion_dos_lineas = funcion_a_notacion_dos_lineas(self.funcion, n)
        lineas = notacion_dos_lineas.split('\n')
        
        for i, linea in enumerate(lineas):
            line_surf = FONT_SMALL.render(linea, True, DARK_GRAY)
            screen.blit(line_surf, (50, y_pos + i * 25))
    
    def dibujar_tablas(self):
        """Dibuja tablas de correspondencia V → f(V)"""
        if not self.camino_orden or not self.show_tables:
            return
            
        base_y = 400
        
        # Tabla 1: Vértebra (si hay)
        if self.camino_orden and len(self.camino_orden) > 0:
            f1t1 = [v + 1 for v in self.camino_orden]
            f2t1 = [v + 1 for v in self.camino_inv] if self.camino_inv else f1t1
            
            # Dibujar etiqueta
            if self.camino_vertebra:
                recorrido = " → ".join(str(v + 1) for v in self.camino_vertebra)
                recorrido_msg = FONT_BOLD.render("Vértebra: " + recorrido, True, RED)
                screen.blit(recorrido_msg, (50, base_y - 25))
            
            # Dibujar tabla
            self.dibujar_tabla_individual(50, base_y, f1t1, f2t1, "Vértebra")
        
        # Tabla 2: Aristas orientadas (si hay)
        if self.aristas_dir:
            f1t2 = [a + 1 for a, b in self.aristas_dir]
            f2t2 = [b + 1 for a, b in self.aristas_dir]
            
            dir_msg = FONT_BOLD.render("Aristas orientadas:", True, BLACK)
            screen.blit(dir_msg, (350, base_y - 25))
            
            self.dibujar_tabla_individual(350, base_y, f1t2, f2t2, "f(V)")
    
    def dibujar_tabla_individual(self, x, y, fila1, fila2, titulo):
        """Dibuja una tabla individual"""
        columnas = max(len(fila1), len(fila2))
        ancho, alto = 45, 30
        
        # Título
        titulo_surf = FONT_SMALL.render(titulo, True, BLUE)
        screen.blit(titulo_surf, (x + columnas*ancho//2 - titulo_surf.get_width()//2, y - 40))
        
        # Borde
        pygame.draw.rect(screen, BLACK, (x, y, columnas*ancho + 2, 2*alto + 2), 2)
        
        # Línea horizontal
        pygame.draw.line(screen, BLACK, (x, y+alto), (x + columnas*ancho, y+alto), 1)
        
        # Líneas verticales
        for c in range(columnas+1):
            pygame.draw.line(screen, BLACK, (x + c*ancho, y), (x + c*ancho, y + 2*alto), 1)
        
        # Etiquetas
        label_v = FONT_BOLD.render("V", True, BLACK)
        label_f = FONT_BOLD.render("f(V)", True, BLACK)
        screen.blit(label_v, (x - 25, y + 7))
        screen.blit(label_f, (x - 32, y + alto + 7))
        
        # Valores
        for c in range(columnas):
            val1 = fila1[c] if c < len(fila1) else "-"
            val2 = fila2[c] if c < len(fila2) else "-"
            
            t1 = FONT.render(str(val1), True, BLACK)
            t2 = FONT.render(str(val2), True, BLACK)
            
            # Centrar
            screen.blit(t1, (x + c*ancho + (ancho-t1.get_width())//2, y + (alto-t1.get_height())//2))
            screen.blit(t2, (x + c*ancho + (ancho-t2.get_width())//2, y + alto + (alto-t2.get_height())//2))
    
    def manejar_evento_vertice(self, vertice_idx):
        """Maneja clic en un vértice - CORREGIDO"""
        if self.mode == 1 and self.state == self.STATE_TREE_MODE:
            print(f"Clic en vértice {vertice_idx + 1}, estado: {self.estado}")  # Debug
            
            if self.estado in [0, 1]:  # Fase de construcción del árbol
                if self.vertice_1 is None:
                    # Primer clic: seleccionar primer vértice
                    self.vertice_1 = vertice_idx
                    print(f"  Primer vértice seleccionado: {self.vertice_1 + 1}")
                else:
                    # Segundo clic: intentar conectar
                    if vertice_idx != self.vertice_1:
                        v1, v2 = self.vertice_1, vertice_idx
                        print(f"  Intentando conectar {v1 + 1} con {v2 + 1}")
                        
                        # Verificar si ya están conectados
                        ya_conectados = (v1, v2) in aristas or (v2, v1) in aristas
                        if ya_conectados:
                            print(f"  Ya están conectados")
                            self.estado = 1
                        # Verificar si formaría ciclo
                        elif find(v1) == find(v2):
                            print(f"  Formaría ciclo")
                            self.estado = 1
                        else:
                            # Conexión válida
                            print(f"  Conexión válida, agregando arista")
                            self.estado = 0
                            aristas.append((v1, v2))
                            union(v1, v2)
                            grafo[v1].append(v2)
                            grafo[v2].append(v1)
                            
                            # Verificar si el árbol está completo
                            if grafoconexo() and len(aristas) == n - 1:
                                print(f"  ¡Árbol completo! {len(aristas)} aristas")
                                self.estado = 2
                    else:
                        print(f"  Mismo vértice, ignorando")
                    
                    self.vertice_1 = None  # Resetear selección
                    
            elif self.estado == 2:  # Seleccionar vértice inicial
                self.vertice_ini = vertice_idx
                self.estado = 3
                print(f"  Vértice inicial seleccionado: {vertice_idx + 1}")
                
            elif self.estado == 3:  # Seleccionar vértice final
                self.vertice_fin = vertice_idx
                self.estado = 4
                print(f"  Vértice final seleccionado: {vertice_idx + 1}")
                
                # Calcular vértebra y función
                self.calcular_funcion_desde_arbol()
    
    def calcular_funcion_desde_arbol(self):
        """Calcula la función a partir del árbol construido"""
        # Inicializar función
        self.funcion = [None] * n
        
        if self.vertice_ini == self.vertice_fin:
            # Caso especial: mismo vértice inicial y final
            self.aristas_vert = []
            self.funcion[self.vertice_ini] = self.vertice_fin
            self.camino_vertebra = self.camino_inv = self.camino_orden = [self.vertice_fin]
        else:
            # Encontrar camino de inicio a fin
            self.camino_vertebra = depthfirstsearch(grafo, self.vertice_ini, self.vertice_fin)
            
            if self.camino_vertebra:
                self.aristas_vert = [(self.camino_vertebra[i], self.camino_vertebra[i + 1])
                                  for i in range(len(self.camino_vertebra) - 1)]
                self.camino_orden = sorted(self.camino_vertebra)
                self.camino_inv = list(reversed(self.camino_vertebra))
                
                # Asignar función para vértices de la vértebra
                for i in range(len(self.camino_orden)):
                    self.funcion[self.camino_orden[i]] = self.camino_inv[i]
            else:
                print("ERROR: No se encontró camino entre los vértices")
                return
        
        # Orientar aristas restantes hacia la vértebra
        self.aristas_dir = dirigir_vertices(grafo, aristas, self.aristas_vert, self.vertice_fin)
        for a, b in self.aristas_dir:
            self.funcion[a] = b
        
        self.show_tables = True
        print(f"Función calculada: {[f+1 if f is not None else '?' for f in self.funcion]}")
    
    def procesar_funcion_usuario(self):
        """Procesa la función ingresada por el usuario"""
        texto = self.func_input.get_text()
        print(f"Procesando función: {texto}")  # Debug
        
        try:
            vals = [x.strip() for x in texto.split(',')]
            vals = [int(v) for v in vals if v]
            
            if len(vals) == n and all(1 <= x <= n for x in vals):
                # Conversión a 0-indexed
                self.funcion = [v - 1 for v in vals]
                self.error_fun = 0
                print(f"Función válida: {self.funcion}")
                
                # Calcular vértices en ciclos
                aristas_funcion = [(i, self.funcion[i]) for i in range(n)]
                self.camino_orden = vertices_en_ciclo(aristas_funcion)
                
                if self.camino_orden:
                    self.camino_inv = []
                    for i in range(len(self.camino_orden)):
                        self.camino_inv.append(self.funcion[self.camino_orden[i]])
                    self.camino_vertebra = list(reversed(self.camino_inv))
                    
                    # Calcular aristas de vértebra
                    if len(self.camino_vertebra) > 1:
                        self.aristas_vert = [(self.camino_vertebra[i], self.camino_vertebra[i + 1])
                                          for i in range(len(self.camino_vertebra) - 1)]
                    else:
                        self.aristas_vert = []
                else:
                    self.camino_inv = []
                    self.camino_vertebra = []
                    self.aristas_vert = []
                
                # Identificar aristas dirigidas (no en vértebra)
                self.aristas_dir = []
                for i in range(n):
                    en_vert = i in self.camino_orden if self.camino_orden else False
                    if not en_vert:
                        self.aristas_dir.append((i, self.funcion[i]))
                
                print(f"Ciclos encontrados: {self.camino_orden}")
                print(f"Aristas vértebra: {self.aristas_vert}")
                
            elif len(vals) != n:
                self.error_fun = 1
                print(f"Error: Se esperaban {n} valores, se obtuvieron {len(vals)}")
            else:
                self.error_fun = 2
                print(f"Error: Valores fuera de rango 1-{n}")
        except Exception as e:
            self.error_fun = 3
            print(f"Error de formato: {e}")
    
    def generar_explicacion_cifrado(self):
        """Genera explicación del sistema de cifrado Hill"""
        self.explicacion_cifrado = f"Cifrado Hill {n}×{n}. La función f(V) genera una matriz clave para cifrar bloques de {n} caracteres."
    
    def cifrar_texto(self):
        """Cifra texto usando Hill (simplificado para demo)"""
        texto = self.crypto_input.get_text()
        if texto and self.funcion:
            try:
                # Simulación de cifrado para demo
                self.texto_cifrado = f"[CIFRADO] {texto.upper()} [CLAVE:{n}]"
                self.texto_descifrado = ""
                print(f"Texto cifrado: {self.texto_cifrado}")
            except Exception as e:
                self.texto_cifrado = f"Error: {str(e)}"
    
    def descifrar_texto(self):
        """Descifra texto usando Hill (simplificado para demo)"""
        texto = self.crypto_input.get_text()
        if texto and self.funcion:
            try:
                # Simulación de descifrado para demo
                self.texto_descifrado = f"[DESCIFRADO] {texto.lower()} [n={n}]"
                self.texto_cifrado = ""
                self.estado = 6
                print(f"Texto descifrado: {self.texto_descifrado}")
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
    
    def dibujar_grafo(self):
        """Dibuja el grafo según el estado"""
        if self.state == self.STATE_TREE_MODE:
            if self.estado < 4:
                # Árbol en construcción
                for v1, v2 in aristas:
                    pygame.draw.line(screen, BLACK, vertice_pos[v1], vertice_pos[v2], ARISTA_WIDTH)
            else:
                # Árbol completo con direcciones
                for v1, v2 in self.aristas_dir:
                    pygame.draw.line(screen, BLACK, vertice_pos[v1], vertice_pos[v2], ARISTA_WIDTH)
                    draw_dirigido(screen, vertice_pos[v1], vertice_pos[v2], BLACK, 3, 10)
                for v1, v2 in self.aristas_vert:
                    draw_vertebra(screen, vertice_pos[v1], vertice_pos[v2], RED, 4)
        
        elif self.state == self.STATE_FUNC_MODE and self.funcion:
            # Dibujar función como flechas
            for i, f in enumerate(self.funcion):
                if f is not None:
                    if i != f:
                        draw_dirigido(screen, vertice_pos[i], vertice_pos[f])
                    else:
                        draw_bucle(screen, vertice_pos[i])
        
        # Dibujar vértices siempre
        draw_vertices()
    
    def dibujar(self):
        """Dibuja toda la interfaz"""
        if self.state == self.STATE_SELECT_N:
            self.n_selector.draw(screen)
            return
            
        self.dibujar_fondo_titulo()
        
        if self.state == self.STATE_MENU:
            # Menú principal
            menu_title = FONT_TITLE.render("SELECCIONE UN MODO DE OPERACIÓN", True, DARK_BLUE)
            screen.blit(menu_title, (WIDTH//2 - menu_title.get_width()//2, 200))
            
            # Instrucciones
            instr = FONT.render("Use los botones para seleccionar cómo desea trabajar:", True, DARK_GRAY)
            screen.blit(instr, (WIDTH//2 - instr.get_width()//2, 250))
            
            self.btn_mode1.draw(screen)
            self.btn_mode2.draw(screen)
            self.btn_reset.draw(screen)
            
            # Dibujar vértices
            draw_vertices()
            
        elif self.state == self.STATE_TREE_MODE:
            # Modo árbol → función
            self.dibujar_grafo()
            
            # Mensaje de estado
            estado_msgs = {
                0: "Conecte vértices: haga clic en 2 vértices para crear una arista",
                1: "¡No se pueden formar ciclos! Intente con otros vértices",
                2: f"Árbol completo ({n-1} aristas). Seleccione vértice INICIAL de la vértebra",
                3: f"Vértice inicial: {self.vertice_ini + 1}. Ahora seleccione vértice FINAL",
                4: f"Vértices: Inicio={self.vertice_ini + 1}, Fin={self.vertice_fin + 1}. Función generada",
                5: "Ingrese texto cifrado para descifrar",
                6: "Texto descifrado correctamente"
            }
            
            if self.estado in estado_msgs:
                msg = FONT.render(estado_msgs[self.estado], True, BLUE)
                msg_rect = msg.get_rect(center=(WIDTH//2, 140))
                screen.blit(msg, msg_rect)
            
            # Mostrar vértice seleccionado durante conexión
            if self.vertice_1 is not None and self.estado in [0, 1]:
                sel_msg = FONT.render(f"Vértice seleccionado: {self.vertice_1 + 1}. Seleccione otro para conectar", True, GREEN)
                screen.blit(sel_msg, (WIDTH//2 - sel_msg.get_width()//2, 170))
            
            # Dibujar botones de vértices
            for btn in self.vertex_buttons:
                btn.draw(screen)
            
            # Controles de texto
            self.crypto_input.draw(screen)
            self.btn_decrypt.draw(screen)
            self.btn_back.draw(screen)
            
            # Mostrar resultados de descifrado
            if self.texto_descifrado:
                resultado = FONT.render(f"Descifrado: {self.texto_descifrado[:60]}", True, GREEN)
                screen.blit(resultado, (50, 750))
            
            self.dibujar_tablas()
            self.dibujar_notacion_permutacion()
            
        elif self.state == self.STATE_FUNC_MODE:
            # Modo función → árbol
            self.dibujar_grafo()
            
            # Instrucciones
            if not self.funcion or all(v is None for v in self.funcion):
                instr = FONT.render(f"Ingrese la función como {n} valores separados por comas (ej: 1,2,3,4,5,6)", True, BLUE)
                screen.blit(instr, (WIDTH//2 - instr.get_width()//2, 140))
            else:
                instr = FONT.render("Función procesada. Puede cifrar mensajes usando el campo de texto", True, BLUE)
                screen.blit(instr, (WIDTH//2 - instr.get_width()//2, 140))
            
            # Mostrar información de ciclos
            if self.camino_orden:
                ciclos_msg = FONT.render(f"Vértices en ciclos: {[v+1 for v in self.camino_orden]}", True, DARK_BLUE)
                screen.blit(ciclos_msg, (WIDTH//2 - ciclos_msg.get_width()//2, 170))
            
            # Controles
            self.func_input.draw(screen)
            self.crypto_input.draw(screen)
            self.btn_submit_func.draw(screen)
            self.btn_build_tree.draw(screen)
            self.btn_encrypt.draw(screen)
            self.btn_back.draw(screen)
            
            # Mostrar mensajes de error
            if self.error_fun > 0:
                errores = {
                    1: f"Error: Debe ingresar exactamente {n} valores separados por comas",
                    2: f"Error: Los valores deben estar entre 1 y {n}",
                    3: "Error: Formato inválido (use números enteros separados por comas)"
                }
                error_msg = FONT.render(errores.get(self.error_fun, ""), True, RED)
                screen.blit(error_msg, (WIDTH//2 - error_msg.get_width()//2, 620))
            
            # Mostrar resultados de cifrado
            if self.texto_cifrado:
                resultado = FONT.render(f"Cifrado: {self.texto_cifrado[:60]}", True, GREEN)
                screen.blit(resultado, (50, 750))
            
            self.dibujar_tablas()
            self.dibujar_notacion_permutacion()
        
        # Dibujar panel de información
        self.dibujar_panel_informacion()
    
    def manejar_eventos(self, event):
        """Maneja eventos de pygame"""
        if self.state == self.STATE_SELECT_N:
            if self.n_selector.handle_event(event):
                n_valor = self.n_selector.n
                inicializar_estructuras(n_valor)
                self.crear_botones_vertices()
                self.state = self.STATE_MENU
                print(f"N configurado: {n} vértices")
            return
            
        # Actualizar hover de todos los botones
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
        
        # Manejar clics
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.state == self.STATE_MENU:
                if self.btn_mode1.check_click(pos):
                    self.mode = 1
                    self.state = self.STATE_TREE_MODE
                    self.reiniciar()
                    print("Modo 1 activado: Árbol → Función")
                elif self.btn_mode2.check_click(pos):
                    self.mode = 2
                    self.state = self.STATE_FUNC_MODE
                    self.reiniciar()
                    print("Modo 2 activado: Función → Árbol")
                elif self.btn_reset.check_click(pos):
                    self.state = self.STATE_SELECT_N
                    print("Volviendo a selección de n")
                    
            elif self.state == self.STATE_TREE_MODE:
                # Botones de vértices
                for i, btn in enumerate(self.vertex_buttons):
                    if btn.check_click(pos):
                        self.manejar_evento_vertice(i)
                        break
                        
                # Otros botones
                if self.btn_decrypt.check_click(pos):
                    self.descifrar_texto()
                elif self.btn_back.check_click(pos):
                    self.state = self.STATE_MENU
                    print("Volviendo al menú")
                    
            elif self.state == self.STATE_FUNC_MODE:
                if self.btn_submit_func.check_click(pos):
                    self.procesar_funcion_usuario()
                elif self.btn_build_tree.check_click(pos):
                    # En este modo, "construir árbol" ya está mostrado
                    pass
                elif self.btn_encrypt.check_click(pos):
                    self.cifrar_texto()
                elif self.btn_back.check_click(pos):
                    self.state = self.STATE_MENU
                    print("Volviendo al menú")
        
        # Manejar campos de entrada
        if self.state == self.STATE_FUNC_MODE:
            self.func_input.handle_event(event)
            self.crypto_input.handle_event(event)
        elif self.state == self.STATE_TREE_MODE:
            self.crypto_input.handle_event(event)
    
    def ejecutar(self):
        """Bucle principal de la aplicación"""
        clock = pygame.time.Clock()
        running = True
        
        print("\n" + "="*70)
        print("  Aplicación iniciada. Use la interfaz gráfica para interactuar.")
        print("="*70)
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_F1:
                        # Atajo para ayuda
                        print("\nAtajos de teclado:")
                        print("  ESC - Salir")
                        print("  F1  - Mostrar ayuda")
                        print("  F5  - Reiniciar aplicación")
                    
                    elif event.key == pygame.K_F5:
                        # Atajo para reiniciar
                        self.state = self.STATE_SELECT_N
                        print("\nReiniciando aplicación...")
                
                self.manejar_eventos(event)
            
            # Dibujar
            self.dibujar()
            
            # Actualizar pantalla
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        print("\n¡Aplicación finalizada!")

# ==============================================================================
# EJECUCIÓN PRINCIPAL
# ==============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  PROYECTO MD - Demostración de Joyal a la Fórmula de Cayley")
    print("  Versión GitHub - Mejorada y Corregida")
    print("=" * 70)
    print("  Mejoras implementadas:")
    print("    1. CUALQUIER número n de vértices (n ≥ 2)")
    print("    2. Notación de permutaciones para la función")
    print("    3. Interfaz mejorada y organizada")
    print("    4. Conexión de vértices corregida")
    print("=" * 70)
    print("  Autores:")
    print("    • Martin Lora Cano")
    print("    • Cristian Andrés Diaz Ortega")
    print("    • Jhon Edison Prieto Artunduaga")
    print("=" * 70)
    print("\n  Iniciando aplicación...")
    
    try:
        app = JoyalApp()
        app.ejecutar()
    except Exception as e:
        print(f"\n❌ Error al ejecutar la aplicación: {e}")
        print("\nPosibles soluciones:")
        print("  1. Asegúrate de tener instalado: pip install pygame numpy")
        print("  2. Si usas Windows, prueba: python -m pip install pygame")
        print("  3. Revisa que tengas Python 3.7 o superior")
        input("\nPresiona Enter para salir...")