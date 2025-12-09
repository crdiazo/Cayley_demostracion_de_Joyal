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

        # Para cada ciclo en _cycles_list: si len>1 conectarlos en orden (forman la vértebra)
        for cyc in self._cycles_list:
            if len(cyc) > 1:
                # conectar en orden c[i] -> c[i+1]
                for i in range(len(cyc)):
                    a = cyc[i]
                    b = cyc[(i+1) % len(cyc)]
                    # Añadir once (orden dirigido/indiferente según uso)
                    if (a, b) not in self.tree_edges and (b, a) not in self.tree_edges:
                        self.tree_edges.append((a, b))
                        self.spine_edges.append((a, b))
            else:
                # punto fijo (ciclo de longitud 1): no arista extra (se mantiene el vértice)
                pass

        # Para los vértices no en ciclos, crear arista (v -> f(v))
        for v in self.vertices_not_in_cycles:
            fv = self.function[v]
            if 0 <= fv < n:
                # evitar duplicados sencillos
                if (v, fv) not in self.tree_edges and (fv, v) not in self.tree_edges:
                    self.tree_edges.append((v, fv))

        self.stage = "tree"
        self.error_message = ""
        if self._debug:
            print("construct_tree_from_function -> edges:", [(a+1,b+1) for a,b in self.tree_edges])
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
