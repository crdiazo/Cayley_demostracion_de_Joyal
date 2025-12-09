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
# MODO 2: FUNCIÓN → ÁRBOL  (versión A: ENVIAR FUNCIÓN -> CONSTRUIR ÁRBOL)
# =======================================================================
class FunctionToTreeMode:
    def __init__(self):
        self.title = "MODO 2: FUNCIÓN → ÁRBOL"
        
        # CARD principal (medidas adaptativas)
        card_w = min(760, WIDTH - 80)
        card_h = 360
        card_x = (WIDTH - card_w) // 2
        card_y = 80
        self.card_rect = pygame.Rect(card_x, card_y, card_w, card_h)
        
        # Campo de entrada (centrado en la card)
        input_width = card_w - 160
        input_x = card_x + (card_w - input_width) // 2
        input_y = card_y + 88
        self.func_input = InputField(input_x, input_y, input_width, 48,
                                     "INGRESE LA FUNCIÓN f: V → V (ej: 2,3,1,5,5,4)",
                                     "Separada por comas, valores de 1 a n")
        
        # Botones: Back, Send, Construct, Clear
        btn_h = 48
        btn_spacing = 18
        center_x = card_x + card_w // 2
        
        # Botón volver (esquina superior izquierda)
        self.btn_back = ProfessionalButton(24, 20, 120, 40, "← MENÚ", COLORS['gray'])
        
        # ENVIAR: procesa la función y muestra el grafo funcional (NO construye el árbol)
        self.btn_send = ProfessionalButton(center_x - 260, input_y + 80, 140, btn_h, "ENVIAR", COLORS['info'])
        
        # CONSTRUIR: construye el árbol (inicialmente no hay función, se habilita cuando hay función)
        self.btn_generate = ProfessionalButton(center_x - 80, input_y + 80, 170, btn_h, "CONSTRUIR", COLORS['success'])
        
        # LIMPIAR: resetea todo
        self.btn_clear = ProfessionalButton(center_x + 120, input_y + 80, 120, btn_h, "LIMPIAR", COLORS['warning'])
        
        # Variables lógicas
        self.function = []
        self.vertices_in_cycles = []
        self.vertices_not_in_cycles = []
        self.spine_edges = []
        self.tree_edges = []
        self.error_message = ""
        
        # Panel de información (izquierda bajo la card) y grafo a la derecha
        info_w = 340
        info_h = HEIGHT - (card_y + card_h) - 44
        info_x = card_x + 20
        info_y = card_y + card_h + 12
        
        graph_x = info_x + info_w + 20
        graph_y = info_y
        graph_w = WIDTH - graph_x - 40
        graph_h = info_h
        
        self.info_panel_rect = pygame.Rect(info_x, info_y, info_w, info_h)
        self.graph_area = pygame.Rect(graph_x, graph_y, graph_w, graph_h)
        
        # Visual tweaks
        self.shadow_offset = 6
        self.corner_radius = 10
        
        # Stage: "idle" (nada), "function" (mostrando grafo funcional), "tree" (mostrando árbol)
        self.stage = "idle"
    
    # -------------------------
    # Small visual helper: shadow
    # -------------------------
    def _draw_shadow_rect(self, surface, rect, alpha=40):
        s = pygame.Surface((rect.w, rect.h), pygame.SRCALPHA)
        s.fill((0, 0, 0, alpha))
        surface.blit(s, (rect.x + self.shadow_offset, rect.y + self.shadow_offset))
    
    # -------------------------
    def draw(self, surface):
        # Fondo
        surface.fill(COLORS['background'])
        
        # Header
        header_h = 72
        header_rect = pygame.Rect(0, 0, WIDTH, header_h)
        pygame.draw.rect(surface, COLORS['header'], header_rect)
        
        title_surf = FONT_TITLE.render(self.title, True, COLORS['white'])
        surface.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 12))
        
        subtitle = "Ingrese una función f: {1,…,n} → {1,…,n}. Pulse ENVIAR para ver la función."
        subtitle_surf = FONT_REGULAR.render(subtitle, True, COLORS['light'])
        surface.blit(subtitle_surf, (WIDTH//2 - subtitle_surf.get_width()//2, 46))
        
        # Card (con sombra)
        self._draw_shadow_rect(surface, self.card_rect)
        pygame.draw.rect(surface, COLORS['white'], self.card_rect, border_radius=self.corner_radius)
        pygame.draw.rect(surface, COLORS['light'], self.card_rect, 2, border_radius=self.corner_radius)
        
        # Label y input
        label = FONT_REGULAR.render("Función f (valores 1..n, separados por comas):", True, COLORS['dark'])
        surface.blit(label, (self.card_rect.x + 28, self.card_rect.y + 36))
        self.func_input.draw(surface)
        
        # Botones
        self.btn_back.draw(surface)
        # Draw send, construct, clear
        self.btn_send.draw(surface)
        self.btn_generate.draw(surface)
        self.btn_clear.draw(surface)
        
        # Mensaje de error elegante (en la card)
        if self.error_message:
            err_w = self.card_rect.w - 80
            err_h = 48
            err_x = self.card_rect.x + 40
            err_y = self.card_rect.y + self.card_rect.h - err_h - 14
            err_rect = pygame.Rect(err_x, err_y, err_w, err_h)
            pygame.draw.rect(surface, (255, 245, 246), err_rect, border_radius=8)
            pygame.draw.rect(surface, COLORS['danger'], err_rect, 2, border_radius=8)
            err_surf = FONT_REGULAR.render(self.error_message, True, COLORS['danger'])
            surface.blit(err_surf, (err_x + 12, err_y + err_h//2 - err_surf.get_height()//2))
        
        # Panel info (izquierda)
        self._draw_shadow_rect(surface, self.info_panel_rect)
        pygame.draw.rect(surface, COLORS['white'], self.info_panel_rect, border_radius=10)
        pygame.draw.rect(surface, COLORS['light'], self.info_panel_rect, 2, border_radius=10)
        title_surf = FONT_BOLD.render("INFORMACIÓN", True, COLORS['dark'])
        surface.blit(title_surf, (self.info_panel_rect.x + 16, self.info_panel_rect.y + 12))
        
        # contenido del panel info
        if self.function:
            self.draw_info_panel(surface)
        else:
            hint = FONT_REGULAR.render("Aún no hay función. Use ENVIAR para visualizar f(V).", True, COLORS['gray'])
            surface.blit(hint, (self.info_panel_rect.x + 16, self.info_panel_rect.y + 52))
        
        # Área de graficación (derecha)
        pygame.draw.rect(surface, COLORS['white'], self.graph_area, border_radius=10)
        pygame.draw.rect(surface, COLORS['light'], self.graph_area, 2, border_radius=10)
        
        # Según la etapa, dibujar grafo funcional o árbol
        if self.stage == "function":
            self.draw_function_graph(surface)
        elif self.stage == "tree":
            self.draw_tree(surface)
    
    # -------------------------
    def draw_function_graph(self, surface):
        # fondo sutil
        pygame.draw.rect(surface, COLORS['background'], self.graph_area, border_radius=10)
        
        # Dibujar flechas de la función
        for i, f in enumerate(self.function):
            if f is None:
                continue
            pos_i = vertice_pos[i]
            pos_f = vertice_pos[f]
            if not (self.graph_area.collidepoint(pos_i) and self.graph_area.collidepoint(pos_f)):
                continue
            if i == f:
                self.draw_loop(surface, pos_i)
            else:
                self.draw_arrow(surface, pos_i, pos_f, COLORS['arrow'])
        
        # Dibujar vértices arriba de las flechas (para legibilidad)
        for i, pos in enumerate(vertice_pos):
            if not self.graph_area.collidepoint(pos):
                continue
            # sombra
            pygame.draw.circle(surface, (180,180,180), (pos[0]+3, pos[1]+3), vertice_rad)
            pygame.draw.circle(surface, COLORS['vertex'], pos, vertice_rad)
            pygame.draw.circle(surface, COLORS['white'], pos, vertice_rad, 2)
            num_surf = FONT_BOLD.render(str(i+1), True, COLORS['white'])
            surface.blit(num_surf, (pos[0] - num_surf.get_width()//2, pos[1] - num_surf.get_height()//2))
    
    # -------------------------
    def draw_tree(self, surface):
        # Usa tu implementación previa (limpia el área, dibuja aristas/ vértebra / loops / vertices)
        # Limpiar área del gráfico
        pygame.draw.rect(surface, COLORS['background'], self.graph_area, border_radius=10)
        
        # Dibujar aristas del árbol
        for v1, v2 in self.tree_edges:
            if v1 < n and v2 < n:
                pos1 = vertice_pos[v1]
                pos2 = vertice_pos[v2]
                if not (self.graph_area.collidepoint(pos1) and self.graph_area.collidepoint(pos2)):
                    continue
                # sombra
                pygame.draw.line(surface, (0,0,0,20), (pos1[0]+2, pos1[1]+2), (pos2[0]+2, pos2[1]+2), 6)
                color = COLORS['edge']
                width = 3
                if (v1, v2) in self.spine_edges or (v2, v1) in self.spine_edges:
                    color = COLORS['spine']
                    width = 5
                pygame.draw.line(surface, color, pos1, pos2, width)
        
        # Flechas para la función (solo para vértices fuera de la vértebra cuando corresponda)
        for i, f in enumerate(self.function):
            if f is not None and f < n and i < n:
                pos_i = vertice_pos[i]
                pos_f = vertice_pos[f]
                if not (self.graph_area.collidepoint(pos_i) and self.graph_area.collidepoint(pos_f)):
                    continue
                if i == f:
                    self.draw_loop(surface, pos_i)
                else:
                    if i in self.vertices_not_in_cycles:
                        self.draw_arrow(surface, pos_i, pos_f, COLORS['arrow'])
        
        # Dibujar vértebra (si existe)
        if self.vertices_in_cycles and len(self.vertices_in_cycles) > 1:
            self.draw_spine(surface)
        
        # Dibujar vértices
        for i, pos in enumerate(vertice_pos):
            if not self.graph_area.collidepoint(pos):
                continue
            # sombra
            pygame.draw.circle(surface, (180,180,180), (pos[0]+3, pos[1]+3), vertice_rad)
            color = COLORS['vertex']
            if i in self.vertices_in_cycles:
                color = COLORS['spine']
            pygame.draw.circle(surface, color, pos, vertice_rad)
            pygame.draw.circle(surface, COLORS['white'], pos, vertice_rad, 2)
            num_surf = FONT_BOLD.render(str(i+1), True, COLORS['white'])
            surface.blit(num_surf, (pos[0] - num_surf.get_width()//2, pos[1] - num_surf.get_height()//2))
    
    # -------------------------
    def draw_arrow(self, surface, start, end, color):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        if length == 0:
            return
        start_adj = (start[0] + (dx / length) * vertice_rad, start[1] + (dy / length) * vertice_rad)
        end_adj = (end[0] - (dx / length) * vertice_rad, end[1] - (dy / length) * vertice_rad)
        pygame.draw.line(surface, color, start_adj, end_adj, 3)
        angle = math.atan2(dy, dx)
        arrow_size = 12
        left = (end_adj[0] - arrow_size * math.cos(angle - math.pi/6),
                end_adj[1] - arrow_size * math.sin(angle - math.pi/6))
        right = (end_adj[0] - arrow_size * math.cos(angle + math.pi/6),
                 end_adj[1] - arrow_size * math.sin(angle + math.pi/6))
        pygame.draw.polygon(surface, color, [end_adj, left, right])
    
    # -------------------------
    def draw_loop(self, surface, pos):
        x, y = pos
        if not self.graph_area.collidepoint((x, y - 25)):
            return
        center = (x + 10, y - 22)
        rx, ry = 18, 12
        rect = pygame.Rect(0, 0, rx*2, ry*2)
        rect.center = center
        start_angle = math.radians(200)
        end_angle = math.radians(520)
        pygame.draw.arc(surface, COLORS['arrow'], rect, start_angle, end_angle, 3)
    
    # -------------------------
    def draw_spine(self, surface):
        for i in range(len(self.vertices_in_cycles) - 1):
            v1 = self.vertices_in_cycles[i]
            v2 = self.vertices_in_cycles[i+1]
            pos1 = vertice_pos[v1]
            pos2 = vertice_pos[v2]
            if not (self.graph_area.collidepoint(pos1) and self.graph_area.collidepoint(pos2)):
                continue
            pygame.draw.line(surface, (120,30,30), (pos1[0]+3, pos1[1]+3), (pos2[0]+3, pos2[1]+3), 7)
            pygame.draw.line(surface, COLORS['spine'], pos1, pos2, 5)
    
    # -------------------------
    def draw_info_panel(self, surface):
        x0 = self.info_panel_rect.x + 16
        y0 = self.info_panel_rect.y + 44
        
        # Función completa (texto envolvente)
        if self.function:
            func_text = "f(V) = " + ", ".join(str(v+1 if v is not None else "?") for v in self.function)
            # wrap texto cada 36 chars
            lines = [func_text[i:i+36] for i in range(0, len(func_text), 36)]
            for k, line in enumerate(lines):
                surf = FONT_SMALL.render(line, True, COLORS['dark'])
                surface.blit(surf, (x0, y0 + k*20))
            y0 += len(lines)*20 + 8
        else:
            hint = FONT_SMALL.render("Sin función cargada.", True, COLORS['gray'])
            surface.blit(hint, (x0, y0))
            y0 += 26
        
        # vértebra / ciclos
        if self.vertices_in_cycles:
            cyc_text = f"Vértebra: {[v+1 for v in self.vertices_in_cycles]}"
            surface.blit(FONT_SMALL.render(cyc_text, True, COLORS['spine']), (x0, y0))
            y0 += 26
        
        # otros vértices
        if self.vertices_not_in_cycles:
            not_text = f"Otras V: {[v+1 for v in self.vertices_not_in_cycles][:15]}"
            surface.blit(FONT_SMALL.render(not_text, True, COLORS['info']), (x0, y0))
            y0 += 26
        
        # permutación (cíclica)
        perm_text = self.get_permutation_notation()
        surface.blit(FONT_SMALL.render(perm_text, True, COLORS['dark']), (x0, y0))
        y0 += 30
        
        # Mostrar ejemplo de la tabla f(V) (hasta 8 filas)
        if self.tree_edges:
            surface.blit(FONT_BOLD.render("ÁRBOL (muestra):", True, COLORS['dark']), (x0, y0))
            y0 += 24
            max_rows = min(n, 8)
            surface.blit(FONT_SMALL.render("V", True, COLORS['dark']), (x0, y0))
            surface.blit(FONT_SMALL.render("f(V)", True, COLORS['dark']), (x0+40, y0))
            y0 += 18
            for i in range(max_rows):
                v_s = FONT_SMALL.render(str(i+1), True, COLORS['dark'])
                fv = self.function[i] if i < len(self.function) else None
                fv_s = FONT_SMALL.render(str(fv+1) if fv is not None else "?", True, COLORS['dark'])
                surface.blit(v_s, (x0, y0 + i*20))
                surface.blit(fv_s, (x0+40, y0 + i*20))
    
    # -------------------------
    def get_permutation_notation(self):
        if not self.function:
            return "Permutación: -"
        visited = [False] * n
        cycles = []
        for i in range(n):
            if not visited[i] and self.function[i] is not None:
                cycle = []
                cur = i
                while not visited[cur]:
                    visited[cur] = True
                    cycle.append(cur+1)
                    cur = self.function[cur]
                if len(cycle) >= 1:
                    cycles.append(cycle)
        if not cycles:
            return "Permutación: identidad"
        cycle_strs = ["(" + " ".join(str(v) for v in c) + ")" for c in cycles]
        return "Permutación: " + " ".join(cycle_strs)
    
    # -------------------------
    def update(self, mouse_pos, dt):
        self.func_input.update(dt)
        self.btn_back.update(mouse_pos)
        self.btn_send.update(mouse_pos)
        self.btn_generate.update(mouse_pos)
        self.btn_clear.update(mouse_pos)
    
    # -------------------------
    def handle_event(self, event):
        # Botón volver
        if self.btn_back.handle_event(event):
            return "BACK"
        
        # ENVIAR FUNCIÓN -> procesar y mostrar grafo funcional
        if self.btn_send.handle_event(event):
            self.process_function()
            if not self.error_message:
                self.stage = "function"
                # cuando se envía función, permitir construir (btn_generate se usa si hay función)
            return None
        
        # CONSTRUIR ÁRBOL -> construir y mostrar árbol (solo si hay función válida)
        if self.btn_generate.handle_event(event):
            if not self.function:
                self.error_message = "Primero ENVÍE una función válida"
            else:
                self.find_cycles()
                self.construct_tree_from_function()
                self.stage = "tree"
            return None
        
        # LIMPIAR
        if self.btn_clear.handle_event(event):
            self.clear()
            return None
        
        # input field events
        self.func_input.handle_event(event)
        return None
    
    # -------------------------
    def process_function(self):
        """Valida y guarda la función sin construir el árbol."""
        try:
            input_text = self.func_input.get_value()
            if not input_text or input_text.strip() == "":
                self.error_message = "Ingrese una función"
                return
            values = [int(x.strip()) for x in input_text.split(',')]
            if len(values) != n:
                self.error_message = f"Debe ingresar exactamente {n} valores"
                return
            if any(x < 1 or x > n for x in values):
                self.error_message = f"Los valores deben estar entre 1 y {n}"
                return
            # OK
            self.function = [x - 1 for x in values]
            self.error_message = ""
            # actualizar ciclos (sin construir aún)
            self.find_cycles()
        except ValueError:
            self.error_message = "Formato inválido. Use números separados por comas"
        except Exception as e:
            self.error_message = f"Error: {str(e)}"
    
    # -------------------------
    def generate_tree(self):
        """Mantengo por compatibilidad si otras partes llaman a este método"""
        # Construye árbol inmediatamente (compatibilidad)
        if self.function:
            self.find_cycles()
            self.construct_tree_from_function()
            self.stage = "tree"
        else:
            self.error_message = "Primero ingrese la función"
    
    # -------------------------
    def find_cycles(self):
        self.vertices_in_cycles = []
        self.vertices_not_in_cycles = []
        visited = [False] * n
        for i in range(n):
            if not visited[i]:
                current = i
                path = []
                while not visited[current]:
                    visited[current] = True
                    path.append(current)
                    current = self.function[current]
                if current in path:
                    start_idx = path.index(current)
                    cycle = path[start_idx:]
                    self.vertices_in_cycles.extend(cycle)
                else:
                    self.vertices_not_in_cycles.extend(path)
        self.vertices_in_cycles = sorted(list(set(self.vertices_in_cycles)))
        all_vertices = set(range(n))
        self.vertices_not_in_cycles = sorted(list(all_vertices - set(self.vertices_in_cycles)))
    
    # -------------------------
    def construct_tree_from_function(self):
        # Construir el árbol por la biyección de Joyal (versión simple)
        self.tree_edges = []
        self.spine_edges = []
        # vértebra: conectar vértices en ciclos en orden (si hay más de 1)
        if len(self.vertices_in_cycles) > 1:
            for i in range(len(self.vertices_in_cycles) - 1):
                v1 = self.vertices_in_cycles[i]
                v2 = self.vertices_in_cycles[i+1]
                self.tree_edges.append((v1, v2))
                self.spine_edges.append((v1, v2))
        # resto: conectar según la función
        for v in self.vertices_not_in_cycles:
            fv = self.function[v]
            if fv is not None:
                self.tree_edges.append((v, fv))
    
    # -------------------------
    def clear(self):
        self.function = []
        self.vertices_in_cycles = []
        self.vertices_not_in_cycles = []
        self.spine_edges = []
        self.tree_edges = []
        self.error_message = ""
        self.func_input.text = ""
        self.stage = "idle"

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
