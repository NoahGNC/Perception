#Noah
import pygame
from script.classes import *

def init():
    """Cette procédure est celle qui sera appelée en premier, elle va initialiser certaines variables globales
    et lancer le processus de pygame"""
    global clock, perso, screen, font, map, top_view, is_touching_grass, gravity , projectiles, w, h, is_touching_grass
    pygame.init() 

    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 18)

    pygame.display.set_caption("Pyracode")
    screen = pygame.display.set_mode((1280, 720), pygame.FULLSCREEN)
    w, h = pygame.display.get_surface().get_size()

    perso = Transform("sprites/perso.png", position=Vector2(w/2, h/2), taille=Vector2(64, 64))
    perso.centrer(Vector2(w / 2, h / 2))
    map = Map("data/map0.json", 64, 4)

    gravity = 0.5
    perso.speed_y = 0  
    is_touching_grass = False
    top_view = True
    projectiles=[]
    is_touching_grass = False


    process()

def process():
    global clavier, clock, top_view, is_touching_grass, map,projectiles,w,h
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
                    if top_view :
                        map.change_map(map.quel_bande(map.pos_matrice(perso.position))+1)
                        perso.centrer(Vector2(w / 2, h / 2))
                        find_ground()
                        top_view = False
                    elif not top_view and is_touching_grass :
                        map.change_map(0)
                        is_touching_grass = False
                        perso.centrer(Vector2(w / 2, h / 2))
                        top_view = True
                  
                    
                
                if event.key == pygame.K_SPACE :
                    if not top_view and is_touching_grass:
                        perso.speed_y = -10
                        is_touching_grass = False


            elif event.type == pygame.KEYUP:
                clavier[event.key] = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                M_posX,M_posY = pygame.mouse.get_pos() 
                M_pos=Vector2(M_posX,M_posY)
                MP_Vect=Vector2.crea_vect(perso.get_centre(),M_pos).normalized()
                
                Proj=Transform("sprites/projectile.png",taille=Vector2(25,25),temps_apparition=180)
                Proj.centrer(perso.get_centre())
                Proj.direction = MP_Vect
                Proj.speed_y = 0
                projectiles.append(Proj)


    pygame.quit()

def find_ground() :
    global is_touching_grass
    while not is_touching_grass :
        perso.position.y += 5
        map.collision(perso.get_centre())

        sens_collision = Vector2(0, 0)
        for col in map.real_col:
            actuel = perso.detecte_collision(col)
            sens_collision.x = actuel.x if actuel.x != 0 else sens_collision.x
            sens_collision.y = actuel.y if actuel.y != 0 else sens_collision.y
        is_touching_grass = sens_collision.y == -1

def update():
    global is_touching_grass
    screen.fill((0, 0, 0))
    print(map.est_dans_matrice(perso.position))
    if map.est_dans_matrice(perso.position) :
        if top_view:
            mouvement = Vector2(clavier.get(pygame.K_q, 0) + clavier.get(pygame.K_d, 0) * -1, clavier.get(pygame.K_z, 0) + clavier.get(pygame.K_s, 0) * -1).normalized() * 10
            
            map.bouge_tout(mouvement)
            map.collision(perso.get_centre())
            
            sens_collision = Vector2(0, 0)
            for col in map.real_col:
                actuel = perso.detecte_collision(col)
                sens_collision.x = actuel.x if actuel.x != 0 else sens_collision.x
                sens_collision.y = actuel.y if actuel.y != 0 else sens_collision.y
            
            map.bouge_tout(mouvement * sens_collision)

        else:
            if not is_touching_grass :
                perso.speed_y += gravity
            else :
                perso.speed_y = 0.1 

            perso.position.y += perso.speed_y
            
            
            mouvement = Vector2(clavier.get(pygame.K_q, 0) + clavier.get(pygame.K_d, 0) * -1, 0) * 10

            map.bouge_tout(mouvement)
            map.collision(perso.get_centre()) # Actualise les colllisions autour

            sens_collision = Vector2(0, 0)
            for col in map.real_col:
                actuel = perso.detecte_collision(col)
                sens_collision.x = actuel.x if actuel.x != 0 else sens_collision.x
                sens_collision.y = actuel.y if actuel.y != 0 else sens_collision.y

            is_touching_grass = sens_collision.y == -1 # Là si le joueur à une contrainte -1 sur y c que il touche le sol

            perso.position.y += perso.speed_y *  sens_collision.y 


            map.bouge_tout(Vector2(mouvement.x * sens_collision.x, 0)) 


        
        map.draw(screen)
        perso.draw(screen)

        for projectile in projectiles[:]:
            if top_view:
                projectile.position += projectile.direction * 20  
            else:
                projectile.speed_y += gravity
                projectile.position.x += projectile.direction.x * 20
                
                projectile.position.y += projectile.direction.y * 20 + projectile.speed_y
            
            
            if projectile.temps_apparition <= 0:
                projectiles.remove(projectile)  
            else:
                projectile.draw(screen)

    else :
        print("Game Over")

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



