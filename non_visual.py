import structure as s
import time

world = s.create_world()

def updtate():
    world.jour_suivant()

while True:
    updtate()