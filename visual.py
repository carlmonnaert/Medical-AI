import structure as s

world = s.create_world()
while True:
    world.jour_suivant()
    population = world.nb_population()
    malades = world.nb_malades()
    morts = world.nb_morts()