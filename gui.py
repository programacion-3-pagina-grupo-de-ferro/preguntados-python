"""
Simple Tkinter GUI with Matplotlib ranking chart.
"""
import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional
import random

from game_trivia import GameEngine, CATEGORIES
from models.question import Question

# Matplotlib for ranking plot
# pip install matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DATA_DIR = "data"

class App(tk.Tk):
    """
    Tkinter application. Keeps GUI isolated from core logic.
    """
    def __init__(self):
        super().__init__()
        self.title("Trivia - Estilo Preguntados")
        self.resizable(False, False)
        self.engine = GameEngine(data_dir=DATA_DIR)
        self.player = None  # type: Optional[object]
        self.current_question = None  # type: Optional[Question]
        self.questions_remaining = 0
        self.answer_vars = []

        self._build_ui()

    # ----------------- UI -----------------
    def _build_ui(self):
        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=10, pady=10)

        # Tab: Registro/Juego
        self.tab_game = ttk.Frame(nb)
        nb.add(self.tab_game, text="Jugar")

        # Tab: Clasificación
        self.tab_rank = ttk.Frame(nb)
        nb.add(self.tab_rank, text="Clasificación")

        # Game tab content
        frm = ttk.LabelFrame(self.tab_game, text="Registro de jugador")
        frm.pack(fill="x", padx=8, pady=8)

        ttk.Label(frm, text="Nombre:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.ent_name = ttk.Entry(frm, width=30)
        self.ent_name.grid(row=0, column=1, padx=5, pady=5)

        self.btn_register = ttk.Button(frm, text="Registrar", command=self._on_register)
        self.btn_register.grid(row=0, column=2, padx=5, pady=5)

        # Roulette + Question area
        self.lbl_spin = ttk.Label(self.tab_game, text="Girá la ruleta para empezar.", font=("Segoe UI", 11, "bold"))
        self.lbl_spin.pack(pady=4)

        self.btn_spin = ttk.Button(self.tab_game, text="Girar ruleta", command=self._on_spin, state="disabled")
        self.btn_spin.pack(pady=6)

        self.lbl_category = ttk.Label(self.tab_game, text="Categoría: -", font=("Segoe UI", 10))
        self.lbl_category.pack(pady=2)

        # Question box
        qbox = ttk.LabelFrame(self.tab_game, text="Pregunta")
        qbox.pack(fill="both", padx=8, pady=8)

        self.lbl_prompt = ttk.Label(qbox, text="—", wraplength=380, justify="left")
        self.lbl_prompt.pack(padx=8, pady=8, anchor="w")

        self.answer_vars = []
        self.radio_var = tk.IntVar(value=-1)
        for i in range(4):
            rb = ttk.Radiobutton(qbox, text=f"Opción {i+1}", variable=self.radio_var, value=i)
            rb.pack(anchor="w", padx=12, pady=2)
            self.answer_vars.append(rb)

        self.btn_submit = ttk.Button(self.tab_game, text="Responder", state="disabled", command=self._on_submit)
        self.btn_submit.pack(pady=8)

        # Remaining
        self.lbl_remaining = ttk.Label(self.tab_game, text="Preguntas restantes: 0")
        self.lbl_remaining.pack(pady=2)

        # Ranking tab content
        self.tree = ttk.Treeview(self.tab_rank, columns=("score", "answered"), show="headings", height=10)
        self.tree.heading("score", text="Aciertos")
        self.tree.heading("answered", text="Respondidas")
        self.tree.column("score", width=100, anchor="center")
        self.tree.column("answered", width=120, anchor="center")
        self.tree.pack(side="left", padx=8, pady=8)

        self.tree_names = ttk.Treeview(self.tab_rank, columns=("name",), show="headings", height=10)
        self.tree_names.heading("name", text="Jugador")
        self.tree_names.column("name", width=160, anchor="w")
        self.tree_names.pack(side="left", padx=(8,0), pady=8)

        # Plot area
        plot_frame = ttk.Frame(self.tab_rank)
        plot_frame.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        self.fig = Figure(figsize=(4,3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self._refresh_ranking()

    # ----------------- Event Handlers -----------------
    def _on_register(self):
        name = self.ent_name.get().strip()
        if not name:
            messagebox.showwarning("Atención", "Ingresá un nombre.")
            return
        try:
            self.player = self.engine.create_player(name)
        except ValueError as e:
            messagebox.showerror("Nombre inválido", str(e))
            return

        messagebox.showinfo("Registro", f"Jugador '{name}' registrado.")
        self.btn_spin.config(state="normal")
        self.btn_submit.config(state="disabled")
        self.questions_remaining = 10
        self.lbl_remaining.config(text=f"Preguntas restantes: {self.questions_remaining}")
        self._refresh_ranking()

    def _on_spin(self):
        if not self.player:
            messagebox.showwarning("Atención", "Primero registrá un jugador.")
            return

        if self.questions_remaining <= 0:
            messagebox.showinfo("Ronda finalizada", "Ya respondiste las 10 preguntas.")
            return

        category = random.choice(CATEGORIES)
        self.lbl_category.config(text=f"Categoría: {category}")
        # draw a question
        q = self.engine._draw_question(category)
        self.current_question = q
        self.lbl_prompt.config(text=q.prompt)
        for i, opt in enumerate(q.options):
            self.answer_vars[i].config(text=opt)
        self.radio_var.set(-1)
        self.btn_submit.config(state="normal")

    def _on_submit(self):
        if self.current_question is None or self.player is None:
            return
        choice = self.radio_var.get()
        if choice == -1:
            messagebox.showwarning("Atención", "Elegí una opción.")
            return
        correct = self.engine.record_answer(self.player, self.current_question, choice)
        if correct:
            messagebox.showinfo("Resultado", "¡Correcto!")
        else:
            correct_opt = self.current_question.options[self.current_question.answer_index]
            messagebox.showinfo("Resultado", f"Incorrecto. Respuesta correcta: {correct_opt}")

        self.questions_remaining -= 1
        self.lbl_remaining.config(text=f"Preguntas restantes: {self.questions_remaining}")
        self.current_question = None
        self.btn_submit.config(state="disabled")

        if self.questions_remaining == 0:
            messagebox.showinfo("Fin", f"Ronda finalizada. Aciertos: {self.player.score}/10")
            self._refresh_ranking()

    # ----------------- Ranking -----------------
    def _refresh_ranking(self):
        for t in (self.tree, self.tree_names):
            for i in t.get_children():
                t.delete(i)

        ranking = self.engine.get_ranking()
        # Fill tables
        for row in ranking:
            self.tree_names.insert("", "end", values=(row["name"],))
            self.tree.insert("", "end", values=(row["score"], row["answered"]))

        # Plot top N
        self.ax.clear()
        if ranking:
            names = [r["name"] for r in ranking[:8]]
            scores = [r["score"] for r in ranking[:8]]
            self.ax.bar(names, scores)
            self.ax.set_title("Top aciertos")
            self.ax.set_ylabel("Aciertos")
            self.ax.set_xticklabels(names, rotation=30, ha="right")
        self.canvas.draw()


if __name__ == "__main__":
    app = App()
    app.mainloop()
