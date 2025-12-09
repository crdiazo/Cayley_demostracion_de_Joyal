# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                                                                            ║
# ║     PROYECTO MD - Demostración de Joyal a la Fórmula de Cayley             ║
# ║                                                                            ║
# ║     Versión GitHub - Mejorada según requerimientos                         ║
# ║                                                                            ║
# ╠════════════════════════════════════════════════════════════════════════════╣
# ║                                                                            ║
# ║     MEJORAS IMPLEMENTADAS:                                                 ║
# ║         1. Elegir número n de vértices (3-15)                              ║
# ║         2. Notación de permutaciones para la función                       ║
# ║         3. Mejor explicación del cifrado Hill                              ║
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
# ║         2. Usar los botones de la interfaz gráfica                         ║
# ║         3. Seleccionar primero el número de vértices                       ║
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

# Dimensiones de la ventana
WIDTH, HEIGHT = 1000, 800

# Crear la ventana
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Proyecto MD - Demostración de Joyal a la Fórmula de Cayley")

# Fuentes
FONT = pygame.font.SysFont(None, 30)
FONT_BOLD = pygame.font.SysFont(None, 28, bold=True)
FONT_SMALL = pygame.font.SysFont(None, 24)
FONT_TITLE = pygame.font.SysFont(None, 36, bold=True)

# Colores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 180, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
LIGHT_GRAY = (230, 230, 230)
DARK_GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# ==============================================================================
# CLASE PARA BOTONES
# ==============================================================================

class Button:
    def __init__(self, x, y, width, height, text, color=LIGHT_BLUE, hover_color=(200, 220, 255)):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.clicked = False
        
    def draw(self, surface):
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=8)
        pygame.draw.rect(surface, DARK_GRAY, self.rect, 2, border_radius=8)
        
        # Renderizar texto centrado
        text_surf = FONT.render(self.text, True, BLACK)
        text_rect = text_surf.get_rect(center=self.rect.center)
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
            return True
        return False

# ==============================================================================
# CLASE PARA CAMPOS DE TEXTO
# ==============================================================================

class InputBox:
    def __init__(self, x, y, width, height, text='', label=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.label = label
        self.active = False
        self.max_length = 100
        
    def draw(self, surface):
        # Dibujar label
        if self.label:
            label_surf = FONT_SMALL.render(self.label, True, BLACK)
            surface.blit(label_surf, (self.rect.x, self.rect.y - 25))
            
        # Dibujar caja
        color = BLUE if self.active else DARK_GRAY
        pygame.draw.rect(surface, WHITE, self.rect)
        pygame.draw.rect(surface, color, self.rect, 2)
        
        # Dibujar texto
        text_surf = FONT.render(self.text, True, BLACK)
        surface.blit(text_surf, (self.rect.x + 5, self.rect.y + 5))
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
            
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    return True
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    if len(self.text) < self.max_length:
                        self.text += event.unicode
        return False
        
    def get_text(self):
        return self.text.strip()

# ==============================================================================
# CLASE PARA SELECTOR DE N
# ==============================================================================

class NSelector:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 300, 200)
        self.n = 9  # Valor por defecto
        self.selected = False
        self.buttons = []
        
        # Crear botones para n=3 a n=15
        for i in range(3, 16):
            row = (i - 3) // 5
            col = (i - 3) % 5
            btn = Button(x + col * 55, y + 50 + row * 40, 50, 35, str(i))
            self.buttons.append((btn, i))
            
        # Botón de confirmar
        self.confirm_btn = Button(x + 100, y + 150, 100, 40, "Confirmar", GREEN)
        
    def draw(self, surface):
        # Fondo
        pygame.draw.rect(surface, LIGHT_GRAY, self.rect, border_radius=10)
        pygame.draw.rect(surface, BLACK, self.rect, 2, border_radius=10)
        
        # Título
        title = FONT_TITLE.render("Seleccionar número de vértices (n)", True, BLUE)
        surface.blit(title, (self.rect.x + 10, self.rect.y + 10))
        
        # Instrucción
        instr = FONT_SMALL.render("Seleccione n entre 3 y 15:", True, BLACK)
        surface.blit(instr, (self.rect.x + 10, self.rect.y + 35))
        
        # Dibujar botones
        for btn, n in self.buttons:
            if n == self.n:
                btn.color = YELLOW
            else:
                btn.color = LIGHT_BLUE
            btn.draw(surface)
            
        # Botón confirmar
        self.confirm_btn.draw(surface)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            # Verificar botones de n
            for btn, n in self.buttons:
                if btn.check_click(pos):
                    self.n = n
                    
            # Verificar botón confirmar
            if self.confirm_btn.check_click(pos):
                self.selected = True
                return True
        return False

