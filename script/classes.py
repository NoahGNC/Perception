import pygame
import json
from math import sqrt

class Vector2 :
    """La classe Vector2 est une classe que nous avons créé pour une question de lisibilité.
    En effet l'avantage de cette classe contrairement à un tuple c'est que pour obtenir la valeur x
    nous faisons juste variable.x et non variable[0]"""
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
                
    def est_null(self) :
        """Renvoie True si les valeurs x et y de la classe valent 0 False sinon"""
        return self.x == 0 and self.y == 0
    
    def to_tuple(self) :
        """Permet de convertir notre classe Vector2 en tuple si besoin"""
        return(self.x, self.y)
    
    def normalized(self) : 
        """Va normaliser ce vecteur avec le vecteur nul"""
        self = normalize(Vector2.ZERO(), self)
        
        return self

    def __add__(self, autre) :
        """Voici une surcharge d'addition, elle permet d'additionner à notre classe
        une variable de type tuple, int, float ou bien un autre Vector2."""
        if isinstance(autre, Vector2) :
            return Vector2(self.x + autre.x, self.y + autre.y)
        elif isinstance(autre, tuple) :
            return (self.x + autre[0], self.y + autre[1])
        elif isinstance(autre, (int, float)) :
            return Vector2(self.x + autre, self.y + autre)
        


    def __sub__(self, autre):
        if isinstance(autre, Vector2):
            return Vector2(self.x - autre.x, self.y - autre.y)
        elif isinstance(autre, tuple):
            return (self.x - autre[0], self.y - autre[1])
        elif isinstance(autre, (int, float)):
            return Vector2(self.x - autre, self.y - autre)

    def __mul__(self, autre) :
        if isinstance(autre, (int, float)) :
            return Vector2(self.x * autre, self.y * autre)
        elif isinstance(autre, Vector2) :
            return Vector2(self.x * autre.x, self.y * autre.y)

    def __truediv__(self, autre) :
        if isinstance(autre, (int, float)) and autre != 0 :
            return Vector2(self.x / autre, self.y / autre)
        elif isinstance(autre, Vector2) and autre != 0 :
            return Vector2(self.x / autre.x, self.y / autre.y)
        else :  # Si il y a division par 0 ou que le type n'est pas supporté on retourne un Vector2 vide.
            return Vector2(0, 0)

    def __str__(self) :
        return "x : " + str(self.x) + " y : " + str(self.y)
    
    def ZERO() :
        return Vector2(0, 0)

    def distance(pos0, pos1):
        """Retourne la distance entre deux point Vector2"""
        return sqrt((pos0.x - pos1.x) ** 2 + (pos0.y - pos1.y) ** 2)
    



