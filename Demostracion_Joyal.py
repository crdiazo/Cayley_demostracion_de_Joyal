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

# =======================================================================
# MODO 2: FUNCIÓN → ÁRBOL (versión mejorada, lista para pegar)
# =======================================================================
class FunctionToTreeMode:
    def __init__(self):
        self.title = "MODO 2: FUNCIÓN → ÁRBOL"

        # CARD / INPUT (anchura pensada para WIDTH=1280)
        self.card_rect = pygame.Rect(36, 72, WIDTH - 72, 160)
        input_w = 900
        input_x = self.card_rect.x + 24
        input_y = self.card_rect.y + 62

        self.func_input = InputField(
            input_x, input_y, input_w, 44,
            "Ingrese f(1..n) separados por comas",
            "Ejemplo: 2,3,1,5,5,4"
        )

        # botones alineados dentro de la card (ENVIAR = ver/mostrar, CONSTRUIR = generar árbol)
        btn_y = input_y + 58
        self.btn_send     = ProfessionalButton(input_x,           btn_y, 140, 44, "ENVIAR",    COLORS['info'])
        self.btn_generate = ProfessionalButton(input_x + 158,     btn_y, 160, 44, "CONSTRUIR", COLORS['success'])
        self.btn_clear    = ProfessionalButton(input_x + 340,     btn_y, 140, 44, "LIMPIAR",   COLORS['warning'])
        self.btn_back     = ProfessionalButton(20, 20, 120, 40, "← MENÚ", COLORS['gray'])

        # Panels
        self.info_rect = pygame.Rect(36, 260, 360, HEIGHT - 320)            # izquierda
        self.graph_rect = pygame.Rect(self.info_rect.right + 24, 260,
                                      WIDTH - (self.info_rect.right + 36), HEIGHT - 320)  # derecha

        # Estado / datos
        self.function = []                 # lista 0-indexed: f[i] = j
        self._cycles_list = []             # lista de ciclos (cada ciclo lista de vértices 0-indexed)
        self.vertices_in_cycles = []       # flatten de vértices en ciclos, orden preservado
        self.vertices_not_in_cycles = []   # los demás
        self.tree_edges = []               # aristas del árbol final (tuplas 0-indexed)
        self.spine_edges = []              # aristas pertenecientes a la vértebra (ordenadas)
        self.error_message = ""
        self.stage = "idle"                # "idle", "function", "tree"

        # posiciones calculadas localmente para dibujar en graph_rect
        self.vertex_pos = []

        # Debug si quieres prints
        self._debug = False

    # -----------------------------
    # Calcula posiciones dentro de graph_rect (centrado, radio dinámico)
    # -----------------------------
    def compute_positions(self):
        area = self.graph_rect
        cx = area.x + area.w // 2
        cy = area.y + area.h // 2

        # margen para etiquetas/flechas
        margin = 70
        R = min(area.w, area.h) // 2 - margin
        R = max(R, 60)

        # Ajuste si n enorme
        if n > 30:
            # reducir radio para que no se salga
            R = int(R * 0.8)

        self.vertex_pos = []
        for i in range(n):
            ang = 2 * math.pi * i / max(1, n) - math.pi/2
            x = int(cx + R * math.cos(ang))
            y = int(cy + R * math.sin(ang))
            self.vertex_pos.append((x, y))

        if self._debug:
            print("compute_positions R:", R, "center:", (cx, cy))

    # -----------------------------
    # DIBUJO / UI
    # -----------------------------
    def draw(self, surface):
        surface.fill(COLORS['background'])

        # header
        header = pygame.Rect(0, 0, WIDTH, 64)
        pygame.draw.rect(surface, COLORS['header'], header)
        htext = FONT_TITLE.render(self.title, True, COLORS['white'])
        surface.blit(htext, (WIDTH//2 - htext.get_width()//2, 10))

        # input card
        pygame.draw.rect(surface, COLORS['white'], self.card_rect, border_radius=12)
        pygame.draw.rect(surface, COLORS['light'], self.card_rect, 2, border_radius=12)
        lbl = FONT_REGULAR.render("f(V):", True, COLORS['dark'])
        surface.blit(lbl, (self.card_rect.x + 18, self.card_rect.y + 16))
        self.func_input.draw(surface)

        # botones de la card
        self.btn_back.draw(surface)
        self.btn_send.draw(surface)
        self.btn_generate.draw(surface)
        self.btn_clear.draw(surface)

        # mensaje de error dentro de la card
        if self.error_message:
            err = FONT_SMALL.render(self.error_message, True, COLORS['danger'])
            surface.blit(err, (self.card_rect.x + 18, self.card_rect.y + self.card_rect.height - 30))

        # izquierdo: info panel
        pygame.draw.rect(surface, COLORS['white'], self.info_rect, border_radius=12)
        pygame.draw.rect(surface, COLORS['light'], self.info_rect, 2, border_radius=12)
        title = FONT_BOLD.render("INFORMACIÓN", True, COLORS['dark'])
        surface.blit(title, (self.info_rect.x + 16, self.info_rect.y + 12))
        if self.function:
            self.draw_info(surface)
        else:
            hint = FONT_SMALL.render("Pulse ENVIAR para visualizar f(V).", True, COLORS['gray'])
            surface.blit(hint, (self.info_rect.x + 16, self.info_rect.y + 48))

        # derecha: panel gráfico
        pygame.draw.rect(surface, COLORS['white'], self.graph_rect, border_radius=12)
        pygame.draw.rect(surface, COLORS['light'], self.graph_rect, 2, border_radius=12)

        # dibujar según etapa
        if self.stage == "function":
            self.draw_function(surface)
        elif self.stage == "tree":
            self.draw_tree(surface)
        else:
            # si estamos idle, mostrar ayuda dentro del panel gráfico
            hint2 = FONT_SMALL.render("Aquí se mostrará la función o el árbol generado.", True, COLORS['gray'])
            surface.blit(hint2, (self.graph_rect.centerx - hint2.get_width()//2,
                                 self.graph_rect.centery - hint2.get_height()//2))

    # -----------------------------
    # Dibuja la información en panel izquierdo (incluye tabla estilo 'excel')
    # -----------------------------
    def draw_info(self, surface):
        x = self.info_rect.x + 16
        y = self.info_rect.y + 44

        # mostrar la función completa con índice 1-based
        ftext = "f(V) = [" + ", ".join(str(v+1) for v in self.function) + "]"
        surface.blit(FONT_SMALL.render(ftext, True, COLORS['dark']), (x, y))
        y += 28

        # vértebra
        if self.vertices_in_cycles:
            spine_txt = "Vértebra: " + " - ".join(str(v+1) for v in self.vertices_in_cycles)
            surface.blit(FONT_SMALL.render(spine_txt, True, COLORS['spine']), (x, y))
            y += 26
        else:
            surface.blit(FONT_SMALL.render("Vértebra: —", True, COLORS['gray']), (x, y))
            y += 26

        # otros
        if self.vertices_not_in_cycles:
            others_txt = "Otros vértices: " + ", ".join(str(v+1) for v in self.vertices_not_in_cycles)
            surface.blit(FONT_SMALL.render(others_txt, True, COLORS['dark']), (x, y))
            y += 26
        else:
            surface.blit(FONT_SMALL.render("Otros vértices: —", True, COLORS['gray']), (x, y))
            y += 26

        # Permutación (ciclos)
        perm = self.get_permutation()
        surface.blit(FONT_SMALL.render("Permutación: " + perm, True, COLORS['dark']), (x, y))
        y += 28

        # Tabla f(V) (estilo compacto tipo Excel)
        surface.blit(FONT_BOLD.render("Tabla f(V):", True, COLORS['dark']), (x, y))
        y += 24

        # encabezados
        col_v = x
        col_f = x + 60
        surface.blit(FONT_TINY.render("V", True, COLORS['dark']), (col_v, y))
        surface.blit(FONT_TINY.render("f(V)", True, COLORS['dark']), (col_f, y))
        y += 18
        pygame.draw.line(surface, COLORS['light'], (col_v, y-6), (self.info_rect.right - 14, y-6), 1)

        # filas (hasta 12)
        max_rows = min(n, 12)
        for i in range(max_rows):
            fv = self.function[i]
            surface.blit(FONT_TINY.render(str(i+1), True, COLORS['dark']), (col_v, y))
            surface.blit(FONT_TINY.render(str(fv+1) if fv is not None else "?", True, COLORS['dark']), (col_f, y))
            y += 18

        if n > max_rows:
            surface.blit(FONT_TINY.render("...", True, COLORS['dark']), (col_v, y))

    # -----------------------------
    # Dibuja la representación funcional (flechas f: i → f(i))
    # -----------------------------
    def draw_function(self, surface):
        # calcular posiciones
        self.compute_positions()

        # flechas (primero las flechas para no tapar vértices)
        for i, f in enumerate(self.function):
            if f is None or f < 0 or f >= n:
                continue
            p1 = self.vertex_pos[i]
            p2 = self.vertex_pos[f]
            if i == f:
                self.draw_loop(surface, p1)
            else:
                self.draw_arrow(surface, p1, p2, COLORS['arrow'])

        # vértices encima
        for i, pos in enumerate(self.vertex_pos):
            pygame.draw.circle(surface, COLORS['vertex'], pos, vertice_rad)
            pygame.draw.circle(surface, COLORS['white'], pos, vertice_rad, 2)
            t = FONT_BOLD.render(str(i+1), True, COLORS['white'])
            surface.blit(t, (pos[0]-t.get_width()//2, pos[1]-t.get_height()//2))

    # -----------------------------
    # Dibuja el árbol final (spine + ramas)
    # -----------------------------
    def draw_tree(self, surface):
        # calcular posiciones
        self.compute_positions()

        # dibujar ramas / aristas normales
        for a, b in self.tree_edges:
            pygame.draw.line(surface, COLORS['edge'], self.vertex_pos[a], self.vertex_pos[b], 3)

        # vértebra (línea más gruesa)
        for a, b in self.spine_edges:
            pygame.draw.line(surface, COLORS['spine'], self.vertex_pos[a], self.vertex_pos[b], 6)

        # flechas orientadas para vértices no en ciclo (mostrar dirección a f(v))
        for i in self.vertices_not_in_cycles:
            fv = self.function[i]
            if fv is None: 
                continue
            self.draw_arrow(surface, self.vertex_pos[i], self.vertex_pos[fv], COLORS['arrow'])

        # vértices encima (spine coloreada)
        for i, pos in enumerate(self.vertex_pos):
            col = COLORS['spine'] if i in self.vertices_in_cycles else COLORS['vertex']
            pygame.draw.circle(surface, col, pos, vertice_rad)
            pygame.draw.circle(surface, COLORS['white'], pos, vertice_rad, 2)
            t = FONT_BOLD.render(str(i+1), True, COLORS['white'])
            surface.blit(t, (pos[0]-t.get_width()//2, pos[1]-t.get_height()//2))

    # -----------------------------
    # Flecha con punta (respetando radios)
    # -----------------------------
    def draw_arrow(self, surface, p1, p2, color):
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        L = math.hypot(dx, dy)
        if L < 1e-6:
            return
        s = vertice_rad
        start = (p1[0] + dx / L * s, p1[1] + dy / L * s)
        end   = (p2[0] - dx / L * s, p2[1] - dy / L * s)
        pygame.draw.line(surface, color, start, end, 3)
        ang = math.atan2(dy, dx)
        arrow_size = 10
        left  = (end[0] - arrow_size * math.cos(ang - math.pi/6), end[1] - arrow_size * math.sin(ang - math.pi/6))
        right = (end[0] - arrow_size * math.cos(ang + math.pi/6), end[1] - arrow_size * math.sin(ang + math.pi/6))
        pygame.draw.polygon(surface, color, [end, left, right])

    def draw_loop(self, surface, pos):
        # pequeño arco encima del vértice para bucle
        rx, ry = 18, 12
        rect = pygame.Rect(pos[0] - rx, pos[1] - ry - vertice_rad - 4, rx*2, ry*2)
        pygame.draw.arc(surface, COLORS['arrow'], rect, math.radians(10), math.radians(350), 3)

    # -----------------------------
    # Procesa el texto ingresado por el usuario (ENVIAR)
    # -----------------------------
    def process_function(self):
        txt = self.func_input.get_value().strip()
        if not txt:
            self.error_message = "Ingrese la función."
            return False
        try:
            vals = [int(x.strip()) for x in txt.split(",") if x.strip() != ""]
        except:
            self.error_message = "Formato inválido: use números separados por comas."
            return False
        if len(vals) != n:
            self.error_message = f"Debe ingresar exactamente {n} valores."
            return False
        if any(v < 1 or v > n for v in vals):
            self.error_message = f"Valores deben estar entre 1 y {n}."
            return False

        # Convertir a 0-indexed
        self.function = [v-1 for v in vals]
        self.error_message = ""
        # detectar ciclos (ordenado)
        self._detect_cycles_ordered()
        # reset prev tree
        self.tree_edges = []
        self.spine_edges = []
        self.stage = "function"
        if self._debug:
            print("process_function OK. cycles:", [[x+1 for x in c] for c in self._cycles_list])
        return True

    # -----------------------------
    # Detecta ciclos y preserva orden: guarda _cycles_list y vertices_in_cycles
    # -----------------------------
    def _detect_cycles_ordered(self):
        visited = [False] * n
        cycles = []
        non_cycles_accum = []

        for i in range(n):
            if visited[i]:
                continue
            cur = i
            stack = []
            idx_map = {}
            while not visited[cur]:
                visited[cur] = True
                idx_map[cur] = len(stack)
                stack.append(cur)
                cur = self.function[cur]
            # Si volvimos a un nodo del stack -> ciclo
            if cur in idx_map:
                start = idx_map[cur]
                cycle = stack[start:]
                cycles.append(cycle)
                # nodos previos al ciclo (si hay) son no-ciclo que conducen al ciclo
                prefix = stack[:start]
                if prefix:
                    non_cycles_accum.extend(prefix)
            else:
                # toda la pila es no-ciclo que termina en región ya visitada
                non_cycles_accum.extend(stack)

        # guardar
        self._cycles_list = cycles
        ordered_vertices = []
        for cyc in cycles:
            for v in cyc:
                if v not in ordered_vertices:
                    ordered_vertices.append(v)
        self.vertices_in_cycles = ordered_vertices
        self.vertices_not_in_cycles = [i for i in range(n) if i not in set(self.vertices_in_cycles)]

        if self._debug:
            print("_detect_cycles_ordered -> cycles:", [[x+1 for x in c] for c in cycles])
            print("in_cycles:", [v+1 for v in self.vertices_in_cycles],
                  "not_in:", [v+1 for v in self.vertices_not_in_cycles])

    # -----------------------------
    # Construye el árbol a partir de la función (CONSTRUIR botón)
    # -----------------------------
def construct_tree_from_function(self):
    if not self.function:
        self.error_message = "Primero envíe una función válida."
        return False

    if not hasattr(self, "_cycles_list"):
        self._detect_cycles_ordered()

    self.tree_edges = []
    self.spine_edges = []

    # construir vértebra como camino
    for cyc in self._cycles_list:
        if len(cyc) > 1:
            for i in range(len(cyc) - 1):
                a = cyc[i]
                b = cyc[i + 1]
                if (a, b) not in self.spine_edges and (b, a) not in self.spine_edges:
                    self.spine_edges.append((a, b))
                if (a, b) not in self.tree_edges and (b, a) not in self.tree_edges:
                    self.tree_edges.append((a, b))

    # ramas v → f(v)
    for v in self.vertices_not_in_cycles:
        fv = self.function[v]
        if 0 <= fv < n:
            if (v, fv) not in self.tree_edges and (fv, v) not in self.tree_edges:
                self.tree_edges.append((v, fv))

    # *** CORRECCIÓN CLAVE ***
    # eliminar las aristas de la vértebra del conjunto de ramas
    self.tree_edges = [e for e in self.tree_edges 
                       if e not in self.spine_edges and (e[1], e[0]) not in self.spine_edges]

    self.stage = "tree"
    self.error_message = ""
    return True

    # -----------------------------
    # Devuelve notación de permutación (ciclos)
    # -----------------------------
    def get_permutation(self):
        if hasattr(self, "_cycles_list") and self._cycles_list:
            return " ".join("(" + " ".join(str(x+1) for x in cyc) + ")" for cyc in self._cycles_list)
        # fallback: intentar construir ciclos
        visited = [False] * n
        cycles = []
        for i in range(n):
            if visited[i]:
                continue
            cur = i
            cyc = []
            while not visited[cur]:
                visited[cur] = True
                cyc.append(cur+1)
                cur = self.function[cur]
            cycles.append(cyc)
        return " ".join("(" + " ".join(map(str, c)) + ")" for c in cycles)

    # -----------------------------
    # update / events
    # -----------------------------
    def update(self, mouse_pos, dt):
        self.btn_back.update(mouse_pos)
        self.btn_send.update(mouse_pos)
        self.btn_generate.update(mouse_pos)
        self.btn_clear.update(mouse_pos)
        self.func_input.update(dt)

    def handle_event(self, event):
        if self.btn_back.handle_event(event):
            return "BACK"

        if self.btn_send.handle_event(event):
            ok = self.process_function()
            if ok:
                self.stage = "function"
            return None

        if self.btn_generate.handle_event(event):
            if not self.function:
                self.error_message = "Primero envíe una función válida."
            else:
                ok = self.construct_tree_from_function()
                if ok:
                    self.stage = "tree"
            return None

        if self.btn_clear.handle_event(event):
            self.clear()
            return None

        # Enter en el input también envía
        if self.func_input.handle_event(event):
            ok = self.process_function()
            if ok:
                self.stage = "function"
        return None

    # -----------------------------
    def clear(self):
        self.function = []
        self._cycles_list = []
        self.vertices_in_cycles = []
        self.vertices_not_in_cycles = []
        self.tree_edges = []
        self.spine_edges = []
        self.stage = "idle"
        self.error_message = ""
        self.func_input.text = ""
        self.vertex_pos = []



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