# ==============================================================================
# FUNCIONES MATEMÁTICAS Y DE GRAFOS
# ==============================================================================

# Variables globales que se configurarán dinámicamente
n = 9
vertice_pos = []
vertice_rad = 20
aristas = []
grafo = []
parent = []

def calcular_posiciones_vertices(n_vertices):
    """Calcula posiciones para n vértices en un círculo"""
    global vertice_pos
    vertice_pos = []
    centro_x, centro_y = WIDTH // 2, 350
    radio = 200
    
    for i in range(n_vertices):
        angulo = 2 * math.pi * i / n_vertices
        x = centro_x + radio * math.sin(angulo)
        y = centro_y - radio * math.cos(angulo)
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
    """Dibuja todos los vértices"""
    for i, pos in enumerate(vertice_pos):
        # Círculo del vértice
        pygame.draw.circle(screen, (255, 128, 128), pos, vertice_rad)
        # Borde
        pygame.draw.circle(screen, BLACK, pos, vertice_rad, 2)
        # Número (1-indexado)
        vertice_num = FONT.render(str(i + 1), True, WHITE)
        screen.blit(vertice_num, (pos[0] - 8, pos[1] - 10))

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

def draw_vertebra(surface, color, p1, p2, ancho=4, largo_linea=12, largo_espacio=8):
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

def draw_bucle(surface, pos, radius=20, color=BLACK, width=3):
    """Dibuja un bucle (arista de un vértice a sí mismo)"""
    x, y = pos
    centro = (x + 6, y - radius + 2)
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
    grafo_local = {}
    for u, v in aristas_dir:
        grafo_local.setdefault(u, []).append(v)
        grafo_local.setdefault(v, [])
        
    vertices_cic = set()
    
    for u, vecinos in grafo_local.items():
        for v in vecinos:
            # Remover temporalmente la arista
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
# SISTEMA DE ENCRIPTACIÓN HILL MEJORADO
# ==============================================================================

# Alfabeto extendido: A-Z, Ñ, , . espacio
ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZÑ,. '
CHAR_TO_NUM = {ch: i for i, ch in enumerate(ALPHABET)}
NUM_TO_CHAR = {i: ch for i, ch in enumerate(ALPHABET)}
MOD = len(ALPHABET)  # 30

def char_a_num(ch):
    """Convierte carácter a número"""
    ch = ch.upper()
    return CHAR_TO_NUM.get(ch, CHAR_TO_NUM[' '])

def num_a_char(n):
    """Convierte número a carácter"""
    n = n % MOD
    return NUM_TO_CHAR.get(n, ' ')

