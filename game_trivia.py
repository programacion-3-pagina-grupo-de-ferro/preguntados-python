import os, json, random, re
from collections import deque

DATA_DIR = "data"
CATEGORIES = ["Historia", "Ciencia", "Geografía", "Deporte"]

class Question:
    def __init__(self, category, qdict):
        self.category = category
        self.tipo = qdict.get("tipo", "mc")  # "mc" o "vf"
        self.prompt = qdict["texto"]
        self.options = qdict.get("opciones", ["Verdadero", "Falso"])  # por defecto para vf
        self.answer_index = qdict.get("respuesta", 0)
        self.image_url = qdict.get("imagen")

    def is_correct(self, choice):
        if self.tipo == "vf":
            # En JSON la respuesta es true/false; las opciones por defecto son [Verdadero, Falso]
            correct_bool = bool(self.answer_index)
            return (choice == 0 and correct_bool) or (choice == 1 and not correct_bool)
        return choice == self.answer_index

class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.total_answered = 0
        self.history = deque(maxlen=50)
        self.category_stats = {c: {"correct": 0, "total": 0} for c in CATEGORIES}

class GameEngine:
    def __init__(self, data_dir="data"):

        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.questions_path = os.path.join(self.data_dir, "preguntas.json")
        self.scoreboard_path = os.path.join(self.data_dir, "scoreboard.json")
        self.players_path = os.path.join(self.data_dir, "jugadores.json")

        self.players = {}  # name -> Player
        self.questions = {c: [] for c in CATEGORIES}

        self._load_questions()
        self._load_players()

    # ---------------- PERSISTENCIA ----------------
    def _load_questions(self):
        if not os.path.exists(self.questions_path):
            raise FileNotFoundError("Falta data/preguntas.json")
        with open(self.questions_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        for cat in CATEGORIES:
            self.questions[cat] = [Question(cat, qd) for qd in raw.get(cat, [])]

    def _load_players(self):
        # Carga jugadores previos (solo nombres)
        if os.path.exists(self.players_path):
            with open(self.players_path, "r", encoding="utf-8") as f:
                names = json.load(f)
            for n in names:
                self.players[n] = Player(n)
        # Carga scoreboard (si existe) para restaurar puntajes totales
        if os.path.exists(self.scoreboard_path):
            with open(self.scoreboard_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for row in data:
                n = row["name"]
                if n not in self.players:
                    self.players[n] = Player(n)
                p = self.players[n]
                p.score = row.get("score", 0)
                p.total_answered = row.get("answered", 0)

    def _save_players(self):
        names = sorted(self.players.keys())
        with open(self.players_path, "w", encoding="utf-8") as f:
            json.dump(names, f, ensure_ascii=False, indent=2)

    def _save_scoreboard(self):
        ranking = self.get_ranking()
        with open(self.scoreboard_path, "w", encoding="utf-8") as f:
            json.dump(ranking, f, ensure_ascii=False, indent=2)

    # ---------------- API JUEGO ----------------
    def create_player(self, name: str) -> Player:
        name = name.strip()
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚÑáéíóúñ0-9_ ]{3,30}", name):
            raise ValueError("Nombre inválido. Usá 3-30 caracteres alfanuméricos/espacios/_")
        if name in self.players:
            raise ValueError("Ese nombre ya existe. Elegí otro.")
        p = Player(name)
        self.players[name] = p
        self._save_players()
        self._save_scoreboard()
        return p

    def _draw_question(self, category: str) -> Question:
        pool = self.questions.get(category, [])
        if not pool:
            raise ValueError("No hay preguntas en esa categoría.")
        return random.choice(pool)

    def record_answer(self, player: Player, question: Question, choice: int) -> bool:
        correct = question.is_correct(choice)
        player.total_answered += 1
        player.category_stats[question.category]["total"] += 1
        if correct:
            player.score += 1
            player.category_stats[question.category]["correct"] += 1
        player.history.append({
            "category": question.category,
            "correct": correct,
            "prompt": question.prompt
        })
        self._save_scoreboard()
        return correct

    def get_ranking(self):
        rows = []
        for p in self.players.values():
            rows.append({
                "name": p.name,
                "score": p.score,
                "answered": p.total_answered
            })
        rows.sort(key=lambda r: (-r["score"], r["name"].lower()))
        return rows
