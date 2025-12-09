# ╔════════════════════════════════════════════════════════════════════════════╗
# ║                                                                            ║
# ║     PROYECTO MD - Demostración de Joyal a la Fórmula de Cayley             ║
# ║                                                                            ║
# ║     VERSIÓN PROFESIONAL - Interfaz Moderna y Fluida                        ║
# ║                                                                            ║
# ╠════════════════════════════════════════════════════════════════════════════╣
# ║                                                                            ║
# ║     CARACTERÍSTICAS AÑADIDAS:                                              ║
# ║         1. Transiciones suaves (Easing) entre pantallas.                   ║
# ║         2. Botones de Menú con texto de dos líneas mejorado.               ║
# ║         3. Animación de dibujo gradual de la vértebra (spine) en Modo 1.  ║
# ║         4. Indicadores de estado visuales (✅/❌) en paneles de info.      ║
# ║                                                                            ║
# ╚════════════════════════════════════════════════════════════════════════════╝

import pygame
import math
import numpy as np
from collections import deque
import sys

# ==============================================================================
# FUNCIONES DE UTILERÍA Y EASING
# ==============================================================================

def ease_in_out_cubic(t):
    """Función de suavizado para transiciones (In-Out-Cubic)."""
    return 4 * t**3 if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2

# ==============================================================================
# INICIALIZACIÓN DE PYGAME
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

# Variables globales (Mantener la estructura original para compatibilidad)
n = 6
vertice_pos = []
vertice_rad = 28
aristas = []
grafo = []
parent = []

# ==============================================================================
# CLASE BASE PARA PANTALLAS (TRANSICIONES)
# ==============================================================================

class BaseScreen:
    """Clase base para todas las pantallas con lógica de transición de opacidad."""
    def __init__(self):
        self.transition_time = 400  # ms
        self.transition_timer = 0
        self.transition_in = True
        self.alpha_progress = 1.0

    def start_transition(self, is_entering):
        self.transition_in = is_entering
        self.transition_timer = self.transition_time
        self.alpha_progress = 0.0 if is_entering else 1.0

    def update_transition(self, dt):
        if self.transition_timer > 0:
            self.transition_timer -= dt
            t = 1.0 - (max(0, self.transition_timer) / self.transition_time)
            
            # Aplicar Easing
            eased_t = ease_in_out_cubic(t)
            
            # Ajustar progreso basado en la dirección
            self.alpha_progress = eased_t if self.transition_in else 1.0 - eased_t
            
            return self.alpha_progress
        
        self.alpha_progress = 1.0 if self.transition_in else 0.0
        return self.alpha_progress

    def draw(self, surface, alpha_progress=1.0):
        # Este método debe ser implementado por las subclases
        raise NotImplementedError
        
    def update(self, mouse_pos, dt):
        pass
        
    def handle_event(self, event):
        return None

# ==============================================================================
# COMPONENTES DE UI PROFESIONALES (MODIFICADO PARA MULTILÍNEA)
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
        
        # Texto - MODIFICADO PARA SOPORTAR SALTOS DE LÍNEA
        lines = self.text.split('\n')
        total_height = sum(FONT_BOLD.get_height() for line in lines)
        start_y = self.rect.centery - total_height // 2
        
        for line in lines:
            text_surf = FONT_BOLD.render(line, True, COLORS['white'])
            text_rect = text_surf.get_rect(centerx=self.rect.centerx, y=start_y)
            surface.blit(text_surf, text_rect)
            start_y += text_surf.get_height()

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

# El resto de la clase InputField no necesita cambios
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
        if self.label:
            label_surf = FONT_SMALL.render(self.label, True, COLORS['dark'])
            surface.blit(label_surf, (self.rect.x, self.rect.y - 25))
        
        shadow_rect = self.rect.move(2, 2)
        pygame.draw.rect(surface, (220, 220, 220), shadow_rect, border_radius=6)
        
        bg_color = COLORS['white'] if not self.active else (250, 250, 255)
        pygame.draw.rect(surface, bg_color, self.rect, border_radius=6)
        
        border_color = COLORS['accent'] if self.active else COLORS['gray']
        pygame.draw.rect(surface, border_color, self.rect, 2, border_radius=6)
        
        display_text = self.text if self.text else self.placeholder
        text_color = COLORS['dark'] if self.text else COLORS['gray']
        text_surf = FONT_REGULAR.render(display_text, True, text_color)
        
        max_width = self.rect.width - 20
        if text_surf.get_width() > max_width:
            temp_text = display_text
            while FONT_REGULAR.render(temp_text + "...", True, text_color).get_width() > max_width and len(temp_text) > 1:
                temp_text = temp_text[:-1]
            text_surf = FONT_REGULAR.render(temp_text + "...", True, text_color)
        
        text_x = self.rect.x + 10
        text_y = self.rect.y + (self.rect.height - text_surf.get_height()) // 2
        surface.blit(text_surf, (text_x, text_y))
        
        if self.active and self.cursor_visible:
            cursor_x = text_x + text_surf.get_width()
            pygame.draw.line(surface, COLORS['accent'], 
                           (cursor_x, text_y + 2),
                           (cursor_x, text_y + text_surf.get_height() - 2), 2)
    
    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer >= 500:
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
# PANTALLA DE SELECCIÓN DE N (AHORA HEREDA DE BaseScreen)
# ==============================================================================

class NSelectionScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.title = "CONFIGURACIÓN INICIAL"
        self.subtitle = "Fórmula de Cayley: n^(n-2) árboles etiquetados"
        
        input_width = 300
        input_x = WIDTH // 2 - input_width // 2
        self.n_input = InputField(input_x, 350, input_width, 50, 
                                 "NÚMERO DE VÉRTICES (n ≥ 2)", "Ej: 6")
        
        btn_width = 200
        btn_x = WIDTH // 2 - btn_width // 2
        self.confirm_btn = ProfessionalButton(btn_x, 450, btn_width, 50, "CONTINUAR", COLORS['success'])
        
        self.info_btn = ProfessionalButton(WIDTH - 120, 30, 100, 40, "ℹ️ INFO", COLORS['info'])
        
        self.error_message = ""
        self.selected_n = 6
        
    def draw(self, surface, alpha_progress=1.0):
        # Usar una superficie temporal para el efecto de transición
        temp_surface = pygame.Surface((WIDTH, HEIGHT))
        temp_surface.fill(COLORS['background'])
        
        # Dibujar todos los elementos en temp_surface
        header_rect = pygame.Rect(0, 0, WIDTH, 120)
        pygame.draw.rect(temp_surface, COLORS['header'], header_rect)
        
        title_surf = FONT_TITLE.render(self.title, True, COLORS['white'])
        title_shadow = FONT_TITLE.render(self.title, True, (20, 40, 80))
        temp_surface.blit(title_shadow, (WIDTH//2 - title_surf.get_width()//2 + 2, 42))
        temp_surface.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 40))
        
        subtitle_surf = FONT_SUBTITLE.render(self.subtitle, True, COLORS['light'])
        temp_surface.blit(subtitle_surf, (WIDTH//2 - subtitle_surf.get_width()//2, 100))
        
        panel_rect = pygame.Rect(WIDTH//2 - 300, 200, 600, 350)
        pygame.draw.rect(temp_surface, COLORS['white'], panel_rect, border_radius=15)
        pygame.draw.rect(temp_surface, COLORS['accent'], panel_rect, 3, border_radius=15)
        
        icon_rect = pygame.Rect(WIDTH//2 - 40, 220, 80, 80)
        pygame.draw.circle(temp_surface, COLORS['info'], icon_rect.center, 40)
        tree_icon = FONT_TITLE.render("T", True, COLORS['white'])
        temp_surface.blit(tree_icon, (icon_rect.centerx - tree_icon.get_width()//2, 
                                icon_rect.centery - tree_icon.get_height()//2))
        
        instructions = [
            "Ingrese el número de vértices (n) para el árbol.",
            "La fórmula de Cayley establece que el número de",
            f"árboles etiquetados con n vértices es n^(n-2).",
            "",
            "Valores recomendados: 3 a 15 vértices"
        ]
        
        for i, line in enumerate(instructions):
            line_surf = FONT_REGULAR.render(line, True, COLORS['dark'])
            temp_surface.blit(line_surf, (WIDTH//2 - line_surf.get_width()//2, 320 + i * 30))
        
        self.n_input.draw(temp_surface)
        
        if self.error_message:
            error_bg = pygame.Rect(WIDTH//2 - 250, 420, 500, 40)
            pygame.draw.rect(temp_surface, (255, 235, 235), error_bg, border_radius=8)
            pygame.draw.rect(temp_surface, COLORS['danger'], error_bg, 2, border_radius=8)
            
            error_surf = FONT_SMALL.render(self.error_message, True, COLORS['danger'])
            temp_surface.blit(error_surf, (WIDTH//2 - error_surf.get_width()//2, 430))
        
        self.confirm_btn.draw(temp_surface)
        self.info_btn.draw(temp_surface)
        
        try:
            temp_n = int(self.n_input.get_value() or "6")
            if 2 <= temp_n <= 20:
                formula = FONT_BOLD.render(f"n = {temp_n}: {temp_n}^({temp_n}-2) = {temp_n**(temp_n-2):,} árboles", 
                                          True, COLORS['success'])
                temp_surface.blit(formula, (WIDTH//2 - formula.get_width()//2, 520))
                self.selected_n = temp_n
        except:
            pass
            
        # Aplicar transparencia y dibujar en la pantalla principal
        alpha_value = int(255 * alpha_progress)
        temp_surface.set_alpha(alpha_value)
        surface.blit(temp_surface, (0, 0))
    
    def update(self, mouse_pos, dt):
        self.n_input.update(dt)
        self.confirm_btn.update(mouse_pos)
        self.info_btn.update(mouse_pos)
    
    # Resto de métodos de NSelectionScreen (handle_event, validate_input, show_info) sin cambios
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
# PANTALLA PRINCIPAL (AHORA HEREDA DE BaseScreen)
# ==============================================================================

class MainMenuScreen(BaseScreen):
    def __init__(self):
        super().__init__()
        self.title = f"DEMOSTRACIÓN DE JOYAL - n = {n}"
        
        btn_width = 300
        btn_height = 100
        center_x = WIDTH // 2
        
        # El texto ahora se maneja correctamente con saltos de línea
        self.btn_mode1 = ProfessionalButton(center_x - btn_width - 20, 300, btn_width, btn_height, 
                                           "MODO 1\nÁRBOL → FUNCIÓN", COLORS['info'])
        
        self.btn_mode2 = ProfessionalButton(center_x + 20, 300, btn_width, btn_height, 
                                           "MODO 2\nFUNCIÓN → ÁRBOL", COLORS['success'])
        
        self.btn_reset = ProfessionalButton(center_x - 100, 450, 200, 60, 
                                           "REINICIAR", COLORS['warning'])
        
        self.btn_back = ProfessionalButton(30, 30, 120, 40, "← VOLVER", COLORS['gray'])
        
        self.tree_info = f"Árboles posibles con {n} vértices: {n**(n-2):,}"
    
    def draw(self, surface, alpha_progress=1.0):
        temp_surface = pygame.Surface((WIDTH, HEIGHT))
        temp_surface.fill(COLORS['background'])
        
        # Encabezado con gradiente
        header_rect = pygame.Rect(0, 0, WIDTH, 180)
        for y in range(header_rect.height):
            color_val = 30 + int(40 * (y / header_rect.height))
            pygame.draw.line(temp_surface, (color_val, 60, 114), (0, y), (WIDTH, y))
        
        # Título
        title_surf = FONT_TITLE.render(self.title, True, COLORS['white'])
        title_shadow = FONT_TITLE.render(self.title, True, (20, 40, 80))
        temp_surface.blit(title_shadow, (WIDTH//2 - title_surf.get_width()//2 + 2, 52))
        temp_surface.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 50))
        
        # Fórmula
        formula = FONT_SUBTITLE.render(f"Fórmula de Cayley: n^(n-2) = {n}^({n}-2) = {n**(n-2):,}", 
                                      True, COLORS['light'])
        temp_surface.blit(formula, (WIDTH//2 - formula.get_width()//2, 120))
        
        # Panel central
        panel_rect = pygame.Rect(WIDTH//2 - 350, 200, 700, 350)
        pygame.draw.rect(temp_surface, COLORS['white'], panel_rect, border_radius=20)
        pygame.draw.rect(temp_surface, COLORS['accent'], panel_rect, 3, border_radius=20)
        
        # Descripción
        desc_lines = [
            "Esta aplicación demuestra la biyección de Joyal para la",
            "fórmula de Cayley, que establece una correspondencia entre",
            "árboles etiquetados y funciones f: V → V.",
            "",
            "Seleccione un modo de operación:"
        ]
        
        for i, line in enumerate(desc_lines):
            line_surf = FONT_REGULAR.render(line, True, COLORS['dark'])
            temp_surface.blit(line_surf, (WIDTH//2 - line_surf.get_width()//2, 220 + i * 30))
        
        # Dibujar botones
        self.btn_mode1.draw(temp_surface)
        self.btn_mode2.draw(temp_surface)
        self.btn_reset.draw(temp_surface)
        self.btn_back.draw(temp_surface)
        
        # Dibujar vértices en círculo (solo visual)
        self.draw_vertices_preview(temp_surface)

        # Aplicar transparencia
        alpha_value = int(255 * alpha_progress)
        temp_surface.set_alpha(alpha_value)
        surface.blit(temp_surface, (0, 0))
    
    # Resto de métodos de MainMenuScreen sin cambios
    def draw_vertices_preview(self, surface):
        center_x, center_y = WIDTH // 2, 650
        radius = 120
        num_vertices = min(n, 12)
        
        preview_area = pygame.Rect(center_x - radius - vertice_rad - 10, 
                                 center_y - radius - vertice_rad - 10,
                                 (radius + vertice_rad + 10) * 2,
                                 (radius + vertice_rad + 10) * 2)
        pygame.draw.rect(surface, COLORS['background'], preview_area)
        
        for i in range(num_vertices):
            angle = 2 * math.pi * i / num_vertices - math.pi/2
            x = center_x + radius * math.cos(angle)
            y = center_y + radius * math.sin(angle)
            
            pygame.draw.circle(surface, COLORS['vertex'], (int(x), int(y)), vertice_rad)
            pygame.draw.circle(surface, COLORS['white'], (int(x), int(y)), vertice_rad, 2)
            
            num_surf = FONT_BOLD.render(str(i+1), True, COLORS['white'])
            surface.blit(num_surf, (int(x) - num_surf.get_width()//2, 
                                   int(y) - num_surf.get_height()//2))
        
        info_text = f"Visualizando {num_vertices} de {n} vértices"
        info_surf = FONT_SMALL.render(info_text, True, COLORS['gray'])
        surface.blit(info_surf, (center_x - info_surf.get_width()//2, center_y + 150))
    
    def update(self, mouse_pos, dt):
        self.btn_mode1.update(mouse_pos)
        self.btn_mode2.update(mouse_pos)
        self.btn_reset.update(mouse_pos)
        self.btn_back.update(mouse_pos)
    
    def handle_event(self, event):
        if self.btn_mode1.handle_event(event):
            return "MODE1"
        elif self.btn_mode2.handle_event(event):
            return "MODE2"
        elif self.btn_reset.handle_event(event):
            return "RESET"
        elif self.btn_back.handle_event(event):
            return "BACK"
        return None

# ==============================================================================
# MODO 1: ÁRBOL → FUNCIÓN (AHORA HEREDA DE BaseScreen)
# ==============================================================================

class TreeToFunctionMode(BaseScreen):
    def __init__(self):
        super().__init__()
        self.title = "MODO 1: CONSTRUIR ÁRBOL → OBTENER FUNCIÓN"
        self.step = 0
        self.selected_vertex = None
        self.start_vertex = None
        self.end_vertex = None
        self.function = [None] * n
        self.spine_edges = []
        self.directed_edges = []
        self.spine_path = None
        
        # Variables de animación
        self.spine_animation_timer = 0
        self.spine_animation_speed = 100 # ms por segmento
        self.animated_spine_segments = 0

        # Botones
        self.btn_back = ProfessionalButton(30, 30, 120, 40, "← MENÚ", COLORS['gray'])
        self.btn_reset = ProfessionalButton(WIDTH - 150, 30, 120, 40, "REINICIAR", COLORS['warning'])
        self.btn_next = ProfessionalButton(WIDTH - 280, HEIGHT - 80, 120, 40, "CONTINUAR", COLORS['success'])
        self.btn_prev = ProfessionalButton(WIDTH - 410, HEIGHT - 80, 120, 40, "ATRÁS", COLORS['gray'])
        
        self.vertex_buttons = []
        self.create_vertex_buttons()
        
        self.info_panel_rect = pygame.Rect(20, 100, 350, HEIGHT - 250)
        self.graph_area = pygame.Rect(400, 100, WIDTH - 420, HEIGHT - 200)
        self.vertex_buttons_area = pygame.Rect(0, HEIGHT - 180, WIDTH, 180)
    
    def create_vertex_buttons(self):
        self.vertex_buttons = []
        max_per_row = min(n, 10)
        start_x = (WIDTH - max_per_row * 60) // 2
        
        for i in range(n):
            row = i // max_per_row
            col = i % max_per_row
            x = start_x + col * 60
            y = HEIGHT - 150 + row * 50
            
            btn = ProfessionalButton(x, y, 55, 40, str(i+1), COLORS['vertex'])
            self.vertex_buttons.append(btn)
    
    def draw(self, surface, alpha_progress=1.0):
        temp_surface = pygame.Surface((WIDTH, HEIGHT))
        temp_surface.fill(COLORS['background'])
        
        # Encabezado
        header_rect = pygame.Rect(0, 0, WIDTH, 100)
        pygame.draw.rect(temp_surface, COLORS['info'], header_rect)
        
        title_surf = FONT_TITLE.render(self.title, True, COLORS['white'])
        temp_surface.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 30))
        
        # Instrucciones según el paso
        instructions = self.get_instructions()
        instr_surf = FONT_REGULAR.render(instructions, True, COLORS['dark'])
        temp_surface.blit(instr_surf, (WIDTH//2 - instr_surf.get_width()//2, 70))
        
        # Dibujar panel de información
        self.draw_info_panel(temp_surface)
        
        # Dibujar árbol en el área designada
        self.draw_tree(temp_surface)
        
        # Limpiar área de botones de vértices
        pygame.draw.rect(temp_surface, COLORS['background'], self.vertex_buttons_area)
        
        # Dibujar botones de vértices
        for btn in self.vertex_buttons:
            btn.draw(temp_surface)
        
        # Dibujar botones de control
        self.btn_back.draw(temp_surface)
        self.btn_reset.draw(temp_surface)
        
        if self.step > 0:
            self.btn_prev.draw(temp_surface)
        
        if self.step < 3 and (self.step == 0 and len(aristas) == n - 1) or (self.step > 0 and self.check_step_complete()):
             self.btn_next.draw(temp_surface)
        
        # Indicador de paso
        self.draw_step_indicator(temp_surface)
        
        # Aplicar transparencia
        alpha_value = int(255 * alpha_progress)
        temp_surface.set_alpha(alpha_value)
        surface.blit(temp_surface, (0, 0))

    def update(self, mouse_pos, dt):
        # Actualización de botones
        for btn in self.vertex_buttons:
            btn.update(mouse_pos)
        self.btn_back.update(mouse_pos)
        self.btn_reset.update(mouse_pos)
        self.btn_next.update(mouse_pos)
        self.btn_prev.update(mouse_pos)
        
        # Animación de la vértebra
        if self.step == 3 and self.spine_path and self.animated_spine_segments < len(self.spine_path) - 1:
            self.spine_animation_timer += dt
            if self.spine_animation_timer >= self.spine_animation_speed:
                self.animated_spine_segments += 1
                self.spine_animation_timer = 0
                if self.animated_spine_segments == len(self.spine_path) - 1:
                    # Una vez que la vértebra está dibujada, dibujar la función
                    self.directed_edges = self.direct_edges()
    
    def draw_tree(self, surface):
        # Limpiar área del gráfico
        pygame.draw.rect(surface, COLORS['background'], self.graph_area)
        
        # Dibujar aristas
        for v1, v2 in aristas:
            x1, y1 = vertice_pos[v1]
            x2, y2 = vertice_pos[v2]
            
            color = COLORS['edge']
            width = 3
            
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), width)
        
        # Dibujar flechas para aristas dirigidas (solo si la animación de la vértebra terminó)
        if self.animated_spine_segments == len(self.spine_path) - 1:
             for v1, v2 in self.directed_edges:
                self.draw_arrow(surface, vertice_pos[v1], vertice_pos[v2], COLORS['arrow'])

        # Dibujar vértebra destacada con animación gradual
        if self.spine_path and len(self.spine_path) > 1 and self.step >= 3:
            for i in range(min(self.animated_spine_segments, len(self.spine_path) - 1)):
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

    def draw_info_panel(self, surface):
        # Fondo y borde
        pygame.draw.rect(surface, COLORS['white'], self.info_panel_rect, border_radius=10)
        pygame.draw.rect(surface, COLORS['accent'], self.info_panel_rect, 2, border_radius=10)
        
        # Título
        title_surf = FONT_BOLD.render("INFORMACIÓN DEL PROCESO", True, COLORS['accent'])
        surface.blit(title_surf, (self.info_panel_rect.x + 20, self.info_panel_rect.y + 20))
        
        info_y = self.info_panel_rect.y + 60
        
        # Indicadores de estado
        info_lines = [
            f"1. Árbol completo: {'✅ Sí' if self.is_tree_complete() else '❌ No'} ({len(aristas)}/{n-1} aristas)",
            f"2. Vértice Inicial (I): {f'✅ {self.start_vertex+1}' if self.start_vertex is not None else '❌ No seleccionado'}",
            f"3. Vértice Final (F): {f'✅ {self.end_vertex+1}' if self.end_vertex is not None else '❌ No seleccionado'}",
        ]
        
        for i, line in enumerate(info_lines):
            line_surf = FONT_REGULAR.render(line, True, COLORS['dark'])
            surface.blit(line_surf, (self.info_panel_rect.x + 20, info_y + i * 25))

        # Función generada - AHORA CON FORMATO DE TABLA
        if self.step == 3:
            func_y = info_y + len(info_lines) * 25 + 20
            func_title = FONT_BOLD.render("FUNCIÓN GENERADA:", True, COLORS['success'])
            surface.blit(func_title, (self.info_panel_rect.x + 20, func_y))

            table_y = func_y + 30
            header_x = self.info_panel_rect.x + 20
            
            # Encabezado de la tabla (V y f(V))
            header_v = FONT_BOLD.render("V", True, COLORS['dark'])
            header_fv = FONT_BOLD.render("f(V)", True, COLORS['dark'])
            surface.blit(header_v, (header_x, table_y))
            surface.blit(header_fv, (header_x + 60, table_y))
            
            pygame.draw.line(surface, COLORS['gray'], (header_x, table_y + 25), (header_x + 150, table_y + 25), 1)

            max_rows = min(n, 12) # Mostrar más filas
            for i in range(max_rows):
                v_text = FONT_REGULAR.render(str(i+1), True, COLORS['dark'])
                fv_value = self.function[i]
                fv_text = FONT_REGULAR.render(str(fv_value+1 if fv_value is not None else "?"), True, 
                                            COLORS['success'] if fv_value is not None else COLORS['gray'])
                
                surface.blit(v_text, (header_x + 5, table_y + 30 + i * 22))
                surface.blit(fv_text, (header_x + 65, table_y + 30 + i * 22))
            
            if n > 12:
                dots_text = FONT_REGULAR.render("...", True, COLORS['dark'])
                surface.blit(dots_text, (header_x + 30, table_y + 30 + 12 * 22))

    # Resto de métodos de TreeToFunctionMode (get_instructions, draw_vertices, draw_arrow, etc.) sin cambios
    
    # ... (código para draw_vertices, draw_arrow, draw_spine_segment, highlight_vertex, draw_step_indicator)
    # ... (código para handle_event, check_step_complete, is_tree_complete, connect_vertex, add_edge)
    # ... (código para calculate_function, find_path, direct_edges, reset_state)
    
    def get_instructions(self):
        instructions = [
            "PASO 1: Conecte vértices para formar un árbol (haga clic en dos vértices)",
            "PASO 2: Seleccione el vértice INICIAL de la vértebra",
            "PASO 3: Seleccione el vértice FINAL de la vértebra",
            "¡Árbol completo! La función ha sido generada y animada"
        ]
        return instructions[self.step]
    
    def draw_vertices(self, surface):
        for i, pos in enumerate(vertice_pos):
            if not self.graph_area.collidepoint(pos):
                continue
                
            shadow_pos = (pos[0] + 2, pos[1] + 2)
            pygame.draw.circle(surface, (100, 100, 100, 100), shadow_pos, vertice_rad)
            
            color = COLORS['vertex']
            if i == self.selected_vertex:
                color = COLORS['highlight']
            elif i == self.start_vertex:
                color = COLORS['success']
            elif i == self.end_vertex:
                color = COLORS['danger']
            
            pygame.draw.circle(surface, color, pos, vertice_rad)
            pygame.draw.circle(surface, COLORS['white'], pos, vertice_rad, 2)
            
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

    def draw_spine_segment(self, surface, start, end):
        pygame.draw.line(surface, (150, 50, 50), 
                        (start[0] + 2, start[1] + 2),
                        (end[0] + 2, end[1] + 2), 6)
        pygame.draw.line(surface, COLORS['spine'], start, end, 4)
    
    def highlight_vertex(self, surface, vertex_idx, color):
        pos = vertice_pos[vertex_idx]
        pygame.draw.circle(surface, color, pos, vertice_rad + 5, 3)
        
        label = ""
        if vertex_idx == self.start_vertex:
            label = "INICIO (I)"
        elif vertex_idx == self.end_vertex:
            label = "FIN (F)"
        
        if label:
            label_surf = FONT_SMALL.render(label, True, color)
            surface.blit(label_surf, (pos[0] - label_surf.get_width()//2, pos[1] - 40))

    def draw_step_indicator(self, surface):
        steps = ["1. Construir", "2. Inicio", "3. Fin", "4. Completado"]
        start_x = WIDTH // 2 - 200
        indicator_y = HEIGHT - 120
        for i in range(4):
            step_rect = pygame.Rect(start_x + i * 130, indicator_y, 120, 40)
            
            if i < self.step:
                color = COLORS['success']
            elif i == self.step:
                color = COLORS['highlight']
            else:
                color = COLORS['gray']
            
            pygame.draw.rect(surface, color, step_rect, border_radius=5)
            pygame.draw.rect(surface, COLORS['dark'], step_rect, 2, border_radius=5)
            
            text_surf = FONT_SMALL.render(steps[i], True, COLORS['white'] if i <= self.step else COLORS['dark'])
            surface.blit(text_surf, (step_rect.centerx - text_surf.get_width()//2, 
                                     step_rect.centery - text_surf.get_height()//2))

    def handle_event(self, event):
        # Manejo de eventos de botones
        if self.btn_back.handle_event(event): return "BACK"
        if self.btn_reset.handle_event(event): self.reset_state(); return None
        if self.btn_prev.handle_event(event) and self.step > 0: self.step -= 1; self.reset_animation_and_next_step_data(); return None
        
        if self.btn_next.handle_event(event) and self.step < 3:
            if self.check_step_complete():
                self.step += 1
                if self.step == 3: self.calculate_function()
                return None

        # Lógica de conexión de vértices
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            # Chequear clicks en los vértices del gráfico
            for i, pos in enumerate(vertice_pos):
                if math.hypot(mouse_pos[0] - pos[0], mouse_pos[1] - pos[1]) <= vertice_rad:
                    self.connect_vertex(i)
                    return None
            
            # Chequear clicks en los botones de vértices
            for i, btn in enumerate(self.vertex_buttons):
                if btn.handle_event(event):
                    self.connect_vertex(i)
                    return None
        return None
    
    def connect_vertex(self, vertex_idx):
        if self.step == 0:
            # PASO 1: CONSTRUIR ÁRBOL
            if self.selected_vertex is None:
                self.selected_vertex = vertex_idx
            elif self.selected_vertex == vertex_idx:
                self.selected_vertex = None
            else:
                self.add_edge(self.selected_vertex, vertex_idx)
                self.selected_vertex = None
        
        elif self.step == 1:
            # PASO 2: SELECCIONAR INICIO (I)
            self.start_vertex = vertex_idx
        
        elif self.step == 2:
            # PASO 3: SELECCIONAR FIN (F)
            if vertex_idx != self.start_vertex:
                self.end_vertex = vertex_idx
        
    def check_step_complete(self):
        if self.step == 0:
            return self.is_tree_complete()
        elif self.step == 1:
            return self.start_vertex is not None
        elif self.step == 2:
            return self.end_vertex is not None
        elif self.step == 3:
            return True
        return False

    def is_tree_complete(self):
        # n-1 aristas y es conexo (un solo componente)
        if len(aristas) != n - 1:
            return False
        return find(0) == find(1) # Basta con chequear que el componente 0 y 1 sean el mismo

    def add_edge(self, v1, v2):
        if (v1, v2) in aristas or (v2, v1) in aristas: return
        if find(v1) == find(v2): return
        aristas.append((v1, v2))
        union(v1, v2)
        grafo[v1].append(v2)
        grafo[v2].append(v1)
    
    def calculate_function(self):
        self.spine_path = self.find_path(self.start_vertex, self.end_vertex)
        if self.spine_path and len(self.spine_path) > 1:
            self.spine_edges = [(self.spine_path[i], self.spine_path[i+1]) for i in range(len(self.spine_path)-1)]
            
            # Asignar función para vértebra: f(v_i) = v_{i-1} (orden inverso de la ruta)
            for i in range(len(self.spine_path)):
                current = self.spine_path[i]
                target = self.spine_path[i-1] if i > 0 else self.spine_path[-1] # Ciclo
                self.function[current] = target
        
        self.directed_edges = self.direct_edges()
        for v1, v2 in self.directed_edges:
            self.function[v1] = v2

    def find_path(self, start, end):
        visited = [False] * n
        parent = [-1] * n
        queue = deque([start])
        visited[start] = True
        
        while queue:
            current = queue.popleft()
            if current == end:
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
        return []

    def direct_edges(self):
        dist = [-1] * n
        queue = deque([self.end_vertex])
        dist[self.end_vertex] = 0
        
        while queue:
            v = queue.popleft()
            for neighbor in grafo[v]:
                if dist[neighbor] == -1:
                    dist[neighbor] = dist[v] + 1
                    queue.append(neighbor)
        
        directed = []
        for v1, v2 in aristas:
            # Check if it's a spine edge (to avoid directing it, handled in calculate_function)
            in_spine = (v1, v2) in self.spine_edges or (v2, v1) in self.spine_edges
            
            if not in_spine:
                # Direct away from the spine path (towards the end_vertex)
                if dist[v1] < dist[v2]:
                    directed.append((v2, v1))
                elif dist[v2] < dist[v1]:
                    directed.append((v1, v2))
        return directed
    
    def reset_animation_and_next_step_data(self):
        self.selected_vertex = None
        if self.step < 3:
            self.function = [None] * n
            self.spine_edges.clear()
            self.directed_edges.clear()
            self.spine_path = None
            self.spine_animation_timer = 0
            self.animated_spine_segments = 0
    
    def reset_state(self):
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
        self.spine_animation_timer = 0
        self.animated_spine_segments = 0

# ==============================================================================
# MODO 2: FUNCIÓN → ÁRBOL (AHORA HEREDA DE BaseScreen)
# ==============================================================================

class FunctionToTreeMode(BaseScreen):
    def __init__(self):
        super().__init__()
        self.title = "MODO 2: FUNCIÓN → CONSTRUIR ÁRBOL"
        
        input_width = 500
        self.func_input = InputField(WIDTH//2 - input_width//2, 120, input_width, 50, "INGRESE LA FUNCIÓN f: V → V (ej: 2,3,1,5,5,4)", "Separada por comas, valores de 1 a n")
        
        self.btn_back = ProfessionalButton(30, 30, 120, 40, "← MENÚ", COLORS['gray'])
        self.btn_generate = ProfessionalButton(WIDTH//2 - 120, 190, 120, 50, "GENERAR ÁRBOL", COLORS['success'])
        self.btn_clear = ProfessionalButton(WIDTH//2 + 10, 190, 110, 50, "LIMPIAR", COLORS['warning'])
        
        self.function = []
        self.vertices_in_cycles = []
        self.vertices_not_in_cycles = []
        self.spine_edges = []
        self.tree_edges = []
        self.error_message = ""
        
        # Variables de animación
        self.tree_animation_timer = 0
        self.tree_animation_speed = 50 # ms por arista
        self.animated_tree_edges = 0

        self.info_panel_rect = pygame.Rect(20, 250, 350, HEIGHT - 300)
        self.graph_area = pygame.Rect(400, 250, WIDTH - 420, HEIGHT - 300)
    
    def draw(self, surface, alpha_progress=1.0):
        temp_surface = pygame.Surface((WIDTH, HEIGHT))
        temp_surface.fill(COLORS['background'])
        
        # Encabezado
        header_rect = pygame.Rect(0, 0, WIDTH, 100)
        pygame.draw.rect(temp_surface, COLORS['success'], header_rect)
        title_surf = FONT_TITLE.render(self.title, True, COLORS['white'])
        temp_surface.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 30))
        
        # Input y botones
        self.func_input.draw(temp_surface)
        self.btn_back.draw(temp_surface)
        self.btn_generate.draw(temp_surface)
        self.btn_clear.draw(temp_surface)
        
        # Mensaje de error
        if self.error_message:
            error_bg = pygame.Rect(WIDTH//2 - 250, 80, 500, 30)
            pygame.draw.rect(temp_surface, (255, 235, 235), error_bg, border_radius=8)
            error_surf = FONT_SMALL.render(self.error_message, True, COLORS['danger'])
            temp_surface.blit(error_surf, (WIDTH//2 - error_surf.get_width()//2, 85))

        # Dibujar panel de información
        self.draw_info_panel(temp_surface)
        
        # Dibujar árbol/función
        self.draw_graph(temp_surface)
        
        # Aplicar transparencia
        alpha_value = int(255 * alpha_progress)
        temp_surface.set_alpha(alpha_value)
        surface.blit(temp_surface, (0, 0))

    def update(self, mouse_pos, dt):
        self.func_input.update(dt)
        self.btn_back.update(mouse_pos)
        self.btn_generate.update(mouse_pos)
        self.btn_clear.update(mouse_pos)
        
        # Animación del árbol
        if self.tree_edges and self.animated_tree_edges < len(self.tree_edges):
            self.tree_animation_timer += dt
            if self.tree_animation_timer >= self.tree_animation_speed:
                self.animated_tree_edges = min(self.animated_tree_edges + 1, len(self.tree_edges))
                self.tree_animation_timer = 0
    
    def draw_graph(self, surface):
        pygame.draw.rect(surface, COLORS['background'], self.graph_area)
        
        # 1. Dibujar aristas del árbol animadas
        for i in range(self.animated_tree_edges):
            v1, v2 = self.tree_edges[i]
            pos1, pos2 = vertice_pos[v1], vertice_pos[v2]
            
            color = COLORS['edge']
            width = 3
            
            # Resaltar la vértebra
            if (v1, v2) in self.spine_edges or (v2, v1) in self.spine_edges:
                color = COLORS['spine']
                width = 5
            
            pygame.draw.line(surface, color, pos1, pos2, width)

        # 2. Dibujar flechas para la función (solo si no hay árbol o si es un paso previo)
        if not self.tree_edges and self.function:
            for i, f in enumerate(self.function):
                if f is not None and f < n and i < n:
                    pos_i = vertice_pos[i]
                    pos_f = vertice_pos[f]
                    if self.graph_area.collidepoint(pos_i) and self.graph_area.collidepoint(pos_f):
                        if i == f:
                            self.draw_loop(surface, pos_i)
                        else:
                            self.draw_arrow(surface, pos_i, pos_f, COLORS['gray'])
        
        # 3. Dibujar vértices
        for i, pos in enumerate(vertice_pos):
            if not self.graph_area.collidepoint(pos):
                continue
                
            shadow_pos = (pos[0] + 2, pos[1] + 2)
            pygame.draw.circle(surface, (100, 100, 100, 100), shadow_pos, vertice_rad)
            
            color = COLORS['vertex']
            if i in self.vertices_in_cycles:
                color = COLORS['spine']
                pygame.draw.circle(surface, color, pos, vertice_rad + 3) # Efecto de pulsación
            
            pygame.draw.circle(surface, color, pos, vertice_rad)
            pygame.draw.circle(surface, COLORS['white'], pos, vertice_rad, 2)
            
            num_surf = FONT_BOLD.render(str(i+1), True, COLORS['white'])
            surface.blit(num_surf, (pos[0] - num_surf.get_width()//2, 
                                   pos[1] - num_surf.get_height()//2))

    def draw_info_panel(self, surface):
        pygame.draw.rect(surface, COLORS['white'], self.info_panel_rect, border_radius=10)
        pygame.draw.rect(surface, COLORS['accent'], self.info_panel_rect, 2, border_radius=10)
        
        title_surf = FONT_BOLD.render("INFORMACIÓN DE LA FUNCIÓN", True, COLORS['accent'])
        surface.blit(title_surf, (self.info_panel_rect.x + 20, self.info_panel_rect.y + 20))
        
        info_y = self.info_panel_rect.y + 60
        
        # 1. Validación
        valid_text = f"Función válida: {'✅ Sí' if not self.error_message and self.function else '❌ No'}"
        valid_surf = FONT_REGULAR.render(valid_text, True, COLORS['success'] if not self.error_message and self.function else COLORS['danger'])
        surface.blit(valid_surf, (self.info_panel_rect.x + 20, info_y))
        
        info_y += 30
        
        # 2. Vértebra (vértices en ciclos)
        if self.vertices_in_cycles:
            cycles_text = f"Vértebra: {[v+1 for v in self.vertices_in_cycles]}"
            cycles_surf = FONT_SMALL.render(cycles_text, True, COLORS['spine'])
            surface.blit(cycles_surf, (self.info_panel_rect.x + 20, info_y))
            info_y += 25
        
        # 3. Otros vértices
        if self.vertices_not_in_cycles:
            not_cycles_text = f"Otros: {[v+1 for v in self.vertices_not_in_cycles]}"
            not_cycles_surf = FONT_SMALL.render(not_cycles_text, True, COLORS['vertex'])
            surface.blit(not_cycles_surf, (self.info_panel_rect.x + 20, info_y))
            info_y += 25
            
        # 4. Resultado del Árbol
        if self.tree_edges:
            tree_info = FONT_BOLD.render("ÁRBOL GENERADO", True, COLORS['success'])
            surface.blit(tree_info, (self.info_panel_rect.x + 20, info_y + 20))

    def draw_arrow(self, surface, start, end, color):
        # Implementación de dibujo de flecha (simétrica a la de TreeToFunctionMode)
        dx = end[0] - start[0]
        dy = end[1] - start[1]
        length = math.hypot(dx, dy)
        if length == 0: return
        start_adj = (start[0] + (dx / length) * vertice_rad, start[1] + (dy / length) * vertice_rad)
        end_adj = (end[0] - (dx / length) * vertice_rad, end[1] - (dy / length) * vertice_rad)
        pygame.draw.line(surface, color, start_adj, end_adj, 2)
        angle = math.atan2(dy, dx)
        arrow_size = 10
        left = (end_adj[0] - arrow_size * math.cos(angle - math.pi/6), end_adj[1] - arrow_size * math.sin(angle - math.pi/6))
        right = (end_adj[0] - arrow_size * math.cos(angle + math.pi/6), end_adj[1] - arrow_size * math.sin(angle + math.pi/6))
        pygame.draw.polygon(surface, color, [end_adj, left, right])

    def draw_loop(self, surface, pos):
        # Dibujar un pequeño bucle para f(v)=v
        radius = vertice_rad + 5
        center = (pos[0] + radius, pos[1] - radius)
        pygame.draw.circle(surface, COLORS['gray'], center, vertice_rad // 3, 2)
        
    def handle_event(self, event):
        if self.btn_back.handle_event(event):
            return "BACK"
        if self.btn_generate.handle_event(event):
            self.generate_tree()
        if self.btn_clear.handle_event(event):
            self.clear()
        
        if self.func_input.handle_event(event):
            self.generate_tree() # Generar al presionar ENTER
        
        return None

    def generate_tree(self):
        self.clear(keep_input=True)
        try:
            input_text = self.func_input.get_value()
            if not input_text:
                self.error_message = "Debe ingresar los valores de la función."
                return

            f_values = [int(x.strip()) - 1 for x in input_text.split(',') if x.strip()]
            
            if len(f_values) != n:
                self.error_message = f"Se esperan {n} valores (uno por vértice)."
                return
            
            for fv in f_values:
                if not (0 <= fv < n):
                    self.error_message = f"Los valores deben estar entre 1 y {n}."
                    return
            
            self.function = f_values
            self.error_message = ""
            self.decompose_function()
            self.construct_tree_from_function()
            self.animated_tree_edges = 0 # Iniciar animación

        except ValueError:
            self.error_message = "Formato no válido. Use números separados por comas."

    def decompose_function(self):
        self.vertices_in_cycles = []
        self.vertices_not_in_cycles = []
        visited = [False] * n

        for i in range(n):
            if not visited[i]:
                path = []
                current = i
                
                # Sigue la función hasta que se encuentre un vértice visitado o se repita
                while current not in path and not visited[current]:
                    path.append(current)
                    visited[current] = True
                    current = self.function[current]
                
                if current in path:
                    cycle_start_index = path.index(current)
                    cycle = path[cycle_start_index:]
                    self.vertices_in_cycles.extend(cycle)
                    self.vertices_not_in_cycles.extend(path[:cycle_start_index])
                else:
                    self.vertices_not_in_cycles.extend(path)

        self.vertices_in_cycles = sorted(list(set(self.vertices_in_cycles)))
        all_vertices = set(range(n))
        self.vertices_not_in_cycles = sorted(list(all_vertices - set(self.vertices_in_cycles)))

    def construct_tree_from_function(self):
        self.tree_edges = []
        self.spine_edges = []

        # 1. Los vértices en ciclos forman la vértebra (un solo camino)
        if len(self.vertices_in_cycles) > 1:
            for i in range(len(self.vertices_in_cycles) - 1):
                v1 = self.vertices_in_cycles[i]
                v2 = self.vertices_in_cycles[i+1]
                self.tree_edges.append((v1, v2))
                self.spine_edges.append((v1, v2))
        
        # 2. Aristas de vértices no en ciclos
        for v in self.vertices_not_in_cycles:
            fv = self.function[v]
            if fv is not None:
                self.tree_edges.append((v, fv))

    def clear(self, keep_input=False):
        self.function = []
        self.vertices_in_cycles = []
        self.vertices_not_in_cycles = []
        self.spine_edges = []
        self.tree_edges = []
        self.error_message = ""
        self.animated_tree_edges = 0
        if not keep_input:
            self.func_input.text = ""

# ==============================================================================
# FUNCIONES DE GRAFOS
# ==============================================================================

# Código para Disjoint Set Union (DSU) (find y union)
def find(i):
    if parent[i] == i:
        return i
    parent[i] = find(parent[i])
    return parent[i]

def union(i, j):
    root_i = find(i)
    root_j = find(j)
    if root_i != root_j:
        parent[root_i] = root_j
        return True
    return False

def calcular_posiciones_vertices(n_vertices):
    global vertice_pos
    vertice_pos = []
    centro_x, centro_y = WIDTH // 2, 500
    radio = min(350, 120 + n_vertices * 8)
    for i in range(n_vertices):
        angulo = 2 * math.pi * i / n_vertices - math.pi/2
        x = centro_x + radio * math.cos(angulo)
        y = centro_y + radio * math.sin(angulo)
        vertice_pos.append((int(x), int(y)))

def inicializar_estructuras(n_vertices):
    global n, aristas, grafo, parent
    n = n_vertices
    calcular_posiciones_vertices(n)
    aristas.clear()
    grafo = [[] for _ in range(n)]
    parent = list(range(n))

# ==============================================================================
# APLICACIÓN PRINCIPAL (MODIFICADO PARA TRANSICIONES)
# ==============================================================================

class JoyalApplication:
    def __init__(self):
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Inicialización de pantallas y estructuras
        inicializar_estructuras(6) # n=6 por defecto
        self.n_selection_screen = NSelectionScreen()
        self.main_menu_screen = MainMenuScreen()
        self.tree_to_func_screen = TreeToFunctionMode()
        self.func_to_tree_screen = FunctionToTreeMode()
        
        # Gestión de estados de transición
        self.screen_map = {
            "SELECT_N": self.n_selection_screen,
            "MAIN_MENU": self.main_menu_screen,
            "MODE1": self.tree_to_func_screen,
            "MODE2": self.func_to_tree_screen
        }
        
        self.current_screen_name = "SELECT_N"
        self.current_screen_obj = self.n_selection_screen
        self.next_screen_name = "SELECT_N"
        self.transition_active = False

    def _transition_to(self, target_screen_name):
        """Inicia una transición hacia una nueva pantalla."""
        if self.current_screen_name != target_screen_name:
            self.next_screen_name = target_screen_name
            self.transition_active = True
            self.current_screen_obj.start_transition(False) # Inicia transición de salida
        
    def _get_screen_obj(self, name):
        """Obtiene la instancia de la pantalla (re-inicializando si es necesario)."""
        if name == "MAIN_MENU":
             return MainMenuScreen()
        elif name == "MODE1":
             return TreeToFunctionMode()
        elif name == "MODE2":
             return FunctionToTreeMode()
        return self.screen_map.get(name)

    def run(self):
        while self.running:
            dt = self.clock.tick(60) # 60 FPS
            mouse_pos = pygame.mouse.get_pos()
            
            # 1. Manejar Eventos
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_F1:
                        self.show_help()

                # Solo procesar eventos en la pantalla actual si no hay transición de salida
                if not self.transition_active or self.current_screen_obj.transition_in:
                    result = self.current_screen_obj.handle_event(event)
                    
                    if result == True and self.current_screen_name == "SELECT_N":
                        n_val = self.n_selection_screen.selected_n
                        inicializar_estructuras(n_val)
                        # Re-inicializar todas las pantallas dependientes de n
                        self.main_menu_screen = MainMenuScreen()
                        self.tree_to_func_screen = TreeToFunctionMode()
                        self.func_to_tree_screen = FunctionToTreeMode()
                        self.screen_map = {
                            "SELECT_N": self.n_selection_screen,
                            "MAIN_MENU": self.main_menu_screen,
                            "MODE1": self.tree_to_func_screen,
                            "MODE2": self.func_to_tree_screen
                        }
                        self._transition_to("MAIN_MENU")
                    
                    elif result == "MODE1": self._transition_to("MODE1")
                    elif result == "MODE2": self._transition_to("MODE2")
                    elif result == "RESET": self._transition_to("SELECT_N")
                    elif result == "BACK": self._transition_to("MAIN_MENU")

            # 2. Lógica de Transición
            if self.transition_active:
                alpha = self.current_screen_obj.update_transition(dt)
                
                if not self.current_screen_obj.transition_in and alpha <= 0.0:
                    # Fin de transición de SALIDA, iniciar transición de ENTRADA
                    self.current_screen_name = self.next_screen_name
                    self.current_screen_obj = self.screen_map.get(self.current_screen_name)
                    self.current_screen_obj.start_transition(True)
                
                elif self.current_screen_obj.transition_in and alpha >= 1.0:
                    # Transición completa
                    self.transition_active = False
            
            # 3. Actualizar pantalla actual
            self.current_screen_obj.update(mouse_pos, dt)

            # 4. Dibujar
            screen.fill(COLORS['background'])
            
            # Dibujar la pantalla actual con el progreso de opacidad
            self.current_screen_obj.draw(screen, self.current_screen_obj.alpha_progress)
            
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
    print("  • Interfaz moderna con transiciones suaves (¡NUEVO!)")
    print("  • Componentes de UI mejorados")
    print("  • Animaciones visuales para la biyección (¡NUEVO!)")
    print("  • Sistema de estados bien separado")
    print("=" * 70)
    print("  Autores:")
    print("  • Martin Lora Cano")
    print("  • Cristian Andrés Diaz Ortega")
    print("  ...")
    app = JoyalApplication()
    app.run()
