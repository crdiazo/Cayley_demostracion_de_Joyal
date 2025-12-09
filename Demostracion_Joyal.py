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

class MainMenuScreen:
    def __init__(self):
        self.title = f"DEMOSTRACIÓN DE JOYAL - n = {n}"

        # Panel izquierdo (botones + texto)
        self.left_x = 80
        self.left_width = 420

        # Botones principales
        self.btn_mode1 = ProfessionalButton(self.left_x + 40, 360, 300, 80,
                                            "MODO 1\nÁRBOL → FUNCIÓN", COLORS['info'])

        self.btn_mode2 = ProfessionalButton(self.left_x + 40, 460, 300, 80,
                                            "MODO 2\nFUNCIÓN → ÁRBOL", COLORS['success'])

        self.btn_reset = ProfessionalButton(self.left_x + 90, 570, 200, 60,
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
        left_panel = pygame.Rect(self.left_x - 20, 180, self.left_width, 500)
        pygame.draw.rect(surface, COLORS['white'], left_panel, border_radius=20)
        pygame.draw.rect(surface, COLORS['accent'], left_panel, 3, border_radius=20)

        # Texto explicativo
        desc_lines = [
            "Esta aplicación demuestra la biyección de Joyal",
            "para la fórmula de Cayley.",
            "",
            "Seleccione un modo de operación:"
        ]

        base_y = 210
        for i, line in enumerate(desc_lines):
            line_surf = FONT_REGULAR.render(line, True, COLORS['dark'])
            surface.blit(line_surf,
                         (self.left_x + self.left_width//2 - line_surf.get_width()//2,
                          base_y + i * 28))

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
        center_y = 430

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

# ==============================================================================
# MODO 1: ÁRBOL → FUNCIÓN
# ==============================================================================

class TreeToFunctionMode:
    def __init__(self):
        self.title = "MODO 1: CONSTRUIR ÁRBOL → OBTENER FUNCIÓN"
        self.step = 0  # 0: Construir, 1: Seleccionar inicio, 2: Seleccionar fin, 3: Completado
        self.selected_vertex = None
        self.start_vertex = None
        self.end_vertex = None
        self.function = [None] * n
        self.spine_edges = []
        self.directed_edges = []
        self.spine_path = None
        
        # Botones
        self.btn_back = ProfessionalButton(30, 30, 120, 40, "← MENÚ", COLORS['gray'])
        self.btn_reset = ProfessionalButton(WIDTH - 150, 30, 120, 40, "REINICIAR", COLORS['warning'])
        self.btn_next = ProfessionalButton(WIDTH - 280, HEIGHT - 80, 120, 40, "CONTINUAR", COLORS['success'])
        self.btn_prev = ProfessionalButton(WIDTH - 410, HEIGHT - 80, 120, 40, "ATRÁS", COLORS['gray'])
        
        # Botones de vértices
        self.vertex_buttons = []
        self.create_vertex_buttons()
        
        # Panel de información - AHORA MÁS GRANDE
        self.info_panel_rect = pygame.Rect(20, 100, 350, HEIGHT - 250)
        
        # Área para el gráfico
        self.graph_area = pygame.Rect(400, 100, WIDTH - 420, HEIGHT - 200)
        
        # Área para botones de vértices
        self.vertex_buttons_area = pygame.Rect(0, HEIGHT - 180, WIDTH, 180)
    
    def create_vertex_buttons(self):
        self.vertex_buttons = []
        max_per_row = min(n, 10)
        start_x = (WIDTH - max_per_row * 60) // 2
        
        # Mover botones de vértices a su área designada
        for i in range(n):
            row = i // max_per_row
            col = i % max_per_row
            x = start_x + col * 60
            y = HEIGHT - 150 + row * 50  # En el área de botones
            
            btn = ProfessionalButton(x, y, 55, 40, str(i+1), COLORS['vertex'])
            self.vertex_buttons.append(btn)
    
    def draw(self, surface):
        # LIMPIAR TODA LA PANTALLA PRIMERO
        surface.fill(COLORS['background'])
        
        # Encabezado
        header_rect = pygame.Rect(0, 0, WIDTH, 100)
        pygame.draw.rect(surface, COLORS['info'], header_rect)
        
        title_surf = FONT_TITLE.render(self.title, True, COLORS['white'])
        surface.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 30))
        
        # Instrucciones según el paso
        instructions = self.get_instructions()
        instr_surf = FONT_REGULAR.render(instructions, True, COLORS['dark'])
        surface.blit(instr_surf, (WIDTH//2 - instr_surf.get_width()//2, 70))
        
        # Dibujar panel de información
        self.draw_info_panel(surface)
        
        # Dibujar árbol en el área designada
        self.draw_tree(surface)
        
        # Limpiar área de botones de vértices
        pygame.draw.rect(surface, COLORS['background'], self.vertex_buttons_area)
        
        # Dibujar botones de vértices
        for btn in self.vertex_buttons:
            btn.draw(surface)
        
        # Dibujar botones de control
        self.btn_back.draw(surface)
        self.btn_reset.draw(surface)
        
        if self.step > 0:
            self.btn_prev.draw(surface)
        
        if self.step < 3 and (self.step == 0 or self.check_step_complete()):
            self.btn_next.draw(surface)
        
        # Indicador de paso
        self.draw_step_indicator(surface)
    
    def get_instructions(self):
        instructions = [
            "PASO 1: Conecte vértices para formar un árbol (haga clic en dos vértices)",
            "PASO 2: Seleccione el vértice INICIAL de la vértebra",
            "PASO 3: Seleccione el vértice FINAL de la vértebra",
            "¡Árbol completo! La función ha sido generada"
        ]
        return instructions[self.step]
    
    def draw_tree(self, surface):
        # Limpiar área del gráfico
        pygame.draw.rect(surface, COLORS['background'], self.graph_area)
        
        # Dibujar aristas
        for v1, v2 in aristas:
            # Ajustar coordenadas al área del gráfico
            x1, y1 = vertice_pos[v1]
            x2, y2 = vertice_pos[v2]
            
            color = COLORS['edge']
            width = 3
            
            # Resaltar vértebra
            if (v1, v2) in self.spine_edges or (v2, v1) in self.spine_edges:
                color = COLORS['spine']
                width = 5
            
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), width)
        
        # Dibujar flechas para aristas dirigidas
        for v1, v2 in self.directed_edges:
            self.draw_arrow(surface, vertice_pos[v1], vertice_pos[v2], COLORS['arrow'])
        
        # Dibujar vértebra destacada
        if self.spine_path and len(self.spine_path) > 1:
            for i in range(len(self.spine_path) - 1):
                v1, v2 = self.spine_path[i], self.spine_path[i+1]
                self.draw_spine_segment(surface, vertice_pos[v1], vertice_pos[v2])
        
        # Dibujar vértices
        self.draw_vertices(surface)
        
        # Resaltar vértices seleccionados
        if self.selected_vertex is not None:
            self.highlight_vertex(surface, self.selected_vertex, COLORS['highlight'])
        if self.start_vertex is not None:
            self.highlight_vertex(surface, self.start_vertex, COLORS['success'])
        if self.end_vertex is not None:
            self.highlight_vertex(surface, self.end_vertex, COLORS['danger'])
    
    def draw_vertices(self, surface):
        for i, pos in enumerate(vertice_pos):
            # Verificar que el vértice esté en el área visible
            if not self.graph_area.collidepoint(pos):
                continue
                
            # Sombra
            shadow_pos = (pos[0] + 2, pos[1] + 2)
            pygame.draw.circle(surface, (100, 100, 100, 100), shadow_pos, vertice_rad)
            
            # Vértice
            color = COLORS['vertex']
            if i == self.selected_vertex:
                color = COLORS['highlight']
            elif i == self.start_vertex:
                color = COLORS['success']
            elif i == self.end_vertex:
                color = COLORS['danger']
            
            pygame.draw.circle(surface, color, pos, vertice_rad)
            pygame.draw.circle(surface, COLORS['white'], pos, vertice_rad, 2)
            
            # Número
            num_surf = FONT_BOLD.render(str(i+1), True, COLORS['white'])
            surface.blit(num_surf, (pos[0] - num_surf.get_width()//2, 
                                   pos[1] - num_surf.get_height()//2))
    
    def draw_arrow(self, surface, start, end, color):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        
        if length == 0:
            return
        
        # Ajustar al borde del círculo
        start_adj = (
            start[0] + (dx / length) * vertice_rad,
            start[1] + (dy / length) * vertice_rad
        )
        end_adj = (
            end[0] - (dx / length) * vertice_rad,
            end[1] - (dy / length) * vertice_rad
        )
        
        # Línea
        pygame.draw.line(surface, color, start_adj, end_adj, 3)
        
        # Punta de flecha
        angle = math.atan2(dy, dx)
        arrow_size = 12
        left = (
            end_adj[0] - arrow_size * math.cos(angle - math.pi/6),
            end_adj[1] - arrow_size * math.sin(angle - math.pi/6)
        )
        right = (
            end_adj[0] - arrow_size * math.cos(angle + math.pi/6),
            end_adj[1] - arrow_size * math.sin(angle + math.pi/6)
        )
        pygame.draw.polygon(surface, color, [end_adj, left, right])
    
    def draw_spine_segment(self, surface, start, end):
        # Línea gruesa con sombra
        pygame.draw.line(surface, (150, 50, 50), 
                        (start[0] + 2, start[1] + 2),
                        (end[0] + 2, end[1] + 2), 6)
        pygame.draw.line(surface, COLORS['spine'], start, end, 4)
    
    def highlight_vertex(self, surface, vertex_idx, color):
        pos = vertice_pos[vertex_idx]
        pygame.draw.circle(surface, color, pos, vertice_rad + 5, 3)
        
        # Etiqueta
        label = ""
        if vertex_idx == self.start_vertex:
            label = "INICIO"
        elif vertex_idx == self.end_vertex:
            label = "FIN"
        
        if label:
            label_surf = FONT_SMALL.render(label, True, color)
            surface.blit(label_surf, (pos[0] - label_surf.get_width()//2, pos[1] - 40))
    
    def draw_info_panel(self, surface):
        # Fondo del panel
        pygame.draw.rect(surface, COLORS['white'], self.info_panel_rect, border_radius=10)
        pygame.draw.rect(surface, COLORS['accent'], self.info_panel_rect, 2, border_radius=10)
        
        # Título
        title_surf = FONT_BOLD.render("INFORMACIÓN DEL ÁRBOL", True, COLORS['accent'])
        surface.blit(title_surf, (self.info_panel_rect.x + 20, self.info_panel_rect.y + 20))
        
        # Contenido - AHORA CON MÁS ESPACIO
        info_y = self.info_panel_rect.y + 60
        info_lines = [
            f"Vértices: {n}",
            f"Aristas: {len(aristas)}/{n-1}",
            f"Conectado: {'Sí' if self.is_connected() else 'No'}",
            f"Paso actual: {self.step + 1}/4"
        ]
        
        if self.start_vertex is not None:
            info_lines.append(f"Inicio vértebra: V{self.start_vertex + 1}")
        if self.end_vertex is not None:
            info_lines.append(f"Fin vértebra: V{self.end_vertex + 1}")
        
        for i, line in enumerate(info_lines):
            line_surf = FONT_SMALL.render(line, True, COLORS['dark'])
            surface.blit(line_surf, (self.info_panel_rect.x + 20, info_y + i * 25))
        
        # Función generada - AHORA CON MÁS ESPACIO
        if self.step == 3:
            func_y = info_y + len(info_lines) * 25 + 20
            func_title = FONT_BOLD.render("FUNCIÓN GENERADA:", True, COLORS['success'])
            surface.blit(func_title, (self.info_panel_rect.x + 20, func_y))
            
            # Mostrar función en formato de tabla
            table_y = func_y + 30
            header_x = self.info_panel_rect.x + 20
            header_v = FONT_TINY.render("V", True, COLORS['dark'])
            header_fv = FONT_TINY.render("f(V)", True, COLORS['dark'])
            surface.blit(header_v, (header_x, table_y))
            surface.blit(header_fv, (header_x + 30, table_y))
            
            # Mostrar hasta 10 filas
            max_rows = min(n, 10)
            for i in range(max_rows):
                v_text = FONT_TINY.render(str(i+1), True, COLORS['dark'])
                fv_value = self.function[i]
                fv_text = FONT_TINY.render(str(fv_value+1 if fv_value is not None else "?"), 
                                          True, COLORS['dark'])
                surface.blit(v_text, (header_x, table_y + 20 + i * 18))
                surface.blit(fv_text, (header_x + 30, table_y + 20 + i * 18))
            
            if n > 10:
                dots_text = FONT_TINY.render("...", True, COLORS['dark'])
                surface.blit(dots_text, (header_x, table_y + 20 + 10 * 18))
    
    def draw_step_indicator(self, surface):
        steps = ["1. Construir", "2. Inicio", "3. Fin", "4. Completado"]
        start_x = WIDTH // 2 - 200
        
        # Asegurar que el indicador no se superponga con botones de vértices
        indicator_y = HEIGHT - 120
        
        for i in range(4):
            step_rect = pygame.Rect(start_x + i * 130, indicator_y, 120, 40)
            
            # Color según estado
            if i < self.step:
                color = COLORS['success']
            elif i == self.step:
                color = COLORS['info']
            else:
                color = COLORS['gray']
            
            pygame.draw.rect(surface, color, step_rect, border_radius=8)
            pygame.draw.rect(surface, COLORS['white'], step_rect, 2, border_radius=8)
            
            step_text = FONT_SMALL.render(steps[i], True, COLORS['white'])
            surface.blit(step_text, (step_rect.centerx - step_text.get_width()//2,
                                    step_rect.centery - step_text.get_height()//2))
    
    def is_connected(self):
        if n == 0:
            return False
        root0 = find(0)
        return all(find(i) == root0 for i in range(n))
    
    def check_step_complete(self):
        if self.step == 0:
            return len(aristas) == n - 1 and self.is_connected()
        elif self.step == 1:
            return self.start_vertex is not None
        elif self.step == 2:
            return self.end_vertex is not None
        return True
    
    def handle_vertex_click(self, vertex_idx):
        if self.step == 0:
            # Construir árbol
            if self.selected_vertex is None:
                self.selected_vertex = vertex_idx
            else:
                if vertex_idx != self.selected_vertex:
                    self.add_edge(self.selected_vertex, vertex_idx)
                self.selected_vertex = None
                
                # Verificar si el árbol está completo
                if len(aristas) == n - 1 and self.is_connected():
                    self.step = 1
        
        elif self.step == 1:
            # Seleccionar inicio de vértebra
            self.start_vertex = vertex_idx
            self.step = 2
        
        elif self.step == 2:
            # Seleccionar fin de vértebra
            if vertex_idx != self.start_vertex:
                self.end_vertex = vertex_idx
                self.calculate_function()
                self.step = 3
    
    def add_edge(self, v1, v2):
        # Verificar si ya existe
        if (v1, v2) in aristas or (v2, v1) in aristas:
            return
        
        # Verificar ciclos
        if find(v1) == find(v2):
            return
        
        # Agregar arista
        aristas.append((v1, v2))
        union(v1, v2)
        grafo[v1].append(v2)
        grafo[v2].append(v1)
    
    def calculate_function(self):
        # Encontrar camino entre inicio y fin
        self.spine_path = self.find_path(self.start_vertex, self.end_vertex)
        
        # Calcular vértebra
        if self.spine_path and len(self.spine_path) > 1:
            self.spine_edges = [(self.spine_path[i], self.spine_path[i+1]) 
                              for i in range(len(self.spine_path)-1)]
            
            # Ordenar vértebra
            spine_sorted = sorted(self.spine_path)
            spine_reversed = list(reversed(self.spine_path))
            
            # Asignar función para vértebra
            for i in range(len(spine_sorted)):
                self.function[spine_sorted[i]] = spine_reversed[i]
        
        # Orientar otras aristas
        self.directed_edges = self.direct_edges()
        
        # Asignar función para otras aristas
        for v1, v2 in self.directed_edges:
            self.function[v1] = v2
    
    def find_path(self, start, end):
        # BFS para encontrar camino
        visited = [False] * n
        parent = [-1] * n
        queue = deque([start])
        visited[start] = True
        
        while queue:
            current = queue.popleft()
            if current == end:
                # Reconstruir camino
                path = []
                while current != -1:
                    path.append(current)
                    current = parent[current]
                return list(reversed(path))
            
            for neighbor in grafo[current]:
                if not visited[neighbor]:
                    visited[neighbor] = True
                    parent[neighbor] = current
                    queue.append(neighbor)
        
        return [start, end]  # Fallback
    
    def direct_edges(self):
        # Calcular distancias al vértice final
        dist = [-1] * n
        queue = deque([self.end_vertex])
        dist[self.end_vertex] = 0
        
        while queue:
            v = queue.popleft()
            for neighbor in grafo[v]:
                if dist[neighbor] == -1:
                    dist[neighbor] = dist[v] + 1
                    queue.append(neighbor)
        
        # Orientar aristas
        directed = []
        for v1, v2 in aristas:
            # Verificar si está en vértebra
            in_spine = False
            for a, b in self.spine_edges:
                if (v1 == a and v2 == b) or (v1 == b and v2 == a):
                    in_spine = True
                    break
            
            if not in_spine:
                if dist[v1] > dist[v2]:
                    directed.append((v1, v2))
                else:
                    directed.append((v2, v1))
        
        return directed
    
    def update(self, mouse_pos, dt):
        self.btn_back.update(mouse_pos)
        self.btn_reset.update(mouse_pos)
        self.btn_next.update(mouse_pos)
        self.btn_prev.update(mouse_pos)
        
        for btn in self.vertex_buttons:
            btn.update(mouse_pos)
    
    def handle_event(self, event):
        if self.btn_back.handle_event(event):
            return "BACK"
        
        if self.btn_reset.handle_event(event):
            self.reset()
            return "RESET"
        
        if self.btn_next.handle_event(event) and self.check_step_complete():
            if self.step < 3:
                self.step += 1
        
        if self.btn_prev.handle_event(event):
            if self.step > 0:
                self.step -= 1
        
        # Manejar clics en botones de vértices
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, btn in enumerate(self.vertex_buttons):
                if btn.rect.collidepoint(event.pos):
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

# ==============================================================================
# MODO 2: FUNCIÓN → ÁRBOL
# ==============================================================================

class FunctionToTreeMode:
    def __init__(self):
        self.title = "MODO 2: FUNCIÓN → CONSTRUIR ÁRBOL"
        
        # Campo de entrada para función
        input_width = 500
        self.func_input = InputField(WIDTH//2 - input_width//2, 120, input_width, 50,
                                    "INGRESE LA FUNCIÓN f: V → V (ej: 2,3,1,5,5,4)",
                                    "Separada por comas, valores de 1 a n")
        
        # Botones
        self.btn_back = ProfessionalButton(30, 30, 120, 40, "← MENÚ", COLORS['gray'])
        self.btn_generate = ProfessionalButton(WIDTH//2 - 120, 190, 120, 50, 
                                              "GENERAR ÁRBOL", COLORS['success'])
        self.btn_clear = ProfessionalButton(WIDTH//2 + 10, 190, 110, 50, 
                                           "LIMPIAR", COLORS['warning'])
        
        # Variables
        self.function = []
        self.vertices_in_cycles = []
        self.vertices_not_in_cycles = []
        self.spine_edges = []
        self.tree_edges = []
        self.error_message = ""
        
        # Panel de información - AHORA MÁS GRANDE
        self.info_panel_rect = pygame.Rect(20, 250, 350, HEIGHT - 300)
        
        # Área para el gráfico
        self.graph_area = pygame.Rect(400, 250, WIDTH - 420, HEIGHT - 300)
    
    def draw(self, surface):
        # LIMPIAR TODA LA PANTALLA PRIMERO
        surface.fill(COLORS['background'])
        
        # Encabezado
        header_rect = pygame.Rect(0, 0, WIDTH, 100)
        pygame.draw.rect(surface, COLORS['success'], header_rect)
        
        title_surf = FONT_TITLE.render(self.title, True, COLORS['white'])
        surface.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 30))
        
        # Instrucciones
        instr = FONT_REGULAR.render("Ingrese una función f: {1,...,n} → {1,...,n} para generar el árbol correspondiente", 
                                   True, COLORS['dark'])
        surface.blit(instr, (WIDTH//2 - instr.get_width()//2, 70))
        
        # Campo de entrada
        self.func_input.draw(surface)
        
        # Botones
        self.btn_back.draw(surface)
        self.btn_generate.draw(surface)
        self.btn_clear.draw(surface)
        
        # Mensaje de error
        if self.error_message:
            error_rect = pygame.Rect(WIDTH//2 - 250, 250, 500, 40)
            pygame.draw.rect(surface, (255, 235, 235), error_rect, border_radius=8)
            pygame.draw.rect(surface, COLORS['danger'], error_rect, 2, border_radius=8)
            
            error_surf = FONT_SMALL.render(self.error_message, True, COLORS['danger'])
            surface.blit(error_surf, (WIDTH//2 - error_surf.get_width()//2, 260))
        
        # Dibujar árbol si hay función
        if self.function:
            # Dibujar panel de información
            self.draw_info_panel(surface)
            # Dibujar árbol
            self.draw_tree(surface)
    
    def draw_tree(self, surface):
        # Limpiar área del gráfico
        pygame.draw.rect(surface, COLORS['background'], self.graph_area)
        
        # Dibujar aristas del árbol
        for v1, v2 in self.tree_edges:
            if v1 < n and v2 < n:
                pos1 = vertice_pos[v1]
                pos2 = vertice_pos[v2]
                
                # Verificar que ambos puntos estén en el área visible
                if not (self.graph_area.collidepoint(pos1) and self.graph_area.collidepoint(pos2)):
                    continue
                
                color = COLORS['edge']
                width = 3
                
                # Resaltar vértebra
                if (v1, v2) in self.spine_edges or (v2, v1) in self.spine_edges:
                    color = COLORS['spine']
                    width = 5
                
                pygame.draw.line(surface, color, pos1, pos2, width)
        
        # Dibujar flechas para la función (solo visual)
        for i, f in enumerate(self.function):
            if f is not None and f < n and i < n:
                pos_i = vertice_pos[i]
                pos_f = vertice_pos[f]
                
                # Verificar que ambos puntos estén en el área visible
                if not (self.graph_area.collidepoint(pos_i) and self.graph_area.collidepoint(pos_f)):
                    continue
                    
                if i == f:  # Bucle (en vértebra)
                    self.draw_loop(surface, pos_i)
                else:
                    # Solo dibujar flechas para vértices que no están en la vértebra
                    if i in self.vertices_not_in_cycles:
                        self.draw_arrow(surface, pos_i, pos_f, COLORS['arrow'])
        
        # Dibujar vértebra si existe
        if self.vertices_in_cycles and len(self.vertices_in_cycles) > 1:
            self.draw_spine(surface)
        
        # Dibujar vértices
        for i, pos in enumerate(vertice_pos):
            # Verificar que el vértice esté en el área visible
            if not self.graph_area.collidepoint(pos):
                continue
                
            # Sombra
            shadow_pos = (pos[0] + 2, pos[1] + 2)
            pygame.draw.circle(surface, (100, 100, 100, 100), shadow_pos, vertice_rad)
            
            # Vértice
            color = COLORS['vertex']
            if i in self.vertices_in_cycles:
                color = COLORS['spine']
            
            pygame.draw.circle(surface, color, pos, vertice_rad)
            pygame.draw.circle(surface, COLORS['white'], pos, vertice_rad, 2)
            
            # Número
            num_surf = FONT_BOLD.render(str(i+1), True, COLORS['white'])
            surface.blit(num_surf, (pos[0] - num_surf.get_width()//2, 
                                   pos[1] - num_surf.get_height()//2))
    
    def draw_arrow(self, surface, start, end, color):
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        
        if length == 0:
            return
        
        start_adj = (
            start[0] + (dx / length) * vertice_rad,
            start[1] + (dy / length) * vertice_rad
        )
        end_adj = (
            end[0] - (dx / length) * vertice_rad,
            end[1] - (dy / length) * vertice_rad
        )
        
        pygame.draw.line(surface, color, start_adj, end_adj, 3)
        
        angle = math.atan2(dy, dx)
        arrow_size = 12
        left = (
            end_adj[0] - arrow_size * math.cos(angle - math.pi/6),
            end_adj[1] - arrow_size * math.sin(angle - math.pi/6)
        )
        right = (
            end_adj[0] - arrow_size * math.cos(angle + math.pi/6),
            end_adj[1] - arrow_size * math.sin(angle + math.pi/6)
        )
        pygame.draw.polygon(surface, color, [end_adj, left, right])
    
    def draw_loop(self, surface, pos):
        x, y = pos
        # Verificar que el bucle esté en el área visible
        if not self.graph_area.collidepoint((x, y - 25)):
            return
            
        center = (x + 6, y - 25)
        rx, ry = 20, 15
        
        rect = pygame.Rect(0, 0, rx * 2, ry * 2)
        rect.center = center
        
        start_angle = math.radians(200)
        end_angle = math.radians(520)
        pygame.draw.arc(surface, COLORS['arrow'], rect, start_angle, end_angle, 3)
    
    def draw_spine(self, surface):
        # Conectar vértices en ciclos
        for i in range(len(self.vertices_in_cycles) - 1):
            v1 = self.vertices_in_cycles[i]
            v2 = self.vertices_in_cycles[i+1]
            
            pos1 = vertice_pos[v1]
            pos2 = vertice_pos[v2]
            
            # Verificar que ambos puntos estén en el área visible
            if not (self.graph_area.collidepoint(pos1) and self.graph_area.collidepoint(pos2)):
                continue
                
            # Línea de vértebra
            pygame.draw.line(surface, (150, 50, 50), 
                            (pos1[0] + 2, pos1[1] + 2),
                            (pos2[0] + 2, pos2[1] + 2), 6)
            pygame.draw.line(surface, COLORS['spine'], 
                            pos1, pos2, 4)
    
    def draw_info_panel(self, surface):
        # Fondo
        pygame.draw.rect(surface, COLORS['white'], self.info_panel_rect, border_radius=10)
        pygame.draw.rect(surface, COLORS['accent'], self.info_panel_rect, 2, border_radius=10)
        
        # Título
        title_surf = FONT_BOLD.render("INFORMACIÓN DE LA FUNCIÓN", True, COLORS['accent'])
        surface.blit(title_surf, (self.info_panel_rect.x + 20, self.info_panel_rect.y + 20))
        
        # Contenido
        info_y = self.info_panel_rect.y + 60
        
        # Función completa
        func_text = "f(V) = " + ", ".join(str(v+1 if v is not None else "?") for v in self.function)
        func_surf = FONT_TINY.render(func_text, True, COLORS['dark'])
        surface.blit(func_surf, (self.info_panel_rect.x + 20, info_y))
        
        # Vértebra (vértices en ciclos)
        if self.vertices_in_cycles:
            cycles_text = f"Vértebra: {[v+1 for v in self.vertices_in_cycles]}"
            cycles_surf = FONT_SMALL.render(cycles_text, True, COLORS['spine'])
            surface.blit(cycles_surf, (self.info_panel_rect.x + 20, info_y + 25))
        
        # Vértices no en ciclos
        if self.vertices_not_in_cycles:
            not_cycles_text = f"Otros vértices: {[v+1 for v in self.vertices_not_in_cycles]}"
            not_cycles_surf = FONT_SMALL.render(not_cycles_text, True, COLORS['info'])
            surface.blit(not_cycles_surf, (self.info_panel_rect.x + 20, info_y + 50))
        
        # Notación de permutación
        perm_text = self.get_permutation_notation()
        perm_surf = FONT_SMALL.render(perm_text, True, COLORS['info'])
        surface.blit(perm_surf, (self.info_panel_rect.x + 20, info_y + 75))
        
        # Información del árbol generado
        if self.tree_edges:
            tree_info_y = info_y + 110
            tree_title = FONT_BOLD.render("ÁRBOL GENERADO:", True, COLORS['success'])
            surface.blit(tree_title, (self.info_panel_rect.x + 20, tree_info_y))
            
            # Vértebra (camino ordenado)
            if self.vertices_in_cycles and len(self.vertices_in_cycles) > 1:
                spine_text = f"Vértebra: {' - '.join(str(v+1) for v in self.vertices_in_cycles)}"
                spine_surf = FONT_SMALL.render(spine_text, True, COLORS['dark'])
                surface.blit(spine_surf, (self.info_panel_rect.x + 20, tree_info_y + 30))
            
            # Tabla de función
            table_y = tree_info_y + 60
            table_title = FONT_BOLD.render("TABLA f(V):", True, COLORS['dark'])
            surface.blit(table_title, (self.info_panel_rect.x + 20, table_y))
            
            # Encabezados
            header_x = self.info_panel_rect.x + 20
            header_v = FONT_SMALL.render("V", True, COLORS['dark'])
            header_fv = FONT_SMALL.render("f(V)", True, COLORS['dark'])
            surface.blit(header_v, (header_x, table_y + 25))
            surface.blit(header_fv, (header_x + 40, table_y + 25))
            
            # Filas de la tabla (hasta 10 filas)
            max_rows = min(n, 10)
            for i in range(max_rows):
                v_text = FONT_SMALL.render(str(i+1), True, COLORS['dark'])
                fv_value = self.function[i]
                fv_text = FONT_SMALL.render(str(fv_value+1 if fv_value is not None else "?"), 
                                           True, COLORS['dark'])
                surface.blit(v_text, (header_x, table_y + 50 + i * 25))
                surface.blit(fv_text, (header_x + 40, table_y + 50 + i * 25))
            
            if n > 10:
                dots_text = FONT_SMALL.render("...", True, COLORS['dark'])
                surface.blit(dots_text, (header_x, table_y + 50 + 10 * 25))
            
            # Aristas orientadas
            oriented_y = table_y + 50 + max_rows * 25 + 20
            oriented_title = FONT_BOLD.render("Aristas orientadas:", True, COLORS['info'])
            surface.blit(oriented_title, (self.info_panel_rect.x + 20, oriented_y))
            
            # Mostrar algunas aristas orientadas
            oriented_text = ""
            count = 0
            for i in self.vertices_not_in_cycles:
                if count < 3:  # Mostrar máximo 3
                    oriented_text += f"V{i+1}→V{self.function[i]+1} "
                    count += 1
            
            if oriented_text:
                oriented_surf = FONT_SMALL.render(oriented_text, True, COLORS['dark'])
                surface.blit(oriented_surf, (self.info_panel_rect.x + 20, oriented_y + 25))
    
    def get_permutation_notation(self):
        if not self.function:
            return "No hay función"
        
        # Encontrar ciclos
        visited = [False] * n
        cycles = []
        
        for i in range(n):
            if not visited[i] and self.function[i] is not None:
                cycle = []
                current = i
                
                while not visited[current]:
                    visited[current] = True
                    cycle.append(current + 1)
                    current = self.function[current]
                    
                    if current == i:
                        break
                
                if len(cycle) > 1:
                    cycles.append(cycle)
        
        if not cycles:
            return "Función identidad"
        
        # Construir notación
        cycle_strs = ["(" + " ".join(str(v) for v in cycle) + ")" for cycle in cycles]
        return "Permutación: " + " ".join(cycle_strs)
    
    def update(self, mouse_pos, dt):
        self.func_input.update(dt)
        self.btn_back.update(mouse_pos)
        self.btn_generate.update(mouse_pos)
        self.btn_clear.update(mouse_pos)
    
    def handle_event(self, event):
        if self.btn_back.handle_event(event):
            return "BACK"
        
        if self.btn_generate.handle_event(event):
            self.generate_tree()
        
        if self.btn_clear.handle_event(event):
            self.clear()
        
        self.func_input.handle_event(event)
        return None
    
    def generate_tree(self):
        try:
            # Obtener y validar entrada
            input_text = self.func_input.get_value()
            if not input_text:
                self.error_message = "Ingrese una función"
                return
            
            # Parsear valores
            values = [int(x.strip()) for x in input_text.split(',')]
            
            if len(values) != n:
                self.error_message = f"Debe ingresar exactamente {n} valores"
                return
            
            if any(x < 1 or x > n for x in values):
                self.error_message = f"Los valores deben estar entre 1 y {n}"
                return
            
            # Convertir a 0-indexed
            self.function = [x - 1 for x in values]
            self.error_message = ""
            
            # Encontrar vértices en ciclos y generar árbol
            self.find_cycles()
            self.construct_tree_from_function()
            
        except ValueError:
            self.error_message = "Formato inválido. Use números separados por comas"
        except Exception as e:
            self.error_message = f"Error: {str(e)}"
    
    def find_cycles(self):
        self.vertices_in_cycles = []
        self.vertices_not_in_cycles = []
        
        visited = [False] * n
        
        for i in range(n):
            if not visited[i]:
                # Seguir la función hasta encontrar un ciclo
                current = i
                path = []
                
                while not visited[current]:
                    visited[current] = True
                    path.append(current)
                    current = self.function[current]
                
                # Si estamos en un ciclo
                if current in path:
                    cycle_start = path.index(current)
                    cycle = path[cycle_start:]
                    self.vertices_in_cycles.extend(cycle)
                else:
                    # No es un ciclo completo
                    self.vertices_not_in_cycles.extend(path)
        
        # Ordenar la vértebra (los ciclos)
        self.vertices_in_cycles = sorted(list(set(self.vertices_in_cycles)))
        
        # Los demás vértices
        all_vertices = set(range(n))
        self.vertices_not_in_cycles = sorted(list(all_vertices - set(self.vertices_in_cycles)))
    
    def construct_tree_from_function(self):
        # Construir el árbol a partir de la función según la biyección de Joyal
        self.tree_edges = []
        self.spine_edges = []
        
        # 1. Los vértices en ciclos forman la vértebra
        if len(self.vertices_in_cycles) > 1:
            # Conectar los vértices en orden para formar la vértebra
            for i in range(len(self.vertices_in_cycles) - 1):
                v1 = self.vertices_in_cycles[i]
                v2 = self.vertices_in_cycles[i+1]
                self.tree_edges.append((v1, v2))
                self.spine_edges.append((v1, v2))
        
        # 2. Para vértices no en ciclos, usar la función para crear aristas
        for v in self.vertices_not_in_cycles:
            fv = self.function[v]
            if fv is not None:
                self.tree_edges.append((v, fv))
    
    def clear(self):
        self.function = []
        self.vertices_in_cycles = []
        self.vertices_not_in_cycles = []
        self.spine_edges = []
        self.tree_edges = []
        self.error_message = ""
        self.func_input.text = ""

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
