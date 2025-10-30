<<<<<<< HEAD
# preguntados-python
=======
# Trivia Estilo Preguntados (Python / Tkinter)

## Requisitos
- Python 3.10+
- Paquetes:
  - `matplotlib` (para el gráfico del ranking)
  
Instalación rápida:
```bash
pip install matplotlib
```

> Tkinter suele venir con las distribuciones oficiales de Python. Si usás Linux y no lo tenés, instalá el paquete correspondiente a tu distro (ej. `sudo apt install python3-tk`).

## Estructura
```
trivia_preguntados/
├─ main.py                  # punto de entrada
├─ gui.py                   # interfaz gráfica (Tkinter + Matplotlib)
├─ game_trivia.py           # motor del juego
├─ models/
│  ├─ base.py               # clase abstracta
│  ├─ player.py             # clase principal que hereda de abstracta
│  └─ player_tree.py        # BST con CRUD completo de Player
├─ data/
│  ├─ questions.json        # banco de preguntas por categoría
│  └─ scoreboard.json       # se genera automáticamente
└─ README.md
```

## Cómo ejecutar
Desde la carpeta `trivia_preguntados`:
```bash
python main.py --gui
```

## Características destacadas (para el TP)
- **Clases**: `AbstractPlayer` (abstracta) y `Player` (principal, hereda). `Player` tiene 5+ atributos, incluyendo `__uid` encapsulado.
- **Estructura de datos (árboles)**: `PlayerBST` (ABB) con **CRUD completo** (create/read/update/delete) por nombre.
- **Módulos utilizados**: `collections.deque`, `queue.Queue`, `json`, `re`, y `matplotlib`.
- **Interfaz**: `Tkinter` separada en `gui.py`. Motor del juego en `game_trivia.py`. `main.py` como entrypoint.
- **Persistencia**: Ranking en `data/scoreboard.json`. Se muestra en tabla + gráfico de barras.
- **Validación**: Los nombres se validan con regex y no pueden repetirse.

## Notas de uso
- Cada partida consta de **10 preguntas** con categorías decididas al azar (ruleta).
- El ranking se ordena por aciertos (desc) y nombre (asc).

## Extensiones posibles
- Agregar más preguntas a `data/questions.json`.
- Exportar ranking a CSV (con `pandas` si querés sumar otro módulo).
- Añadir temporizador por pregunta o sonidos.
>>>>>>> 67882d6 (Primer commit - Juego Preguntados)
