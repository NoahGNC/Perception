import pygame
from script.classes import *

def init():
    """Cette procédure est celle qui sera appelée en premier, elle va initialiser certaines variables globales
    et lancer le processus de pygame"""
    global clock, perso, screen, font, map, top_view, is_jumping, gravity_active
    pygame.init()

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)

    pygame.display.set_caption("Pyracode")
    screen = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
    w, h = pygame.display.get_surface().get_size()

    perso = Transform("sprites/perso.png", position=Vector2(w/2, h/2), taille=Vector2(64, 84))
    map = Map("data/map0.json", 64)

    perso.gravity = 0.5
    perso.speed_y = 0  
    is_jumping = False
    top_view = True
    gravity_active = False  

    print(map.liste_col[0].position)
    process()

def process():
    global clavier, clock, top_view, is_jumping, gravity_active
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

                if event.key == pygame.K_v:
                    top_view = not top_view
                    gravity_active = not gravity_active  
                
                if event.key == pygame.K_SPACE and not top_view and not is_jumping:
                    perso.speed_y = -10
                    is_jumping = True

            elif event.type == pygame.KEYUP:
                clavier[event.key] = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

    pygame.quit()

def update():
    global is_jumping
    screen.fill((0, 0, 0))

    if top_view:
        mouvement = Vector2(clavier.get(pygame.K_q, 0) + clavier.get(pygame.K_d, 0) * -1, clavier.get(pygame.K_z, 0) + clavier.get(pygame.K_s, 0) * -1).normalized()
        
        map.bouge_tout(mouvement)
        map.collision(perso.get_centre())
        
        sens_collision = Vector2(0, 0)
        for col in map.real_col:
            actuel = perso.detecte_collision(col)
            sens_collision.x = actuel.x if actuel.x != 0 else sens_collision.x
            sens_collision.y = actuel.y if actuel.y != 0 else sens_collision.y
        
        map.bouge_tout(mouvement * sens_collision)

    else:
        if is_jumping:
            perso.position.y += perso.speed_y
            perso.speed_y += perso.gravity  
        
       
        if gravity_active:
            perso.position.y += perso.speed_y
            perso.speed_y += perso.gravity  
        else:
            
            perso.speed_y = 0  

        mouvement = Vector2(clavier.get(pygame.K_q, 0) + clavier.get(pygame.K_d, 0) * -1, 0)

        map.bouge_tout(mouvement)
        map.collision(perso.get_centre())
        
        sens_collision = Vector2(0, 0)
        for col in map.real_col:
            actuel = perso.detecte_collision(col)
            sens_collision.x = actuel.x if actuel.x != 0 else sens_collision.x
            sens_collision.y = actuel.y if actuel.y != 0 else sens_collision.y

        if sens_collision.x != 0:
            perso.position.x -= mouvement.x 
            
        if sens_collision.y != 0:
            perso.speed_y = 0
            is_jumping = False
            if sens_collision.y < 0:
                perso.position.y = col.position.y - perso.taille.y  # sol
            elif sens_collision.y > 0:
                perso.position.y = col.position.y + col.taille.y  # plafond

      

    perso.draw(screen)
    map.draw(screen)

    pos_perso = map.pos_matrice(perso.get_centre())
    posi_mat = font.render(f'({pos_perso[0]}, {pos_perso[1]})', 1, pygame.Color("aqua"))
    screen.blit(posi_mat, (10, 20))

    screen.blit(update_fps(), (10, 0))
    pygame.display.flip()

def update_fps():
    """Renvoie un compteur de fps de type surface que l'on peut afficher avec blit"""
    global clock
    fps = str(int(clock.get_fps()))
    fps_text = font.render(fps, 1, pygame.Color("aqua"))
    return fps_text    

init()
