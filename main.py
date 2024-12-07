import pygame
from script.classes import *

def init():
    """Initialisation des variables globales et du processus principal Pygame."""
    global clock, perso, screen, font, map, top_view, is_touching_grass, gravity, projectiles, w, h
    pygame.init()

    # Configuration initial
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)
    pygame.display.set_caption("Pyracode")
    screen = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
    w, h = pygame.display.get_surface().get_size()

    # Initialisation des objet principal
    perso = Transform("sprites/perso.png", position=Vector2(w / 2, h / 2), taille=Vector2(64, 64))
    perso.centrer(Vector2(w / 2, h / 2))
    map = Map("data/map0.json", 64, 4)

    # Variables de gravités et états
    gravity = 0.5
    perso.speed_y = 1
    is_touching_grass = False
    top_view = True
    projectiles = []

    process()


def process():
    """Boucle principale du jeu."""
    global clavier, clock, top_view, is_touching_grass, map, projectiles, w, h
    clavier = {}
    running = True

    while running:
        update()
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                clavier[event.key] = True
                gere_keydown(event.key)  # Gère les touches pressées
            elif event.type == pygame.KEYUP:
                clavier[event.key] = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                create_projectile()

    pygame.quit()


def gere_keydown(key):
    """Gère les événements clavier."""
    global top_view, is_touching_grass, map, perso, w, h

    if key == pygame.K_v:
        if top_view:
            map.change_map(map.quel_bande(map.pos_matrice(perso.position)) + 1)
            perso.centrer(Vector2(w / 2, h / 2))
            find_ground()
            top_view = False
        elif not top_view and is_touching_grass:
            map.change_map(0)
            is_touching_grass = False
            perso.centrer(Vector2(w / 2, h / 2))
            top_view = True

    elif key == pygame.K_SPACE:
        if not top_view and is_touching_grass:
            perso.speed_y = -10
            is_touching_grass = False

    elif key == pygame.K_ESCAPE:
        pygame.quit()
        exit()


def create_projectile():
    """Crée un projectile à partir de la position actuelle du personnage."""
    M_posX, M_posY = pygame.mouse.get_pos()
    M_pos = Vector2(M_posX, M_posY)
    MP_Vect = Vector2.crea_vect(perso.get_centre(), M_pos).normalized()

    proj = Transform("sprites/projectile.png", taille=Vector2(15, 15), temps_apparition=180)
    proj.centrer(perso.get_centre())
    proj.direction = MP_Vect
    proj.speed_y = 0
    projectiles.append(proj)


def find_ground():
    """Positionne le personnage au sol s'il est en chute."""
    global is_touching_grass
    while not is_touching_grass:
        perso.position.y += 1
        map.collision(perso.get_centre())

        collide = False
        for col in map.real_col:
            actuel = perso.est_dedans(col, 1)
            collide = actuel if actuel else collide


        is_touching_grass = collide


def update():
    """Met à jour l'état du jeu à chaque frame."""
    global is_touching_grass
    screen.fill((0, 0, 0))  # noir

    if map.est_dans_matrice(perso.get_centre()) :
        if top_view:
            gere_top_view_movement()
        else:
            gere_side_view_movement()

        map.draw(screen)
        perso.draw(screen)

        update_projectiles()

    else :
        print("Game Over")

    display_info()
    pygame.display.flip()


def gere_top_view_movement():
    """Gère les mouvements du personnage en vue du dessus."""
    mouvement = Vector2(
        clavier.get(pygame.K_q, 0) + clavier.get(pygame.K_d, 0) * -1,
        clavier.get(pygame.K_z, 0) + clavier.get(pygame.K_s, 0) * -1
    ).normalized() * 10

    map.collision(perso.get_centre())


    collide = [False, False]
    for col in map.real_col:
        actuel = perso.est_dedans(col, mouvement * Vector2(-1, 0))
        collide[0] = actuel if actuel else collide[0]

        actuel = perso.est_dedans(col, mouvement * Vector2(0, -1))
        collide[1] = actuel if actuel else collide[1]

    if not collide[0] :
        map.bouge_tout(mouvement * Vector2(1, 0))

    if not collide[1] :
        map.bouge_tout(mouvement * Vector2(0, 1))


def gere_side_view_movement():
    """Gère les mouvements du personnage en vue de côté."""
    global is_touching_grass

    mouvement = Vector2(
        clavier.get(pygame.K_q, 0) + clavier.get(pygame.K_d, 0) * -1, 0
    ) * 10


    map.collision(perso.get_centre())

    if not is_touching_grass:
        perso.speed_y += gravity
    else:
        perso.speed_y = 1


    collide = [False, False]
    for col in map.real_col:
        actuel = perso.est_dedans(col, mouvement * Vector2(-1, 0))
        collide[0] = actuel if actuel else collide[0]

        actuel = perso.est_dedans(col, perso.speed_y)
        collide[1] = actuel if actuel else collide[1]

    is_touching_grass = collide[1]
    
    if not collide[0] :
        map.bouge_tout(mouvement)

    if not is_touching_grass :
         perso.position.y += perso.speed_y


def update_projectiles():
    """Gère les mouvements et la suppression des projectiles."""
    for projectile in projectiles[:]:
        if top_view:
            projectile.position += projectile.direction * 20
        else:
            projectile.speed_y += gravity
            projectile.position.x += projectile.direction.x * 20
            projectile.position.y += projectile.direction.y * 20 + projectile.speed_y

        if map.est_dans_matrice(projectile.get_centre()) :
            if map.est_dans_col(projectile.position) :
                projectiles.remove(projectile)
            
    
        for col in map.collisions_optionels[map.actual_map] :
            if col.actif and projectile.est_dedans(col) :
                projectiles.remove(projectile)
                break

        for levier in map.leviers[map.actual_map] :
            if projectile.est_dedans(levier) :
                try :
                    projectiles.remove(projectile)
                except :
                    pass
                if not levier.actif :                   
                    levier.charge_nouveau_sprite("sprites/levier1.png")
                    levier.actif = True
                else :
                    levier.charge_nouveau_sprite("sprites/levier0.png")
                    levier.actif = False
                
                for i in range(len(map.collisions_optionels[map.actual_map])) :
                    print(levier.actionnement)
                    if i in levier.actionnement :
                        col = map.collisions_optionels[map.actual_map][i]
                        col.actif = not col.actif



        if projectile.temps_apparition <= 0:
            projectiles.remove(projectile)
        else:
            projectile.draw(screen)


def display_info():
    """Affiche des informations à l'écran (FPS, position)."""
    pos_perso = map.pos_matrice(perso.get_centre())
    posi_mat = font.render(f'({pos_perso[0]}, {pos_perso[1]})', 1, pygame.Color("aqua"))
    screen.blit(posi_mat, (10, 20))
    screen.blit(update_fps(), (10, 0))


def update_fps():
    """Renvoie un compteur de FPS."""
    global clock
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, 1, pygame.Color("aqua"))
    return fps_text


init()
