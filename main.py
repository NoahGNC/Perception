import pygame
from script.classes import *

#ok 

def init() :
    """Cette procédure est celle qui sera appelée en premier, elle va initialiser certaines variables globales
    et lancer le processus de pygame"""
    global clock, perso, screen, font, map
    pygame.init()

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18) 

    pygame.display.set_caption("Pyracode")
    screen = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
    w, h = pygame.display.get_surface().get_size()

    perso = Transform("sprites/perso.png", position=Vector2(w/2, h/2), taille=Vector2(64, 84))
    map = Map("data/map0.json", 64)
    print(map.liste_col[0].position)
    process()

def process() :
    """Cette procédure est ce qu'on appelle la boucle de jeu, c'est elle qui va éxécuter les fonctionalités du jeu
    tant que la variable running vaut True"""
    global clavier, clock

    clavier = {} 
    running = True    
    while running :

        update()

        clock.tick(60)

        for event in pygame.event.get() : 
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN :
                clavier[event.key] = True 
            elif event.type == pygame.KEYUP :
                clavier[event.key] = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE :
                running = False
                
    pygame.quit()


def update() :
    screen.fill((0, 0, 0))
    mouvement = Vector2(clavier.get(pygame.K_q, 0) + clavier.get(pygame.K_d, 0) * - 1, clavier.get(pygame.K_z, 0) + clavier.get(pygame.K_s, 0) * - 1).normalized()
    
    #Met a jour la pos de la map
    map.bouge_tout(mouvement)
    
    #Dessine carte et perso
    perso.draw(screen)
    map.draw(screen)

    # Détection collision
    map.collision(perso.get_centre())
    sens_collision = Vector2(0, 0)
    for col in map.real_col :
        actuel = perso.detecte_collision(col)
        sens_collision.x = actuel.x if actuel.x != 0 else sens_collision.x
        sens_collision.y = actuel.y if actuel.y != 0 else sens_collision.y
    map.bouge_tout(mouvement * sens_collision)
    
    
    #Calcul pos perso dans matrice 
    pos_perso = map.pos_matrice(perso.get_centre())
    posi_mat=font.render(f'({pos_perso[0]}, {pos_perso[1]})', 1, pygame.Color("aqua"))
    screen.blit(posi_mat,(10,20))
    
    
    screen.blit(update_fps(), (10,0)) 

    pygame.display.flip()

def update_fps():
    """Renvoie un compteur de fps de type surface que l'on peut afficher avec blit"""
    global clock
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, 1, pygame.Color("aqua"))
    return fps_text    

init()

