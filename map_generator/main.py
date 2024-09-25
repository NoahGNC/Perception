import json
from PIL import Image

# Fonction pour personnaliser l'encodage JSON et garder les lignes de la matrice sur une seule ligne
class CustomJSONEncoder(json.JSONEncoder):
    def encode(self, obj):
        if isinstance(obj, list):
            # Pour chaque sous-liste (ligne de la matrice), on la formate sur une seule ligne
            return '[\n' + ',\n'.join('  ' + json.dumps(ligne) for ligne in obj) + '\n]'
        return super().encode(obj)



with Image.open("map.png") as img :
    width, height = img.size

    matrice = []

    for y in range(height):
        mat_ligne = []
        for x in range(width):
            gris = img.getpixel((x,y))
            print(gris)

            if gris > 0 : # Le pixel est plutôt blanc
                mat_ligne.append(0)
            else :
                mat_ligne.append(1)
        matrice.append(mat_ligne)

    fichier_json = json.dumps(matrice, indent=0, cls=CustomJSONEncoder)
    
    with open("map.json", "w") as fichier:
        fichier.write(fichier_json)