def determinante_bareiss(mat):
    """Calcula determinante con algoritmo de Bareiss (enteros)"""
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
            # Matriz menor
            minor = [[M[r][c] for c in range(n) if c != j] 
                    for r in range(n) if r != i]
            det_minor = determinante_bareiss(minor)
            cofactor = ((-1) ** (i + j)) * det_minor
            adj[j][i] = cofactor % MOD  # Transpuesta
            
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
    
    # Calcular determinante
    detM = determinante_bareiss(M)
    det_mod = detM % MOD
    
    # Verificar si es invertible
    g, x, y = egcd(det_mod, MOD)
    if g != 1:
        return None  # No invertible
        
    det_inv = x % MOD
    
    # Calcular adjunta
    adj = matriz_adjunta(M, MOD)
    
    # Inversa = det^(-1) * adjunta
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
    # Limpiar función
    clean = [(0 if v is None else int(v)) for v in funcion]
    func = [clean[i % len(clean)] for i in range(n_vertices)]
    
    # Construir matriz inicial
    arr = []
    for i in range(n_vertices):
        row = []
        for j in range(n_vertices):
            row.append((func[i] * (j + 1) + (func[j] + 1)) % MOD)
        arr.append(row)
    
    mat = np.array(arr, dtype=int)
    
    # Si es invertible, usarla
    if es_invertible_mod(mat, MOD):
        return mat
    
    # Si no, crear matriz diagonal con valores coprimos
    I = np.eye(n_vertices, dtype=int)
    for i in range(n_vertices):
        v = 3 * (func[i] + 1) + 1
        v %= MOD
        # Asegurar coprimo con 30
        while math.gcd(v, MOD) != 1:
            v = (v + 1) % MOD
        I[i][i] = v
        
    return I

def cifrar_hill(texto, clave):
    """Cifra texto usando cifrado Hill"""
    # Convertir a números
    nums = [char_a_num(ch) for ch in texto]
    n_size = len(clave)
    
    # Rellenar si es necesario
    while len(nums) % n_size != 0:
        nums.append(char_a_num(' '))
    
    # Cifrar por bloques
    cifrado = []
    for i in range(0, len(nums), n_size):
        bloque = nums[i:i + n_size]
        cifrado_bloque = multiplicar_matriz_vector(clave, bloque, MOD)
        cifrado.extend(cifrado_bloque)
    
    # Convertir a texto
    return ''.join(num_a_char(n) for n in cifrado)

