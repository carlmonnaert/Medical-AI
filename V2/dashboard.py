import tkinter as tk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
import numpy as np


def creer_graphique(frame_width, frame_height):
    x_data = np.linspace(0, 5, 100)  # 100 points entre 0 et 5
    y_data = np.cos(x_data)  # Fonction cosinus appliquée aux x

    fig, ax = plt.subplots(figsize=(frame_width / 100, frame_height / 100))  # Adapter la taille du graphique
    ax.plot(x_data, y_data, label="fonction cosinus", color='blue')
    ax.set_title("Courbe de la fonction cosinus")
    ax.set_xlabel("x")
    ax.set_ylabel("cos(x)")
    ax.legend()

    return fig

# Fonction pour afficher le graphique dans Tkinter
def afficher_graphique():
    frame_width = frame_graphique.winfo_width()
    frame_height = frame_graphique.winfo_height()

    fig = creer_graphique(frame_width, frame_height)

    for widget in frame_graphique.winfo_children():
        widget.destroy()

    canvas = FigureCanvasTkAgg(fig, master=frame_graphique)  # Attacher le graphique au frame
    canvas.draw()
    canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

# Création de la fenêtre principale
root = tk.Tk()
root.title("Affichage de la fonction Cosinus")
root.geometry("600x400")

# Frame pour la partie gauche (navigation)
frame_left = tk.Frame(root, width=150, bg="lightgray", height=400)
frame_left.grid(row=0, column=0, rowspan=2, sticky="nsew")

# Frame pour afficher le graphique
frame_graphique = tk.Frame(root, width=450, height=300)
frame_graphique.grid(row=0, column=1, sticky="nsew")

# Frame pour les informations
frame_info = tk.Frame(root, width=450, height=100)
frame_info.grid(row=1, column=1, sticky="nsew")

# Ajouter un bouton pour afficher la fonction cosinus
btn1 = tk.Button(frame_left, text="Afficher la fonction cosinus", command=afficher_graphique)
btn1.pack(pady=20, fill="x")

# bouton pour quitter l'application
btn_quit = tk.Button(frame_left, text="Quitter", command=root.quit)
btn_quit.pack(pady=20, fill="x")

# Démarrer l'interface
root.mainloop()
