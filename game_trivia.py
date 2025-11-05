import os, json, random, re
from collections import deque

DATA_DIR = "data"
CATEGORIES = ["Historia", "Ciencia", "Geografía", "Deporte"]

class Question:
    def __init__(self, category, qdict):
        self.category = category
        self.tipo = qdict.get("tipo", "mc")
        self.prompt = qdict["texto"]
        self.options = qdict.get("opciones", ["Verdadero", "Falso"])
        self.answer_index = qdict.get("respuesta", 0)
        self.image_url = qdict.get("imagen")

    def is_correct(self, choice):
        if self.tipo == "vf":
            if self.answer_index is True:
                return choice == 0
            else:
                return choice == 1
        return choice == self.answer_index


class Player:
    def __init__(self, name):
        self.name = name
        self.score = 0
        self.total_answered = 0
        self.category_stats = {c: {"correct": 0, "total": 0} for c in CATEGORIES}


class GameEngine:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        os.makedirs(self.data_dir, exist_ok=True)
        self.questions_path = os.path.join(self.data_dir, "preguntas.json")
        self.scoreboard_path = os.path.join(self.data_dir, "scoreboard.json")
        self.players_path = os.path.join(self.data_dir, "jugadores.json")

        self.players = {}
        self.questions = {c: [] for c in CATEGORIES}
        self._pending_questions = {c: deque() for c in CATEGORIES}

        self._load_questions()
        self._load_players()

    # ---------------- CARGA ----------------
    def _load_questions(self):
        if not os.path.exists(self.questions_path):
            raise FileNotFoundError("Falta data/preguntas.json")

        with open(self.questions_path, "r", encoding="utf-8") as f:
            raw = json.load(f)

        for cat in CATEGORIES:
            qlist = [Question(cat, qd) for qd in raw.get(cat, [])]
            self.questions[cat] = qlist
            # Preparamos la cola inicial sin repetir
            self._pending_questions[cat] = deque(random.sample(qlist, len(qlist)))

    def _load_players(self):
        self.players = {}

        # Cargamos los nombres
        if os.path.exists(self.players_path):
            try:
                with open(self.players_path, "r", encoding="utf-8") as f:
                    names = json.load(f)
                for n in names:
                    self.players[n] = Player(n)
            except json.JSONDecodeError:
                self.players = {}

    # Cargamos los puntajes del scoreboard
    if os.path.exists(self.scoreboard_path):
        try:
            with open(self.scoreboard_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            for row in data:
                name = row["name"]
                if name not in self.players:
                    self.players[name] = Player(name)
                p = self.players[name]
                p.score = row.get("score", 0)
                p.total_answered = row.get("answered", 0)
        except json.JSONDecodeError:
            pass


    # ---------------- GUARDADO ----------------
    def _save_players(self):
        names = sorted(self.players.keys())
        with open(self.players_path, "w", encoding="utf-8") as f:
            json.dump(names, f, ensure_ascii=False, indent=2)

    def _save_scoreboard(self):
        try:
            # Creamos el ranking a partir de los jugadores activos
            ranking = []
            for name, player in self.players.items():
                if isinstance(player, Player):
                    ranking.append({
                        "name": name,
                        "score": player.score,
                        "answered": player.total_answered
                    })

            # Si no hay jugadores válidos, no hacemos nada
            if not ranking:
                print("[DEBUG] No hay jugadores válidos para guardar en scoreboard.")
                return

            # Ordenar por puntaje descendente
            ranking.sort(key=lambda x: (-x["score"], x["name"].lower()))

            # Guardar en el archivo
            with open(self.scoreboard_path, "w", encoding="utf-8") as f:
                json.dump(ranking, f, ensure_ascii=False, indent=2)

            print(f"[DEBUG] Scoreboard actualizado: {len(ranking)} jugadores guardados.")

        except Exception as e:
            print(f"[ERROR] No se pudo guardar el scoreboard: {e}")


    # ---------------- CRUD ----------------
    def create_player(self, name: str) -> Player:
        name = name.strip()
        if not re.fullmatch(r"[A-Za-zÁÉÍÓÚÑáéíóúñ0-9_ ]{3,30}", name):
            raise ValueError("Nombre inválido. Usá 3-30 caracteres alfanuméricos o espacios/_")
        if name in self.players:
            raise ValueError("Ese nombre ya existe. Elegí otro.")
        p = Player(name)
        self.players[name] = p
        self._save_players()
        self._save_scoreboard()
        return p

    # ---------------- JUEGO ----------------
    def _draw_question(self, category: str) -> Question:
        # Rotación de preguntas sin repetir
        queue = self._pending_questions.get(category)
        if not queue:
            # Se acabaron -> se remezclan
            pool = self.questions.get(category, [])
            if not pool:
                raise ValueError("No hay preguntas en esta categoría.")
            queue = deque(random.sample(pool, len(pool)))
            self._pending_questions[category] = queue

        q = queue.popleft()
        return q

    def record_answer(self, player: Player, question: Question, choice: int) -> bool:
        correct = question.is_correct(choice)
        player.total_answered += 1
        player.category_stats[question.category]["total"] += 1

        if correct:
            player.score += 1
            player.category_stats[question.category]["correct"] += 1

        # Sincronizamos jugador con self.players
        self.players[player.name] = player

        # 🔥 Guardamos inmediatamente en ambos JSON
        self._save_players()
        self._save_scoreboard()

        # Para debug visual (opcional)
        print(f"[DEBUG] Guardado: {player.name} | Score: {player.score} | Respondidas: {player.total_answered}")

        return correct



    def get_ranking(self):
        # Aseguramos que los jugadores estén actualizados
        ranking = []
        for name, player in self.players.items():
            if isinstance(player, Player):
                ranking.append({
                    "name": name,
                    "score": player.score,
                    "answered": player.total_answered
                })
        ranking.sort(key=lambda x: (-x["score"], x["name"].lower()))
        return ranking

