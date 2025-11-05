<<<<<<< HEAD
# 🎯 Preguntados Python – Trivia Interactiva

Juego estilo **Preguntados**, desarrollado en **Python** con una interfaz moderna basada en **CustomTkinter**.

---
## 📂 Estructura del proyecto

preguntados-python/
├─ gui_moderno_v3.py # Interfaz moderna (CustomTkinter)
├─ game_trivia.py # Motor lógico del juego
├─ main.py # Punto de entrada opcional
├─ models/
│ ├─ base.py # Clase abstracta AbstractPlayer
│ ├─ player.py # Clase Player (hereda de AbstractPlayer)
│ └─ player_tree.py # Árbol binario (BST) con CRUD de jugadores
├─ data/
│ ├─ questions.json # Banco de preguntas
│ ├─ jugadores.json # Jugadores registrados
│ └─ scoreboard.json # Ranking persistente
└─ README.md

## 🚀 Características principales

✅ **Juego completo tipo Preguntados**  
- 4 categorías: Historia, Ciencia, Geografía y Deporte  
- Ruleta interactiva con colores distintivos por categoría  
- 15 preguntas por categoría (mezcladas aleatoriamente, sin repetir)  
- Algunas preguntas incluyen **verdadero/falso** e **imágenes ilustrativas**

✅ **Pantalla unificada y moderna**
- Interfaz creada con **CustomTkinter**  
- Todo ocurre en una misma ventana (registro, juego, resultados y ranking)  
- Modo **pantalla completa (F11)** y salida con **ESC**  
- Animaciones suaves y paneles coloridos de “Respuesta correcta / incorrecta”  

✅ **Sistema de jugadores y ranking**
- Registro único (no se permiten nombres repetidos)  
- Persistencia automática en `data/jugadores.json`  
- Ranking ordenado por aciertos (mayor a menor)  
- Visualización en tabla + gráfico de barras con **Matplotlib**

✅ **Arquitectura modular**
- Código dividido en módulos, siguiendo las buenas prácticas de POO.  
- Motor de juego separado de la interfaz.  
- Árbol binario (BST) con **CRUD completo** de jugadores.

---

## 🧠 Requisitos

- **Python 3.10+**
- Paquetes necesarios:
  ```bash
  pip install customtkinter matplotlib
