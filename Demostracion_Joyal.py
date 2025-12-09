"""
PROYECTO MD - DEMOSTRACIÓN DE JOYAL
"""

import pygame
import sys
import math
import numpy as np
from collections import deque

# -------------------- Configuración PyGame --------------------
pygame.init()
WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Proyecto MD - Demostración de Joyal")
clock = pygame.time.Clock()

# Fuentes
FONT = pygame.font.SysFont(None, 26)
FONT_BOLD = pygame.font.SysFont(None, 28, bold=True)
FONT_SMALL = pygame.font.SysFont(None, 18)

# Visual
vertice_rad = 22

# Posiciones para 9 vértices (fijas)
vertice_pos = [
    (450, 100),
    (579, 147),
    (646, 265),
    (623, 400),
    (518, 488),
    (382, 488),
    (277, 400),
    (254, 265),
    (322, 147),
]

# Estado global
n = 9
aristas = []            # aristas no dirigidas del grafo/árbol
grafo = [[] for _ in range(n)]
parent = list(range(n))
funcion = [None] * n    # f: V -> V (0-indexed)
aristas_dir = []        # aristas orientadas (no vértebra)
aristas_vert = []       # aristas de la vértebra (camino)
selected = None         # vértice seleccionado
mode = 'graph'          # 'graph', 'tree', 'permutation'
message = "Modo: GRAFO"
message_timer = 0

# -------------------- Utilidades Union-Find --------------------

def find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]


def union(a, b):
    ra, rb = find(a), find(b)
    if ra == rb:
        return False
    parent[rb] = ra
    return True

# -------------------- Algoritmos de grafos --------------------

def depthfirstsearch(graph, vertice_ini, vertice_fin, path=None, visited=None):
    if path is None:
        path = []
    if visited is None:
        visited = set()
    path = path + [vertice_ini]
    visited.add(vertice_ini)
    if vertice_ini == vertice_fin:
        return path
    for neighbor in graph[vertice_ini]:
        if neighbor not in visited:
            newpath = depthfirstsearch(graph, neighbor, vertice_fin, path, visited)
            if newpath:
                return newpath
    return None


def vertices_en_ciclo(aristas_list):
    # Aristas_list debe ser lista de pares (u,v) dirigidos o no; construiremos grafo
    grafo_local = {}
    for u, v in aristas_list:
        grafo_local.setdefault(u, []).append(v)
        grafo_local.setdefault(v, [])
    vertices_cic = set()
    for u, p in list(grafo_local.items()):
        for v in list(p):
            grafo_local[u].remove(v)
            camino = depthfirstsearch(grafo_local, v, u) if v in grafo_local else None
            grafo_local[u].append(v)
            if camino:
                vertices_cic.add(u); vertices_cic.add(v)
    return sorted(vertices_cic)


def dirigir_vertices(grafo_local, aristas_all, aristas_vert_local, vertice_fin):
    # BFS desde vertice_fin para distancias
    distancia = [-1] * len(grafo_local)
    q = deque([vertice_fin])
    distancia[vertice_fin] = 0
    while q:
        v = q.popleft()
        for ady in grafo_local[v]:
            if distancia[ady] == -1:
                distancia[ady] = distancia[v] + 1
                q.append(ady)
    aristas_d = []
    for a, b in aristas_all:
        if (a, b) in aristas_vert_local or (b, a) in aristas_vert_local:
            continue
        da = distancia[a] if distancia[a] != -1 else float('inf')
        db = distancia[b] if distancia[b] != -1 else float('inf')
        if da > db:
            aristas_d.append((a, b))
        else:
            aristas_d.append((b, a))
    return aristas_d

# -------------------- Funciones gráficas --------------------

