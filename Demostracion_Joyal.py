# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                                                                            ║
# ║     PROYECTO MD - Demostración de Joyal a la Fórmula de Cayley             ║
# ║                                                                            ║
# ║     VERSIÓN PROFESIONAL - Interfaz Moderna y Fluida                        ║
# ║                                                                            ║
# ╠════════════════════════════════════════════════════════════════════════════╣
# ║                                                                            ║
# ║     CARACTERÍSTICAS:                                                       ║
# ║         1. Interfaz moderna con transiciones suaves                        ║
# ║         2. Sistema de estados bien separado (sin superposición)            ║
# ║         3. Animaciones y efectos visuales profesionales                    ║
# ║         4. Panel de control con información clara                          ║
# ║         5. Diseño responsivo y organizado                                  ║
# ║                                                                            ║
# ╚════════════════════════════════════════════════════════════════════════════╝

import pygame
import math
import numpy as np
from collections import deque
import sys

# ==============================================================================
# INICIALIZACIÓN
# ==============================================================================

pygame.init()

# Configuración de pantalla
WIDTH, HEIGHT = 1280, 900
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Demostración de Joyal - Fórmula de Cayley")

# Fuentes profesionales
try:
    FONT_TITLE = pygame.font.Font(None, 48)
    FONT_SUBTITLE = pygame.font.Font(None, 32)
    FONT_BOLD = pygame.font.Font(None, 28)
    FONT_REGULAR = pygame.font.Font(None, 24)
    FONT_SMALL = pygame.font.Font(None, 20)
    FONT_TINY = pygame.font.Font(None, 16)
except:
    FONT_TITLE = pygame.font.SysFont('Arial', 48, bold=True)
    FONT_SUBTITLE = pygame.font.SysFont('Arial', 32, bold=True)
    FONT_BOLD = pygame.font.SysFont('Arial', 28, bold=True)
    FONT_REGULAR = pygame.font.SysFont('Arial', 24)
    FONT_SMALL = pygame.font.SysFont('Arial', 20)
    FONT_TINY = pygame.font.SysFont('Arial', 16)

# Paleta de colores profesional
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

# Variables globales
n = 6
vertice_pos = []
vertice_rad = 28
aristas = []
grafo = []
parent = []

# ==============================================================================
# COMPONENTES DE UI PROFESIONALES
# ==============================================================================

class ProfessionalButton:
    def __init__(self, x, y, width, height, text, color=COLORS['accent'], hover_color=COLORS['info']):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.is_hovered = False
        self.is_clicked = False
        self.shadow_offset = 3
        self.border_radius = 8
        
    def draw(self, surface):
        # Sombra
        shadow_rect = self.rect.move(self.shadow_offset, self.shadow_offset)
        pygame.draw.rect(surface, (220, 220, 220), shadow_rect, border_radius=self.border_radius)
        
        # Fondo del botón
        pygame.draw.rect(surface, self.current_color, self.rect, border_radius=self.border_radius)
        
        # Borde
        border_color = COLORS['white'] if self.is_hovered else COLORS['accent']
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=self.border_radius)
        
        # Texto
        text_surf = FONT_BOLD.render(self.text, True, COLORS['white'])
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
        
        # Efecto de hover
        if self.is_hovered:
            overlay = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 30))
            surface.blit(overlay, self.rect)
    
    def update(self, mouse_pos):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.current_color = self.hover_color if self.is_hovered else self.color
        return self.is_hovered
    
    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.is_hovered:
                self.is_clicked = True
                return True
        return False

class InputField:
    def __init__(self, x, y, width, height, label="", placeholder=""):
        self.rect = pygame.Rect(x, y, width, height)
        self.label = label
        self.placeholder = placeholder
        self.text = ""
        self.active = False
        self.cursor_visible = True
        self.cursor_timer = 0
        
    def draw(self, surface):
        # Dibujar etiqueta primero (si existe)
        if self.label:
            label_surf = FONT_SMALL.render(self.label, True, COLORS['dark'])
            surface.blit(label_surf, (self.rect.x, self.rect.y - 25))
        
        # Sombra
        shadow_rect = self.rect.move(2, 2)
        pygame.draw.rect(surface, (220, 220, 220), shadow_rect, border_radius=6)
        
        # Fondo
        bg_color = COLORS['white'] if not self.active else (250, 250, 255)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=6)
        
        # Borde
        border_color = COLORS['accent'] if self.active else COLORS['gray']
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=6)
        
        # Texto o placeholder
        display_text = self.text if self.text else self.placeholder
        text_color = COLORS['dark'] if self.text else COLORS['gray']
        text_surf = FONT_REGULAR.render(display_text, True, text_color)
        
        # Recortar si es necesario
        max_width = self.rect.width - 20
        if text_surf.get_width() > max_width:
            # Crear texto recortado
            temp_text = display_text
            while FONT_REGULAR.render(temp_text + "...", True, text_color).get_width() > max_width and len(temp_text) > 1:
                temp_text = temp_text[:-1]
            text_surf = FONT_REGULAR.render(temp_text + "...", True, text_color)
        
        text_x = self.rect.x + 10
        text_y = self.rect.y + (self.rect.height - text_surf.get_height()) // 2
        surface.blit(text_surf, (text_x, text_y))
        
        # Cursor
        if self.active and self.cursor_visible:
            cursor_x = text_x + text_surf.get_width()
            pygame.draw.line(surface, COLORS['accent'], 
                           (cursor_x, text_y + 2),
                           (cursor_x, text_y + text_surf.get_height() - 2), 2)
    
    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 500:  # Parpadeo cada 500ms
            self.cursor_visible = not self.cursor_visible
            self.cursor_timer = 0
    
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
                if event.unicode.isprintable() and len(self.text) < 50:
                    self.text += event.unicode
        return False
    
    def get_value(self):
        return self.text.strip()

# ==============================================================================
# PANTALLA DE SELECCIÓN DE N
# ==============================================================================

