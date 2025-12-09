#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Joyal - Desktop version (PyGame)
- Permite elegir n al inicio (2 <= n <= 14)
- Modo 1: Construir árbol con clicks -> genera función f y muestra notación en ciclos
- Modo 2: Ingresar función f (CSV) -> reconstruye bosque y muestra ciclos
- Tiene funciones Hill (bloque = n) para encriptar / desencriptar (opcional)
- Uso: python joyal_desktop.py
"""

import pygame
import math
import sys
import numpy as np
from collections import deque
import tkinter as tk
from tkinter import simpledialog, messagebox

# ---------------------------
# Configuración inicial
# ---------------------------
pygame.init()
WIDTH, HEIGHT = 1000, 820
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Demostración de Joyal - Desktop")
FONT = pygame.font.SysFont(None, 24)
FONT_BOLD = pygame.font.SysFont(None, 26, bold=True)
FPS = 30
clock = pygame.time.Clock()

# Alfabeto para Hill (igual que en tu proyecto)
ALPHABET = {chr(ord('A') + i): i for i in range(26)}
ALPHABET['Ñ'] = 26
ALPHABET[','] = 27
ALPHABET['.'] = 28
ALPHABET[' '] = 29
REV_ALPH = {v: k for k, v in ALPHABET.items()}
MOD = 30

# Límite razonable de n (visual + rendimiento)
MIN_N = 2
MAX_N = 14
DEFAULT_N = 9

# ---------------------------
# Utilidades matemáticas
# ---------------------------
def egcd(a, b):
    if b == 0:
        return (a, 1, 0)
    else:
        g, x1, y1 = egcd(b, a % b)
        return (g, y1, x1 - (a // b) * y1)

def determinante_bareiss(mat):
    """Determinante entero usando Bareiss (robusto para enteros). mat es lista de listas."""
    n = len(mat)
    if n == 0: return 1
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

def inverse_matrix_mod(M, MOD=30):
    """Inversa modular utilizando adjugate y Bareiss. Devuelve lista de listas o None."""
    n = len(M)
    if any(len(row) != n for row in M):
        raise ValueError("Matrix must be square")
    detM = determinante_bareiss(M)
    det_mod = detM % MOD
    g, x, y = egcd(det_mod, MOD)
    if g != 1:
        return None
    det_inv = x % MOD
    adj = [[0] * n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            # construir menor
            minor = [[M[r][c] for c in range(n) if c != j] for r in range(n) if r != i]
            det_minor = determinante_bareiss(minor)
            cofactor = ((-1) ** (i + j)) * det_minor
            adj[j][i] = cofactor % MOD
    inv = [[(det_inv * adj[i][j]) % MOD for j in range(n)] for i in range(n)]
    return inv

def mat_mul_vec_nxn(M, vec, MOD=30):
    n = len(vec)
    out = [0]*n
    for i in range(n):
        s = 0
        row = M[i]
        for j in range(n):
            s += row[j] * vec[j]
        out[i] = s % MOD
    return out

# ---------------------------
# Construcción de posiciones
# ---------------------------
def generate_vertex_positions(n, center=(WIDTH//2, 260), radius=220):
    cx, cy = center
    pos = []
    for i in range(n):
        angle = 2 * math.pi * i / n - math.pi/2
        x = cx + int(radius * math.cos(angle))
        y = cy + int(radius * math.sin(angle))
        pos.append((x, y))
    return pos

# ---------------------------
# Notación de ciclos
# ---------------------------
def mapping_to_cycles(mapping):
    """mapping: list 0-based f(i). Devuelve string con ciclos 1-indexed."""
    n = len(mapping)
    seen = [False]*n
    cycles = []
    for i in range(n):
        if not seen[i]:
            cycle = []
            cur = i
            while not seen[cur]:
                seen[cur] = True
                cycle.append(cur+1)  # mostrar 1-indexed
                cur = mapping[cur]
            # representar siempre como ciclo (incluir fijos como (i))
            cycles.append('(' + ' '.join(str(x) for x in cycle) + ')')
    return ''.join(cycles)

# ---------------------------
# DFS y ciclos (Joyal)
# ---------------------------
def depthfirstsearch(graph, start, goal, path=None, visited=None):
    if path is None: path = []
    if visited is None: visited = set()
    path = path + [start]
    visited.add(start)
    if start == goal:
        return path
    for neighbor in graph[start]:
        if neighbor not in visited:
            newpath = depthfirstsearch(graph, neighbor, goal, path, visited)
            if newpath:
                return newpath
    return None

def vertices_en_ciclo_from_mapping(mapping):
    n = len(mapping)
    grafo_local = {i: [] for i in range(n)}
    for i in range(n):
        grafo_local[i].append(mapping[i])
    vertices_cic = set()
    for u in range(n):
        for v in list(grafo_local[u]):
            grafo_local[u].remove(v)
            camino = depthfirstsearch(grafo_local, v, u)
            grafo_local[u].append(v)
            if camino:
                vertices_cic.add(u)
                vertices_cic.add(v)
    return sorted(vertices_cic)

# ---------------------------
# Generar matriz clave desde función
# ---------------------------
def get_matrix_from_function(funcion, MOD=30, dim=None):
    if dim is None: dim = len(funcion)
    clean = [(0 if v is None else int(v)) for v in funcion]
    func = [clean[i % len(clean)] for i in range(dim)]
    arr = []
    for i in range(dim):
        row = []
        for j in range(dim):
            row.append((func[i] * (j + 1) + (func[j] + 1)) % MOD)
        arr.append(row)
    det = int(round(np.linalg.det(np.array(arr, dtype=float))))
    if math.gcd(det % MOD, MOD) == 1:
        return arr
    # fallback: diagonal coprima con MOD
    I = [[0]*dim for _ in range(dim)]
    for i in range(dim):
        v = 3 * (func[i] + 1) + 1
        v %= MOD
        while math.gcd(v, MOD) != 1:
            v = (v + 1) % MOD
            if v == 0: v = 1
        I[i][i] = v
    return I

# ---------------------------
# Codificación / Hill adaptada a bloque n
# ---------------------------
def char_a_num(ch):
    ch = ch.upper()
    if ch == 'Ñ': return ALPHABET['Ñ']
    if ch in ALPHABET: return ALPHABET[ch]
    if ch == 'ñ': return ALPHABET['Ñ']
    return ALPHABET[' ']

def num_a_char(n):
    return REV_ALPH.get(n % MOD, ' ')

def encode_text_to_numbers(text, block):
    L = len(text)
    if L > MOD*MOD - 1:
        raise ValueError("Texto muy largo")
    high = L // MOD
    low = L % MOD
    nums = [high, low]
    for ch in text:
        nums.append(char_a_num(ch))
    while len(nums) % block != 0:
        nums.append(ALPHABET[' '])
    return nums

def decode_numbers_to_text(nums):
    if len(nums) < 2: return ""
    high, low = nums[0], nums[1]
    L = high * MOD + low
    chars = []
    pos = 2
    needed = L
    while needed > 0 and pos < len(nums):
        chars.append(num_a_char(nums[pos]))
        pos += 1
        needed -= 1
    return ''.join(chars)

def hill_encrypt_numbers(nums, key, MOD=30):
    out = []
    n = len(key)
    for i in range(0, len(nums), n):
        block = nums[i:i+n]
        v = mat_mul_vec_nxn(key, block, MOD)
        out.extend(v)
    return out

def hill_decrypt_numbers(nums, key, MOD=30):
    inv = inverse_matrix_mod(key, MOD)
    if inv is None:
        raise ValueError("Key not invertible modulo {}".format(MOD))
    out = []
    n = len(inv)
    for i in range(0, len(nums), n):
        block = nums[i:i+n]
        v = mat_mul_vec_nxn(inv, block, MOD)
        out.extend(v)
    return out

# ---------------------------
# Estado de la aplicación
# ---------------------------
class AppState:
    def __init__(self, n):
        self.n = n
        self.positions = generate_vertex_positions(n)
        self.radius = max(14, int(420/n))
        self.reset()

    def reset(self):
        self.mode = 'menu'   # 'menu', 'tree', 'function'
        self.aristas = []    # lista de aristas (u,v) no dirigidas (0-based)
        self.grafo = [[] for _ in range(self.n)]
        self.parent = list(range(self.n))  # simple dsu
        self.vertice_first = None
        self.funcion = [None] * self.n
        self.construir_bosque = False
        self.construir_arbol = False
        self.vertice_ini = None
        self.vertice_fin = None
        self.aristas_vert = []
        self.aristas_dir = []
        self.camino_orden = None
        self.camino_inv = None
        self.camino_vertebra = None
        self.encriptado = None

    # DSU simple
    def find(self, x):
        while self.parent[x] != x:
            self.parent[x] = self.parent[self.parent[x]]
            x = self.parent[x]
        return x
    def union(self, a, b):
        ra = self.find(a); rb = self.find(b)
        if ra != rb:
            self.parent[rb] = ra
            return True
        return False
    def is_connected_all(self):
        root = self.find(0)
        return all(self.find(i) == root for i in range(self.n))

state = None  # se inicializa después de pedir n

# ---------------------------
# Dibujado
# ---------------------------
def draw_vertices(positions, radius):
    for i, pos in enumerate(positions):
        pygame.draw.circle(screen, (255, 128, 128), pos, radius)
        txt = FONT.render(str(i+1), True, (255,255,255))
        screen.blit(txt, (pos[0]-8, pos[1]-10))

def draw_line(a_pos, b_pos, color=(0,0,0), width=4):
    pygame.draw.line(screen, color, a_pos, b_pos, width)

def draw_dir_arrow(a_pos, b_pos, color=(0,0,0), width=3, head_size=10):
    ax, ay = a_pos; bx, by = b_pos
    total = math.hypot(bx-ax, by-ay)
    if total == 0: return
    sx = ax + (state.radius/total) * (bx-ax)
    sy = ay + (state.radius/total) * (by-ay)
    ex = bx - (state.radius/total) * (bx-ax)
    ey = by - (state.radius/total) * (by-ay)
    pygame.draw.line(screen, color, (sx,sy), (ex,ey), width)
    angle = math.atan2(ey-sy, ex-sx)
    left = (ex - head_size * math.cos(angle - math.pi/6), ey - head_size * math.sin(angle - math.pi/6))
    right = (ex - head_size * math.cos(angle + math.pi/6), ey - head_size * math.sin(angle + math.pi/6))
    pygame.draw.polygon(screen, color, [(ex,ey), left, right])

def draw_vertebra_segment(a_pos, b_pos, color=(255,0,0), ancho=4, seg_len=12, gap=6):
    x1, y1 = a_pos; x2,y2 = b_pos
    length = math.hypot(x2-x1, y2-y1)
    if length == 0: return
    dx = (x2-x1)/length; dy = (y2-y1)/length
    dibujo = 0.0
    while dibujo < length:
        ini_x = x1 + dx*dibujo; ini_y = y1 + dy*dibujo
        final = min(dibujo + seg_len, length)
        fin_x = x1 + dx*final; fin_y = y1 + dy*final
        pygame.draw.line(screen, color, (ini_x, ini_y), (fin_x, fin_y), ancho)
        dibujo += seg_len + gap

# ---------------------------
# Lógica principal (event handlers)
# ---------------------------
def handle_click(pos):
    # devuelve índice de vértice cliqueado o None
    for i, p in enumerate(state.positions):
        if math.hypot(pos[0]-p[0], pos[1]-p[1]) <= state.radius + 4:
            return i
    return None

def try_add_edge(u, v):
    # evita ciclos (DSU)
    if u == v: return False
    if state.find(u) == state.find(v):
        return False
    state.aristas.append((u, v))
    state.union(u, v)
    state.grafo[u].append(v); state.grafo[v].append(u)
    return True

def build_function_from_tree():
    # pide inicio y fin preseleccionados; si iguales -> trivial
    if state.vertice_ini is None or state.vertice_fin is None:
        return
    if state.vertice_ini == state.vertice_fin:
        # función: ese vértice se autoapunta; resto orientados hacia camino (none before)
        state.aristas_vert = []
        state.funcion[state.vertice_ini] = state.vertice_fin
        state.camino_vertebra = [state.vertice_fin]
        state.camino_orden = [state.vertice_fin]
        state.camino_inv = [state.vertice_fin]
    else:
        camino = depthfirstsearch(state.grafo, state.vertice_ini, state.vertice_fin)
        state.camino_vertebra = camino
        state.aristas_vert = [(camino[i], camino[i+1]) for i in range(len(camino)-1)]
        state.camino_orden = sorted(camino)
        state.camino_inv = list(reversed(camino))
        # asignar f para vértebra
        for i, v in enumerate(state.camino_orden):
            state.funcion[v] = state.camino_inv[i]
    # orientar aristas restantes hacia vértebra (distancias BFS desde vertice_fin)
    distancia_a_fin = [-1]*state.n
    q = deque([state.vertice_fin]); distancia_a_fin[state.vertice_fin] = 0
    while q:
        x = q.popleft()
        for a in state.grafo[x]:
            if distancia_a_fin[a] == -1:
                distancia_a_fin[a] = distancia_a_fin[x] + 1
                q.append(a)
    state.aristas_dir = []
    for a,b in state.aristas:
        en_vert = any((a==x and b==y) or (a==y and b==x) for (x,y) in state.aristas_vert)
        if not en_vert:
            da = distancia_a_fin[a]; db = distancia_a_fin[b]
            if da > db:
                state.aristas_dir.append((a,b)); state.funcion[a] = b
            else:
                state.aristas_dir.append((b,a)); state.funcion[b] = a
    state.construir_bosque = True
    state.construir_arbol = True

def process_function_input(csv_text):
    try:
        vals = list(map(int, csv_text.strip().split(',')))
        if len(vals) != state.n:
            messagebox.showerror("Formato", f"Se requieren {state.n} valores (1..{state.n}).")
            return
        if not all(1 <= x <= state.n for x in vals):
            messagebox.showerror("Rango", f"Los valores deben estar entre 1 y {state.n}.")
            return
        state.funcion = [v-1 for v in vals]
        state.construir_bosque = True
        # hallar vértices en ciclos
        state.camino_orden = vertices_en_ciclo_from_mapping(state.funcion)
        state.camino_inv = [state.funcion[i] for i in state.camino_orden]
        state.camino_vertebra = list(reversed(state.camino_inv))
        state.aristas_vert = [(state.camino_vertebra[i], state.camino_vertebra[i+1]) for i in range(len(state.camino_vertebra)-1)] if state.camino_vertebra else []
        state.aristas_dir = []
        for i in range(state.n):
            if i not in state.camino_orden:
                state.aristas_dir.append((i, state.funcion[i]))
        state.mode = 'function'
    except Exception as e:
        messagebox.showerror("Error", "Formato inválido. Use CSV: 1,2,3,...")

# ---------------------------
# Interacción para encriptar / desencriptar
# ---------------------------
def encrypt_text_prompt():
    if not state.construir_bosque and not state.construir_arbol:
        messagebox.showinfo("Info", "Primero genere la función (desde árbol o ingresándola).")
        return
    text = simpledialog.askstring("Encriptar", "Texto a encriptar (A-Z, Ñ, , . espacio):")
    if text is None or text == "": return
    block = state.n
    nums = encode_text_to_numbers(text, block)
    key = get_matrix_from_function(state.funcion, MOD=MOD, dim=block)
    try:
        enc_nums = hill_encrypt_numbers(nums, key, MOD)
        cipher = ''.join(num_a_char(n) for n in enc_nums)
        state.encriptado = cipher
        messagebox.showinfo("Encriptado", f"Texto encriptado:\n{cipher}")
    except Exception as ex:
        messagebox.showerror("Error", f"No se pudo encriptar: {ex}")

def decrypt_text_prompt():
    if not state.construir_bosque and not state.construir_arbol:
        messagebox.showinfo("Info", "Primero genere la función (desde árbol o ingresándola).")
        return
    text = simpledialog.askstring("Desencriptar", "Texto cifrado:")
    if text is None or text == "": return
    block = state.n
    nums = [char_a_num(ch) for ch in text]
    while len(nums) % block != 0:
        nums.append(ALPHABET[' '])
    key = get_matrix_from_function(state.funcion, MOD=MOD, dim=block)
    try:
        dec_nums = hill_decrypt_numbers(nums, key, MOD)
        plain = decode_numbers_to_text(dec_nums)
        messagebox.showinfo("Desencriptado", f"Texto desencriptado:\n{plain}")
    except Exception as ex:
        messagebox.showerror("Error", f"No se pudo desencriptar: {ex}")

# ---------------------------
# UI principal y loop
# ---------------------------
def main():
    global state
    # pedir n con dialog tkinter
    root = tk.Tk()
    root.withdraw()
    while True:
        try:
            n = simpledialog.askinteger("n vértices", f"Ingrese número de vértices n ({MIN_N}-{MAX_N}):", initialvalue=DEFAULT_N, minvalue=MIN_N, maxvalue=MAX_N)
            if n is None:
                if messagebox.askyesno("Salir", "¿Desea salir?"):
                    pygame.quit(); sys.exit(0)
                else:
                    continue
            break
        except Exception:
            continue
    state = AppState(n)
    root.destroy()

    running = True
    info_msg = "Teclas: 1=Modo Árbol, 2=Modo Función, S=Ingresar función, E=Encriptar, D=Desencriptar, R=Reiniciar, Q=Salir"
    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    running = False
                elif event.key == pygame.K_1:
                    state.mode = 'tree'
                elif event.key == pygame.K_2:
                    state.mode = 'function'
                elif event.key == pygame.K_r:
                    state.reset()
                elif event.key == pygame.K_s:
                    # dialog para ingresar función CSV
                    root = tk.Tk(); root.withdraw()
                    text = simpledialog.askstring("Función f", f"Ingrese f(1..{state.n}) en formato CSV (ej: 1,2,3,...):")
                    root.destroy()
                    if text: process_function_input(text)
                elif event.key == pygame.K_e:
                    # encriptar
                    root = tk.Tk(); root.withdraw()
                    encrypt_text_prompt()
                    root.destroy()
                elif event.key == pygame.K_d:
                    root = tk.Tk(); root.withdraw()
                    decrypt_text_prompt()
                    root.destroy()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                idx = handle_click(pos)
                if idx is not None:
                    if state.mode == 'tree':
                        # construir árbol por clicks: click en primer vértice, luego en segundo para crear arista
                        if state.vertice_first is None:
                            state.vertice_first = idx
                        else:
                            if try_add_edge(state.vertice_first, idx):
                                # si ya se completó el árbol (n-1 aristas) pedir inicio/fin por clicks
                                if len(state.aristas) == state.n - 1 and state.is_connected_all():
                                    # cambiar estado: ahora seleccionar inicio y fin en orden
                                    # aqui la app espera dos clicks: primero ini, luego fin
                                    # usamos vertice_ini/veritce_fin como None->set
                                    state.vertice_ini = None
                                    state.vertice_fin = None
                                    messagebox.showinfo("Seleccionar", "Árbol completo. Seleccione con dos clicks: primero INICIO, luego FIN (en la pantalla).")
                                # else continue building
                            state.vertice_first = None
                    elif state.mode == 'function':
                        # cuando ya hay función (ingresada), el click no cambia la función
                        # pero si la función no está generada desde árbol, nada hace
                        pass
                    # Si se pidieron inicio/fin manualmente (cuando árbol completo)
                    if state.mode == 'tree' and len(state.aristas) == state.n - 1 and state.is_connected_all():
                        # si vertice_ini no definido, primer click define vertice_ini, segundo define vertice_fin
                        if state.vertice_ini is None:
                            state.vertice_ini = idx
                            messagebox.showinfo("Inicio", f"Vértice INICIO seleccionado: {idx+1}. Ahora seleccione FIN.")
                        elif state.vertice_fin is None:
                            state.vertice_fin = idx
                            messagebox.showinfo("Fin", f"Vértice FIN seleccionado: {idx+1}. Ahora se construye la función.")
                            build_function_from_tree()

        # Dibujar
        screen.fill((240,240,240))
        title = FONT_BOLD.render(f"Demostración de Joyal - n = {state.n}", True, (10,10,80))
        screen.blit(title, (20,10))
        small = FONT.render(info_msg, True, (40,40,40))
        screen.blit(small, (20,40))

        # dibujar aristas (no dirigidas)
        for a,b in state.aristas:
            draw_line(state.positions[a], state.positions[b], (0,0,0), 3)

        # si hay función (modo function o after build), dibujar flechas
        if state.construir_bosque or state.construir_arbol:
            # dibujar aristas de vértebra (punteadas)
            for (a,b) in getattr(state, 'aristas_vert', []):
                draw_vertebra_segment(state.positions[a], state.positions[b], (200,30,30), ancho=4)
            # dibujar aristas dirigidas
            for (a,b) in getattr(state, 'aristas_dir', []):
                draw_dir_arrow(state.positions[a], state.positions[b], (0,0,0), width=3, head_size=10)
            # dibujar bucles y demás
            # mostrar notación en ciclos
            cycles = mapping_to_cycles(state.funcion) if state.funcion and None not in state.funcion else "(función incompleta)"
            cycles_txt = FONT_BOLD.render("Notación de permutaciones (ciclos): " + cycles, True, (0,0,0))
            screen.blit(cycles_txt, (20, 700))

        # dibujar vértices
        draw_vertices(state.positions, state.radius)

        # mostrar función completa como lista (1-indexed)
        if state.construir_bosque or state.construir_arbol:
            func_list = [str((f+1) if f is not None else '-') for f in state.funcion]
            func_txt = FONT.render("f = [" + ", ".join(func_list) + "]", True, (0,0,0))
            screen.blit(func_txt, (20, 670))

        # indicación de selección de inicio/fin si aplica
        if state.mode == 'tree' and len(state.aristas) == state.n - 1 and state.is_connected_all():
            hint = FONT.render("Árbol completo: haga click para seleccionar INICIO y FIN (en ese orden).", True, (80,0,0))
            screen.blit(hint, (20, 100))

        pygame.display.flip()

    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()
