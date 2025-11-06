import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk
import math, random, io
import requests
from PIL import Image, ImageTk

from game_trivia import GameEngine, CATEGORIES

# Apariencia / colores
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG_CYAN = "#B2EBF2"
PANEL = "#E0F7FA"
TEXT_DARK = "#263238"

CATEGORY_COLORS = {
    "Historia": "#E57373",   # rojo
    "Ciencia": "#64B5F6",    # azul
    "Geografía": "#81C784",  # verde
    "Deporte": "#FFF176",    # amarillo
}
CATEGORY_ICONS = {
    "Historia": "🏛️",
    "Ciencia": "🧠",
    "Geografía": "🗺️",
    "Deporte": "⚽",
}

TIMER_SECONDS = 15  # fijo, por requerimiento

class TriviaGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("🎡 Trivia V3 — Preguntados")
        self.geometry("980x700")
        self.resizable(False, False)
        self.configure(fg_color=BG_CYAN)

        # Lógica
        self.engine = GameEngine()
        self.player = None
        self.current_question = None
        self.questions_remaining = 0
        self.current_category = None

        # Ruleta estado
        self._angle = 0.0
        self._spinning = False
        self._spin_velocity = 0.0
        self._spin_friction = 0.985

        # Timer
        self._time_left = 0
        self._timer_id = None

        self._build_ui()
        self._refresh_ranking()

        # ----- Frame principal (donde se dibujan las pantallas) -----
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(expand=True, fill="both")

        # Mostrar pantalla de registro al iniciar
        #self._show_registration()


        # ----- Pantalla completa (ajustada) -----
        # Inicia maximizada, pero se puede restaurar con F11 o ESC
        self.state('zoomed')  # Maximiza la ventana en Windows

        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

    def toggle_fullscreen(self, event=None):
        """Activa o desactiva el modo pantalla completa"""
        current_state = self.attributes("-fullscreen")
        self.attributes("-fullscreen", not current_state)

    def exit_fullscreen(self, event=None):
        """Sale del modo pantalla completa"""
        self.attributes("-fullscreen", False)
        self.state('zoomed')


    
    #def _show_registration(self):
        #"""Pantalla de registro dentro de la app"""
        # Limpiamos cualquier contenido anterior
        #for widget in self.content_frame.winfo_children():
        #    widget.destroy()

        #lbl_title = ctk.CTkLabel(self.content_frame, text="🎮 Bienvenido a Preguntados", font=("Arial Rounded MT Bold", 36))
        #lbl_title.pack(pady=60)

        #lbl_name = ctk.CTkLabel(self.content_frame, text="Ingresá tu nombre:", font=("Arial", 22))
        #lbl_name.pack(pady=10)

        #self.entry_name = ctk.CTkEntry(self.content_frame, placeholder_text="Tu nombre", width=300, height=40)
        #self.entry_name.pack(pady=10)

        #btn_start = ctk.CTkButton(
        #    self.content_frame,
        #    text="🚀 Comenzar",
        #    font=("Arial Rounded MT Bold", 20),
        #    fg_color="#0077b6",
        #    hover_color="#0096c7",
        #    height=45,
        #    width=200,
        #    command=self._register_player
        #)
        #btn_start.pack(pady=30)
        
    def _register_player(self):
            """Registra al jugador y pasa al juego"""
            name = self.entry_name.get().strip()
            if not name:
                self.entry_name.configure(placeholder_text="⚠️ Ingresá un nombre")
                return
    
            try:
                self.player = self.engine.create_player(name)
            except ValueError as e:
                self.entry_name.delete(0, "end")
                self.entry_name.configure(placeholder_text=str(e))
                return
    
            # Una vez registrado, mostramos la pantalla de la ruleta o primera pregunta
            self._show_wheel_screen()




    # ---------------- UI ----------------
    def _build_ui(self):
        title = ctk.CTkLabel(self, text="🎯 TRIVIA PREGUNTADOS — V3",
                             font=("Arial Black", 28), text_color=TEXT_DARK)
        title.pack(pady=10)

        self.tabs = ctk.CTkTabview(self, width=930, height=600)
        self.tabs.pack(pady=5)
        self.tab_game = self.tabs.add("Jugar")
        self.tab_rank = self.tabs.add("Clasificación")

        self._build_tab_game(self.tab_game)
        self._build_tab_rank(self.tab_rank)

    def _build_tab_game(self, parent):
        container = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=14)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Izquierda: ruleta
        left = ctk.CTkFrame(container, fg_color=PANEL)
        left.pack(side="left", fill="y", padx=10, pady=10)

        self.canvas = tk.Canvas(left, width=360, height=360, bg=PANEL, highlightthickness=0)
        self.canvas.pack(pady=(10, 0))
        self._draw_roulette()

        self.btn_spin = ctk.CTkButton(left, text="🎡 Girar ruleta", width=220, height=40,
                                      command=self._on_spin, state="disabled",
                                      fg_color="#0288D1", hover_color="#03A9F4")
        self.btn_spin.pack(pady=10)

        self.lbl_category = ctk.CTkLabel(left, text="Categoría: —", font=("Arial", 18, "bold"), text_color=TEXT_DARK)
        self.lbl_category.pack(pady=4)

        # Derecha: registro + pregunta
        right = ctk.CTkFrame(container, fg_color=PANEL)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        reg = ctk.CTkFrame(right, fg_color="#FFFFFF", corner_radius=12)
        reg.pack(fill="x", padx=6, pady=(6, 10))
        ctk.CTkLabel(reg, text="Nombre del jugador:", text_color=TEXT_DARK).grid(row=0, column=0, padx=10, pady=10)
        self.ent_name = ctk.CTkEntry(reg, width=220)
        self.ent_name.grid(row=0, column=1, padx=6, pady=10)
        self.btn_register = ctk.CTkButton(reg, text="Registrar", command=self._on_register, width=120,
                                          fg_color="#388E3C", hover_color="#43A047")
        self.btn_register.grid(row=0, column=2, padx=10, pady=10)
        self.lbl_status = ctk.CTkLabel(reg, text="Sin jugador", text_color="#546E7A")
        self.lbl_status.grid(row=0, column=3, padx=10, pady=10)

        # Pregunta + imagen + opciones
        qbox = ctk.CTkFrame(right, fg_color="#FFFFFF", corner_radius=12)
        qbox.pack(fill="both", expand=True, padx=6, pady=6)

        # Imagen (arriba)
        self.img_label = ctk.CTkLabel(qbox, text="")
        self.img_label.pack(pady=(12, 4))

        self.lbl_timer = ctk.CTkLabel(qbox, text="⏳ Tiempo: —", text_color="#D84315", font=("Arial", 14, "bold"))
        self.lbl_timer.pack(pady=(0, 4))

        self.lbl_prompt = ctk.CTkLabel(qbox, text="Registrate y girá la ruleta para comenzar.",
                                       wraplength=520, justify="left", font=("Arial", 16), text_color=TEXT_DARK)
        self.lbl_prompt.pack(padx=14, pady=(4, 6), anchor="w")

        self.option_var = tk.IntVar(value=-1)
        self.option_buttons = []
        for i in range(4):
            rb = ctk.CTkRadioButton(qbox, text=f"Opción {i+1}", variable=self.option_var, value=i,
                                    text_color=TEXT_DARK, fg_color="#03A9F4", hover_color="#4FC3F7", border_color="#0288D1")
            rb.pack(anchor="w", padx=16, pady=4)
            self.option_buttons.append(rb)

        # Botones inferiores
        btns = ctk.CTkFrame(right, fg_color=PANEL)
        btns.pack(fill="x", padx=6, pady=(6, 2))

        self.btn_submit = ctk.CTkButton(btns, text="Responder", command=self._on_submit,
                                        state="disabled", width=160, fg_color="#00796B", hover_color="#26A69A")
        self.btn_submit.pack(side="left", padx=6, pady=6)

        self.btn_restart = ctk.CTkButton(btns, text="Volver a jugar", command=self._on_restart,
                                         state="disabled", width=160, fg_color="#8E24AA", hover_color="#AB47BC")
        self.btn_restart.pack(side="right", padx=6, pady=6)

        self.lbl_remaining = ctk.CTkLabel(right, text="Preguntas restantes: 0", text_color="#455A64")
        self.lbl_remaining.pack(padx=10, pady=(0, 8), anchor="e")

    def _build_tab_rank(self, parent):
        wrapper = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=12)
        wrapper.pack(fill="both", expand=True, padx=10, pady=10)

        cols = ("name", "score", "answered")
        self.rank_tree = ttk.Treeview(wrapper, columns=cols, show="headings", height=20)
        self.rank_tree.heading("name", text="Jugador")
        self.rank_tree.heading("score", text="Aciertos")
        self.rank_tree.heading("answered", text="Respondidas")
        self.rank_tree.column("name", width=300, anchor="w")
        self.rank_tree.column("score", width=120, anchor="center")
        self.rank_tree.column("answered", width=140, anchor="center")
        self.rank_tree.pack(fill="both", expand=True, padx=8, pady=8)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF", foreground=TEXT_DARK, rowheight=26)
        style.configure("Treeview.Heading", background=BG_CYAN, foreground=TEXT_DARK, font=("Arial", 11, "bold"))

        btn_refresh = ctk.CTkButton(wrapper, text="Refrescar ranking", command=self._refresh_ranking,
                                    fg_color="#0288D1", hover_color="#03A9F4", width=180)
        btn_refresh.pack(pady=6)

    # ---------------- RULETA ----------------
    def _draw_roulette(self):
        self.canvas.delete("all")
        angle_per = 360 / len(CATEGORIES)
        start_angle = self._angle % 360
        bbox = (30, 30, 330, 330)
        for cat in CATEGORIES:
            color = CATEGORY_COLORS[cat]
            self.canvas.create_arc(*bbox, start=start_angle, extent=angle_per, fill=color, outline=BG_CYAN, width=2)
            mid = math.radians(start_angle + angle_per/2)
            cx, cy = 180, 180
            x = cx + 95 * math.cos(mid)
            y = cy - 95 * math.sin(mid)
            self.canvas.create_text(x, y, text=CATEGORY_ICONS[cat], font=("Arial", 18))
            start_angle += angle_per
        # Indicador fijo
        self.canvas.create_polygon(175, 12, 185, 12, 180, 28, fill=TEXT_DARK, outline="")

    def _spin_step(self):
        if not self._spinning:
            return
        # Ease-out: multiplicamos por fricción
        self._angle = (self._angle + self._spin_velocity) % 360
        self._spin_velocity *= self._spin_friction
        self._draw_roulette()

        if self._spin_velocity < 0.6:  # umbral de parada
            self._spinning = False
            self._on_spin_finished()
        else:
            self.after(12, self._spin_step)  # alta fluidez

    def _category_at_indicator(self):
        angle_per = 360 / len(CATEGORIES)
        effective = (90 - self._angle) % 360
        index = int(effective // angle_per) % len(CATEGORIES)
        return CATEGORIES[index]

    def _on_spin(self):
        if not self.player:
            messagebox.showwarning("Atención", "Primero registrá un jugador.")
            return
        if self.questions_remaining <= 0:
            messagebox.showinfo("Fin", "Ya respondiste las 10 preguntas.")
            return
        if self._spinning or self.current_question is not None:
            return

        self.btn_spin.configure(state="disabled")
        self.btn_submit.configure(state="disabled")
        # Velocidad inicial aleatoria (más grande => más vueltas)
        self._spin_velocity = random.uniform(12.0, 18.0)
        self._spinning = True
        self._spin_step()

    def _on_spin_finished(self):
        cat = self._category_at_indicator()
        self.current_category = cat
        self.lbl_category.configure(text=f"Categoría: {CATEGORY_ICONS[cat]} {cat}", text_color=TEXT_DARK)
        self._show_question(cat)
        self._start_timer()

    # ---------------- REGISTRO / JUEGO ----------------
    def _on_register(self):
        if self.player is not None:
            return
        name = self.ent_name.get().strip()
        if not name:
            messagebox.showwarning("Atención", "Ingresá un nombre.")
            return
        try:
            self.player = self.engine.create_player(name)
        except ValueError as e:
            messagebox.showerror("Error", str(e))
            return

        self.questions_remaining = 10
        self.lbl_remaining.configure(text=f"Preguntas restantes: {self.questions_remaining}")
        self.lbl_status.configure(text=f"Jugador: {name} ✅", text_color="#2E7D32")
        self.ent_name.configure(state="disabled")
        self.btn_register.configure(state="disabled")
        self.btn_spin.configure(state="normal")
        self.btn_restart.configure(state="disabled")
        messagebox.showinfo("Listo", f"Jugador '{name}' registrado. ¡A jugar!")

    def _show_question(self, category):
        q = self.engine._draw_question(category)
        self.current_question = q
        # Imagen
        self._set_image(q.image_url)
        # Enunciado
        self.lbl_prompt.configure(text=q.prompt)
        # Opciones (según tipo)
        if q.tipo == "vf":
            options = ["Verdadero", "Falso"]
        else:
            options = q.options
        for i, btn in enumerate(self.option_buttons):
            if i < len(options):
                btn.configure(text=options[i])
                btn.configure(state="normal")
                btn.pack(anchor="w", padx=16, pady=4)
            else:
                btn.configure(text="")
                btn.configure(state="disabled")
                btn.pack_forget()
        self.option_var.set(-1)
        # Controles
        self.btn_submit.configure(state="normal")

    def _on_submit(self):
        if self.current_question is None or self.player is None:
            return
        choice = self.option_var.get()
        if choice == -1:
            messagebox.showwarning("Atención", "Seleccioná una opción.")
            return

        self._stop_timer()
        correct = self.engine.record_answer(self.player, self.current_question, choice)
        self._after_answer(correct)

    def _after_answer(self, correct: bool):
        """Muestra el resultado usando los widgets ya creados (sin usar content_frame)."""
        # Deshabilitamos opciones y el botón de enviar
        for btn in self.option_buttons:
            btn.configure(state="disabled")
        self.btn_submit.configure(state="disabled")

        # Mensajes y feedback visual
        emoji = "✅" if correct else "❌"
        msg = "¡Respuesta correcta!" if correct else "Respuesta incorrecta"
        sub = "Sumás un punto 😎" if correct else "La próxima te sale 😉"

        # Mostramos feedback en la imagen y el enunciado
        self.img_label.configure(image=None, text=emoji)
        self.lbl_prompt.configure(text=f"{msg}\n\n{sub}")

        # Actualizamos contadores y estado de botones
        self.questions_remaining = max(0, self.questions_remaining - 1)
        self.lbl_remaining.configure(text=f"Preguntas restantes: {self.questions_remaining}")

        # Si ya no quedan preguntas, activamos botón de reinicio
        if self.questions_remaining <= 0:
            self.btn_spin.configure(state="disabled")
            self.btn_restart.configure(state="normal")
        else:
            # permitir girar para la siguiente pregunta
            self.btn_spin.configure(state="normal")

        # Reseteamos la pregunta actual y actualizamos ranking por si cambió el puntaje
        self.current_question = None
        try:
            self._refresh_ranking()
        except Exception:
            pass



    def _on_restart(self):
        self._stop_timer()
        self.player = None
        self.current_question = None
        self.questions_remaining = 0
        self.current_category = None
        self._angle = 0.0
        self._spinning = False
        self._spin_velocity = 0.0
        self.ent_name.configure(state="normal")
        self.ent_name.delete(0, tk.END)
        self.btn_register.configure(state="normal")
        self.btn_spin.configure(state="disabled")
        self.btn_submit.configure(state="disabled")
        self.btn_restart.configure(state="disabled")
        self.lbl_status.configure(text="Sin jugador", text_color="#546E7A")
        self.lbl_prompt.configure(text="Registrate y girá la ruleta para comenzar.")
        self.lbl_category.configure(text="Categoría: —", text_color=TEXT_DARK)
        self.lbl_remaining.configure(text="Preguntas restantes: 0")
        self.lbl_timer.configure(text="⏳ Tiempo: —")
        self.option_var.set(-1)
        self._draw_roulette()
        messagebox.showinfo("Nuevo juego", "Podés registrar un nuevo jugador.")

    # ---------------- TIMER ----------------
    def _start_timer(self):
        self._stop_timer()
        self._time_left = TIMER_SECONDS
        self._tick()

    def _tick(self):
        self.lbl_timer.configure(text=f"⏳ Tiempo: {self._time_left}s")
        if self._time_left <= 0:
            # timeout -> incorrecto
            self._stop_timer()
            messagebox.showwarning("Tiempo", "⏰ Se acabó el tiempo.")
            # Forzamos incorrecta con choice inválido
            self.engine.record_answer(self.player, self.current_question, -1)
            self._after_answer(False)
            return
        self._time_left -= 1
        self._timer_id = self.after(1000, self._tick)

    def _stop_timer(self):
        if self._timer_id is not None:
            try:
                self.after_cancel(self._timer_id)
            except Exception:
                pass
            self._timer_id = None

    # ---------------- IMÁGENES ----------------
    def _set_image(self, url: str | None):
        if not url:
            self.img_label.configure(image=None, text="")
            return
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            img = Image.open(io.BytesIO(resp.content)).convert("RGB")
            # Redimensionar manteniendo aspecto
            max_w, max_h = 520, 220
            img.thumbnail((max_w, max_h), Image.LANCZOS)
            self._photo = ImageTk.PhotoImage(img)
            self.img_label.configure(image=self._photo, text="")
        except Exception:
            # Si falla, no rompe la UI
            self.img_label.configure(image=None, text="(No se pudo cargar la imagen)")

    # ---------------- RANKING ----------------
    def _refresh_ranking(self):
        for i in self.rank_tree.get_children():
            self.rank_tree.delete(i)
        for row in self.engine.get_ranking():
            self.rank_tree.insert("", "end", values=(row["name"], row["score"], row["answered"]))

if __name__ == "__main__":
    app = TriviaGUI()
    app.mainloop()