class NSelectionScreen:
    def __init__(self):
        self.title = "CONFIGURACIÓN INICIAL"
        self.subtitle = "Fórmula de Cayley: n^(n-2) árboles etiquetados"
        
        # Campo de entrada
        input_width = 300
        input_x = WIDTH // 2 - input_width // 2
        self.n_input = InputField(input_x, 350, input_width, 50, 
                                 "NÚMERO DE VÉRTICES (n ≥ 2)", "Ej: 6")
        
        # Botón de confirmación
        btn_width = 200
        btn_x = WIDTH // 2 - btn_width // 2
        self.confirm_btn = ProfessionalButton(btn_x, 450, btn_width, 50, "CONTINUAR", COLORS['success'])
        
        # Botón de información
        self.info_btn = ProfessionalButton(WIDTH - 120, 30, 100, 40, "ℹ️ INFO", COLORS['info'])
        
        self.error_message = ""
        self.selected_n = 6
        
    def draw(self, surface):
        # Fondo general
        surface.fill(COLORS['background'])

        # Encabezado
        header_rect = pygame.Rect(0, 0, WIDTH, 130)
        pygame.draw.rect(surface, COLORS['header'], header_rect)

        # Título
        title_surf = FONT_TITLE.render(self.title, True, COLORS['white'])
        surface.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 30))

        # Subtítulo
        subtitle_surf = FONT_SUBTITLE.render(self.subtitle, True, COLORS['light'])
        surface.blit(subtitle_surf, (WIDTH//2 - subtitle_surf.get_width()//2, 80))

        # Panel central (más grande y con más aire)
        panel_rect = pygame.Rect(WIDTH//2 - 320, 170, 640, 420)
        pygame.draw.rect(surface, COLORS['white'], panel_rect, border_radius=15)
        pygame.draw.rect(surface, COLORS['accent'], panel_rect, 3, border_radius=15)

        # --- Encabezado dentro del panel (rectángulo en vez de círculo) ---
        header_w = 500
        header_h = 70
        header_x = WIDTH//2 - header_w//2
        header_y = 195

        header_rect = pygame.Rect(header_x, header_y, header_w, header_h)
        pygame.draw.rect(surface, COLORS['info'], header_rect, border_radius=20)

        # Texto dentro del nuevo encabezado
        header_text = FONT_REGULAR.render("DEMOSTRACIÓN MEDIANTE EL MÉTODO DE JOYAL", True, COLORS['white'])
        surface.blit(header_text, (WIDTH//2 - header_text.get_width()//2,
                                header_y + header_h//2 - header_text.get_height()//2))

        # Instrucciones (limpias, sin recomendación)
        instructions = [
            "Ingrese el número de vértices (n).",
            "Cayley: número de árboles = n^(n−2)."
        ]

        base_y = 310
        for i, line in enumerate(instructions):
            text = FONT_REGULAR.render(line, True, COLORS['dark'])
            surface.blit(text, (WIDTH//2 - text.get_width()//2, base_y + i * 28))

        # Input (posición correcta)
        self.n_input.rect.y = 400
        self.n_input.draw(surface)

        # Botón continuar
        self.confirm_btn.rect.y = 455
        self.confirm_btn.draw(surface)

        # Error
        if self.error_message:
            err = FONT_SMALL.render(self.error_message, True, COLORS['danger'])
            surface.blit(err, (WIDTH//2 - err.get_width()//2, 520))

        # Resultado fórmula (bien separado)
        try:
            temp_n = int(self.n_input.get_value() or "6")
            if 2 <= temp_n <= 20:
                result = FONT_BOLD.render(
                    f"n = {temp_n}: {temp_n}^({temp_n}-2) = {temp_n**(temp_n-2):,} árboles",
                    True, COLORS['success']
                )
                surface.blit(result, (WIDTH//2 - result.get_width()//2, 560))
                self.selected_n = temp_n
        except:
            pass

        # Botón info
        self.info_btn.draw(surface)

    def update(self, mouse_pos, dt):
        self.n_input.update(dt)
        self.confirm_btn.update(mouse_pos)
        self.info_btn.update(mouse_pos)
    
    def handle_event(self, event):
        if self.n_input.handle_event(event):
            self.validate_input()
        
        if self.confirm_btn.handle_event(event):
            if self.validate_input():
                return True
        
        if self.info_btn.handle_event(event):
            self.show_info()
        
        return False
    
    def validate_input(self):
        try:
            n_val = int(self.n_input.get_value() or "0")
            if n_val < 2:
                self.error_message = "El número debe ser al menos 2"
                return False
            elif n_val > 30:
                self.error_message = "Para mejor rendimiento, use n ≤ 30"
                return False
            else:
                self.error_message = ""
                self.selected_n = n_val
                return True
        except ValueError:
            self.error_message = "Ingrese un número válido"
            return False
    
    def show_info(self):
        self.error_message = "Ingrese el número de vértices del árbol (ej: 6)"

# ============================================================================== 
# PANTALLA PRINCIPAL (REEMPLAZAR ESTA CLASE) 
# ==============================================================================

class MainMenuScreen:
    def __init__(self):
        self.title = f"DEMOSTRACIÓN DE JOYAL - n = {n}"

        # Panel izquierdo (botones + texto)
        self.left_x = 70
        self.left_width = 550

        # Botones principales
        self.btn_mode1 = ProfessionalButton(self.left_x + 100, 360, 300, 80,
                                            "MODO 1\nÁRBOL → FUNCIÓN", COLORS['info'])

        self.btn_mode2 = ProfessionalButton(self.left_x + 100, 460, 300, 80,
                                            "MODO 2\nFUNCIÓN → ÁRBOL", COLORS['success'])

        self.btn_reset = ProfessionalButton(self.left_x + 150, 570, 200, 60,
                                            "REINICIAR", COLORS['warning'])

        self.btn_back = ProfessionalButton(30, 30, 120, 40, "← VOLVER", COLORS['gray'])

    def draw(self, surface):
        surface.fill(COLORS['background'])

        # Encabezado con gradiente
        header_rect = pygame.Rect(0, 0, WIDTH, 160)
        for y in range(header_rect.height):
            color_val = 30 + int(40 * (y / header_rect.height))
            pygame.draw.line(surface, (color_val, 60, 114), (0, y), (WIDTH, y))

        # Título centrado
        title_surf = FONT_TITLE.render(self.title, True, COLORS['white'])
        surface.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 30))

        # Subtítulo (fórmula)
        formula = FONT_SUBTITLE.render(
            f"Fórmula de Cayley: n^(n-2) = {n}^({n}-2) = {n**(n-2):,}",
            True,
            COLORS['light']
        )
        surface.blit(formula, (WIDTH//2 - formula.get_width()//2, 90))

        # PANEL IZQUIERDO (texto + botones)
        left_panel = pygame.Rect(self.left_x - 20, 180, self.left_width, 520)
        pygame.draw.rect(surface, COLORS['white'], left_panel, border_radius=20)
        pygame.draw.rect(surface, COLORS['accent'], left_panel, 3, border_radius=20)

        # Texto explicativo
        desc_lines = [
            "Esta aplicación demuestra la biyección de Joyal para la",
            "fórmula de Cayley, que establece una correspondencia entre",
            "árboles etiquetados y funciones f: V → V.",
            "",
            "Seleccione un modo de operación:"
        ]

        base_y = 210
        panel_center = self.left_x + self.left_width // 2

        for i, line in enumerate(desc_lines):
            line_surf = FONT_REGULAR.render(line, True, COLORS['dark'])
            surface.blit(
                line_surf,
                (panel_center - line_surf.get_width() // 2,
                base_y + i * 28)
            )
   
        # Botones
        self.btn_mode1.draw(surface)
        self.btn_mode2.draw(surface)
        self.btn_reset.draw(surface)
        self.btn_back.draw(surface)

        # PREVIEW DEL ÁRBOL — AHORA A LA DERECHA
        self.draw_vertices_preview(surface)

    def draw_vertices_preview(self, surface):
        # Círculo centrado a la derecha
        center_x = WIDTH - 350
        center_y = 480

        # Radio dinámico
        if n <= 8:
            radius = 120
        elif n <= 15:
            radius = 170
        elif n <= 25:
            radius = 210
        else:
            radius = 260

        num_vertices = n

        # Dibujar vértices
        for i in range(num_vertices):
            angle = 2 * math.pi * i / num_vertices - math.pi/2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)

            pygame.draw.circle(surface, COLORS['vertex'], (int(x), int(y)), vertice_rad)
            pygame.draw.circle(surface, COLORS['white'], (int(x), int(y)), vertice_rad, 2)

            num_surf = FONT_BOLD.render(str(i+1), True, COLORS['white'])
            surface.blit(num_surf, (int(x)-num_surf.get_width()//2,
                                    int(y)-num_surf.get_height()//2))

        # Texto informativo
        info = FONT_SMALL.render(f"Mostrando {num_vertices} vértices", True, COLORS['gray'])
        surface.blit(info, (center_x - info.get_width()//2, center_y + radius + 30))

    def update(self, mouse_pos, dt):
        self.btn_mode1.update(mouse_pos)
        self.btn_mode2.update(mouse_pos)
        self.btn_reset.update(mouse_pos)
        self.btn_back.update(mouse_pos)

    def handle_event(self, event):
        if self.btn_mode1.handle_event(event): return "MODE1"
        if self.btn_mode2.handle_event(event): return "MODE2"
        if self.btn_reset.handle_event(event): return "RESET"
        if self.btn_back.handle_event(event): return "BACK"
        return None

# ============================================================================
# MODO 1 — ÁRBOL → FUNCIÓN (Versión final mejorada para panel e interfaz)
# ============================================================================

class TreeToFunctionMode:
    def __init__(self):
        self.title = "MODO 1: ÁRBOL → FUNCIÓN"

        self.step = 0
        self.selected_vertex = None
        self.start_vertex = None
        self.end_vertex = None

        self.function = [None] * n
        self.spine_edges = []
        self.directed_edges = []
        self.spine_path = None

        # Botones superiores
        self.btn_back = ProfessionalButton(30, 25, 130, 45, "← MENÚ", COLORS["gray"])
        self.btn_reset = ProfessionalButton(WIDTH - 170, 25, 140, 45, "REINICIAR", COLORS["warning"])

        # Botones inferiores — estilo final (A la izquierda y derecha)
        button_width = 170
        button_height = 48
        y = HEIGHT - 125

        self.btn_prev = ProfessionalButton(440, y, button_width, button_height, "← Atrás", COLORS["gray"])
        self.btn_next = ProfessionalButton(WIDTH - button_width - 50, y, button_width, button_height, "Continuar →", COLORS["success"])


        # Panel izquierdo
        self.info_panel = pygame.Rect(40, 120, 360, HEIGHT - 220)

        # Área del árbol
        self.graph_area = pygame.Rect(430, 120, WIDTH - 470, HEIGHT - 260)

        # Posicionamiento mejorado
        self.vertex_pos = []
        self.compute_vertex_positions()

    # -------------------------------------------------------------------------
    def compute_vertex_positions(self):
        """ Genera los vértices en un círculo dentro del área del grafo. """
        cx = self.graph_area.x + self.graph_area.width // 2
        cy = self.graph_area.y + self.graph_area.height // 2

        # Radio dinámico — SIEMPRE centrado y sin salirse
        base = min(self.graph_area.width, self.graph_area.height) * 0.38
        radius = int(max(80, base - n * 6))   # seguro y proporcional a n

        self.vertex_pos = []
        for i in range(n):
            angle = 2 * math.pi * i / n - math.pi / 2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            self.vertex_pos.append((int(x), int(y)))

    # -------------------------------------------------------------------------
    def draw(self, surface):
        surface.fill(COLORS["background"])

        # Encabezado
        pygame.draw.rect(surface, COLORS["info"], (0, 0, WIDTH, 80))
        title_surf = FONT_TITLE.render(self.title, True, COLORS["white"])
        surface.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 22))

        # Instrucciones
        instr = FONT_REGULAR.render(self.get_instructions(), True, COLORS["dark"])
        surface.blit(instr, (WIDTH//2 - instr.get_width()//2, 85))

        # Panel izquierdo (info)
        pygame.draw.rect(surface, COLORS["white"], self.info_panel, border_radius=12)
        pygame.draw.rect(surface, COLORS["accent"], self.info_panel, 2, border_radius=12)
        self.draw_info_panel(surface)

        # Área del árbol (derecha)
        pygame.draw.rect(surface, COLORS["white"], self.graph_area, border_radius=12)
        pygame.draw.rect(surface, COLORS["accent"], self.graph_area, 2, border_radius=12)
        self.draw_tree(surface)

        # Botones superiores
        self.btn_back.draw(surface)
        self.btn_reset.draw(surface)

        # Botones inferiores (si aplica)
        if self.step > 0:
            self.btn_prev.draw(surface)
        if self.step < 3 and self.check_step_complete():
            self.btn_next.draw(surface)

        # Indicador de pasos (ajustado para dejar espacio a botones)
        self.draw_step_indicator(surface)

    # -------------------------------------------------------------------------
    def get_instructions(self):
        texts = [
            "PASO 1: Construya el árbol haciendo clic en dos vértices.",
            "PASO 2: Seleccione el vértice INICIAL de la vértebra.",
            "PASO 3: Seleccione el vértice FINAL de la vértebra.",
            "PASO 4: Función generada correctamente."
        ]
        return texts[self.step]

    # -------------------------------------------------------------------------
    def draw_tree(self, surface):
        # Aristas (base)
        for v1, v2 in aristas:
            x1, y1 = self.vertex_pos[v1]
            x2, y2 = self.vertex_pos[v2]

            color = COLORS["edge"]
            width = 3
            if (v1, v2) in self.spine_edges or (v2, v1) in self.spine_edges:
                color = COLORS["spine"]
                width = 5
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), width)

        # Aristas orientadas (flechas)
        for v1, v2 in self.directed_edges:
            self.draw_arrow(surface, self.vertex_pos[v1], self.vertex_pos[v2], COLORS["arrow"])

        # Vértices
        self.draw_vertices(surface)

        # Destacar inicio y fin
        if self.start_vertex is not None:
            self.highlight_vertex(surface, self.start_vertex, COLORS["success"])
        if self.end_vertex is not None:
            self.highlight_vertex(surface, self.end_vertex, COLORS["danger"])

    # -------------------------------------------------------------------------
    def draw_vertices(self, surface):
        for i, pos in enumerate(self.vertex_pos):
            # Sombra
            pygame.draw.circle(surface, (80, 80, 80), (pos[0] + 2, pos[1] + 2), vertice_rad)

            color = COLORS["vertex"]
            if i == self.selected_vertex:
                color = COLORS["highlight"]
            if i == self.start_vertex:
                color = COLORS["success"]
            if i == self.end_vertex:
                color = COLORS["danger"]

            pygame.draw.circle(surface, color, pos, vertice_rad)
            pygame.draw.circle(surface, COLORS["white"], pos, vertice_rad, 2)

            label = FONT_BOLD.render(str(i+1), True, COLORS["white"])
            surface.blit(label, (pos[0] - label.get_width()//2, pos[1] - label.get_height()//2))

    # -------------------------------------------------------------------------
    def draw_arrow(self, surface, start, end, color):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        L = math.hypot(dx, dy)
        if L == 0:
            return

        start_adj = (start[0] + dx / L * vertice_rad, start[1] + dy / L * vertice_rad)
        end_adj = (end[0] - dx / L * vertice_rad, end[1] - dy / L * vertice_rad)

        pygame.draw.line(surface, color, start_adj, end_adj, 3)
        angle = math.atan2(dy, dx)
        s = 12
        p1 = (end_adj[0] - s*math.cos(angle - 0.5), end_adj[1] - s*math.sin(angle - 0.5))
        p2 = (end_adj[0] - s*math.cos(angle + 0.5), end_adj[1] - s*math.sin(angle + 0.5))
        pygame.draw.polygon(surface, color, [end_adj, p1, p2])

    def highlight_vertex(self, surface, i, color):
        pos = self.vertex_pos[i]
        pygame.draw.circle(surface, color, pos, vertice_rad + 5, 3)

    # -------------------------------------------------------------------------
    def draw_info_panel(self, surface):
        x = self.info_panel.x + 20
        y = self.info_panel.y + 20

        # Título
        surface.blit(FONT_BOLD.render("INFORMACIÓN DEL ÁRBOL", True, COLORS["accent"]), (x, y))
        y += 40

        # Datos principales
        info_lines = [
            f"Vértices: {n}",
            f"Aristas: {len(aristas)}/{n-1}",
            f"Conectado: {'Sí' if self.is_connected() else 'No'}",
            f"Paso actual: {self.step+1}/4",
        ]
        if self.start_vertex is not None:
            info_lines.append(f"Inicio: {self.start_vertex+1}")
        if self.end_vertex is not None:
            info_lines.append(f"Fin: {self.end_vertex+1}")

        for txt in info_lines:
            surface.blit(FONT_SMALL.render(txt, True, COLORS["dark"]), (x, y))
            y += 20

        # Separador
        y += 6
        pygame.draw.line(surface, COLORS["light"], (x, y), (self.info_panel.right - 20, y), 2)
        y += 12

        # VÉRTEBRA (mostrar solo números, ordenada)
        if self.spine_path:
            surface.blit(FONT_BOLD.render("VÉRTEBRA:", True, COLORS["spine"]), (x, y))
            y += 26

            # Mostrar sin prefijo 'V' y con separación clara:
            spine_txt = "  •  ".join(str(v+1) for v in self.spine_path)
            # Si muy larga, romper en varias líneas
            max_px = self.info_panel.width - 40
            rendered = FONT_TINY.render(spine_txt, True, COLORS["dark"])
            if rendered.get_width() <= max_px:
                surface.blit(FONT_TINY.render(spine_txt, True, COLORS["dark"]), (x, y))
                y += 26
            else:
                # partir en bloques de tamaño razonable
                parts = []
                current = ""
                for token in (str(v+1) for v in self.spine_path):
                    if FONT_TINY.size(current + "  " + token)[0] < max_px:
                        current = (current + "  " + token).strip()
                    else:
                        parts.append(current)
                        current = token
                if current:
                    parts.append(current)
                for p in parts:
                    surface.blit(FONT_TINY.render(p, True, COLORS["dark"]), (x, y))
                    y += 20
                y += 6

        # ARISTAS ORIENTADAS (formato u → v), con envoltura si hay muchas
        if self.directed_edges:
            surface.blit(FONT_BOLD.render("ARISTAS ORIENTADAS:", True, COLORS["info"]), (x, y))
            y += 26

            # Preparamos líneas agrupadas por columnas para que entren ordenadamente
            max_px = self.info_panel.width - 40
            col_texts = []
            cur_line = ""
            for (u, v) in self.directed_edges:
                pair = f"{u+1} → {v+1}"
                if FONT_TINY.size(cur_line + "   " + pair)[0] < max_px:
                    cur_line = (cur_line + "   " + pair).strip()
                else:
                    col_texts.append(cur_line)
                    cur_line = pair
            if cur_line:
                col_texts.append(cur_line)

            # Renderizamos las líneas resultantes
            for line in col_texts:
                surface.blit(FONT_TINY.render(line, True, COLORS["dark"]), (x, y))
                y += 18
            y += 6

        # FUNCIÓN (cuando paso 3 = completado)
        if self.step == 3:
            surface.blit(FONT_BOLD.render("FUNCIÓN:", True, COLORS["success"]), (x, y))
            y += 26
            for i in range(n):
                fv = self.function[i]
                txt = f"f({i+1}) = {fv+1 if fv is not None else '?'}"
                surface.blit(FONT_TINY.render(txt, True, COLORS["dark"]), (x, y))
                y += 16

    # -------------------------------------------------------------------------
    def draw_step_indicator(self, surface):
        steps = ["1. Construir", "2. Inicio", "3. Fin", "4. Listo"]
        # Ubicar indicador ligeramente por encima de los botones inferiores
        x = WIDTH // 2 - 100
        y = HEIGHT - 185

        for i in range(4):
            color = COLORS["gray"]
            if i < self.step:
                color = COLORS["success"]
            elif i == self.step:
                color = COLORS["info"]

            box = pygame.Rect(x + i * 150, y, 140, 36)
            pygame.draw.rect(surface, color, box, border_radius=10)
            pygame.draw.rect(surface, COLORS["white"], box, 2, border_radius=10)

            txt = FONT_SMALL.render(steps[i], True, COLORS["white"])
            surface.blit(txt, (box.centerx - txt.get_width()//2,
                               box.centery - txt.get_height()//2))

    # -------------------------------------------------------------------------
    # LÓGICA
    # -------------------------------------------------------------------------
    def is_connected(self):
        root = find(0)
        return all(find(i) == root for i in range(n))

    def check_step_complete(self):
        if self.step == 0:
            return len(aristas) == n-1 and self.is_connected()
        if self.step == 1:
            return self.start_vertex is not None
        if self.step == 2:
            return self.end_vertex is not None
        return True

    def handle_vertex_click(self, i):
        if self.step == 0:
            if self.selected_vertex is None:
                self.selected_vertex = i
            else:
                if i != self.selected_vertex:
                    self.add_edge(self.selected_vertex, i)
                self.selected_vertex = None

                if len(aristas) == n-1 and self.is_connected():
                    self.step = 1

        elif self.step == 1:
            self.start_vertex = i
            self.step = 2

        elif self.step == 2:
            if i != self.start_vertex:
                self.end_vertex = i
                self.calculate_function()
                self.step = 3

    def add_edge(self, v1, v2):
        if (v1, v2) in aristas or (v2, v1) in aristas:
            return
        if find(v1) == find(v2):
            return

        aristas.append((v1, v2))
        union(v1, v2)
        grafo[v1].append(v2)
        grafo[v2].append(v1)

    # -------------------------------------------------------------------------
    def calculate_function(self):
        self.spine_path = self.find_path(self.start_vertex, self.end_vertex)

        # Generar vértebra y aristas de vértebra
        if len(self.spine_path) > 1:
            self.spine_edges = [(self.spine_path[i], self.spine_path[i+1])
                                for i in range(len(self.spine_path)-1)]

            # Emparejamiento de la biyección (Joyal)
            sorted_spine = sorted(self.spine_path)
            reversed_spine = list(reversed(self.spine_path))
            for i in range(len(sorted_spine)):
                self.function[sorted_spine[i]] = reversed_spine[i]

        # Aristas orientadas fuera de la vértebra
        self.directed_edges = self.direct_edges()

        # Completar función con aristas orientadas
        for v1, v2 in self.directed_edges:
            self.function[v1] = v2

    def find_path(self, start, end):
        visited = [False] * n
        parent = [-1] * n
        q = deque([start])
        visited[start] = True

        while q:
            v = q.popleft()
            if v == end:
                path = []
                while v != -1:
                    path.append(v)
                    v = parent[v]
                return list(reversed(path))

            for u in grafo[v]:
                if not visited[u]:
                    visited[u] = True
                    parent[u] = v
                    q.append(u)
        return [start, end]

    def direct_edges(self):
        dist = [-1] * n
        q = deque([self.end_vertex])
        dist[self.end_vertex] = 0

        while q:
            v = q.popleft()
            for u in grafo[v]:
                if dist[u] == -1:
                    dist[u] = dist[v] + 1
                    q.append(u)

        out = []
        for v1, v2 in aristas:
            if (v1, v2) in self.spine_edges or (v2, v1) in self.spine_edges:
                continue
            if dist[v1] > dist[v2]:
                out.append((v1, v2))
            else:
                out.append((v2, v1))

        return out

    # -------------------------------------------------------------------------
    def update(self, mouse_pos, dt):
        self.btn_back.update(mouse_pos)
        self.btn_reset.update(mouse_pos)
        self.btn_prev.update(mouse_pos)
        self.btn_next.update(mouse_pos)

    def handle_event(self, event):
        if self.btn_back.handle_event(event):
            return "BACK"
        if self.btn_reset.handle_event(event):
            self.reset()
            return "RESET"
        if self.btn_prev.handle_event(event) and self.step > 0:
            self.step -= 1
        if self.btn_next.handle_event(event) and self.check_step_complete() and self.step < 3:
            self.step += 1

        # Click en vértices
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            for i, pos in enumerate(self.vertex_pos):
                if (mx - pos[0])**2 + (my - pos[1])**2 <= vertice_rad**2:
                    self.handle_vertex_click(i)
                    break
        return None

    def reset(self):
        global aristas, grafo, parent
        aristas.clear()
        grafo = [[] for _ in range(n)]
        parent = list(range(n))

        self.step = 0
        self.selected_vertex = None
        self.start_vertex = None
        self.end_vertex = None
        self.function = [None] * n
        self.spine_edges.clear()
        self.directed_edges.clear()
        self.spine_path = None

        self.compute_vertex_positions()

# ==========================
# Clase corregida FunctionToTreeMode
# Reemplaza la clase anterior por esta
# Usa globals existentes: pygame, math, n, vertice_rad,
# InputField, ProfessionalButton, COLORS, FONT_*, WIDTH, HEIGHT
# ==========================

class FunctionToTreeMode:
    def __init__(self):
        self.title = "MODO 2: FUNCIÓN → ÁRBOL"

        # estado
        self.function = []                     # list 0-based
        self.cycles_list = []                  # list of cycles (each cycle is list of ints 0-based, ordered)
        self.vertices_in_cycles = []           # ordered list of vertices in cycles (concatenation of cycles)
        self.vertices_not_in_cycles = []       # list of other vertices
        self.spine_edges = []                  # list of (u,v)
        self.tree_edges = []                   # list of (u,v)
        self.error_message = ""
        self.success_message = ""

        # estado de flujo
        self.function_submitted = False
        self.tree_built = False

        # panels (match your layout: left input, right viz, bottom info)
        left_x = 36
        left_w = 420
        top = 115
        margin = 36

        self.left_panel = pygame.Rect(left_x, top, left_w, HEIGHT - top - margin)
        self.right_panel = pygame.Rect(self.left_panel.right + 20, top, WIDTH - self.left_panel.right - margin, int((HEIGHT - top - margin) * 0.62))
        self.info_panel = pygame.Rect(self.right_panel.x, self.right_panel.bottom + 14, self.right_panel.width, HEIGHT - self.right_panel.bottom - margin - 14)

        # input field (place it with enough top margin)
        self.func_input = InputField(self.left_panel.x + 28, self.left_panel.y + 120, self.left_panel.width - 56, 54,
                                     "FUNCIÓN f:", f"Ej: 2,3,1,5,5,4  (n={n})")

        # botones (alineados y con suficiente gap)
        bw = 170; bh = 48; gap = 14
        bx = self.left_panel.x + (self.left_panel.width - (bw*2 + gap)) // 2
        self.btn_send = ProfessionalButton(bx, self.func_input.rect.bottom + 20, bw, bh, "ENVIAR FUNCIÓN", COLORS['success'])
        self.btn_build = ProfessionalButton(bx + bw + gap, self.func_input.rect.bottom + 20, bw, bh, "CONSTRUIR ÁRBOL", COLORS['accent'])
        self.btn_clear = ProfessionalButton(bx, self.btn_send.rect.bottom + 14, bw, bh - 6, "LIMPIAR", COLORS['warning'])
        self.btn_menu = ProfessionalButton(self.left_panel.x + 18, self.left_panel.bottom - 62, 100, 44, "Menú", COLORS['gray'])

        # posiciones de vértices
        self.vertex_pos = []
        self.compute_vertex_positions()

    # -------------------------
    # posiciones
    # -------------------------
    def compute_vertex_positions(self):
        cx = self.right_panel.x + self.right_panel.width // 2
        cy = self.right_panel.y + self.right_panel.height // 2
        # radio adaptativo
        radius = min(250, self.right_panel.width // 2 - 40)
        radius = max(radius, 100)
        self.vertex_pos = []
        for i in range(n):
            angle = 2 * math.pi * i / n - math.pi/2
            x = cx + radius * math.cos(angle)
            y = cy + radius * math.sin(angle)
            self.vertex_pos.append((int(x), int(y)))

    # -------------------------
    # dibujado general
    # -------------------------
    def draw(self, surface):
        surface.fill(COLORS['background'])
        self._draw_header(surface)
        self._draw_left_panel(surface)
        self._draw_right_panel(surface)
        if self.function_submitted or self.tree_built:
            self._draw_info_panel(surface)
        self._draw_status(surface)
        self.btn_menu.draw(surface)

    def _draw_header(self, surface):
        header_rect = pygame.Rect(0, 0, WIDTH, 100)
        pygame.draw.rect(surface, COLORS['header'], header_rect)
        title_surf = FONT_TITLE.render(self.title, True, COLORS['white'])
        surface.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 26))

    # -------------------------
    # izquierda: input + instrucciones + botones
    # -------------------------
    def _draw_left_panel(self, surface):
        shadow = self.left_panel.move(4,4)
        pygame.draw.rect(surface, (220,220,220), shadow, border_radius=14)
        pygame.draw.rect(surface, COLORS['white'], self.left_panel, border_radius=14)
        pygame.draw.rect(surface, COLORS['accent'], self.left_panel, 3, border_radius=14)

        # title
        t = FONT_BOLD.render("ENTRADA DE FUNCIÓN", True, COLORS['accent'])
        surface.blit(t, (self.left_panel.x + 22, self.left_panel.y + 18))

        # instrucciones con spacing suficiente (evita solapamiento)
        y = self.left_panel.y + 56
        lines = [
            f"Ingrese f: {{1..{n}}} → {{1..{n}}}",
            f"Debe contener exactamente {n} valores, separados por comas.",
            "Pulse ENVIAR FUNCIÓN para validar y mostrar la función (flechas).",
            "Luego pulse CONSTRUIR ÁRBOL para generar el árbol final."
        ]
        for line in lines:
            surface.blit(FONT_SMALL.render(line, True, COLORS['dark']), (self.left_panel.x + 22, y))
            y += 22

        # input y botones
        self.func_input.draw(surface)
        self.btn_send.draw(surface)
        self.btn_build.draw(surface)
        self.btn_clear.draw(surface)

    # -------------------------
    # derecha: visualización
    # -------------------------
    def _draw_right_panel(self, surface):
        shadow = self.right_panel.move(4,4)
        pygame.draw.rect(surface, (220,220,220), shadow, border_radius=12)
        pygame.draw.rect(surface, COLORS['white'], self.right_panel, border_radius=12)
        pygame.draw.rect(surface, COLORS['accent'], self.right_panel, 3, border_radius=12)

        title = FONT_BOLD.render("VISUALIZACIÓN", True, COLORS['accent'])
        surface.blit(title, (self.right_panel.x + 18, self.right_panel.y + 12))

        # si no hay función enviada
        if not self.function_submitted and not self.tree_built:
            msg = FONT_REGULAR.render("Aún no se ha enviado la función.", True, COLORS['gray'])
            sub = FONT_SMALL.render("Ingrese la función y presione ENVIAR FUNCIÓN.", True, COLORS['gray'])
            surface.blit(msg, (self.right_panel.centerx - msg.get_width()//2, self.right_panel.centery - 14))
            surface.blit(sub, (self.right_panel.centerx - sub.get_width()//2, self.right_panel.centery + 10))
            return

        # si la función fue enviada y árbol no construido -> dibujar flechas f(i)
        if self.function_submitted and not self.tree_built:
            # draw light arrows
            for i, f in enumerate(self.function):
                if f is None:
                    continue
                p1 = self.vertex_pos[i]
                p2 = self.vertex_pos[f]
                self._draw_arrow(surface, p1, p2, COLORS['arrow'], width=3, shadow=True)

        # si árbol construido -> dibuja aristas y vértebra (respetando orden)
        if self.tree_built:
            # aristas (ramas)
            for (u,v) in self.tree_edges:
                if 0 <= u < n and 0 <= v < n:
                    pygame.draw.line(surface, COLORS['edge'], self.vertex_pos[u], self.vertex_pos[v], 4)
            # spine (vértebra) con prioridad visual
            for (u,v) in self.spine_edges:
                pygame.draw.line(surface, COLORS['spine'], self.vertex_pos[u], self.vertex_pos[v], 6)

        # dibujar nodos
        for i, pos in enumerate(self.vertex_pos):
            # sombra
            pygame.draw.circle(surface, (80,80,80), (pos[0]+2, pos[1]+2), vertice_rad+2)
            # color según si parte de vértebra (cuando árbol construido) o si está en ciclo (al enviar)
            col = COLORS['vertex']
            if (self.tree_built and i in self.vertices_in_cycles) or (self.function_submitted and i in self.vertices_in_cycles):
                col = COLORS['spine']
            pygame.draw.circle(surface, col, pos, vertice_rad)
            pygame.draw.circle(surface, COLORS['white'], pos, vertice_rad, 2)
            lbl = FONT_BOLD.render(str(i+1), True, COLORS['white'])
            surface.blit(lbl, (pos[0] - lbl.get_width()//2, pos[1] - lbl.get_height()//2))

    # -------------------------
    # flecha elegante
    # -------------------------
    def _draw_arrow(self, surf, start, end, color, width=3, shadow=False):
        dx = end[0] - start[0]; dy = end[1] - start[1]
        dist = math.hypot(dx, dy)
        if dist < vertice_rad * 1.2:
            # small loop
            cx, cy = start
            r = vertice_rad * 0.6
            pygame.draw.circle(surf, color, (cx + vertice_rad, cy - int(r)), int(r), 2)
            return
        ux, uy = dx/dist, dy/dist
        s = (start[0] + ux * vertice_rad, start[1] + uy * vertice_rad)
        e = (end[0] - ux * vertice_rad * 1.15, end[1] - uy * vertice_rad * 1.15)
        if shadow:
            pygame.draw.line(surf, (110,110,110), (s[0]+1,s[1]+1), (e[0]+1,e[1]+1), width+1)
        pygame.draw.line(surf, color, s, e, width)
        ang = math.atan2(dy, dx)
        a = 10
        left = (e[0] - a*math.cos(ang - 0.45), e[1] - a*math.sin(ang - 0.45))
        right = (e[0] - a*math.cos(ang + 0.45), e[1] - a*math.sin(ang + 0.45))
        pygame.draw.polygon(surf, color, [e, left, right])

    # -------------------------
    # panel info (inferior)
    # -------------------------
    def _draw_info_panel(self, surface):
        shadow = self.info_panel.move(4,4)
        pygame.draw.rect(surface, (220,220,220), shadow, border_radius=12)
        pygame.draw.rect(surface, COLORS['white'], self.info_panel, border_radius=12)
        pygame.draw.rect(surface, COLORS['accent'], self.info_panel, 3, border_radius=12)

        x = self.info_panel.x + 22
        y = self.info_panel.y + 18
        title = FONT_BOLD.render("INFORMACIÓN ANALÍTICA", True, COLORS['accent'])
        surface.blit(title, (x, y)); y += 32

        # función
        ftxt = "f = [" + ", ".join(str(v+1) for v in self.function) + "]" if self.function else "f = []"
        surface.blit(FONT_SMALL.render(ftxt, True, COLORS['dark']), (x, y)); y += 22

        pygame.draw.line(surface, COLORS['light'], (x, y), (self.info_panel.right - 20, y), 1); y += 12

        # permutaciones (usar cycles_list para preservar orden)
        perm_title = FONT_BOLD.render("Notación de Permutaciones:", True, COLORS['info'])
        surface.blit(perm_title, (x, y)); y += 28

        if self.cycles_list:
            # mostrar cada ciclo en su propia línea (ordenado)
            for cyc in self.cycles_list:
                txt = "(" + " ".join(str(v+1) for v in cyc) + ")"
                surface.blit(FONT_TINY.render(txt, True, COLORS['dark']), (x, y))
                y += 20
        else:
            surface.blit(FONT_SMALL.render("Sin ciclos (identidad o vacía)", True, COLORS['gray']), (x, y))
            y += 20

        # stats
        y += 8
        st = FONT_BOLD.render("Estadísticas:", True, COLORS['success'])
        surface.blit(st, (x, y)); y += 24
        stats = [
            f"Vértices en vértebra: {len(self.vertices_in_cycles)}",
            f"Otros vértices: {len(self.vertices_not_in_cycles)}",
            f"Aristas totales: {len(self.tree_edges)}"
        ]
        for s in stats:
            surface.blit(FONT_TINY.render(s, True, COLORS['dark']), (x, y)); y += 18

    # -------------------------
    # status messages
    # -------------------------
    def _draw_status(self, surface):
        if self.error_message:
            rect = pygame.Rect(WIDTH//2 - 300, HEIGHT - 78, 600, 56)
            pygame.draw.rect(surface, (255,235,235), rect, border_radius=10)
            pygame.draw.rect(surface, COLORS['danger'], rect, 2, border_radius=10)
            surface.blit(FONT_REGULAR.render(self.error_message, True, COLORS['danger']), (rect.x + 14, rect.y + 14))
        elif self.success_message:
            rect = pygame.Rect(WIDTH//2 - 300, HEIGHT - 78, 600, 56)
            pygame.draw.rect(surface, (235,255,240), rect, border_radius=10)
            pygame.draw.rect(surface, COLORS['success'], rect, 2, border_radius=10)
            surface.blit(FONT_REGULAR.render(self.success_message, True, COLORS['success']), (rect.x + 14, rect.y + 14))

    # -------------------------
    # update / events
    # -------------------------
    def update(self, mouse_pos, dt):
        self.func_input.update(dt)
        self.btn_send.update(mouse_pos)
        self.btn_build.update(mouse_pos)
        self.btn_clear.update(mouse_pos)
        self.btn_menu.update(mouse_pos)

    def handle_event(self, event):
        if self.btn_menu.handle_event(event):
            return "BACK"
        if self.btn_send.handle_event(event):
            self.submit_function()
        if self.btn_build.handle_event(event):
            self.build_tree()
        if self.btn_clear.handle_event(event):
            self.clear()
        # Enter in input triggers submit
        if self.func_input.handle_event(event):
            self.submit_function()
        return None

    # -------------------------
    # lógica: submit / find cycles / build tree / clear
    # -------------------------
    def submit_function(self):
        txt = self.func_input.get_value()
        if not txt:
            self.error_message = "Ingrese una función."
            self.success_message = ""
            return
        try:
            vals = [int(x.strip()) for x in txt.split(",") if x.strip() != ""]
        except:
            self.error_message = "Formato inválido (solo números separados por comas)."
            self.success_message = ""
            return
        if len(vals) != n:
            self.error_message = f"Debe ingresar exactamente {n} valores (ingresados: {len(vals)})."
            self.success_message = ""
            return
        if any(v < 1 or v > n for v in vals):
            self.error_message = f"Valores deben estar en 1..{n}."
            self.success_message = ""
            return

        # guardar 0-based
        self.function = [v-1 for v in vals]
        self.function_submitted = True
        self.tree_built = False
        self.error_message = ""
        self.success_message = "Función enviada correctamente (flechas mostradas)."
        self.compute_vertex_positions()
        # detect cycles (ordered) for display
        self._detect_cycles_ordered()
        # clear tree edges until build
        self.tree_edges = []
        self.spine_edges = []

    def _detect_cycles_ordered(self):
        """Detecta ciclos preservando el orden cíclico.
           Rellena self.cycles_list, self.vertices_in_cycles (ordered), self.vertices_not_in_cycles.
        """
        self.cycles_list = []
        visited = [False] * n
        for i in range(n):
            if visited[i]:
                continue
            current = i
            stack = []
            index_map = {}
            while not visited[current]:
                visited[current] = True
                index_map[current] = len(stack)
                stack.append(current)
                current = self.function[current]
            # si current está en stack, hay ciclo
            if current in index_map:
                idx = index_map[current]
                cycle = stack[idx:]               # order preserved
                self.cycles_list.append(cycle)
        # construir vertices_in_cycles (concatenate cycles in detection order)
        ordered_vertices = []
        for cyc in self.cycles_list:
            for v in cyc:
                if v not in ordered_vertices:
                    ordered_vertices.append(v)
        self.vertices_in_cycles = ordered_vertices
        # vertices not in cycles = complement
        self.vertices_not_in_cycles = [v for v in range(n) if v not in set(self.vertices_in_cycles)]

    def build_tree(self):
        if not self.function_submitted:
            self.error_message = "Primero presione ENVIAR FUNCIÓN."
            self.success_message = ""
            return
        # ensure cycles_list is up-to-date
        self._detect_cycles_ordered()
        self.tree_edges = []
        self.spine_edges = []

        # spine: for each cycle, add edges in cycle order (closing the cycle if >1)
        for cyc in self.cycles_list:
            if len(cyc) == 1:
                # single-loop: nothing to connect between distinct nodes
                # optionally, you could show a loop (not implemented as edge)
                pass
            else:
                for i in range(len(cyc)):
                    a = cyc[i]
                    b = cyc[(i+1) % len(cyc)]
                    self.spine_edges.append((a, b))
                    self.tree_edges.append((a, b))

        # connect each non-cycle vertex to its f(v)
        for v in self.vertices_not_in_cycles:
            fv = self.function[v]
            if fv is not None:
                self.tree_edges.append((v, fv))

        self.tree_built = True
        self.error_message = ""
        self.success_message = "Árbol construido correctamente."

    def clear(self):
        self.function = []
        self.cycles_list = []
        self.vertices_in_cycles = []
        self.vertices_not_in_cycles = []
        self.spine_edges = []
        self.tree_edges = []
        self.function_submitted = False
        self.tree_built = False
        self.func_input.text = ""
        self.error_message = ""
        self.success_message = ""
        self.compute_vertex_positions()

    # -------------------------
    # Permutation notation (public)
    # -------------------------
    def find_cycles_permutation(self):
        """Devuelve ciclos en 1-based lists (para mostrar en panel)."""
        if not self.cycles_list:
            return []
        return [[v+1 for v in cyc] for cyc in self.cycles_list]


# ==============================================================================
# FUNCIONES DE GRAFOS
# ==============================================================================

def calcular_posiciones_vertices(n_vertices):
    """Calcula posiciones para n vértices en un círculo"""
    global vertice_pos
    vertice_pos = []
    centro_x, centro_y = WIDTH // 2, 500  # Movido hacia abajo para más espacio
    radio = min(200, 120 + n_vertices * 8)  # Radio reducido para más espacio
    
    for i in range(n_vertices):
        angulo = 2 * math.pi * i / n_vertices - math.pi/2
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
    vertice_rad = max(18, min(25, 180 // n))
    
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

# ==============================================================================
# APLICACIÓN PRINCIPAL
# ==============================================================================

class JoyalApplication:
    def __init__(self):
        self.current_screen = "SELECT_N"
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Pantallas
        self.n_selection_screen = NSelectionScreen()
        self.main_menu_screen = MainMenuScreen()
        self.tree_to_func_screen = TreeToFunctionMode()
        self.func_to_tree_screen = FunctionToTreeMode()
        
        # Inicializar con n=6
        inicializar_estructuras(6)
    
    def run(self):
        while self.running:
            dt = self.clock.tick(60)  # 60 FPS
            mouse_pos = pygame.mouse.get_pos()
            
            # Manejar eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_F1:
                        self.show_help()
                
                # Procesar evento según pantalla actual
                result = None
                
                if self.current_screen == "SELECT_N":
                    result = self.n_selection_screen.handle_event(event)
                    if result:
                        n_val = self.n_selection_screen.selected_n
                        inicializar_estructuras(n_val)
                        self.main_menu_screen = MainMenuScreen()
                        self.tree_to_func_screen = TreeToFunctionMode()
                        self.func_to_tree_screen = FunctionToTreeMode()
                        self.current_screen = "MAIN_MENU"
                
                elif self.current_screen == "MAIN_MENU":
                    result = self.main_menu_screen.handle_event(event)
                    if result == "MODE1":
                        self.current_screen = "TREE_TO_FUNC"
                    elif result == "MODE2":
                        self.current_screen = "FUNC_TO_TREE"
                    elif result == "RESET":
                        self.current_screen = "SELECT_N"
                    elif result == "BACK":
                        self.current_screen = "SELECT_N"
                
                elif self.current_screen == "TREE_TO_FUNC":
                    result = self.tree_to_func_screen.handle_event(event)
                    if result == "BACK":
                        self.current_screen = "MAIN_MENU"
                    elif result == "RESET":
                        self.tree_to_func_screen.reset()
                
                elif self.current_screen == "FUNC_TO_TREE":
                    result = self.func_to_tree_screen.handle_event(event)
                    if result == "BACK":
                        self.current_screen = "MAIN_MENU"
            
            # Actualizar pantalla actual
            if self.current_screen == "SELECT_N":
                self.n_selection_screen.update(mouse_pos, dt)
                self.n_selection_screen.draw(screen)
            
            elif self.current_screen == "MAIN_MENU":
                self.main_menu_screen.update(mouse_pos, dt)
                self.main_menu_screen.draw(screen)
            
            elif self.current_screen == "TREE_TO_FUNC":
                self.tree_to_func_screen.update(mouse_pos, dt)
                self.tree_to_func_screen.draw(screen)
            
            elif self.current_screen == "FUNC_TO_TREE":
                self.func_to_tree_screen.update(mouse_pos, dt)
                self.func_to_tree_screen.draw(screen)
            
            # Actualizar pantalla
            pygame.display.flip()
        
        pygame.quit()
    
    def show_help(self):
        print("Ayuda:")
        print("F1: Mostrar esta ayuda")
        print("ESC: Salir de la aplicación")
        print("Click izquierdo: Interactuar con elementos")
        print("Modo 1: Construya un árbol y obtenga la función correspondiente")
        print("Modo 2: Ingrese una función y visualice el árbol correspondiente")

# ==============================================================================
# EJECUCIÓN
# ==============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print("  DEMOSTRACIÓN DE JOYAL - FÓRMULA DE CAYLEY")
    print("  Versión Profesional")
    print("=" * 70)
    print("  Características:")
    print("  • Interfaz moderna con transiciones suaves")
    print("  • Sistema de estados bien separado")
    print("  • Animaciones y efectos visuales")
    print("  • Panel de control con información clara")
    print("=" * 70)
    print("  Autores:")
    print("  • Martin Lora Cano")
    print("  • Cristian Andrés Diaz Ortega")
    print("  • Jhon Edison Prieto Artunduaga")
    print("=" * 70)
    print("\n  Iniciando aplicación...\n")
    
    app = JoyalApplication()
    app.run()
