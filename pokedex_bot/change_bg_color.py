from PIL import Image
import io

def change_background(image_data, background_color=(22, 30, 39)):
    """
    Change le fond d'une image PNG avec transparence par une couleur RGB donnée.

    :param image_data: Les données binaires de l'image (bytes).
    :param background_color: Tuple RGB représentant la couleur du fond (par défaut : (22, 30, 39)).
    :return: L'image avec le fond modifié, sous forme de bytes.
    """

    # Charger l'image depuis les données binaires
    image = Image.open(io.BytesIO(image_data)).convert("RGBA")

    # Créer un nouveau fond de la même taille que l'image
    background = Image.new("RGBA", image.size, background_color + (255,))  # (255,) ajoute l'opacité maximale

    # Fusionner le fond et l'image
    final_image = Image.alpha_composite(background, image)

    # Convertir en RGB (supprimer la transparence pour certains formats comme JPEG)
    # final_image = final_image.convert("RGB")

    # Enregistrer l'image en mémoire
    output = io.BytesIO()
    final_image.save(output, format="PNG")
    return output.getvalue()
