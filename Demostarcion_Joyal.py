import pygame
import math
import sys
import numpy as np
from collections import deque
import tkinter as tk
from tkinter import simpledialog, messagebox

#############################################################
# CONFIGURACIÓN GENERAL
#############################################################

pygame.init()
WIDTH, HEIGHT = 900, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Proyecto MD - Demostración de Joyal (Versión Local)")
FONT = pygame.font.SysFont(None, 26)
FONT_BOLD = pygame.font.SysFont(None, 28, bold=True)

MOD = 30  # módulo para Hill

#############################################################
# UTILIDADES PARA CIFRADO HILL Y MATRICES
#############################################################

ALPHABET = {chr(ord('A') + i): i for i in range(26)}
ALPHABET["Ñ"] = 26
ALPHABET[","] = 27
ALPHABET["."] = 28
ALPHABET[" "] = 29
REV = {v: k for k, v in ALPHABET.items()}


def char_to_num(c):
    c = c.upper()
    return ALPHABET.get(c, 29)


def num_to_char(n):
    return REV.get(n % MOD, " ")


def determinante_bareiss(mat):
    n = len(mat)
    A = [row[:] for row in mat]
    prev = 1
    sign = 1
    for k in range(n - 1):
        if A[k][k] == 0:
            for r in range(k + 1, n):
                if A[r][k] != 0:
                    A[k], A[r] = A[r], A[k]
                    sign *= -1
                    break
        pivot = A[k][k]
        if pivot == 0:
            return 0
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                A[i][j] = (A[i][j] * pivot - A[i][k] * A[k][j]) // prev
        prev = pivot
    return sign * A[n - 1][n - 1]


def adjugate_matrix(M):
    n = len(M)
    adj = [[0]*n for _ in range(n)]
    for i in range(n):
        for j in range(n):
            minor = [[M[r][c] for c in range(n) if c != j]
                     for r in range(n) if r != i]
            adj[j][i] = ((-1)**(i + j)) * determinante_bareiss(minor)
    return adj


def egcd(a, b):
    if b == 0:
        return (a, 1, 0)
    g, x1, y1 = egcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)


def inverse_matrix_mod(M, mod=30):
    det = determinante_bareiss(M) % mod
    g, x, _ = egcd(det, mod)
    if g != 1:
        return None
    det_inv = x % mod
    adj = adjugate_matrix(M)
    inv = [[(adj[i][j] * det_inv) % mod for j in range(len(M))]
           for i in range(len(M))]
    return inv


def mat_vec_mul(M, v, mod=30):
    return [sum(M[i][j] * v[j] for j in range(len(v))) % mod for i in range(len(v))]


#############################################################
# UTILIDADES DE JOYAL: PERMUTACIONES, VÉRTICES, ETC.
#############################################################

def ciclos_desde_funcion(f):
    n = len(f)
    visit = [False]*n
    ciclos = []
    for i in range(n):
        if not visit[i]:
            c = []
            x = i
            while not visit[x]:
                visit[x] = True
                c.append(x+1)
                x = f[x]
            ciclos.append(c)
    ciclos.sort(key=lambda x: min(x))
    return "".join("(" + " ".join(map(str, c)) + ")" for c in ciclos)


def depthfirstsearch(graph, start, goal, path=None, visited=None):
    if path is None: path = []
    if visited is None: visited = set()
    path = path + [start]
    visited.add(start)
    if start == goal:
        return path
    for nb in graph[start]:
        if nb not in visited:
            p = depthfirstsearch(graph, nb, goal, path, visited)
            if p:
                return p
    return None


def vertices_en_ciclo(f):
    n = len(f)
    g = {i: [f[i]] for i in range(n)}
    cyc = set()
    for u in range(n):
        v = f[u]
        g[u].remove(v)
        if depthfirstsearch(g, v, u):
            cyc.add(u)
            cyc.add(v)
        g[u].append(v)
    return sorted(cyc)


#############################################################
# CLASE PRINCIPAL DEL ESTADO DEL PROGRAMA
#############################################################

