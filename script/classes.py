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
    
    def crea_vect(p1,p2):
        """Renvoie un vecteur a partir de deux points"""
        return Vector2(p2.x-p1.x,p2.y-p1.y)


class Map :
    """Cette classe sert simplement à stocker tous les objets que nous voulons sur une map.
    Par exemple les collisions, les sprites affichés, les objets avec lesquelles on peut intéragir (porte, enigme etc...)
    et également les monstres. Cela nous permettra de faire un parcours par compréhension de chacune des listes
    et d'agir en fonction de leur besoin. Par exemple faire fonctionner l'intelligence artificielle des monstres pour liste monstre"""
    def __init__ (self, path, chunk_size:int=16, num_bande:int=4) :
        self.chunk_size = chunk_size
        self.matrices = [] # Liste de matrice de 1 et de 0
        self.liste_col = [] # Liste de liste de collision dont l'index correlle avec self.matrices
        self.real_col = [] # Juste les collisions autours du perso
        self.actual_map = 0 # Index de la map actuel, 0 étant celle vu du haut
        
        self.leviers = []
        self.collisions_optionels = []

        self.only_visuals = []
        self.num_bande = num_bande
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            #self.liste_sprite_affiche = data["sprites"]
            self.build_map(data["top"], "top")
            self.build_map(data["side"][0], "side")
            self.build_map(data["side"][1], "side")
            self.build_map(data["side"][2], "side")
            self.build_map(data["side"][3], "side")
            
            self.add_leviers(data)
            self.add_collisions_optionels(data)
    
            #self.liste_interactable = []
            #self.liste_monstres = []

    def build_map(self, matrice, sprite_set:str) :
        tab = []
        cosmetic = []
        for i in range(len(matrice)) :
            for j in range(len(matrice[i])) :
                if matrice[i][j] >= 5:
                    
                    tab.append(Transform(sprite="sprites/" + sprite_set + "/" + str(matrice[i][j]) + ".png", position=Vector2(j*self.chunk_size, i*self.chunk_size), taille=Vector2(self.chunk_size, self.chunk_size)))
                    
                else :
                    cosmetic.append(Transform(sprite="sprites/" + sprite_set + "/" + str(matrice[i][j]) + ".png", position=Vector2(j*self.chunk_size, i*self.chunk_size), taille=Vector2(self.chunk_size, self.chunk_size)))
        self.liste_col.append(tab)
        self.only_visuals.append(cosmetic)
        self.matrices.append(matrice)

    def add_leviers(self, data) :
        """Pour construire les leviers etc..."""
        self.leviers = [[] for _ in range(self.num_bande + 1)]
        for objet in data["leviers"] :
            levier = Transform(objet["sprite"], Vector2(objet["x"], objet["y"]) * self.chunk_size,
                                                        Vector2(objet["tx"], objet["ty"]) * self.chunk_size)
            levier.actionnement = objet["affect"]
            levier.actif = False
            self.leviers[objet["map"]].append(levier)

    def add_collisions_optionels(self, data) :
            """Pour construire les leviers etc..."""
            self.collisions_optionels = [[] for _ in range(self.num_bande + 1)]
            for objet in data["collisions"] :
                col = Transform(objet["sprite"], Vector2(objet["x"], objet["y"]) * self.chunk_size,
                                                            Vector2(objet["tx"], objet["ty"]) * self.chunk_size)
                col.actif = True if objet["actif"] == 1 else 0
                self.collisions_optionels[objet["map"]].append(col)

            
        


    def change_map(self, index) :
        ancienne = self.actual_map
        self.actual_map = index
        
        ancienne_ref = self.liste_col[ancienne][0] # On obtient la collision origine
        
        
        new_ref = self.liste_col[index][0]


        self.bouge_tout(Vector2(ancienne_ref.position.x - new_ref.position.x, 0))


        

    def draw(self, screen) :
        for col in self.liste_col[self.actual_map] :
            col.draw(screen)
        for col in self.real_col :
            col.draw(screen)
        for obj in self.only_visuals[self.actual_map] :
            obj.draw(screen)
        for obj in self.leviers[self.actual_map] :
            obj.draw(screen)
        for obj in self.collisions_optionels[self.actual_map] :
            if obj.actif :
                obj.draw(screen)

    def bouge_tout(self, vecteur:Vector2) :
        for col in self.liste_col[self.actual_map] :
            col.position += vecteur
        for obj in self.only_visuals[self.actual_map] :
            obj.position += vecteur
        for obj in self.leviers[self.actual_map] :
            obj.position += vecteur
        for obj in self.collisions_optionels[self.actual_map] :
            obj.position += vecteur

    
    def pos_theorique(self,pos):
        pos_theo = pos - self.liste_col[self.actual_map][0].position

        return pos_theo
    
    def pos_matrice(self,pos):
        pos_th = self.pos_theorique(pos)
        pos_x= int(pos_th.x // self.chunk_size)
        pos_y= int(pos_th.y // self.chunk_size)

        return pos_x,pos_y
    
    def quel_bande(self,pos_matrice):
        matrice_actuelle = self.matrices[self.actual_map]
        numero_bande =  pos_matrice[1] // (len(matrice_actuelle)//self.num_bande)

        return numero_bande
    
    def est_dans_matrice(self, pos) :
        mat = self.pos_matrice(pos)
        tiles_height = len(self.matrices[self.actual_map]) - 1
        tiles_width = len(self.matrices[self.actual_map][0]) - 1
        return 1 < mat[0] < tiles_width and 0 < mat[1] < tiles_height


    def collision_autour_tuple(self, pos):
        """Renvoie un tuple des collision adjacentes a l'objet (H,D,B,G)"""
        pos_mat = self.pos_matrice(pos)
        x = pos_mat[0]
        y = pos_mat[1]
        tab = [(x-1, y-1), (x, y-1), (x+1, y-1), (x-1, y), (x+1, y), (x-1, y+1), (x, y+1), (x+1, y+1)] # Les 8 coordonnes autour de l'objet
        #tab = [(x, y-1), (x-1, y), (x+1, y), (x, y+1)] 
        garde = []

        for c in tab :
            if self.matrices[self.actual_map][c[1]][c[0]] >= 5 :
                garde.append(c)

        return garde
    
    def est_dans_col(self, pos:Vector2) :
        pos_mat = self.pos_matrice(pos)
        x = pos_mat[0]
        y = pos_mat[1]

        if self.matrices[self.actual_map][y][x] == 6  :
            return True
        return False

    
    def collision(self, pos) :
        """Active les collisions seulement autour du personnage"""
        autour = self.collision_autour_tuple(pos)
        self.real_col = []
        for c in autour :
            x = c[0]*self.chunk_size+self.liste_col[self.actual_map][0].position.x
            y = c[1]*self.chunk_size+self.liste_col[self.actual_map][0].position.y
            self.real_col.append(Transform("sprites/shrek.png", Vector2(x, y), Vector2(self.chunk_size, self.chunk_size)))
        for c in self.collisions_optionels[self.actual_map] :
            if c.actif :
                self.real_col.append(c)

    #def dic_to_obj(list, TYPE) :
     #   SPRITE = 0

      #  liste = []
       # for dic in list :
        #    if TYPE == SPRITE :
         #       liste = Transform(dic["sprite"], Vector2(dic["posx"], dic["posy"]), Vector2(dic["taillex"], dic["tailley"]))



class Transform :
    """La classe transform est une classe permettant d'initialiser un objet
    avec comme attribut son visuel, sa position, sa taille et si il a une collision"""

    def __init__(self, sprite:str="sprites/collision.png", position=Vector2(), taille=Vector2(), temps_apparition=None, direction=None) :
        self.position = position
        self.temps_apparition = temps_apparition  # Si on veut que l'objet disparaisse après un certains nombre de frame.
        self.direction = direction if direction is not None else Vector2(0, 0)
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
    
    def centrer(self,position:Vector2) : 
        """"""
        self.position = Vector2(position.x - self.taille.x /2 , position.y - self.taille.y/2)
    
    def get_points_cardinaux(self) :
        pos = []
        pos.append(self.position)
        pos.append(self.position + self.taille)
        pos.append(self.position + Vector2(self.taille.x, 0))
        pos.append(self.position + Vector2(0, self.taille.y))
        return pos

    def est_dedanddds(self, autre_objet, offset:Vector2=Vector2(0, 0)) -> bool:
        pos = self.get_centre() + offset
        return (pos.x >= autre_objet.position.x and
                pos.y >= autre_objet.position.y and
                pos.x <= autre_objet.position.x + autre_objet.taille.x and
                pos.y <= autre_objet.position.y + autre_objet.taille.y)
    
    def est_dedans(self, autre_objet, offset:Vector2=Vector2(0, 0)) -> bool:
        positions = self.get_points_cardinaux()
        for pos in positions :
            pos += offset
            if (pos.x >= autre_objet.position.x and
                    pos.y >= autre_objet.position.y and
                    pos.x <= autre_objet.position.x + autre_objet.taille.x and
                    pos.y <= autre_objet.position.y + autre_objet.taille.y) :
                return True
        return False


    def detecte_collision(self, autre_objet, offset:Vector2=Vector2(0, 0)):
        x1, y1 = (self.position + offset).to_tuple()
        l1, h1 = self.taille.to_tuple()
        x2, y2 = autre_objet.position.to_tuple()
        l2, h2 = autre_objet.taille.to_tuple()

        collision_x = (x1 < x2 + l2) and (x1 + l1 > x2)
        collision_y = (y1 < y2 + h2) and (y1 + h1 > y2)

        sens = Vector2(1, 1)
        if collision_x and collision_y:
            collision_gauche = abs(x1 + l1 - x2)
            collision_droite = abs(x1 - (x2 + l2))
            collision_haut = abs(y1 + h1 - y2)
            collision_bas = abs(y1 - (y2 + h2))

            min_collision = min(collision_gauche, collision_droite, collision_haut, collision_bas)

            sens.x = (min_collision == collision_gauche or min_collision == collision_droite) * 1

            sens.y = (min_collision == collision_bas or min_collision == collision_haut) * 1

        return sens
    

def normalize(pos0, pos1) :
    """Retourne le veteur normalistée avec x et y compris entre -1 et 1"""
    return Vector2(pos1.x - pos0.x, pos1.y - pos0.y) / Vector2.distance(pos0, pos1)