def descifrar_hill(texto_cifrado, clave):
    """Descifra texto usando cifrado Hill"""
    # Convertir a números
    nums = [char_a_num(ch) for ch in texto_cifrado]
    n_size = len(clave)
    
    # Obtener inversa de la clave
    clave_inv = inversa_modular_matriz(clave, MOD)
    if clave_inv is None:
        raise ValueError("Clave no invertible")
    
    # Descifrar por bloques
    descifrado = []
    for i in range(0, len(nums), n_size):
        bloque = nums[i:i + n_size]
        descifrado_bloque = multiplicar_matriz_vector(clave_inv, bloque, MOD)
        descifrado.extend(descifrado_bloque)
    
    # Convertir a texto
    return ''.join(num_a_char(n) for n in descifrado)

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
            # Para bucles (f(v) = v), manejarlos separadamente
            elif len(ciclo) == 1 and mapa[ciclo[0]-1] == ciclo[0]-1:
                # Los bucles se manejan en la representación como (v)
                pass
    
    # Construir notación
    if not ciclos:
        return "Id (permutación identidad)"
    
    # Representar ciclos
    ciclo_strs = []
    for ciclo in ciclos:
        ciclo_strs.append("(" + " ".join(str(v) for v in ciclo) + ")")
    
    # Agregar puntos fijos (bucles)
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
        self.n_selector = NSelector(WIDTH//2 - 150, HEIGHT//2 - 100)
        
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
        self.func_input = InputBox(50, 600, 400, 35, label="Función f(1..n) (ej: 1,2,3,6,6,6,7,8,9)")
        self.crypto_input = InputBox(50, 700, 400, 35, label="Texto para cifrar/descifrar")
        
        # Botones principales
        self.btn_mode1 = Button(50, 500, 200, 40, "Modo 1: Árbol → Función")
        self.btn_mode2 = Button(270, 500, 200, 40, "Modo 2: Función → Árbol")
        self.btn_reset = Button(490, 500, 120, 40, "Reiniciar", RED)
        
        # Botones de acción
        self.btn_submit_func = Button(470, 600, 150, 35, "Enviar Función", GREEN)
        self.btn_build_tree = Button(630, 600, 150, 35, "Construir Árbol", ORANGE)
        self.btn_encrypt = Button(470, 700, 120, 35, "Cifrar", PURPLE)
        self.btn_decrypt = Button(600, 700, 120, 35, "Descifrar", BLUE)
        self.btn_back = Button(730, 700, 100, 35, "Volver", DARK_GRAY)
        
        # Botones de vértices (se crearán dinámicamente)
        self.vertex_buttons = []
        
    def crear_botones_vertices(self):
        """Crea botones para los n vértices"""
        self.vertex_buttons = []
        for i in range(n):
            # Posicionar botones en una fila en la parte inferior
            x = 50 + (i % 9) * 55
            y = 550 + (i // 9) * 45
            if n > 9:
                x = 50 + (i % 12) * 55
                y = 550 + (i // 12) * 45
            btn = Button(x, y, 50, 35, str(i+1), ORANGE)
            self.vertex_buttons.append(btn)
    
    def dibujar_fondo_titulo(self):
        """Dibuja el fondo y título de la aplicación"""
        # Fondo
        screen.fill(LIGHT_GRAY)
        
        # Título principal
        title = FONT_TITLE.render("DEMOSTRACIÓN DE JOYAL - FÓRMULA DE CAYLEY", True, BLUE)
        screen.blit(title, (WIDTH//2 - title.get_width()//2, 10))
        
        # Subtítulo
        subt = FONT_SMALL.render(f"Número de vértices: n = {n}", True, DARK_GRAY)
        screen.blit(subt, (WIDTH//2 - subt.get_width()//2, 50))
        
        # Fórmula de Cayley
        formula = FONT_BOLD.render(f"Número de árboles etiquetados con {n} vértices: {n}^{{{n}-2}} = {n**(n-2)}", 
                                  True, GREEN)
        screen.blit(formula, (WIDTH//2 - formula.get_width()//2, 80))
    
    def dibujar_panel_informacion(self):
        """Dibuja panel lateral con información"""
        panel_x = 650
        panel_y = 150
        panel_w = 320
        panel_h = 300
        
        # Fondo del panel
        pygame.draw.rect(screen, WHITE, (panel_x, panel_y, panel_w, panel_h))
        pygame.draw.rect(screen, BLUE, (panel_x, panel_y, panel_w, panel_h), 2)
        
        # Título del panel
        panel_title = FONT_BOLD.render("INFORMACIÓN", True, BLUE)
        screen.blit(panel_title, (panel_x + 10, panel_y + 10))
        
        info_y = panel_y + 40
        
        if self.mode == 1:  # Modo árbol → función
            textos = [
                "Modo 1: Árbol → Función",
                f"Estado: {self.estado}",
                f"Aristas: {len(aristas)}/{n-1}",
                f"Conectado: {'Sí' if grafoconexo() else 'No'}"
            ]
            
            if self.vertice_ini is not None:
                textos.append(f"Inicio: {self.vertice_ini + 1}")
            if self.vertice_fin is not None:
                textos.append(f"Fin: {self.vertice_fin + 1}")
                
        else:  # Modo función → árbol
            textos = [
                "Modo 2: Función → Árbol",
                f"Función: {[f+1 if f is not None else '?' for f in self.funcion]}"
            ]
            
            if self.camino_orden:
                textos.append(f"Vértebra: {[v+1 for v in self.camino_orden]}")
        
        # Dibujar textos
        for i, texto in enumerate(textos):
            text_surf = FONT_SMALL.render(texto, True, BLACK)
            screen.blit(text_surf, (panel_x + 10, info_y + i * 25))
        
        # Explicación del cifrado
        if self.explicacion_cifrado:
            crypto_y = panel_y + panel_h + 20
            crypto_h = 100
            
            pygame.draw.rect(screen, WHITE, (panel_x, crypto_y, panel_w, crypto_h))
            pygame.draw.rect(screen, GREEN, (panel_x, crypto_y, panel_w, crypto_h), 2)
            
            crypto_title = FONT_BOLD.render("CIFRADO HILL", True, GREEN)
            screen.blit(crypto_title, (panel_x + 10, crypto_y + 10))
            
            # Dividir explicación en líneas
            palabras = self.explicacion_cifrado.split()
            lineas = []
            linea_actual = ""
            
            for palabra in palabras:
                if len(linea_actual + " " + palabra) < 45:
                    linea_actual += " " + palabra if linea_actual else palabra
                else:
                    lineas.append(linea_actual)
                    linea_actual = palabra
            if linea_actual:
                lineas.append(linea_actual)
            
            for i, linea in enumerate(lineas[:4]):  # Máximo 4 líneas
                line_surf = FONT_SMALL.render(linea, True, BLACK)
                screen.blit(line_surf, (panel_x + 10, crypto_y + 35 + i * 20))
    
    def dibujar_notacion_permutacion(self):
        """Dibuja la notación de permutaciones de la función"""
        if not self.funcion or all(v is None for v in self.funcion):
            return
            
        y_pos = 650 if n <= 9 else 600
        
        # Notación en ciclos
        notacion_ciclos = funcion_a_notacion_permutacion(self.funcion, n)
        ciclos_surf = FONT_BOLD.render(f"Notación cíclica: {notacion_ciclos}", True, PURPLE)
        
        # Ajustar posición si el texto es muy largo
        if ciclos_surf.get_width() > WIDTH - 100:
            # Dibujar en múltiples líneas
            palabras = notacion_ciclos.split()
            lineas = []
            linea_actual = ""
            
            for palabra in palabras:
                if len(linea_actual + " " + palabra) < 60:
                    linea_actual += " " + palabra if linea_actual else palabra
                else:
                    lineas.append(linea_actual)
                    linea_actual = palabra
            if linea_actual:
                lineas.append(linea_actual)
            
            title_surf = FONT_BOLD.render("Notación cíclica:", True, PURPLE)
            screen.blit(title_surf, (50, y_pos))
            
            for i, linea in enumerate(lineas):
                line_surf = FONT_SMALL.render(linea, True, PURPLE)
                screen.blit(line_surf, (50, y_pos + 25 + i * 25))
        else:
            screen.blit(ciclos_surf, (WIDTH//2 - ciclos_surf.get_width()//2, y_pos))
        
        # Notación de dos líneas
        y_pos += 60 if n <= 9 else 100
        notacion_dos_lineas = funcion_a_notacion_dos_lineas(self.funcion, n)
        lineas = notacion_dos_lineas.split('\n')
        
        for i, linea in enumerate(lineas):
            line_surf = FONT_SMALL.render(linea, True, DARK_GRAY)
            screen.blit(line_surf, (WIDTH//2 - line_surf.get_width()//2, y_pos + i * 25))
    
    def dibujar_tablas(self):
        """Dibuja tablas de correspondencia V → f(V)"""
        if not self.camino_orden or not self.show_tables:
            return
            
        base_y = 400 if n <= 9 else 350
        
        # Tabla 1: Vértebra
        f1t1 = [v + 1 for v in self.camino_orden]
        f2t1 = [v + 1 for v in self.camino_inv]
        
        # Dibujar etiqueta
        recorrido = " - ".join(str(v + 1) for v in self.camino_vertebra) if self.camino_vertebra else "—"
        recorrido_msg = FONT_BOLD.render("Vértebra: " + recorrido, True, RED)
        screen.blit(recorrido_msg, (50, base_y - 25))
        
        # Dibujar tabla
        self.dibujar_tabla_individual(50, base_y, f1t1, f2t1, "Vértebra")
        
        # Tabla 2: Aristas orientadas
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
        """Maneja clic en un vértice"""
        if self.mode == 1:  # Modo árbol → función
            if not grafoconexo():
                # Fase de construcción del árbol
                if self.vertice_1 is None:
                    self.vertice_1 = vertice_idx
                else:
                    if vertice_idx != self.vertice_1:
                        v1, v2 = self.vertice_1, vertice_idx
                        if find(v1) == find(v2):
                            self.estado = 1  # Error: ciclo
                        else:
                            self.estado = 0  # OK
                            aristas.append((v1, v2))
                            union(v1, v2)
                            grafo[v1].append(v2)
                            grafo[v2].append(v1)
                    self.vertice_1 = None
                    
                    # Verificar si el árbol está completo
                    if grafoconexo() and len(aristas) == n - 1:
                        self.estado = 2
                        
            elif None in self.funcion:
                # Fase de selección de vértices inicial y final
                if self.vertice_ini is None:
                    self.vertice_ini = vertice_idx
                    self.estado = 3
                elif self.vertice_fin is None:
                    self.vertice_fin = vertice_idx
                    self.estado = 4
                    
                    # Calcular vértebra y función
                    if self.vertice_ini == self.vertice_fin:
                        # Caso especial
                        self.aristas_vert = []
                        self.funcion[self.vertice_ini] = self.vertice_fin
                        self.camino_vertebra = self.camino_inv = self.camino_orden = [self.vertice_fin]
                    else:
                        # Encontrar camino
                        self.camino_vertebra = depthfirstsearch(grafo, self.vertice_ini, self.vertice_fin)
                        self.aristas_vert = [(self.camino_vertebra[i], self.camino_vertebra[i + 1])
                                          for i in range(len(self.camino_vertebra) - 1)]
                        self.camino_orden = sorted(self.camino_vertebra)
                        self.camino_inv = list(reversed(self.camino_vertebra))
                        
                        # Asignar función para vértebra
                        for i in range(len(self.camino_orden)):
                            self.funcion[self.camino_orden[i]] = self.camino_inv[i]
                    
                    # Orientar aristas restantes
                    self.aristas_dir = dirigir_vertices(grafo, aristas, self.aristas_vert, self.vertice_fin)
                    for a, b in self.aristas_dir:
                        self.funcion[a] = b
                    
                    self.show_tables = True
                    
                    # Generar explicación del cifrado
                    self.generar_explicacion_cifrado()
    
    def procesar_funcion_usuario(self):
        """Procesa la función ingresada por el usuario"""
        texto = self.func_input.get_text()
        try:
            vals = list(map(int, texto.split(',')))
            
            if len(vals) == n and all(1 <= x <= n for x in vals):
                # Conversión a 0-indexed
                self.funcion = [v - 1 for v in vals]
                self.error_fun = 0
                
                # Calcular vértices en ciclos
                self.camino_orden = vertices_en_ciclo(list(enumerate(self.funcion)))
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
                
                # Identificar aristas dirigidas
                self.aristas_dir = []
                for i in range(n):
                    en_vert = i in self.camino_orden
                    if not en_vert:
                        self.aristas_dir.append((i, self.funcion[i]))
                
                # Generar explicación del cifrado
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
            
        # Generar matriz clave
        matriz_clave = generar_matriz_desde_funcion(self.funcion, n)
        
        explicacion = f"""
        Sistema de cifrado Hill {n}×{n}:
        • Usa la función f para generar matriz clave de {n}×{n}
        • Alfabeto: {len(ALPHABET)} caracteres (A-Z, Ñ, puntuación)
        • Matriz invertible módulo {MOD}
        • Cifra bloques de {n} caracteres
        • La seguridad depende de la invertibilidad modular
        """
        
        # Simplificar explicación
        self.explicacion_cifrado = f"Cifrado Hill {n}×{n}. Matriz clave generada desde f(V). Alfabeto de {len(ALPHABET)} caracteres."
    
    def cifrar_texto(self):
        """Cifra texto usando Hill"""
        texto = self.crypto_input.get_text()
        if texto and self.funcion:
            try:
                matriz_clave = generar_matriz_desde_funcion(self.funcion, n)
                self.texto_cifrado = cifrar_hill(texto, matriz_clave)
                self.texto_descifrado = ""
            except Exception as e:
                self.texto_cifrado = f"Error: {str(e)}"
    
    def descifrar_texto(self):
        """Descifra texto usando Hill"""
        texto = self.crypto_input.get_text()
        if texto and self.funcion:
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
    
    def dibujar(self):
        """Dibuja toda la interfaz"""
        if self.state == self.STATE_SELECT_N:
            self.n_selector.draw(screen)
            return
            
        self.dibujar_fondo_titulo()
        
        if self.state == self.STATE_MENU:
            # Menú principal
            menu_title = FONT_TITLE.render("SELECCIONE UN MODO", True, BLUE)
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
                    pygame.draw.line(screen, BLACK, vertice_pos[v1], vertice_pos[v2], 4)
                    draw_dirigido(screen, vertice_pos[v1], vertice_pos[v2], BLACK, 3, 10)
                for v1, v2 in self.aristas_vert:
                    draw_vertebra(screen, RED, vertice_pos[v1], vertice_pos[v2], 4)
            
            draw_vertices()
            
            # Mensajes de estado
            mensajes = {
                0: "Conecte vértices (click en 2 vértices para conectar)",
                1: "¡No se pueden formar ciclos! Intente otros vértices",
                2: "Árbol completo. Seleccione el vértice INICIAL de la vértebra",
                3: "Ahora seleccione el vértice FINAL de la vértebra",
                4: "Función formada. Use el campo de texto para descifrar mensajes",
                5: "Ingrese texto cifrado...",
                6: "Texto descifrado correctamente"
            }
            
            if self.estado in mensajes:
                msg = FONT.render(mensajes[self.estado], True, BLUE)
                screen.blit(msg, (WIDTH//2 - msg.get_width()//2, 120))
            
            # Mostrar vértice seleccionado
            if self.vertice_1 is not None:
                sel_msg = FONT.render(f"Vértice seleccionado: {self.vertice_1 + 1}", True, GREEN)
                screen.blit(sel_msg, (WIDTH//2 - sel_msg.get_width()//2, 150))
            
            # Dibujar botones y controles
            for btn in self.vertex_buttons:
                btn.draw(screen)
            
            self.crypto_input.draw(screen)
            self.btn_decrypt.draw(screen)
            self.btn_back.draw(screen)
            
            # Mostrar resultados de descifrado
            if self.texto_descifrado:
                resultado = FONT.render(f"Descifrado: {self.texto_descifrado[:50]}", True, GREEN)
                screen.blit(resultado, (50, 750))
            
            self.dibujar_tablas()
            self.dibujar_notacion_permutacion()
            
        elif self.state == self.STATE_FUNC_MODE:
            # Modo función → árbol
            # Dibujar función como flechas
            for i, f in enumerate(self.funcion):
                if f is not None:
                    if i != f:
                        draw_dirigido(screen, vertice_pos[i], vertice_pos[f])
                    else:
                        draw_bucle(screen, vertice_pos[i])
            
            draw_vertices()
            
            # Mostrar información de ciclos
            if self.camino_orden:
                ciclos_msg = FONT.render(f"Vértices en ciclos: {[v+1 for v in self.camino_orden]}", True, BLUE)
                screen.blit(ciclos_msg, (WIDTH//2 - ciclos_msg.get_width()//2, 120))
            
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
                    1: f"Error: Debe ingresar {n} valores separados por comas",
                    2: f"Error: Valores deben estar entre 1 y {n}",
                    3: "Error: Formato inválido (use números separados por comas)"
                }
                error_msg = FONT.render(errores.get(self.error_fun, ""), True, RED)
                screen.blit(error_msg, (WIDTH//2 - error_msg.get_width()//2, 650))
            
            # Mostrar resultados de cifrado
            if self.texto_cifrado:
                resultado = FONT.render(f"Cifrado: {self.texto_cifrado[:50]}", True, GREEN)
                screen.blit(resultado, (50, 750))
            
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
                    # En este modo, "construir árbol" muestra las flechas
                    pass
                elif self.btn_encrypt.check_click(pos):
                    self.cifrar_texto()
                elif self.btn_back.check_click(pos):
                    self.state = self.STATE_MENU
        
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
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                
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
    print("  Versión GitHub - Mejorada")
    print("=" * 70)
    print("  Mejoras implementadas:")
    print("    1. Elegir número n de vértices (3-15)")
    print("    2. Notación de permutaciones para la función")
    print("    3. Explicación mejorada del cifrado Hill")
    print("=" * 70)
    print("  Autores:")
    print("    • Martin Lora Cano")
    print("    • Cristian Andrés Diaz Ortega")
    print("    • Jhon Edison Prieto Artunduaga")
    print("=" * 70)
    print("\n  Iniciando aplicación...")
    
    app = JoyalApp()
    app.ejecutar()