class Game:
    def __init__(self, n=9):
        self.n = n
        self.reset()

    def reset(self):
        self.radius = 300
        self.positions = [self.node_position(i) for i in range(self.n)]
        self.funcion = [None]*self.n
        self.state = "menu"   # menu, ingresar_funcion, ver_funcion, cifrado
        self.cadena = ""
        self.encriptado = ""
        self.matriz = None

    def node_position(self, i):
        cx, cy = WIDTH//2, HEIGHT//2 - 60
        angle = 2*math.pi*i/self.n - math.pi/2
        return (cx + int(self.radius*math.cos(angle)),
                cy + int(self.radius*math.sin(angle)))

    def draw(self):
        screen.fill((240, 240, 240))
        title = FONT_BOLD.render("Proyecto MD - Demostración de Joyal (Local)", True, (0,0,120))
        screen.blit(title, (20, 20))

        if self.state == "menu":
            self.draw_menu()

        elif self.state == "ingresar_funcion":
            self.draw_ingresar_funcion()

        elif self.state == "ver_funcion":
            self.draw_grafo_funcion()

        elif self.state == "cifrado":
            self.draw_cifrado()

        pygame.display.flip()

    def draw_menu(self):
        opts = [
            "1. Elegir valor de n",
            "2. Ingresar función f: {1..n}→{1..n}",
            "3. Ver grafo y permutación",
            "4. Cifrar/Descifrar con Hill",
            "5. Salir"
        ]
        y = 100
        for op in opts:
            t = FONT.render(op, True, (0,0,0))
            screen.blit(t, (80, y))
            y += 40

    def draw_ingresar_funcion(self):
        msg = FONT.render("Ingrese la función f como lista separada por comas:", True, (0,0,0))
        screen.blit(msg, (80, 120))
        box = FONT_BOLD.render(self.cadena, True, (0,0,120))
        screen.blit(box, (80, 170))

    def draw_grafo_funcion(self):
        if None in self.funcion:
            msg = FONT.render("Función incompleta.", True, (200,0,0))
            screen.blit(msg, (80, 120))
            return

        ciclos = ciclos_desde_funcion(self.funcion)
        msg = FONT_BOLD.render("Permutación: " + ciclos, True, (0,120,0))
        screen.blit(msg, (40, HEIGHT - 60))

        # Dibujo de aristas
        for i, f in enumerate(self.funcion):
            if i == f:
                continue
            x1, y1 = self.positions[i]
            x2, y2 = self.positions[f]
            pygame.draw.line(screen, (0,0,0), (x1,y1), (x2,y2), 3)

            # flecha
            dx, dy = x2-x1, y2-y1
            ang = math.atan2(dy, dx)
            head = 15
            left = (x2 - head*math.cos(ang - math.pi/6),
                    y2 - head*math.sin(ang - math.pi/6))
            right = (x2 - head*math.cos(ang + math.pi/6),
                     y2 - head*math.sin(ang + math.pi/6))
            pygame.draw.polygon(screen, (0,0,0), [(x2,y2), left, right])

        # Dibujo de vértices
        for i,pos in enumerate(self.positions):
            pygame.draw.circle(screen, (255,128,128), pos, 20)
            t = FONT.render(str(i+1), True, (255,255,255))
            screen.blit(t, (pos[0]-t.get_width()//2, pos[1]-t.get_height()//2))

    def draw_cifrado(self):
        msg = FONT.render("Texto ingresado:", True, (0,0,0))
        screen.blit(msg, (80, 120))
        t = FONT_BOLD.render(self.cadena, True, (0,0,120))
        screen.blit(t, (80, 160))

        msg2 = FONT.render("Resultado:", True, (0,0,0))
        screen.blit(msg2, (80, 240))
        t2 = FONT_BOLD.render(self.encriptado, True, (0,120,0))
        screen.blit(t2, (80, 280))

    #############################################################
    # EVENTOS DE TECLADO / MENÚ
    #############################################################

    def key_event(self, key):
        if self.state == "menu":
            if key == pygame.K_1:
                self.elegir_n()
            elif key == pygame.K_2:
                self.state = "ingresar_funcion"
                self.cadena = ""
            elif key == pygame.K_3:
                self.state = "ver_funcion"
            elif key == pygame.K_4:
                self.state = "cifrado"
                self.cadena = ""
                self.encriptado = ""
            elif key == pygame.K_5:
                pygame.quit()
                sys.exit()

        elif self.state == "ingresar_funcion":
            if key == pygame.K_RETURN:
                self.guardar_funcion()
            elif key == pygame.K_BACKSPACE:
                self.cadena = self.cadena[:-1]
            else:
                self.cadena += pygame.key.name(key)

        elif self.state == "cifrado":
            if key == pygame.K_RETURN:
                self.procesar_cifrado()
            elif key == pygame.K_BACKSPACE:
                self.cadena = self.cadena[:-1]
            else:
                self.cadena += pygame.key.name(key)

    #############################################################
    # FUNCIONALIDAD
    #############################################################

    def elegir_n(self):
        root = tk.Tk()
        root.withdraw()
        n = simpledialog.askinteger("Elegir n", "Ingrese un entero n ≥ 2:")
        if n and n >= 2:
            self.n = n
            self.reset()

    def guardar_funcion(self):
        try:
            vals = list(map(int, self.cadena.split(",")))
            if len(vals) != self.n:
                raise ValueError
            if any(x < 1 or x > self.n for x in vals):
                raise ValueError
            self.funcion = [x - 1 for x in vals]
            self.cadena = ""
            self.state = "ver_funcion"
        except:
            messagebox.showerror("Error", "Formato inválido. Ejemplo: 1,2,3,4,4")

    def get_matrix_from_function(self):
        n = self.n
        f = self.funcion
        mat = []
        for i in range(n):
            row = []
            for j in range(n):
                row.append((f[i] * (j + 1) + (f[j] + 1)) % MOD)
            mat.append(row)

        inv = inverse_matrix_mod(mat, MOD)
        if inv is None:
            # crear diagonal invertible
            mat = [[0]*n for _ in range(n)]
            for i in range(n):
                mat[i][i] = (3*(f[i]+1)+1) % MOD or 1
        return mat

    def procesar_cifrado(self):
        if None in self.funcion:
            messagebox.showerror("Error", "Primero ingrese una función válida")
            return

        self.matriz = self.get_matrix_from_function()
        text = self.cadena.upper()
        nums = [char_to_num(ch) for ch in text]

        # padding
        while len(nums) % self.n != 0:
            nums.append(29)

        enc = []
        for i in range(0, len(nums), self.n):
            block = nums[i:i+self.n]
            enc.extend(mat_vec_mul(self.matriz, block, MOD))

        self.encriptado = "".join(num_to_char(x) for x in enc)


#############################################################
# LOOP PRINCIPAL
#############################################################

game = Game()

clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            game.key_event(event.key)

    game.draw()
    clock.tick(30)