def draw_vertices():
    for i, pos in enumerate(vertice_pos):
        pygame.draw.circle(screen, (255, 128, 128), pos, vertice_rad)
        txt = FONT.render(str(i+1), True, (255,255,255))
        screen.blit(txt, (pos[0]-txt.get_width()//2, pos[1]-txt.get_height()//2))


def draw_dirigido(surface, a_pos, b_pos, color=(0,0,0), width=3, head_size=10):
    ax, ay = a_pos; bx, by = b_pos
    total = math.hypot(bx-ax, by-ay)
    if total == 0:
        return
    sx = ax + (vertice_rad/total)*(bx-ax)
    sy = ay + (vertice_rad/total)*(by-ay)
    ex = bx - (vertice_rad/total)*(bx-ax)
    ey = by - (vertice_rad/total)*(by-ay)
    pygame.draw.line(surface, color, (sx,sy), (ex,ey), width)
    angle = math.atan2(ey-sy, ex-sx)
    left = (ex - head_size*math.cos(angle - math.pi/6), ey - head_size*math.sin(angle - math.pi/6))
    right = (ex - head_size*math.cos(angle + math.pi/6), ey - head_size*math.sin(angle + math.pi/6))
    pygame.draw.polygon(surface, color, [(ex,ey), left, right])


def draw_vertebra(surface, color, p1, p2, ancho=4, largo_linea=12, largo_espacio=8):
    x1,y1 = p1; x2,y2 = p2
    length = math.hypot(x2-x1, y2-y1)
    if length == 0:
        return
    dx = (x2-x1)/length; dy = (y2-y1)/length
    d = 0.0
    while d < length:
        ini_x = x1 + dx*d; ini_y = y1 + dy*d
        fin = min(d + largo_linea, length)
        fin_x = x1 + dx*fin; fin_y = y1 + dy*fin
        pygame.draw.line(surface, color, (ini_x, ini_y), (fin_x, fin_y), ancho)
        d += largo_linea + largo_espacio

# -------------------- Hill cipher (soporte básico) --------------------
ALPHABET = {chr(ord('A')+i): i for i in range(26)}
ALPHABET['Ñ'] = 26; ALPHABET[','] = 27; ALPHABET['.'] = 28; ALPHABET[' '] = 29
REV_ALPH = {v:k for k,v in ALPHABET.items()}
MOD = 30; BLOCK = 9


def char_a_num(ch):
    ch = ch.upper()
    return ALPHABET.get(ch, ALPHABET[' '])

def num_a_char(n):
    return REV_ALPH.get(n%MOD, ' ')


def mat_mul_vec_nxn(M, vec, MOD=30):
    n = len(vec)
    out = [0]*n
    for i in range(n):
        s = 0
        for j in range(n):
            s += int(M[i][j]) * int(vec[j])
        out[i] = s % MOD
    return out

# Determinante Bareiss e inversa modular (simples, suficientes para 9x9)

def determinante_bareiss(mat):
    n = len(mat)
    if n == 0:
        return 1
    A = [list(map(int,row)) for row in mat]
    prev = 1
    sign = 1
    for k in range(n-1):
        if A[k][k] == 0:
            swap = None
            for r in range(k+1, n):
                if A[r][k] != 0:
                    swap = r; break
            if swap is None:
                return 0
            A[k], A[swap] = A[swap], A[k]
            sign *= -1
        piv = A[k][k]
        for i in range(k+1, n):
            for j in range(k+1, n):
                A[i][j] = (A[i][j]*piv - A[i][k]*A[k][j]) // prev
        prev = piv
    return sign * A[n-1][n-1]


def minor_matrix(M, row, col):
    n = len(M)
    return [[M[r][c] for c in range(n) if c != col] for r in range(n) if r != row]


def adjugate_matrix(M, MOD=30):
    n = len(M)
    adj = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            minor = minor_matrix(M, i, j)
            detm = determinante_bareiss(minor)
            cofactor = ((-1)**(i+j))*detm
            adj[j][i] = cofactor % MOD
    return adj


def egcd(a,b):
    if b==0:
        return (a,1,0)
    g,x1,y1 = egcd(b, a%b)
    return (g, y1, x1 - (a//b)*y1)


def inverse_matrix_mod(M, MOD=30):
    n = len(M)
    detM = determinante_bareiss(M)
    det_mod = detM % MOD
    g,x,y = egcd(det_mod, MOD)
    if g != 1:
        return None
    det_inv = x % MOD
    adj = adjugate_matrix(M, MOD)
    inv = [[(det_inv * adj[i][j]) % MOD for j in range(n)] for i in range(n)]
    return inv


def is_invertible_mod(mat, mod):
    det = int(round(np.linalg.det(np.array(mat, dtype=float))))
    return math.gcd(det, mod) == 1


def get_matrix_from_function(funcion_list, MOD=30, dim=9):
    clean = [(0 if v is None else int(v)) for v in funcion_list]
    func = [clean[i % len(clean)] for i in range(dim)]
    arr = []
    for i in range(dim):
        row = []
        for j in range(dim):
            row.append((func[i] * (j + 1) + (func[j] + 1)) % MOD)
        arr.append(row)
    if is_invertible_mod(arr, MOD):
        return arr
    I = [[0]*dim for _ in range(dim)]
    for i in range(dim):
        v = 3 * (func[i] + 1) + 1
        v %= MOD
        while math.gcd(v, MOD) != 1:
            v = (v + 1) % MOD
        I[i][i] = v
    return I


def hill_encrypt_numbers(nums, key, MOD=30):
    out = []
    n = BLOCK
    for i in range(0, len(nums), n):
        block = nums[i:i+n]
        out.extend(mat_mul_vec_nxn(key, block, MOD))
    return out


def hill_decrypt_numbers(nums, key, MOD=30):
    inv = inverse_matrix_mod(key, MOD)
    if inv is None:
        raise ValueError('Key not invertible modulo {}'.format(MOD))
    out=[]
    n=BLOCK
    for i in range(0, len(nums), n):
        block = nums[i:i+n]
        out.extend(mat_mul_vec_nxn(inv, block, MOD))
    return out


def encode_text_to_numbers(text):
    L = len(text)
    high = L // MOD; low = L % MOD
    nums = [high, low]
    for ch in text:
        nums.append(char_a_num(ch))
    while len(nums) % BLOCK != 0:
        nums.append(ALPHABET[' '])
    return nums


def decode_numbers_to_text(nums):
    if len(nums) < 2: return ''
    high, low = nums[0], nums[1]
    L = high * MOD + low
    chars=[]; pos=2; needed=L
    while needed>0 and pos < len(nums):
        chars.append(num_a_char(nums[pos])); pos+=1; needed-=1
    return ''.join(chars)


def encrypt_text(plain, key):
    nums = encode_text_to_numbers(plain)
    enc = hill_encrypt_numbers(nums, key, MOD)
    return ''.join(num_a_char(n) for n in enc)


def decrypt_text(cipher, key):
    nums = [char_a_num(ch) for ch in cipher]
    if len(nums) % BLOCK != 0:
        raise ValueError('Invalid ciphertext length')
    dec_nums = hill_decrypt_numbers(nums, key, MOD)
    return decode_numbers_to_text(dec_nums)

# -------------------- Lógica de interacción --------------------

def reset_all():
    global aristas, grafo, parent, funcion, aristas_dir, aristas_vert, selected, mode, message
    aristas = []
    grafo = [[] for _ in range(n)]
    parent = list(range(n))
    funcion = [None] * n
    aristas_dir = []
    aristas_vert = []
    selected = None
    mode = 'graph'
    message = 'Modo: GRAFO'


def handle_vertex_click(pos):
    global selected, aristas, grafo, message
    for i, vpos in enumerate(vertice_pos):
        if math.hypot(pos[0]-vpos[0], pos[1]-vpos[1]) <= vertice_rad:
            # click sobre vértice i
            if mode == 'graph':
                if selected is None:
                    selected = i
                    message = f'Seleccionado {i+1}'
                else:
                    if selected != i:
                        if (selected, i) in aristas or (i, selected) in aristas:
                            message = 'Arista ya existe'
                        elif not union(selected, i):
                            message = 'Crearía ciclo (no permitido en árbol)'
                        else:
                            aristas.append((selected, i))
                            grafo[selected].append(i)
                            grafo[i].append(selected)
                            message = f'Arista {selected+1}-{i+1} añadida ({len(aristas)}/{n-1})'
                    selected = None
            elif mode == 'tree':
                if selected is None:
                    selected = i
                    message = f'Seleccione destino para f({i+1})'
                else:
                    if selected != i:
                        funcion[selected] = i
                        aristas_dir.append((selected, i))
                        message = f'Definido f({selected+1})={i+1}'
                        if None not in funcion:
                            message = '¡Función completamente definida!'
                    selected = None
            return True
    return False

# -------------------- Dibujado principal --------------------

def draw():
    screen.fill((245,245,250))
    title = FONT_BOLD.render('DEMOSTRACIÓN DE JOYAL', True, (30,30,80))
    screen.blit(title, (20, 10))

    # Dibujar aristas no dirigidas
    for u,v in aristas:
        pygame.draw.line(screen, (30,30,30), vertice_pos[u], vertice_pos[v], 4)

    # Dibujar aristas dirigidas
    for u,v in aristas_dir:
        draw_dirigido(screen, vertice_pos[u], vertice_pos[v], (0,0,0), width=3)

    # Dibujar vértebra punteada
    for u,v in aristas_vert:
        draw_vertebra(screen, (200,20,20), vertice_pos[u], vertice_pos[v])

    draw_vertices()

    # Panel derecho
    panel = pygame.Rect(WIDTH-320, 80, 280, HEIGHT-120)
    pygame.draw.rect(screen, (255,255,255), panel)
    pygame.draw.rect(screen, (80,80,120), panel, 2)
    info = FONT.render(f'n={n}  V={n}  E={len(aristas)}', True, (20,20,40))
    screen.blit(info, (panel.x+10, panel.y+10))

    mode_txt = FONT.render(f'MODO: {mode.upper()}', True, (20,20,40))
    screen.blit(mode_txt, (panel.x+10, panel.y+40))

    # Mostrar función parcial si existe
    ftext = 'f = [' + ','.join(str(x+1) if x is not None else '?' for x in funcion) + ']'
    fsurf = FONT_SMALL.render(ftext, True, (20,20,40))
    screen.blit(fsurf, (panel.x+10, panel.y+80))

    # Mensaje
    if message:
        msgsurf = FONT.render(message, True, (10,80,150))
        screen.blit(msgsurf, (20, HEIGHT-40))

# -------------------- Operaciones auxiliares --------------------

def try_switch_to_tree():
    global mode, message
    if len(aristas) == n-1:
        mode = 'tree'
        message = 'Modo ÁRBOL: defina f clickeando origen->destino'
    else:
        message = f'Necesita {n-1} aristas para formar un árbol (ah: {len(aristas)})'


def build_demo_cycle():
    # Reiniciar y construir un árbol en cadena + función cíclica
    reset_all()
    for i in range(n-1):
        aristas.append((i, i+1))
        grafo[i].append(i+1); grafo[i+1].append(i)
        union(i, i+1)
    for i in range(n):
        funcion[i] = (i+1)%n
    for i in range(n):
        if funcion[i] != i:
            aristas_dir.append((i, funcion[i]))
    message = 'Demostración generada: ciclo'


def show_permutation_notation():
    # Mostrar notación de permutación si función completa
    global mode, perm_two_lines, perm_cycles, message
    if None in funcion:
        message = 'Defina la función completa primero'
        return
    nloc = len(funcion)
    superior = list(range(1,nloc+1))
    inferior = [x+1 for x in funcion]
    linestr = '(' + ' '.join(str(x) for x in superior) + ')\n(' + ' '.join(str(x) for x in inferior) + ')'
    # ciclos
    ciclos = []
    visited = [False]*nloc
    for i in range(nloc):
        if not visited[i]:
            cycle = []
            x = i
            while not visited[x]:
                visited[x] = True
                cycle.append(x+1)
                x = funcion[x]
            if len(cycle)>1:
                ciclos.append('('+' '.join(map(str, cycle))+')')
    perm_two_lines = linestr
    perm_cycles = ' '.join(ciclos) if ciclos else 'id'
    mode = 'permutation'
    message = 'Notación de permutación generada'

# -------------------- Main loop --------------------

def main():
    global selected, message, message_timer, aristas_dir, aristas_vert
    reset_all()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if not handle_vertex_click(event.pos):
                    selected = None
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    reset_all()
                elif event.key == pygame.K_t:
                    try_switch_to_tree()
                elif event.key == pygame.K_p:
                    show_permutation_notation()
                elif event.key == pygame.K_d:
                    # generar demo
                    build_demo_cycle()

        draw()
        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()

    main()
