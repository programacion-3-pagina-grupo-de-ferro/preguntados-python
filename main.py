"""
Entry point for console or GUI mode.
"""
import argparse

def main():
    parser = argparse.ArgumentParser(description="Trivia - Estilo Preguntados")
    parser.add_argument("--gui", action="store_true", help="Iniciar interfaz gráfica (Tkinter).")
    args = parser.parse_args()

    if args.gui:
        import gui  # lazy import to keep GUI separate
    else:
        # Simple console notice
        print("Ejecutá con GUI:")
        print("    python main.py --gui")

if __name__ == "__main__":
    main()
