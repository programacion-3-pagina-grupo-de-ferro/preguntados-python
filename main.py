import sys

def main():
    # Si el usuario pasa el argumento --gui, abrir la interfaz moderna
    if "--gui" in sys.argv:
        import gui_moderno_v2 as gui
    else:
        print("Uso: python main.py --gui")

if __name__ == "__main__":
    main()