class Map :
    """Cette classe sert simplement à stocker tous les objets que nous voulons sur une map.
    Par exemple les collisions, les sprites affichés, les objets avec lesquelles on peut intéragir (porte, enigme etc...)
    et également les monstres. Cela nous permettra de faire un parcours par compréhension de chacune des listes
    et d'agir en fonction de leur besoin. Par exemple faire fonctionner l'intelligence artificielle des monstres pour liste monstre"""
    def __init__ (self, path, chunk_size:int=16) :
        self.chunk_size = chunk_size
        self.liste_col = []
        self.real_col = []
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            #self.liste_sprite_affiche = data["sprites"]
            matrice = data["haut"]
            self.matrice = matrice
            #self.liste_interactable = []
            #self.liste_monstres = []
        for i in range(len(matrice)) :
            for j in range(len(matrice[i])) :
                if matrice[i][j] == 1 :
                    self.liste_col.append(Transform(position=Vector2(j*chunk_size, i*chunk_size), taille=Vector2(chunk_size, chunk_size)))

        

    def draw(self, screen) :
        for col in self.liste_col :
            col.draw(screen)
        for col in self.real_col :
            col.draw(screen)

    def bouge_tout(self, vecteur:Vector2) :
        for col in self.liste_col :
            col.position += vecteur
    
    def pos_theorique(self,pos):
        pos_theo = pos - self.liste_col[0].position

        return pos_theo
    
    def pos_matrice(self,pos):
        pos_th = self.pos_theorique(pos)
        pos_x= int(pos_th.x // self.chunk_size)
        pos_y= int(pos_th.y // self.chunk_size)

        return pos_x,pos_y
    

    def collision_autour_tuple(self, pos):
        """Renvoie un tuple des collision adjacentes a l'objet (H,D,B,G)"""
        pos_mat = self.pos_matrice(pos)
        x = pos_mat[0]
        y = pos_mat[1]
        tab = [(x-1, y-1), (x, y-1), (x+1, y-1), (x-1, y), (x+1, y), (x-1, y+1), (x, y+1), (x+1, y+1)] # Les 8 coordonnes autour de l'objet
        garde = []

        for c in tab :
            if self.matrice[c[1]][c[0]] == 1 :
                garde.append(c)

        return garde
    
    def collision(self, pos) :
        """Active les collisions seulement autour du personnage"""
        autour = self.collision_autour_tuple(pos)
        self.real_col = []
        for c in autour :
            x = (c[0])*self.chunk_size+self.liste_col[0].position.x
            y = c[1]*self.chunk_size+self.liste_col[0].position.y
            self.real_col.append(Transform("sprites/shrek.png", Vector2(x, y), Vector2(self.chunk_size, self.chunk_size)))


    #def dic_to_obj(list, TYPE) :
     #   SPRITE = 0

      #  liste = []
       # for dic in list :
        #    if TYPE == SPRITE :
         #       liste = Transform(dic["sprite"], Vector2(dic["posx"], dic["posy"]), Vector2(dic["taillex"], dic["tailley"]))



class Transform :
    """La classe transform est une classe permettant d'initialiser un objet
    avec comme attribut son visuel, sa position, sa taille et si il a une collision"""

    def __init__(self, sprite:str="sprites/collision.png", position=Vector2(), taille=Vector2(), temps_apparition=None) :
        self.position = position
        self.temps_apparition = temps_apparition  # Si on veut que l'objet disparaisse après un certains nombre de frame.
        
        if sprite != None :
            self.sprite = pygame.image.load(sprite).convert_alpha()  # On charge le sprite de l'objet dans la ram

        if taille.est_null() and sprite != None :  # Si on n'a pas spécifié de taille à l'objet, sa taille sera par défaut la taille de l'image.
            self.taille = Vector2(sprite.get_rect().size[0], sprite.get_rect().size[1])
        else:
            self.taille = taille

        if sprite != None :
            self.resize(self.taille)

    def resize(self, taille) :
        """Permet de changer la taille de l'objet grâce à la fonction intégré de pygame
        Prend en paramètre un Vector2 étant la nouvelle taille voulue"""
        self.taille = taille
        self.sprite = pygame.transform.scale(self.sprite, (taille.x, taille.y))

    def draw(self, screen) :
        """Cette procédure nous a permis de stocker tous les objets à afficher dans une liste
        et d'appeler leur méthode draw grâce à un parcours par compréhension. Ainsi nous avons pu afficher de façon
        efficace tous les objets du jeu à afficher"""
        if self.temps_apparition != None or self.sprite != None and self.temps_apparition != None :
            if self.temps_apparition >= 0 :
                screen.blit(self.sprite, (self.position.x, self.position.y))
                self.temps_apparition -= 1
        elif self.sprite != None:
            screen.blit(self.sprite, (self.position.x, self.position.y))

    def charge_nouveau_sprite(self, nouveau_sprite:str) :
        """Cette fonction sert simplement a remplacer le sprite de l'objet par un nouveau
        Prend en paramètre une string qui est le nom du fichier du nouveau sprite"""
        self.sprite = pygame.image.load(nouveau_sprite).convert_alpha()
        self.sprite = pygame.transform.scale(self.sprite, (self.taille.x, self.taille.y))

    def get_centre(self) :
        """Le repère orthonormé étant en haut à gauche, on veut parfois récupérer le centre notamment pour le système de collision"""
        return Vector2(self.position.x + self.taille.x // 2, self.position.y + self.taille.y // 2) 


    def detecte_collision(self, autre_objet):
        x1, y1 = self.position.to_tuple()
        l1, h1 = self.taille.to_tuple()
        x2, y2 = autre_objet.position.to_tuple()
        l2, h2 = autre_objet.taille.to_tuple()

        collision_x = (x1 < x2 + l2) and (x1 + l1 > x2)
        collision_y = (y1 < y2 + h2) and (y1 + h1 > y2)

        sens = Vector2(0, 0)
        if collision_x and collision_y:
            collision_gauche = abs(x1 + l1 - x2)
            collision_droite = abs(x1 - (x2 + l2))
            collision_haut = abs(y1 + h1 - y2)
            collision_bas = abs(y1 - (y2 + h2))

            min_collision = min(collision_gauche, collision_droite, collision_haut, collision_bas)

            sens.x = -(min_collision == collision_gauche or min_collision == collision_droite)
            sens.y = -(min_collision == collision_bas or min_collision == collision_haut)

        return sens

def normalize(pos0, pos1) :
    """Retourne le veteur normalistée avec x et y compris entre -1 et 1"""
    return Vector2(pos1.x - pos0.x, pos1.y - pos0.y) / Vector2.distance(pos0, pos1)

