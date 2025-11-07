import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, ttk, simpledialog
import math, random, io, requests
from PIL import Image, ImageTk

from game_trivia import GameEngine, CATEGORIES

# ===================== CONFIG VISUAL =====================
ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

BG_CYAN = "#B2EBF2"
PANEL = "#E0F7FA"
TEXT_DARK = "#263238"

CATEGORY_COLORS = {
    "Historia": "#E57373",
    "Ciencia": "#64B5F6",
    "Geografía": "#81C784",
    "Deporte": "#FFF176",
}
CATEGORY_ICONS = {
    "Historia": "🏛️",
    "Ciencia": "🧠",
    "Geografía": "🗺️",
    "Deporte": "⚽",
}
TIMER_SECONDS = 15


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

        # UI
        self._build_ui()
        self._refresh_ranking()

        # Pantalla completa
        self.state('zoomed')
        self.bind("<F11>", self.toggle_fullscreen)
        self.bind("<Escape>", self.exit_fullscreen)

    # ---------------- Pantalla completa ----------------
    def toggle_fullscreen(self, event=None):
        self.attributes("-fullscreen", not self.attributes("-fullscreen"))

    def exit_fullscreen(self, event=None):
        self.attributes("-fullscreen", False)
        self.state('zoomed')

    # ===================== UI ROOT =====================
    def _build_ui(self):
        title = ctk.CTkLabel(self, text="🎯 TRIVIA PREGUNTADOS — V3",
                             font=("Arial Black", 28), text_color=TEXT_DARK)
        title.pack(pady=10)

        self.tabs = ctk.CTkTabview(self, width=930, height=600)
        self.tabs.pack(pady=5)

        self.tab_game = self.tabs.add("Jugar")
        self.tab_rank = self.tabs.add("Clasificación")
        self.tab_manage = self.tabs.add("Gestión de jugadores")

        self._build_tab_game(self.tab_game)
        self._build_tab_rank(self.tab_rank)
        self._build_tab_manage(self.tab_manage)

    # ===================== TAB: JUGAR =====================
    def _build_tab_game(self, parent):
        container = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=14)
        container.pack(fill="both", expand=True, padx=10, pady=10)

        # Izquierda: ruleta
        left = ctk.CTkFrame(container, fg_color=PANEL)
        left.pack(side="left", fill="y", padx=10, pady=10)

        self.canvas = tk.Canvas(left, width=360, height=360, bg=PANEL, highlightthickness=0)
        self.canvas.pack(pady=(10, 0))
        self._draw_roulette()

        self.btn_spin = ctk.CTkButton(
            left, text="🎡 Girar ruleta", width=220, height=40,
            command=self._on_spin, state="disabled",
            fg_color="#0288D1", hover_color="#03A9F4"
        )
        self.btn_spin.pack(pady=10)

        self.lbl_category = ctk.CTkLabel(left, text="Categoría: —",
                                         font=("Arial", 18, "bold"),
                                         text_color=TEXT_DARK)
        self.lbl_category.pack(pady=4)

        # Derecha: registro + pregunta
        right = ctk.CTkFrame(container, fg_color=PANEL)
        right.pack(side="left", fill="both", expand=True, padx=10, pady=10)

        # Registro
        reg = ctk.CTkFrame(right, fg_color="#FFFFFF", corner_radius=12)
        reg.pack(fill="x", padx=6, pady=(6, 10))
        ctk.CTkLabel(reg, text="Nombre del jugador:", text_color=TEXT_DARK)\
            .grid(row=0, column=0, padx=10, pady=10)
        self.ent_name = ctk.CTkEntry(reg, width=220)
        self.ent_name.grid(row=0, column=1, padx=6, pady=10)
        self.btn_register = ctk.CTkButton(
            reg, text="Registrar", command=self._on_register, width=120,
            fg_color="#388E3C", hover_color="#43A047"
        )
        self.btn_register.grid(row=0, column=2, padx=10, pady=10)
        self.lbl_status = ctk.CTkLabel(reg, text="Sin jugador", text_color="#546E7A")
        self.lbl_status.grid(row=0, column=3, padx=10, pady=10)

        # Pregunta + imagen + opciones
        qbox = ctk.CTkFrame(right, fg_color="#FFFFFF", corner_radius=12)
        qbox.pack(fill="both", expand=True, padx=6, pady=6)

        self.img_label = ctk.CTkLabel(qbox, text="")
        self.img_label.pack(pady=(12, 4))

        self.lbl_timer = ctk.CTkLabel(qbox, text="⏳ Tiempo: —",
                                      text_color="#D84315", font=("Arial", 14, "bold"))
        self.lbl_timer.pack(pady=(0, 4))

        self.lbl_prompt = ctk.CTkLabel(
            qbox, text="Registrate y girá la ruleta para comenzar.",
            wraplength=520, justify="left", font=("Arial", 16), text_color=TEXT_DARK
        )
        self.lbl_prompt.pack(padx=14, pady=(4, 6), anchor="w")

        self.option_var = tk.IntVar(value=-1)
        self.option_buttons = []
        for i in range(4):
            rb = ctk.CTkRadioButton(
                qbox, text=f"Opción {i+1}", variable=self.option_var, value=i,
                text_color=TEXT_DARK, fg_color="#03A9F4",
                hover_color="#4FC3F7", border_color="#0288D1"
            )
            rb.pack(anchor="w", padx=16, pady=4)
            self.option_buttons.append(rb)

        # Botones inferiores
        btns = ctk.CTkFrame(right, fg_color=PANEL)
        btns.pack(fill="x", padx=6, pady=(6, 2))

        self.btn_submit = ctk.CTkButton(
            btns, text="Responder", command=self._on_submit,
            state="disabled", width=160, fg_color="#00796B", hover_color="#26A69A"
        )
        self.btn_submit.pack(side="left", padx=6, pady=6)

        self.btn_restart = ctk.CTkButton(
            btns, text="Volver a jugar", command=self._on_restart,
            state="disabled", width=160, fg_color="#8E24AA", hover_color="#AB47BC"
        )
        self.btn_restart.pack(side="right", padx=6, pady=6)

        self.lbl_remaining = ctk.CTkLabel(right, text="Preguntas restantes: 0",
                                          text_color="#455A64")
        self.lbl_remaining.pack(padx=10, pady=(0, 8), anchor="e")

    # ===================== TAB: CLASIFICACIÓN =====================
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
        style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF",
                        foreground=TEXT_DARK, rowheight=26)
        style.configure("Treeview.Heading", background=BG_CYAN,
                        foreground=TEXT_DARK, font=("Arial", 11, "bold"))

        btn_refresh = ctk.CTkButton(wrapper, text="Refrescar ranking",
                                    command=self._refresh_ranking,
                                    fg_color="#0288D1", hover_color="#03A9F4", width=180)
        btn_refresh.pack(pady=6)

    # ===================== TAB: GESTIÓN JUGADORES (CRUD) =====================
    def _build_tab_manage(self, parent):
        wrapper = ctk.CTkFrame(parent, fg_color=PANEL, corner_radius=12)
        wrapper.pack(fill="both", expand=True, padx=10, pady=10)

        lbl_title = ctk.CTkLabel(wrapper, text="⚙️ Gestión de Jugadores",
                                 font=("Arial Rounded MT Bold", 24))
        lbl_title.pack(pady=10)

        cols = ("name", "score", "answered")
        self.players_tree = ttk.Treeview(wrapper, columns=cols, show="headings", height=15)
        self.players_tree.heading("name", text="Jugador")
        self.players_tree.heading("score", text="Aciertos")
        self.players_tree.heading("answered", text="Respondidas")
        self.players_tree.column("name", width=280, anchor="w")
        self.players_tree.column("score", width=120, anchor="center")
        self.players_tree.column("answered", width=120, anchor="center")
        self.players_tree.pack(fill="both", expand=True, padx=8, pady=8)

        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass
        style.configure("Treeview", background="#FFFFFF", fieldbackground="#FFFFFF",
                        foreground=TEXT_DARK, rowheight=26)
        style.configure("Treeview.Heading", background=BG_CYAN,
                        foreground=TEXT_DARK, font=("Arial", 11, "bold"))

        btn_frame = ctk.CTkFrame(wrapper, fg_color=PANEL)
        btn_frame.pack(fill="x", pady=10)

        ctk.CTkButton(btn_frame, text="🔄 Actualizar lista",
                      command=self._refresh_players_list,
                      fg_color="#0288D1", hover_color="#03A9F4",
                      width=160).pack(side="left", padx=8)

        ctk.CTkButton(btn_frame, text="✏️ Modificar puntaje",
                      command=self._edit_selected_player,
                      fg_color="#1976D2", hover_color="#2196F3",
                      width=180).pack(side="left", padx=8)

        ctk.CTkButton(btn_frame, text="🗑️ Eliminar jugador",
                      command=self._delete_selected_player,
                      fg_color="#D32F2F", hover_color="#E53935",
                      width=180).pack(side="left", padx=8)

        self._refresh_players_list()

    # ===================== RULETA =====================
    def _draw_roulette(self):
        self.canvas.delete("all")
        angle_per = 360 / len(CATEGORIES)
        start_angle = self._angle % 360
        bbox = (30, 30, 330, 330)

        for cat in CATEGORIES:
            color = CATEGORY_COLORS[cat]
            self.canvas.create_arc(*bbox, start=start_angle, extent=angle_per,
                                   fill=color, outline=BG_CYAN, width=2)
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
        self._angle = (self._angle + self._spin_velocity) % 360
        self._spin_velocity *= self._spin_friction
        self._draw_roulette()

        if self._spin_velocity < 0.6:
            self._spinning = False
            self._on_spin_finished()
        else:
            self.after(12, self._spin_step)

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
        self._spin_velocity = random.uniform(12.0, 18.0)
        self._spinning = True
        self._spin_step()

    def _on_spin_finished(self):
        cat = self._category_at_indicator()
        self.current_category = cat
        self.lbl_category.configure(text=f"Categoría: {cat} {CATEGORY_ICONS[cat]}",
                                    text_color=TEXT_DARK)
        self._show_question(cat)
        self._start_timer()

    # ===================== REGISTRO/JUEGO =====================
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
        self.lbl_prompt.configure(text=q.prompt, text_color=TEXT_DARK)

        # Opciones
        options = ["Verdadero", "Falso"] if q.tipo == "vf" else q.options
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
        """Feedback y botón 'Siguiente pregunta' debajo de la ruleta."""
        # Deshabilitar opciones / enviar
        for btn in self.option_buttons:
            btn.configure(state="disabled")
        self.btn_submit.configure(state="disabled")

        # calcular texto “correcta” para VF/MC
        if self.current_question.tipo == "vf":
            correcta = "Verdadero" if bool(self.current_question.answer_index) else "Falso"
        else:
            correcta = self.current_question.options[self.current_question.answer_index]

        if correct:
            emoji = "✅"; msg = "¡Respuesta correcta!"; sub = "Sumás un punto 😎"; color = "green"
        else:
            emoji = "❌"; msg = "Respuesta incorrecta"; sub = f"La correcta era: {correcta}"; color = "red"

        # feedback en la zona de pregunta
        self.img_label.configure(image=None, text=emoji)
        self.lbl_prompt.configure(text=f"{msg}\n{sub}", text_color=color)

        # contador y controles
        self.questions_remaining = max(0, self.questions_remaining - 1)
        self.lbl_remaining.configure(text=f"Preguntas restantes: {self.questions_remaining}")
        self.btn_spin.configure(state="disabled")

        # botón siguiente (o terminar) debajo de la ruleta
        try:
            if hasattr(self, "btn_next"):
                self.btn_next.destroy()
            self.btn_next = ctk.CTkButton(
                master=self.btn_spin.master,
                text="➡️ Siguiente pregunta",
                font=("Arial Rounded MT Bold", 20),
                fg_color="#00b4d8",
                hover_color="#0096c7",
                width=self.btn_spin.cget("width"),
                height=self.btn_spin.cget("height"),
                command=self._on_next_question
            )
            self.btn_next.pack(pady=15)

            if self.questions_remaining <= 0:
                self.btn_next.configure(text="🏁 Terminar", command=self._restart_game)
        except Exception as e:
            print(f"[ERROR] No se pudo crear el botón 'Siguiente pregunta': {e}")

        # refresh ranking
        self.current_question = None
        try:
            self._refresh_ranking()
        except Exception:
            pass

    def _on_next_question(self):
        """Limpia feedback y hace girar la ruleta para la próxima categoría."""
        if hasattr(self, "btn_next"):
            self.btn_next.destroy()

        # limpiar visual
        self.lbl_prompt.configure(text="", text_color=TEXT_DARK)
        self.img_label.configure(text="")
        self.option_var.set(-1)
        for btn in self.option_buttons:
            btn.configure(state="disabled")

        if self.questions_remaining > 0 and not self._spinning:
            self.after(200, self._on_spin)
        else:
            self.btn_restart.configure(state="normal")

    def _restart_game(self):
        """Acción final cuando se terminan las 10 preguntas (desde el botón 'Terminar')."""
        self._on_restart()

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
        self.lbl_prompt.configure(text="Registrate y girá la ruleta para comenzar.",
                                  text_color=TEXT_DARK)
        self.lbl_category.configure(text="Categoría: —", text_color=TEXT_DARK)
        self.lbl_remaining.configure(text="Preguntas restantes: 0")
        self.lbl_timer.configure(text="⏳ Tiempo: —")
        self.option_var.set(-1)
        self._draw_roulette()
        messagebox.showinfo("Nuevo juego", "Podés registrar un nuevo jugador.")

    # ===================== TIMER =====================
    def _start_timer(self):
        self._stop_timer()
        self._time_left = TIMER_SECONDS
        self._tick()

    def _tick(self):
        self.lbl_timer.configure(text=f"⏳ Tiempo: {self._time_left}s")
        if self._time_left <= 0:
            self._stop_timer()
            messagebox.showwarning("Tiempo", "⏰ Se acabó el tiempo.")
            # choice inválido (-1) -> incorrecta
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

    # ===================== IMÁGENES =====================
    def _set_image(self, url: str | None):
        if not url:
            self.img_label.configure(image=None, text="")
            return
        try:
            resp = requests.get(url, timeout=5)
            resp.raise_for_status()
            img = Image.open(io.BytesIO(resp.content)).convert("RGB")
            max_w, max_h = 520, 220
            img.thumbnail((max_w, max_h), Image.LANCZOS)
            self._photo = ImageTk.PhotoImage(img)
            self.img_label.configure(image=self._photo, text="")
        except Exception:
            self.img_label.configure(image=None, text="(No se pudo cargar la imagen)")

    # ===================== RANKING =====================
    def _refresh_ranking(self):
        for i in self.rank_tree.get_children():
            self.rank_tree.delete(i)
        for row in self.engine.get_ranking():
            self.rank_tree.insert("", "end",
                                  values=(row["name"], row["score"], row["answered"]))

    # ===================== GESTIÓN JUGADORES (CRUD) =====================
    def _refresh_players_list(self):
        for i in self.players_tree.get_children():
            self.players_tree.delete(i)
        for row in self.engine.get_ranking():
            self.players_tree.insert("", "end",
                                     values=(row["name"], row["score"], row["answered"]))

    def _edit_selected_player(self):
        sel = self.players_tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná un jugador de la lista.")
            return
        name = self.players_tree.item(sel[0], "values")[0]
        new_score = simpledialog.askinteger("Modificar puntaje",
                                            f"Nuevo puntaje para '{name}':",
                                            minvalue=0)
        if new_score is None:
            return
        ok = self.engine.update_player_score(name, new_score)
        if ok:
            messagebox.showinfo("Actualizado", f"Puntaje de '{name}' actualizado.")
            self._refresh_players_list()
            self._refresh_ranking()
        else:
            messagebox.showerror("Error", f"No se pudo actualizar a '{name}'.")

    def _delete_selected_player(self):
        sel = self.players_tree.selection()
        if not sel:
            messagebox.showwarning("Atención", "Seleccioná un jugador de la lista.")
            return
        name = self.players_tree.item(sel[0], "values")[0]
        if not messagebox.askyesno("Confirmar eliminación", f"¿Eliminar definitivamente a '{name}'?"):
            return
        ok = self.engine.delete_player(name)
        if ok:
            # si está jugando el que eliminaste, reseteo UI
            if self.player and self.player.name.lower() == name.lower():
                self._on_restart()
            messagebox.showinfo("Eliminado", f"Jugador '{name}' eliminado.")
            self._refresh_players_list()
            self._refresh_ranking()
        else:
            messagebox.showerror("Error", f"No se pudo eliminar a '{name}'.")


if __name__ == "__main__":
    app = TriviaGUI()
    app.mainloop()
