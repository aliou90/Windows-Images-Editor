# -*- coding: utf-8 -*-
#----------------------------------------------------------------------------
# Author      :   Aliou Mbengues
developer = {
    "name" : "Aliou Mbengue",
    "email": "mbengue.tech@gmail.com",
    "tel": "(+221) 77-664-70-80",
    "version": 1.0
    }
# ---------------------------------------------------------------------------
# Modules 
import tempfile
import json
import os
from datetime import datetime
import cv2
import requests
import io
import glob
import numpy as np
from rembg import remove
from PIL import Image, ImageTk, ExifTags, ImageFilter, ImageDraw, ImageFont, ImageEnhance, ImageOps, ImageChops
import customtkinter as ctk
from customtkinter import CTkImage
import tkinter as tk
from tkinter import BooleanVar, StringVar, filedialog, ttk, messagebox, Entry, StringVar, Button, colorchooser, Canvas 
from pathlib import Path
import sys  
from math import cos, sin, radians

# Path to JSON files
saved_apis_file = str(Path.home() / ".fastEdit" / ".api" / "saved_apis_file.json")
chosen_api_file = str(Path.home() / ".fastEdit" / ".api" / "chosen_api_file.json")
# Temp dir
temp_dir = str(Path.home() / ".fastEdit" / ".temp")

# Créer le dossier de destination s'il n'existe pas
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# Ensure the directory exists
os.makedirs(Path(saved_apis_file).parent, exist_ok=True)

# Ensure the files exist
if not os.path.exists(saved_apis_file):
    with open(saved_apis_file, 'w') as file:
        json.dump({}, file)

if not os.path.exists(chosen_api_file):
    with open(chosen_api_file, 'w') as file:
        json.dump({"api_key": None}, file)
        
# Définir la variable globale pour l'API
global_api_key = None

# Liens 
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Gestion des images
# Fonction pour charger une image, la redimensionner et la convertir en CTkImage
def create_icon(image_path, size=(20, 20)):
    if os.path.exists(image_path):
        img = Image.open(image_path)
        img = img.resize(size, Image.LANCZOS)
        ctk_image = CTkImage(light_image=img, dark_image=img)
        return ctk_image
    else:
        print(f"Erreur : le fichier {image_path} n'existe pas.")
        return None

# Chemins des images
icon_path = resource_path('assets/ico/Fast_Edit.png') # Définir l'icône de l'application
img_crop_path = resource_path('assets/ico/crop.png')
img_flipv_path = resource_path('assets/ico/flip-1.png')
img_fliph_path = resource_path('assets/ico/flip-2.png')
img_rotate_plus_path = resource_path('assets/ico/rotate-1.png')
img_rotate_moins_path = resource_path('assets/ico/rotate-2.png')
img_browse_path = resource_path('assets/ico/browse.png')
img_delete_path = resource_path('assets/ico/delete.png')
img_dump_path = resource_path('assets/ico/dump.png')
img_previous_path = resource_path('assets/ico/previous.png')
img_next_path = resource_path('assets/ico/next.png')
img_start_path = resource_path('assets/ico/start.png')

# Extensions prises en charge
filetypes = [
    ("All image files", "*.jpg *.jpeg *.png *.gif *.jfif *.bmp *.tiff *.webp *.heif *.ico *.raw *.svg "
                        "*.JPG *.JPEG *.PNG *.GIF *.JFIF *.BMP *.TIFF *.WEBP *.HEIF *.ICO *.RAW *.SVG")
]

# Fonction pour basculer l'apparence
def toggle_appearance():
    current_mode = ctk.get_appearance_mode()
    new_mode = "Dark" if current_mode == "Light" or current_mode == "System" else "Light"
    ctk.set_appearance_mode(new_mode)
    appearance_button.configure(text=new_mode.capitalize())

# Fonction pour afficher le guide d'utilisation
def show_help():
    help_text = (
        "Guide d'utilisation de FAST-EDIT\n\n"
        "1. Choisissez les images à traiter en cliquant sur 'Choisir des images'.\n"
        "2. Sélectionnez le répertoire de destination où les images traitées seront sauvegardées.\n"
        "3. Vous pouvez redimensionner les images en sélectionnant une résolution dans la liste déroulante.\n"
        "   - Résolutions standard disponibles :\n"
        "     - 640x480 (VGA)\n"
        "     - 800x600 (SVGA)\n"
        "     - 1024x768 (XGA)\n"
        "     - 1280x800 (WXGA)\n"
        "     - 1280x720 (HD)\n"
        "     - 1366x768 (HD+)\n"
        "     - 1600x900 (HD+)\n"
        "     - 1920x1080 (Full HD)\n"
        "     - 300x250 (Bannière publicitaire)\n"
        "     - 400x300 (Image de miniatures)\n"
        "     - 600x400 (Affiche ou poster de petite taille)\n"
        "     - 1200x628 (Image pour les réseaux sociaux)\n"
        "     - 728x90 (Leaderboard)\n"
        "     - 300x600 (Skyscraper)\n"
        "     - 3840x2160 (4K)\n"
        "     - 150x150 (Profil)\n"
        "4. Cochez 'Supprimer l'arrière-plan' si vous souhaitez enlever l'arrière-plan des images.\n"
        "5. Appliquez une nouvelle couleur de fond (Si vous le souhaitez.).\n"
        "6. Appliquer plus d'effet à l'image (Rotation, 3D etc...).\n"
        "7. Cliquez sur 'Commencer' pour lancer le traitement des images.\n\n"
        "Pour toute autre aide, veuillez nous contacter.\n"
        f"Développeur:\n{developer['name']} ({developer['email']})\n"
        f"Tél: ({developer['tel']})\n\n"
        f"{developer['name']} - Tous droits Réservés"
    )
    close_all_popups()
    messagebox.showinfo("Aide", help_text)

# fonction pour vider le répertoire temporaire temp_dir en supprimant tous les fichiers qu'il contient.
def clear_temp_dir(temp_dir):
    files = glob.glob(os.path.join(temp_dir, '*'))
    for f in files:
        try:
            os.remove(f)
        except Exception as e:
            print(f"Erreur lors de la suppression du fichier {f}: {str(e)}")    

# Fonction pour créer une image fictive
def create_loading_image(text="Traitement en cours...", size=(400, 400), font_size=24, save_path=None):
    if save_path is None:
        save_path = str(Path.home() / ".fastEdit" / ".img" / "loading.png")
    
    # Créer le répertoire si nécessaire
    save_dir = Path(save_path).parent
    if not save_dir.exists():
        save_dir.mkdir(parents=True, exist_ok=True)
    
    image = Image.new("RGBA", size, (255, 255, 255, 255))  # Image blanche
    draw = ImageDraw.Draw(image)
    
    try:
        font = ImageFont.truetype("helvetica.ttf", font_size)  # Utiliser une police spécifique si elle est disponible
    except IOError:
        font = ImageFont.load_default()  # Utiliser une police par défaut
    
    # Utiliser textbbox pour obtenir les dimensions du texte
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    draw.text(position, text, fill="black", font=font)
    
    image.save(save_path)

# Créer et sauvegarder l'image
create_loading_image()
print("Image de chargement créé et sauvegardé !")

def display_loading_image():
    # Afficher l'image de chargement
    loading_img_path = str(Path.home() / ".fastEdit" / ".img" / "loading.png")
    loading_img_path = Image.open(loading_img_path).convert("RGBA")
    destroy_image_frame_widgets(image_frame)
    create_image_frame_image(image_frame, loading_img_path)
    
# Fonction pour afficher l'animation GIF pendant le traitement
def remove_background_with_rembg(image_file):
    print("Traitement avec rembg en cours")

    # Charger l'image depuis le fichier
    input_image = Image.open(image_file).convert('RGBA')
    
    # Supprimer l'arrière-plan
    output_image = remove(input_image)
    
    # Convertir le résultat en RGBA si ce n'est pas déjà le cas
    if output_image.mode != 'RGBA':
        output_image = output_image.convert('RGBA')

    print(f"Background removed for {image_file}.")
    return output_image

def remove_background_with_api(image_file, api_key):
    print("Traitement avec remove.bg en cours")
    # Charger l'image depuis le fichier
    with open(image_file, 'rb') as image:
        response = requests.post(
            'https://api.remove.bg/v1.0/removebg',
            files={'image_file': image},
            data={'size': 'auto'},
            headers={'X-Api-Key': api_key},
        )
    
    if response.status_code == requests.codes.ok:
        output_image = Image.open(io.BytesIO(response.content)).convert('RGBA')
        print(f"Background removed for {image_file}.")
        return output_image
    else:
        error_message = f"Error: {response.status_code} - {response.text}"
        if response.status_code == 402:
            error_message = ("Le serveur remove.bg n'a pas accepté le traitement.\n"
                             "Veuillez vérifier si vous avez assez de crédit.")
        elif response.status_code == 400:
            error_message = "La requête était invalide. Veuillez vérifier l'image et réessayer."
        elif response.status_code == 403:
            error_message = ("Accès refusé. Veuillez vérifier votre clé API ou "
                             "les permissions associées.")
        elif response.status_code == 429:
            error_message = ("Trop de requêtes. Vous avez dépassé la limite de "
                             "requêtes par minute. Veuillez réessayer plus tard.")
        else:
            error_message = f"Erreur inconnue : {response.status_code}\n{response.text}"
        
        print(error_message)
        return error_message

# Correction de l'image avant traitement
def correct_image_orientation(image):
    try:
        # Vérifier si l'image a des métadonnées EXIF
        if hasattr(image, '_getexif') and image._getexif() is not None:
            # Trouver la clé d'orientation dans les métadonnées EXIF
            orientation = None
            for key, value in ExifTags.TAGS.items():
                if value == 'Orientation':
                    orientation = key
                    break
            
            # Obtenir les données EXIF
            exif = dict(image._getexif().items())
            
            # Corriger l'orientation de l'image si nécessaire
            if orientation and orientation in exif:
                if exif[orientation] == 3:
                    image = image.rotate(180, expand=True)
                elif exif[orientation] == 6:
                    image = image.rotate(270, expand=True)
                elif exif[orientation] == 8:
                    image = image.rotate(90, expand=True)
    except (AttributeError, KeyError, IndexError):
        # L'image n'a pas de métadonnées EXIF ou aucune orientation n'a besoin d'être corrigée
        pass
    
    return image

def resize_image(image, width, height):
    # Convertir l'image reçue à "RGBA" si ce n'est pas déjà le cas
    if image.mode != "RGBA":
        image = image.convert("RGBA")
    
    # Obtenez les dimensions de l'image reçue
    img_width, img_height = image.size
    print(f"Dimension de l'image sans BG: {img_width}x{img_height}")
    
    # Calculer le facteur de redimensionnement pour maintenir les proportions
    aspect_ratio = img_width / img_height
    container_ratio = width / height
    
    if aspect_ratio > container_ratio:
        # Redimensionner l'image en fonction de la largeur
        new_width = width
        new_height = int(new_width / aspect_ratio)
    else:
        # Redimensionner l'image en fonction de la hauteur
        new_height = height
        new_width = int(new_height * aspect_ratio)
    
    # Redimensionner l'image
    resized_image = image.resize((new_width, new_height), Image.LANCZOS)
    print(f"Dimension de l'image redimensionnée: {new_width}x{new_height}")    
    
    # Créer une nouvelle image avec les dimensions spécifiées
    new_image = Image.new("RGBA", (width, height), (255, 255, 255, 0))
    
    # Calculer les coordonnées pour centrer l'image redimensionnée
    left = (width - new_width) // 2
    top = (height - new_height) // 2
    
    # Coller l'image redimensionnée et éventuellement tournée au centre de la nouvelle image
    new_image.paste(resized_image, (left, top), resized_image)
    
    return new_image

def add_new_background(image, new_color):
    # Convertir la couleur hexadécimale en RGB
    rgb_color = hex_to_rgb(new_color)
    
    # Obtenez les dimensions de l'image reçue
    img_width, img_height = image.size

    # Créez une nouvelle image avec la couleur de fond spécifiée
    background_image = Image.new("RGB", (img_width, img_height), rgb_color)
    
    # Convertir l'image d'origine au mode RGBA pour inclure la transparence si nécessaire
    image = image.convert("RGBA")
    
    # Coller l'image reçue sur le fond coloré
    # Le troisième argument (masque) assure que la transparence est respectée
    background_image.paste(image, (0, 0), image)
    
    return background_image

# Fonction pour récupérer les chemins des fichiers du tableau
def get_file_paths_from_treeview():
    file_paths = []
    for item in tree.get_children():
        file_paths.append(tree.item(item, "values")[2])
    return file_paths

def configure_widgets_on_process():
    if current_process:
        start_button.configure(text="Traitement en cours ....", state="disabled")
        clear_button.configure(state="disabled")
        clear_all_button.configure(state="disabled")
    else:
        start_button.configure(text="Commencer le traitement", state="normal")
        clear_button.configure(state="normal")
        clear_all_button.configure(state="normal")

# Fonction pour appliquer l'effet 3D uniquement à l'élément central
def apply_3d_effect(image):
    # Convertir l'image en mode RGBA pour manipulations d'alpha
    image = image.convert('RGBA')
    
    # Créer un masque pour isoler l'élément central
    mask = Image.new('L', image.size, 0)
    mask_draw = ImageDraw.Draw(mask)
    element_bbox = image.getbbox()
    mask_draw.rectangle(element_bbox, fill=255)

    # Extraire l'élément central à partir du masque
    element = Image.new('RGBA', image.size, (0, 0, 0, 0))
    element.paste(image, mask=mask)

    # Ajouter une bordure noire pour l'effet 3D
    border_width = 15
    element_with_border = ImageOps.expand(element, border=border_width, fill='black')

    # Ajouter une ombre projetée plus prononcée
    shadow_offset = 30
    shadow_blur_radius = 20
    shadow = Image.new('RGBA', (element_with_border.width + shadow_offset, element_with_border.height + shadow_offset), (0, 0, 0, 0))
    shadow.paste(element_with_border, (shadow_offset, shadow_offset))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=shadow_blur_radius))

    # Ajouter une bordure blanche pour accentuer l'effet de relief
    border_white_width = 5
    element_with_double_border = ImageOps.expand(element_with_border, border=border_white_width, fill='white')

    # Ajuster la taille de l'ombre pour correspondre à l'élément central avec les bordures
    final_element = Image.new('RGBA', (element_with_double_border.width, element_with_double_border.height), (0, 0, 0, 0))
    final_element.paste(shadow, (0, 0), shadow)
    final_element.paste(element_with_double_border, (0, 0), element_with_double_border)

    # Ajouter un contour lumineux pour accentuer l'effet de relief
    edge_enhanced_element = final_element.filter(ImageFilter.UnsharpMask(radius=3, percent=200, threshold=3))

    # Créer une nouvelle image de la taille de l'image d'origine pour combiner les résultats
    combined_image = Image.new('RGBA', image.size, (0, 0, 0, 0))

    # Coller l'image d'origine (sans les effets) sur l'image combinée
    combined_image.paste(image, (0, 0), mask=ImageChops.invert(mask))

    # Calculer la position pour centrer l'élément transformé
    offset_x = (image.width - edge_enhanced_element.width) // 2
    offset_y = (image.height - edge_enhanced_element.height) // 2

    # Coller l'élément transformé sur l'image combinée
    combined_image.paste(edge_enhanced_element, (offset_x, offset_y), edge_enhanced_element)

    return combined_image

# Apliquer la rotation et retournement sur le Background
def add_advenced_setting(image):    
    # Appliquer l'effet 3D
    if effect_3d_state:
        image = apply_3d_effect(image)

    # Appliquer la rotation
    degree = int(degree_var.get())
    if degree != 0:
        image = image.rotate(degree, expand=True)

    # Appliquer le flip vertical
    if vertical_flip_state:
        image = image.transpose(Image.FLIP_TOP_BOTTOM)

    # Appliquer le flip horizontal
    if horizontal_flip_state:
        image = image.transpose(Image.FLIP_LEFT_RIGHT)
        
    # Appliquer luminosité
    luminosity_value = luminosity_slider.get()
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1 + luminosity_value / 10.0)
    
    # Appliquer le contraste
    contrast_value = contrast_slider.get()
    if contrast_value > 0:
        contrast_value = contrast_value / 10.0
        # Convertir l'image en mode 'RGB' si elle est en mode 'RGBA'
        if image.mode == 'RGBA':
            image = image.convert('RGB')
        # Appliquer l'ombre
        image = ImageOps.autocontrast(image, cutoff=contrast_value * 100)
        # Revenir en mode 'RGBA' si nécessaire
        if image.mode == 'RGB':
            image = image.convert('RGBA')
    else:
        image = image

    return image


def process_images():
    global global_api_key, current_resized_image, save_image_action, save_all_images_action, cancel_action_action, cancel_all_actions_action, next_process, current_process, current_resized_image_path, processed_images, process_one, threads, temp_files, temp_files_number, temp_files_index

    try:
        threads = threads + 1
        source_paths = get_file_paths_from_treeview() # paths sur le tableau
        
        # Vérifier si le tableau est vide
        if not source_paths:
            close_all_popups()
            messagebox.showerror("Erreur", "Aucune image à traiter.")
            current_process = False
            configure_widgets_on_process()
            return

        unprocessed_files = []

        # Filter et enlever les images déjà traitées
        if processed_images:
            source_paths = [i for i in source_paths if i not in processed_images]

        # traiter une seule image
        if process_one:
            processed_images = []
            source_paths = []
            source_paths.append(process_one)

        for image_path in source_paths:
            destination_dir = destination_path.get() # Répertoire de Destination
            if not os.path.isdir(destination_dir):
                destination_dir = downloads_folder # Remettre par défaut
                destination_path.set(destination_dir)  # Mettre à jour la valeur de l'entry
            # Créer le dossier de destination s'il n'existe pas
            if not os.path.exists(destination_dir):
                os.makedirs(destination_dir)

            temp_files_infos = {}
            temp_files = [] # Vider Liste des échantillons de modifications de l'image en cours de traitement
            clear_temp_dir(temp_dir) # Vider Répertoire temporaire
            current_resized_image = None 
            current_process = True  # Processus en cours
            configure_widgets_on_process()

            img_path = os.path.normpath(image_path)
            temp_image = Image.open(img_path)
            # Sauvegarder l'image dans le répertoire temporaire
            with tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=".png") as temp_file:
                temp_image = correct_image_orientation(temp_image) # Corriger l'orientation
                temp_image.save(temp_file, format="PNG")
                temp_image_path = temp_file.name # Lien vers fichier temporaire
                
            try:
                # Afficahe de chargement en cours 
                display_loading_image()
                if remove_bg_var.get():
                    print("Remove BG selon le choix de plateforme !")
                    if remove_bg_api_activate.get():
                        error_message_or_image = remove_background_with_api(temp_image_path, global_api_key)
                        if isinstance(error_message_or_image, str):
                            # Si remove_background__with_api renvoie un message d'erreur
                            close_all_popups()
                            messagebox.showerror("Erreur", f"{error_message_or_image}")
                            remove_bg_var.set(False)
                            previous_remove_bg_state = False
                            remove_bg_api_activate.set(False)
                            edited_image = Image.open(temp_image_path)
                        else:
                            edited_image = error_message_or_image
                    else:
                        edited_image = remove_background_with_rembg(temp_image_path)
                else:
                    edited_image = Image.open(temp_image_path)
                    
                # Apliquer la rotation et retournement sur l'image et non le Background
                resized_image = add_advenced_setting(edited_image)

                # Redimentionner l'image
                resize_option = resize_options.get()
                width, height = map(int, resize_option.split('x'))
                resized_image = resize_image(resized_image, width, height)
                
                new_bg = color_label.cget('text').strip() 
                if new_bg:
                    # Ajouter un nouveau background 
                    resized_image = add_new_background(resized_image, new_bg)
                
                input_img_name = os.path.splitext(os.path.basename(img_path))[0] + '.png'
                output_img_name = os.path.splitext(os.path.basename(img_path))[0] + '_edited.png'
                output_path = os.path.join(destination_dir, output_img_name)
                
                # Dernières infos sur l'image en cours de modifications
                current_resized_image = resized_image        # Image
                current_resized_image_path = temp_image_path # Lien image tempo dernière

                # Référencer les paramètres de l'action en cours
                temp_files_infos = get_temp_files_infos()
                temp_files.append(temp_files_infos)
                temp_files_number = 0
                temp_files_index = 0

                # Prévisualisation de l'image
                if current_resized_image and not save_all_images_action.get():
                    # Créez et affichez les widgets pour la première image
                    destroy_image_frame_widgets(image_frame)  # Nettoyer les anciens widgets
                    create_image_frame_widgets(image_frame, current_resized_image)
                                        
                    # Attendez l'action de l'utilisateur
                    app.wait_variable(next_process)
                    next_process.set(False) # Action choisie, passer au suivant

                    if save_all_images_action.get():
                        # Sauvegarder cette image
                        current_resized_image.save(output_path)
                        processed_images.append(img_path)
                        # Afficher l'image dans le frame sans les boutons
                        destroy_image_frame_widgets(image_frame)
                        create_image_frame_image(image_frame, current_resized_image)
                        continue  # Passer à la prochaine image
                    elif cancel_all_actions_action.get():
                        close_all_popups()
                        messagebox.showinfo("Annulation", "L'opération a été annulée.")
                        destroy_image_frame_widgets(image_frame)
                        initialize_vars()
                        current_process = False
                        current_resized_image = None
                        current_resized_image_path = None
                        processed_images = []
                        process_one = None
                        configure_widgets_on_process()
                        return  # Quitter la fonction
                    elif cancel_action_action.get():
                        # Réinitialiser l'action
                        processed_images.append(img_path)
                        cancel_action_action.set(False)
                        continue  # Passer à la prochaine image sans sauvegarder
                    elif save_image_action.get():
                        # Sauvegarder cette image
                        current_resized_image.save(output_path)
                        processed_images.append(img_path)
                        # Réinitialiser l'action
                        save_image_action.set(False)
                elif save_all_images_action.get():
                    # Sauvegarder toutes les images sans afficher les boutons
                    current_resized_image.save(output_path)
                    processed_images.append(img_path) # Images déjà traitées
                    # Afficher l'image dans le frame sans les boutons
                    destroy_image_frame_widgets(image_frame)
                    create_image_frame_image(image_frame, current_resized_image)
                    continue  # Passer à la prochaine image

                # Sauvegarde de l'image 
                #current_resized_image.save(output_path)
     
            except Exception as e:
                print(f"Could not process file {img_path}: {e}")
                unprocessed_files.append((img_path, str(e)))

            finally:
                current_process = False           # Processus en cours
                current_resized_image = None      # Image traités en attente de sauvegarde
                current_resized_image_path = None # Image en cours de traitement
                destroy_image_frame_widgets(image_frame)
                temp_files_infos = {}
                temp_files = [] # Vider Liste des échantillons de modifications de l'image en cours de traitement
                temp_files_number = 0
                temp_files_index = 0
                clear_temp_dir(temp_dir) # Vider Répertoire temporaire
                configure_widgets_on_process()

        if unprocessed_files:
            unprocessed_files_str = "\n".join([f"{os.path.basename(path)}: {error}" for path, error in unprocessed_files])
            close_all_popups()
            messagebox.showwarning("Fichiers non traités", f"Les fichiers suivants n'ont pas été traités :\n{unprocessed_files_str}\nVeuillez vérifier si ce(s) fichier(s) son des images valides ou si leurs nom ne contiennent pas de caractère(s) invalides.")

        processed_images = [] # Images déjà traitées
        process_one = None   # Traitement unique
        initialize_vars() # Initialiser les variables globales

        if threads <= 1:
            close_all_popups()
            messagebox.showinfo("Succès", "Traitement des images terminé.")
    except Exception as e:
        close_all_popups()
        messagebox.showerror("Erreur", f"Une erreur s'est produite : {str(e)}")

    finally:
        threads = threads - 1

def process_image_review(img_in_process, prev = False, next=False):
    global current_resized_image, global_api_key, temp_files, temp_files_number, temp_files_index
    print(temp_files_index)

    try:
        # Afficahe de chargement en cours 
        display_loading_image()                    
        if remove_bg_var.get():
            print("Remove BG selon le choix de plateforme !")
            if remove_bg_api_activate.get():
                error_message_or_image = remove_background_with_api(img_in_process, global_api_key)
                if isinstance(error_message_or_image, str):
                    # Si remove_background__with_api renvoie un message d'erreur
                    close_all_popups()
                    messagebox.showerror("Erreur", f"{error_message_or_image}")
                    remove_bg_var.set(False)
                    previous_remove_bg_state = False
                    remove_bg_api_activate.set(False)
                    edited_image = Image.open(img_in_process)
                else:
                    edited_image = error_message_or_image
            else:
                edited_image = remove_background_with_rembg(img_in_process)
        else:
            edited_image = Image.open(img_in_process)
            
        # Redimentionner l'image et ajouter les effets supplémentaires
        resize_option = resize_options.get()
        width, height = map(int, resize_option.split('x'))
        resized_image = resize_image(edited_image, width, height)
        
        # Apliquer la rotation et retournement sur l'image et non le Background
        resized_image = add_advenced_setting(resized_image)
        
        new_bg = color_label.cget('text').strip() 
        if new_bg:
            # Ajouter un nouveau background 
            resized_image = add_new_background(resized_image, new_bg)

        # Dernières infos sur l'image en cours de modifications
        current_resized_image = resized_image        # Image
        current_resized_image_path = img_in_process # Lien image tempo dernière

        temp_files_infos = get_temp_files_infos()
        if not prev and not next:
            # Ajouter aux échantillons des dernières modifications
            temp_files_number += 1
            temp_files_index += 1 
            temp_files.append(temp_files_infos) 

        create_image_frame_widgets(image_frame, current_resized_image)

    except Exception as e:
        print("Erreur", str(e))

def get_temp_files_infos():
    temp_files_infos = { # Dictionnaire d'état pour prev-next
    'path': current_resized_image_path,
    'resize': resize_options.get(),
    'rembg': remove_bg_var.get(),
    'bg':  color_label.cget('text').strip(),
    'rotate': int(degree_var.get()),
    'effect3d': effect_3d_state,
    'flipv': vertical_flip_state,
    'fliph': horizontal_flip_state,
    'luminosity': luminosity_slider.get(),
    'contrast': contrast_slider.get()
    }
    return temp_files_infos

# Dummy functions for callbacks
def on_resize_option_change(*args):
    global previous_resize_option, temp_files, temp_files_number, temp_files_index, current_resized_image_path
    current_value = resize_option_var.get()
    if current_value and current_value != previous_resize_option:
        previous_resize_option = current_value
        if current_resized_image_path:
            # Mettre à jour la file d'attente / Écraser suivants annulés
            temp_files = [file for idx, file in enumerate(temp_files) if idx <= temp_files_index]
            # Mettre à jour les variables temp_files_number et temp_files_index
            temp_files_number = len(temp_files)
            temp_files_index = temp_files_number - 1

            try:
                process_image_review(current_resized_image_path)
            except ValueError as e:
                print(f"Erreur de valeur : {e}")
            except Exception as e:
                print(f"Erreur inattendue : {e}")

def select_previous_option(event=None):
    current_index = resize_option_values.index(resize_option_var.get())
    if current_index > 0:
        resize_option_var.set(resize_option_values[current_index - 1])

def select_next_option(event=None):
    current_index = resize_option_values.index(resize_option_var.get())
    if current_index < len(resize_option_values) - 1:
        resize_option_var.set(resize_option_values[current_index + 1])

def on_remove_bg_change():
    global previous_remove_bg_state, temp_files, temp_files_number, temp_files_index
    current_value = remove_bg_var.get()
    if current_value != previous_remove_bg_state:
        previous_remove_bg_state = current_value
        if current_resized_image_path:
            # Mettre à jour la file d'atente / Écraser suivants annulés
            temp_files = [file for idx, file in enumerate(temp_files) if idx <= temp_files_index]
            # Mettre à jour les variables temp_files_number et temp_files_index
            temp_files_number = len(temp_files) - 1
            temp_files_index = temp_files_number

            process_image_review(current_resized_image_path)

# Fonction pour activer/désactiver la case à cocher
def toggle_remove_bg_checkbox(event):
    current_value = remove_bg_var.get()
    remove_bg_var.set(not current_value)
    on_remove_bg_change()  # Appeler la fonction de changement pour mettre à jour l'état si nécessaire

def update_color_label(new_color):
    global previous_color_text, temp_files, temp_files_number, temp_files_index
    if new_color != previous_color_text:
        previous_color_text = new_color
        if current_resized_image_path:
            # Mettre à jour la file d'atente / Écraser suivants annulés
            temp_files = [file for idx, file in enumerate(temp_files) if idx <= temp_files_index]
            # Mettre à jour les variables temp_files_number et temp_files_index
            temp_files_number = len(temp_files) - 1
            temp_files_index = temp_files_number

            process_image_review(current_resized_image_path)

def check_color_label_update():
    new_color = color_label.cget("text")
    update_color_label(new_color)
    color_label.after(100, check_color_label_update)

def crop_image(image, crop_box):
    return image.crop(crop_box)

def on_crop_start(event):
    global crop_start_x, crop_start_y
    crop_start_x = event.x
    crop_start_y = event.y

def on_crop_end(event):
    global crop_start_x, crop_start_y, crop_end_x, crop_end_y, crop_rectangle, canvas
    crop_end_x = event.x
    crop_end_y = event.y

    if crop_rectangle:
        canvas.delete(crop_rectangle)

    crop_rectangle = canvas.create_rectangle(crop_start_x, crop_start_y, crop_end_x, crop_end_y, outline="red")

def on_crop_release(event):
    response = messagebox.askokcancel("Confirmation du recadrage", "Voulez recadrer l'image avec la sélection ?")
    if response:
        apply_crop()

def apply_crop():
    global crop_start_x, crop_start_y, crop_end_x, crop_end_y, current_image, current_resized_image_path, temp_files, temp_files_number, temp_files_index
    
    if crop_start_x and crop_start_y and crop_end_x and crop_end_y:
        crop_box = (crop_start_x, crop_start_y, crop_end_x, crop_end_y)
        cropped_image = crop_image(current_image, crop_box)
        
        # Sauvegarder l'image recadrée dans le répertoire temporaire
        with tempfile.NamedTemporaryFile(delete=False, dir=temp_dir, suffix=".png") as temp_file:
            cropped_image.save(temp_file, format="PNG")
            temp_file_path = temp_file.name

        # Mettre à jour la variable current_resized_image_path avec le chemin du fichier temporaire
        current_resized_image_path = temp_file_path

        # Appeler la fonction process_image_review avec le chemin de l'image recadrée
        if current_resized_image_path:
            # Mettre à jour la file d'atente / Écraser suivants annulés
            temp_files = [file for idx, file in enumerate(temp_files) if idx <= temp_files_index]
            # Mettre à jour les variables temp_files_number et temp_files_index
            temp_files_number = len(temp_files) - 1
            temp_files_index = temp_files_number

            process_image_review(current_resized_image_path)

# Restituer les paramètres pour l'état actuel
def restitute_state_infos():
    global previous_contrast, previous_luminosity, horizontal_flip_state, vertical_flip_state, previous_resize_option, previous_remove_bg_state, previous_color_text

    print(temp_files)
    try:
        current_info = temp_files[temp_files_index]

        # Restaure l'option de redimensionnement
        resize_option_var.set(current_info['resize'])
        resize_options.set(current_info['resize'])
        previous_resize_option = current_info['resize']

        # Restaure l'état de suppression de l'arrière-plan
        remove_bg_var.set(current_info['rembg'])
        previous_remove_bg_state = current_info['rembg']

        # Restaure la couleur de fond
        if current_info['bg']:
            color_label.configure(text=f"  {current_info['bg']}", fg_color=current_info['bg'])
            previous_color_text = current_info['bg']
            try:
                color_delete_button.destroy()
            except NameError:
                pass
            color_delete_button = ctk.CTkButton(palette_frame, text="X", width=5, command=delete_selected_color)
            color_delete_button.place(relx=0.9, rely=0.45)
        else:
            color_label.configure(text='', fg_color='transparent')
            previous_color_text = ''
            try:
                color_delete_button.destroy()
            except NameError:
                pass

        # Restaure la rotation
        degree_var.set(current_info['rotate'])
        degree_entry.configure(textvariable=degree_var)

        # Restaure l'état de l'effet 3D 
        effect_3d_var.set(current_info['effect3d'])
        effect_3d_state = current_info['effect3d']

        # Restaure l'état de flip vertical et horizontal
        vertical_flip_state = current_info['flipv']
        vertical_flip_var.set(vertical_flip_state)

        horizontal_flip_state = current_info['fliph']
        horizontal_flip_var.set(horizontal_flip_state)

        # Restaure la luminosité
        luminosity_slider.set(current_info['luminosity'])
        previous_luminosity = current_info['luminosity']

        # Restaure l'ombre
        contrast_slider.set(current_info['contrast'])
        previous_contrast = current_info['contrast']
    
    except KeyError as e:
        print(f"Erreur : clé manquante dans le dictionnaire - {e}")
    except IndexError as e:
        print(f"Erreur : index hors limites - {e}")
    except Exception as e:
        print(f"Erreur inattendue : {e}")

def previous_action():
    global temp_files, temp_files_number, temp_files_index, current_resized_image_path
    if temp_files_index >= 1:
        temp_files_index -= 1 # Utilise l'index précédent
        current_resized_image_path = temp_files[temp_files_index]['path']
        restitute_state_infos() # Réapplique les paramètres associés à cet état
        process_image_review(current_resized_image_path, prev=True)

def next_action():
    global temp_files, temp_files_number, temp_files_index, current_resized_image_path
    if temp_files_index <= temp_files_number - 1:
        temp_files_index += 1 # Utilise l'index suivant
        current_resized_image_path = temp_files[temp_files_index]['path']
        restitute_state_infos() # Réapplique les paramètres associés à cet état
        process_image_review(current_resized_image_path, next=True)
        
def create_image_frame_widgets(frame, image):
    global current_image, canvas, crop_rectangle
    
    # Redimensionner
    current_image = resize_image(image, 400, 400)

    # Supprimer l'ancien widget si présent
    for widget in frame.winfo_children():
        widget.destroy()

    # Créez et configurez le canvas pour l'image
    canvas = Canvas(frame, width=400, height=400)
    tk_image = ImageTk.PhotoImage(current_image)
    canvas.create_image(0, 0, anchor="nw", image=tk_image)
    canvas.image = tk_image  # Gardez une référence pour éviter que l'image soit supprimée
    canvas.place(x=10, y=40)  # Positionnez le canvas à gauche du frame
    canvas.bind("<ButtonPress-1>", on_crop_start)
    canvas.bind("<B1-Motion>", on_crop_end)
    canvas.bind("<ButtonRelease-1>", on_crop_release)
    
    crop_rectangle = None

    # Créez les boutons
    button_width = 90  # Largeur des boutons
    button_height = 30  # Hauteur des boutons
    button_font = ("Helvetica", 10)
    button_padx = 10    # Espacement horizontal entre les boutons
    button_pady = 10    # Espacement vertical entre les boutons

    save_button = ctk.CTkButton(frame, text="Enregistrer", width=button_width, height=button_height, font=button_font, command=save_image)
    save_all_button = ctk.CTkButton(frame, text="Enregistrer tout", width=button_width, height=button_height, font=button_font, command=save_all_images)
    cancel_button = ctk.CTkButton(frame, text="Annuler", width=button_width, height=button_height, font=button_font, command=cancel_action)
    cancel_all_button = ctk.CTkButton(frame, text="Annuler tout", width=button_width, height=button_height, font=button_font, command=cancel_all_actions)
    # Raccourci CTRL+ENTRÉE pour enregistrer
    app.bind('<Control-Shift-Return>', lambda event: save_image())
    # Raccourci CTRL+SHIFT+ENTRÉE pour enregistrer tout
    app.bind('<Control-Shift-a>', lambda event: save_all_images())
    # Raccourci Échap pour annuler
    app.bind('<Escape>', lambda event: cancel_action())
    # Raccourci F12 pour annuler tout
    app.bind('<Control-Escape>', lambda event: cancel_all_actions())

    crop_button = ctk.CTkButton(frame, text="Appliquer recadrage", width=button_width, height=button_height, font=button_font, command=apply_crop)

    # Positionnez les boutons en dessous de l'image
    canvas.update_idletasks()  # Assurez-vous que le canvas est mis à jour pour obtenir la hauteur correcte
    canvas_bottom_y = canvas.winfo_y() + canvas.winfo_height() + button_pady

    # Ajout d'instructions textuelles pour l'utilisateur
    instructions_frame = ctk.CTkFrame(frame, width=400, height=10)
    instructions_frame.place(relx=0.5, rely=0.03, anchor="center")
    instructions = ctk.CTkLabel(instructions_frame, text="Cliquez et faites glisser pour recadrer l'image", font=("Helvetica", 11, "italic"))
    instructions.pack(side="top")

    preview_frame = ctk.CTkFrame(frame, width=400, height=10)
    next_frame = ctk.CTkFrame(frame, width=400, height=10)
    preview_button = ctk.CTkButton(preview_frame, text="", image=icon_previous, fg_color="transparent", width=20, height=button_height, font=button_font, command=previous_action)
    next_button = ctk.CTkButton(next_frame, text="", image=icon_next, fg_color="transparent", width=20, height=button_height, font=button_font, command=next_action)
    if temp_files_number >= 1 :
        if temp_files_index >=1:
            preview_frame.place(relx=0.0, rely=0.03, anchor="w")
            preview_button.pack(side="left")
            # Raccourci CTRL+Z pour action précédente
            app.bind('<Control-z>', lambda event: previous_action())
        if temp_files_index < temp_files_number:
            next_frame.place(relx=1.0, rely=0.03, anchor="e")
            next_button.pack(side="right")
            # Raccourci CTRL+Y pour action suivante
            app.bind('<Control-y>', lambda event: next_action())

    save_button.place(x=10, y=canvas_bottom_y)
    save_all_button.place(x=10 + button_width + button_padx, y=canvas_bottom_y)
    cancel_button.place(x=10 + 2 * (button_width + button_padx), y=canvas_bottom_y)
    cancel_all_button.place(x=10 + 3 * (button_width + button_padx), y=canvas_bottom_y)
    crop_button.place(x=10 + 4 * (button_width + button_padx), y=canvas_bottom_y)

# Afficher images seulement
def create_image_frame_image(frame, image):
    # Redimentionner
    image = resize_image(image, 400, 400)

    # Créez et configurez le label pour l'image
    if image:
        ctk_image = ctk.CTkImage(light_image=image, dark_image=image, size=(400, 400))
        image_label = ctk.CTkLabel(frame, image=ctk_image, width=400, height=400, text="")
        image_label.image = ctk_image  # Gardez une référence pour éviter que l'image soit supprimée
        image_label.place(x=10, y=40)  # Positionnez le label à gauche du frame

    image_label.update_idletasks()

def destroy_image_frame_widgets(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def save_image():
    global save_image_action, next_process
    save_image_action.set(True)
    next_process.set(True)

def save_all_images():
    global save_all_images_action, next_process
    save_all_images_action.set(True)
    next_process.set(True)

def cancel_action():
    global cancel_action_action, next_process
    cancel_action_action.set(True)
    next_process.set(True)

def cancel_all_actions():
    global cancel_all_actions_action, next_process
    cancel_all_actions_action.set(True)
    next_process.set(True)

def initialize_vars():
    global cancel_all_actions_action, cancel_action_action, save_all_images_action, save_image_action, next_process
    save_image_action.set(False)
    save_all_images_action.set(False)
    cancel_all_actions_action.set(False)
    cancel_action_action.set(False)
    next_process.set(False)

# Vérifier si c'est une image
def is_image(file_path):
    try:
        with Image.open(file_path) as img:
            img.verify()  # Vérifie que le fichier est une image valide
        return True
    except (IOError, SyntaxError):
        return False

# Fonction pour parcourir et sélectionner les fichiers
def browse_files():
    files = filedialog.askopenfilenames(filetypes=filetypes)
    if files:
        # Nettoyer les chemins avant de les utiliser
        cleaned_files = [file.strip().strip('"') for file in files if is_image(file)]
        for file in cleaned_files:
            file_name = os.path.basename(file)
            file_size = os.path.getsize(file)
            tree.insert("", "end", values=(file_name, f"{file_size} bytes", file))

# Changer la chemin de sortie des images traitées
def browse_destination():
    folder_selected = filedialog.askdirectory()
    if folder_selected:
        destination_path.set(folder_selected)

# Vider le tableau 
def dump_table():
    if not current_process:
        # Supprime tous les éléments du tableau
        for item in tree.get_children():
            tree.delete(item)
        destroy_image_frame_widgets(image_frame) # Éffacer Prévisualisation

def clear_selected_item():
    selected_items = tree.selection()  # Obtenez tous les éléments sélectionnés
    if not current_process:
        if selected_items:
            for item in selected_items:
                tree.delete(item)  # Supprimez chaque élément sélectionné

            source_paths = get_file_paths_from_treeview()  # Obtenez les chemins de fichiers restants dans le tableau
            
            # Vérifiez si le tableau est vide
            if not source_paths:
                destroy_image_frame_widgets(image_frame)
        else:
            close_all_popups()
            messagebox.showinfo("Information", "Aucun élément sélectionné.")

def on_treeview_select(event):
    # Obtenez la sélection actuelle
    selected_item = event.widget.selection()
    if selected_item and not current_process:
        # Obtenez le chemin de l'image sélectionnée dans la troisième colonne
        selected_image_path = event.widget.item(selected_item[0], 'values')[2]
        
        # Ouvrir l'image sans redimensionner
        selected_image_path = os.path.normpath(selected_image_path)
        selected_image = Image.open(selected_image_path)

        # Convertir l'image à "RGBA" si ce n'est pas déjà le cas
        if selected_image.mode != "RGBA":
            selected_image = selected_image.convert("RGBA")

        # Corriger l'orientation de l'image
        selected_image = resize_image(selected_image, 400, 400)
        selected_image = correct_image_orientation(selected_image)

        # Afficher l'image dans le cadre sans la redimensionner
        create_image_frame_image(image_frame, selected_image)
    elif current_process:
        close_all_popups()
        #messagebox.showinfo("Traitement unique", "Double-cliquez pour traiter cette image")

def on_treeview_double_click(event):
    global process_one
    # Récupérer l'élément sélectionné
    selected_item = tree.selection()
    if selected_item:
        # Récupérer les valeurs des colonnes de l'élément sélectionné
        item_values = tree.item(selected_item, "values")
        if item_values:
            # Récupérer le lien dans la 3ème colonne (index 2)
            image_path = item_values[2]
            # Appeler la fonction process_image avec le lien récupéré
            process_one = image_path
            if not current_process:
                process_images()

# Ajouter les bindings pour les touches des flèches
def scroll_up(event):
    tree.yview_scroll(-1, 'units')

def scroll_down(event):
    tree.yview_scroll(1, 'units')

def scroll_left(event):
    tree.xview_scroll(-1, 'units')

def scroll_right(event):
    tree.xview_scroll(1, 'units')

# Convertir le format de couleur en RGB
def hex_to_rgb(hex_color):
    """ Convertit une couleur hexadécimale en RGB """
    hex_color = hex_color.lstrip("#")
    # Convertir les valeurs hexadécimales en tuples RGB
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

# Choisir une nouvelle couleur de fond
def choose_color():
    # Label pour afficher la couleur sélectionnée
    global color_delete_button
    color_code = colorchooser.askcolor(title="Choisissez une couleur de fond")
    if color_code[1]:  # Vérifie si une couleur a été choisie
        chosen_color = color_code[1]  # Obtenir la couleur au format hexadécimal
        color_label.configure(text=f"  {chosen_color}", fg_color=chosen_color)
        try:
            color_delete_button.destroy()
        except:
            pass
        color_delete_button = ctk.CTkButton(palette_frame, text="X", width=5, command=delete_selected_color)
        color_delete_button.place(relx=0.9, rely=0.45)
        return chosen_color

def delete_selected_color():
    # Réinitialiser le texte et rendre le fond transparent
    color_label.configure(text="", fg_color='transparent')
    color_delete_button.destroy()

# Fonction pour fermer toutes les fenêtres contextuelles
def close_all_popups():
    for widget in tk.Toplevel.winfo_children(app):
        if isinstance(widget, tk.Toplevel):
            widget.destroy()

# Function to load saved APIs
def load_saved_apis():
    if os.path.exists(saved_apis_file):
        with open(saved_apis_file, 'r') as file:
            try:
                return json.load(file)
            except json.JSONDecodeError:
                return {}
    return {}

# Function to save APIs to JSON
def save_apis(apis):
    with open(saved_apis_file, 'w') as file:
        json.dump(apis, file, indent=4)

# Function to save the chosen API
def save_chosen_api(api_key):
    with open(chosen_api_file, 'w') as file:
        json.dump({"api_key": api_key}, file, indent=4)
    global global_api_key
    global_api_key = api_key

# Function to load the chosen API
def load_chosen_api():
    if os.path.exists(chosen_api_file):
        with open(chosen_api_file, 'r') as file:
            try:
                data = json.load(file)
                if "api_key" in data:
                    global global_api_key
                    global_api_key = data["api_key"]
            except json.JSONDecodeError:
                pass

# Function to add a new API
def add_new_api(api_key):
    apis = load_saved_apis()
    if api_key not in apis:
        apis[api_key] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        save_apis(apis)
        save_chosen_api(api_key)
        close_all_popups()
        messagebox.showinfo("API ajoutée", "La nouvelle clé API a été ajoutée et sélectionnée.")
    else:
        close_all_popups()
        messagebox.showwarning("Clé API existante", "Cette clé API existe déjà dans le fichier.")

# Function to delete an API
def delete_api(api_key, api_frame, api_window):
    apis = load_saved_apis()
    confirm  = messagebox.askokcancel("Supprimer API", "Voulez-vous supprimer définitivement cette API ?")
    if confirm:
        if api_key in apis:
            del apis[api_key]
            save_apis(apis)
            if global_api_key == api_key:
                save_chosen_api(None)
            api_frame.destroy()
            api_window.update()

# Function to handle API selection and window closure
def handle_api_selection(api_key, api_window):
    save_chosen_api(api_key)
    api_window.destroy()
    if current_resized_image:
        process_images()

# Function to handle window close without API selection
def on_close(api_window):
    global remove_bg_api_activate
    remove_bg_api_activate.set(False)
    api_window.destroy()
    if current_resized_image:
        process_images()

def toggle_remove_bg_api_activation():
    global remove_bg_api_activate
    # Inverser l'état actuel de la case à cocher
    remove_bg_api_activate.set(not remove_bg_api_activate.get())
    # Appeler la fonction pour activer/désactiver l'API
    remove_bg_api_activation()


# Function to display API selection window
def remove_bg_api_activation():
    global remove_bg_api_activate
    if remove_bg_api_activate.get():
        apis = load_saved_apis()

        # Create a new top-level window
        api_window = tk.Toplevel()
        api_window.title("Activation de l'API de remove.bg")
        api_window.geometry("400x300")
        api_window.protocol("WM_DELETE_WINDOW", lambda: on_close(api_window))

        # Display message
        info_label = ctk.CTkLabel(api_window, text="Vous allez utiliser l'API de remove.bg pour supprimer les arrière-plans de vos images. \nremove.bg peut appliquer des frais pour l'utilisation de son API.\nVeuillez visiter le site remove.bg pour plus d'informations.", wraplength=380)
        info_label.pack(pady=10)

        # Create a frame for the API list with a scrollbar
        frame = tk.Frame(api_window)
        frame.pack(fill=tk.BOTH, expand=True, pady=10)

        canvas = tk.Canvas(frame, height=50)
        scrollbar = tk.Scrollbar(frame, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # List existing APIs
        if apis:
            for api_key, date in apis.items():
                api_frame = tk.Frame(scrollable_frame, borderwidth=1, relief="solid")
                api_frame.pack(fill="x", pady=5, padx=5)

                api_button = ctk.CTkButton(api_frame, text=f"API Key: {api_key}\nAdded on: {date}", command=lambda key=api_key: handle_api_selection(key, api_window))
                api_button.pack(side="left", padx=5)

                delete_button = ctk.CTkButton(api_frame, text="X", fg_color="red", width=5, command=lambda key=api_key, frame=api_frame: delete_api(key, frame, api_window))
                delete_button.pack(side="right", padx=5)
        else:
            no_api_label = ctk.CTkLabel(scrollable_frame, text="Aucune API enregistrée.")
            no_api_label.pack(pady=10, anchor="center")

        # Entry to add new API
        new_api_label = ctk.CTkLabel(api_window, text="Ajouter une nouvelle clé API:")
        new_api_label.pack(pady=10)

        new_api_entry = ctk.CTkEntry(api_window, width=300)
        new_api_entry.pack(pady=5)

        def on_add_api():
            new_api = new_api_entry.get()
            if new_api:
                add_new_api(new_api)
                api_window.destroy()
                remove_bg_api_activation()  # Re-open the window to reflect changes

        add_api_button = ctk.CTkButton(api_window, text="Ajouter API", command=on_add_api)
        add_api_button.pack(pady=10)

        api_window.mainloop()

# Fonction pour incrémenter le degré de rotation
def increment_degree():
    current_degree = int(degree_var.get())
    new_degree = current_degree + 15 if current_degree <= 330 else 0
    degree_var.set(new_degree)
    update_rotated_image(new_degree)

# Fonction pour décrémenter le degré de rotation
def decrement_degree():
    current_degree = int(degree_var.get())
    new_degree = current_degree - 15 if current_degree >= -330 else 0
    degree_var.set(new_degree)
    update_rotated_image(new_degree)

# Fonction pour mettre à jour l'image après rotation
def update_rotated_image(degree):
    global temp_files, temp_files_number, temp_files_index
    if current_resized_image_path:
        # Mettre à jour la file d'atente / Écraser suivants annulés
        temp_files = [file for idx, file in enumerate(temp_files) if idx <= temp_files_index]
        # Mettre à jour les variables temp_files_number et temp_files_index
        temp_files_number = len(temp_files) - 1
        temp_files_index = temp_files_number

        process_image_review(current_resized_image_path)

def update_luminosity(event):
    global previous_luminosity, temp_files, temp_files_number, temp_files_index
    current_luminosity = luminosity_slider.get()
    if current_luminosity != previous_luminosity:
        previous_luminosity = current_luminosity
        if current_resized_image_path:
            # Mettre à jour la file d'atente / Écraser suivants annulés
            temp_files = [file for idx, file in enumerate(temp_files) if idx <= temp_files_index]
            # Mettre à jour les variables temp_files_number et temp_files_index
            temp_files_number = len(temp_files) - 1
            temp_files_index = temp_files_number

            process_image_review(current_resized_image_path)            

def update_contrast(event):
    global previous_contrast, temp_files, temp_files_number, temp_files_index
    current_contrast = contrast_slider.get()
    if current_contrast != previous_contrast:
        previous_contrast = current_contrast
        if current_resized_image_path:
            # Mettre à jour la file d'atente / Écraser suivants annulés
            temp_files = [file for idx, file in enumerate(temp_files) if idx <= temp_files_index]
            # Mettre à jour les variables temp_files_number et temp_files_index
            temp_files_number = len(temp_files) - 1
            temp_files_index = temp_files_number

            process_image_review(current_resized_image_path)            

def increase_luminosity(event=None):
    # Augmenter la luminosité
    current_value = luminosity_slider.get()
    luminosity_slider.set(min(current_value + 1, luminosity_slider.cget('to')))
    update_luminosity(event=True)

def decrease_luminosity(event=None):
    # Diminuer la luminosité
    current_value = luminosity_slider.get()
    luminosity_slider.set(max(current_value - 1, luminosity_slider.cget('from')))
    update_luminosity(event=True)

def increase_contrast(event=None):
    # Augmenter l'ombre
    current_value = contrast_slider.get()
    contrast_slider.set(min(current_value + 1, contrast_slider.cget('to')))
    update_contrast(event=True)

def decrease_contrast(event=None):
    # Diminuer l'ombre
    current_value = contrast_slider.get()
    contrast_slider.set(max(current_value - 1, contrast_slider.cget('from')))
    update_contrast(event=True)

# Fonction pour mettre à jour l'effet 3D
def update_3d_effect():
    global effect_3d_state, temp_files, temp_files_number, temp_files_index
    effect_3d_state = not effect_3d_state  # Inverser l'état de flip vertical
    if current_resized_image_path:
        # Mettre à jour la file d'atente / Écraser suivants annulés
        temp_files = [file for idx, file in enumerate(temp_files) if idx <= temp_files_index]
        # Mettre à jour les variables temp_files_number et temp_files_index
        temp_files_number = len(temp_files) - 1
        temp_files_index = temp_files_number

        process_image_review(current_resized_image_path)

def toggle_3d_effect():
    # Inverser l'état de la case à cocher pour l'effet 3D
    effect_3d_var.set(not effect_3d_var.get())
    update_3d_effect()

# Fonction pour mettre à jour le flip vertical
def update_vertical_flip():
    global vertical_flip_state, temp_files, temp_files_number, temp_files_index
    vertical_flip_state = not vertical_flip_state  # Inverser l'état de flip vertical
    if current_resized_image_path:
        # Mettre à jour la file d'atente / Écraser suivants annulés
        temp_files = [file for idx, file in enumerate(temp_files) if idx <= temp_files_index]
        # Mettre à jour les variables temp_files_number et temp_files_index
        temp_files_number = len(temp_files) - 1
        temp_files_index = temp_files_number

        process_image_review(current_resized_image_path)

def toggle_vertical_flip():
    # Inverser l'état de la case à cocher pour le retournement vertical
    vertical_flip_var.set(not vertical_flip_var.get())
    update_vertical_flip()

# Fonction pour mettre à jour l'image après flip horizontal
def update_horizontal_flip():
    global horizontal_flip_state, temp_files, temp_files_number, temp_files_index
    horizontal_flip_state = not horizontal_flip_state  # Inverser l'état de flip horizontal
    if current_resized_image_path:
        # Mettre à jour la file d'atente / Écraser suivants annulés
        temp_files = [file for idx, file in enumerate(temp_files) if idx <= temp_files_index]
        # Mettre à jour les variables temp_files_number et temp_files_index
        temp_files_number = len(temp_files) - 1
        temp_files_index = temp_files_number

        process_image_review(current_resized_image_path)

def toggle_horizontal_flip():
    # Inverser l'état de la case à cocher pour le retournement horizontal
    horizontal_flip_var.set(not horizontal_flip_var.get())
    update_horizontal_flip()

# Initialisation de customtkinter avec le mode d'apparence système
ctk.set_appearance_mode("System")  # Mode d'apparence du système d'exploitation
ctk.set_default_color_theme("blue")  # Choisissez un thème, par exemple "blue"

app = ctk.CTk()  # create CTk window like you do with the Tk window
app.title("IMAGES FAST-EDIT")
app.geometry("1200x600")
#app.resizable(False, False)

# Variables globales pour stocker les valeurs précédentes
save_image_action = tk.BooleanVar(value=False)
save_all_images_action = tk.BooleanVar(value=False)
cancel_action_action = tk.BooleanVar(value=False)
cancel_all_actions_action = tk.BooleanVar(value=False)  # Utilisez un nom distinct
next_process = tk.BooleanVar(value=False) 
current_resized_image = None  # Pour stocker l'image actuelle à sauvegarder
current_resized_image_path = None
current_process = False
previous_resize_option = None
previous_remove_bg_state = None
previous_color_text = None
effect_3d_state = False 
vertical_flip_state = False     # Tournée Vertical ou Non
horizontal_flip_state = False   # Tournée Horizontal ou Non
previous_luminosity = None
previous_contrast = None
reprocess_images = None
processed_images = []
process_one = None
threads = 0 # Nombre de tâches en cours
# Variables globales pour le recadrer
current_image = None
crop_start_x = None
crop_start_y = None
crop_end_x = None
crop_end_y = None
crop_rectangle = None
temp_files = []
temp_files_number = 0
temp_files_index = 0

# Préparation des icônes
icon_crop = create_icon(img_crop_path)
icon_flipv = create_icon(img_flipv_path)
icon_fliph = create_icon(img_fliph_path)
icon_rotate_plus = create_icon(img_rotate_plus_path)
icon_rotate_moins = create_icon(img_rotate_moins_path)
icon_browse = create_icon(img_browse_path)
icon_delete = create_icon(img_delete_path)
icon_dump = create_icon(img_dump_path)
icon_previous = create_icon(img_previous_path)
icon_next = create_icon(img_next_path)
icon_start = create_icon(img_start_path)

# Ruban blanc en haut
header = ctk.CTkFrame(app, height=50, corner_radius=0)
header.pack(fill="x")
header_label = ctk.CTkLabel(header, text="FAST-EDIT (IMAGES)", font=("Helvetica", 16, "bold"))
header_label.pack(pady=10)

# Sous-titre descriptif
subtitle_label = ctk.CTkLabel(header, text="Traitez vos images facilement et rapidement !", font=("Helvetica", 12, "italic"))
subtitle_label.pack()

# Ajouter le bouton d'aide
help_button = ctk.CTkButton(app, text="?", fg_color="blue", text_color="white", border_width=1, border_color="white", font=("Helvetica", 12, "bold"), width=5, command=show_help)
help_button.place(relx=1.0, rely=0.0, anchor="ne", x=-10, y=10)
# Ajouter le binding pour F1
app.bind('<F1>', lambda event: show_help())

# Bouton de basculement de l'apparence
appearance_button = ctk.CTkButton(app, text="Dark", width=10, border_width=1, fg_color="white", text_color="black", border_color="white", command=toggle_appearance)
appearance_button.place(relx=0.97, rely=0.0, anchor="ne", x=-10, y=10)
app.bind('<F2>', lambda event: toggle_appearance())

# Cadre pour déposer les images ou dossiers
frame = ctk.CTkFrame(app, width=800, height=280, corner_radius=10, border_width=1)
frame.place(relx=0.0, rely=0.38, anchor="w")

# Variables de chemin de dossier ou fichier
folder_path = tk.StringVar()
downloads_folder = str(Path.home() / "Downloads" / "fastEditOutput")
destination_path = tk.StringVar(value=downloads_folder)

browse_button_frame = ctk.CTkFrame(frame, fg_color="transparent")
browse_button_frame.place(relx=0.0, rely=0.05, anchor='w')
# Bouton pour choisir des images
browse_button_files = ctk.CTkButton(browse_button_frame, image=icon_browse, text="Choisir des images", command=browse_files)
browse_button_files.pack(side="left", padx=5)
app.bind("<Control-n>", lambda event: browse_files())

clear_button_frame = ctk.CTkFrame(frame, fg_color="transparent")
clear_button_frame.place(relx=1.0, rely=0.05, anchor='e')
# Bouton pour effacer
clear_button = ctk.CTkButton(clear_button_frame, image=icon_delete, text="Effacer", command=clear_selected_item)
clear_button.pack(side="left", padx=5)
# Ajouter le raccourci clavier CTRL+X pour effacer
app.bind('<Control-x>', lambda event: clear_selected_item())

# Bouton pour vider le tableau
clear_all_button = ctk.CTkButton(clear_button_frame, image=icon_dump, text="Vider le tableau", command=dump_table)
clear_all_button.pack(side="left", padx=5)
# Ajouter le binding pour CTRL+C
app.bind('<Control-c>', lambda event: dump_table())

# Tableau Treeview
tree = ttk.Treeview(frame, columns=("col1", "col2", "col3"), show='headings')
tree.heading("col1", text="Nom du fichier")
tree.heading("col2", text="Taille")
tree.heading("col3", text="Chemin")
tree.column("col1", width=200)
tree.column("col2", width=100)
tree.column("col3", width=500)
tree.place(x=10, y=30, width=780, height=230)

# Configuration des barres de défilement
scrollbar_x = tk.Scrollbar(frame, orient='horizontal', command=tree.xview)
scrollbar_y = tk.Scrollbar(frame, orient='vertical', command=tree.yview)
tree.configure(xscrollcommand=scrollbar_x.set, yscrollcommand=scrollbar_y.set)

scrollbar_x.place(x=10, y=260, width=780)
scrollbar_y.place(x=790, y=30, height=230)

# Binding des touches flèche
app.bind('<Up>', scroll_up)
app.bind('<Down>', scroll_down)
app.bind('<Left>', scroll_left)
app.bind('<Right>', scroll_right)

# Ajouter le gestionnaire d'événements à votre tableau (treeview)
tree.bind("<Double-1>", on_treeview_double_click)
tree.bind('<<TreeviewSelect>>', on_treeview_select)

# Cadre les commandes de manipulation des images
palette_frame = ctk.CTkFrame(app, width=380, height=170, corner_radius=5, border_width=1)
palette_frame.place(relx=0.010, rely=0.76, anchor="w")

# Liste déroulante des options de redimensionnement
resize_option_values = ["640x480", "800x600", "800x800", "1024x768", "1280x800", "1280x720", "1366x768", "1600x900", 
                   "1920x1080", "300x250", "400x300", "600x400", "1200x628", "728x90", "300x600", "3840x2160", "150x150"]

resize_options_label = ctk.CTkLabel(palette_frame, text="Résolution")
resize_options_label.place(relx=0.0, rely=0.0)
resize_option_var = tk.StringVar(value="800x800")
resize_option_var.trace("w", on_resize_option_change)
resize_options = ctk.CTkComboBox(palette_frame, width=180, values=resize_option_values, variable=resize_option_var)
resize_options.set("800x800")
resize_options.place(relx=0.5, rely=0.0)
resize_options.configure(state='readonly')
# Lier Ctrl+Flèche Haut et Ctrl+Flèche Bas pour changer les options
app.bind('<Control-Up>', select_previous_option)
app.bind('<Control-Down>', select_next_option)

# Boîte à cocher pour supprimer l'arrière-plan
remove_bg_var = tk.BooleanVar()
remove_bg_checkbox = ctk.CTkCheckBox(palette_frame, text="Supprimer l'arrière-plan de(s) image(s)        ", border_color="white", variable=remove_bg_var, command=on_remove_bg_change)
remove_bg_checkbox.place(relx=0.0, rely=0.25)
# Ajouter le binding pour CTRL+D
app.bind('<Control-b>', toggle_remove_bg_checkbox)

# Bouton pour appliquer une couleur fond
add_bg_button = ctk.CTkButton(palette_frame, text="Nouvelle arrière-plan", command=choose_color, width=200)
add_bg_button.place(relx=0.0, rely=0.45)

# Label pour afficher la couleur sélectionnée
color_label = ctk.CTkLabel(palette_frame, text="", width=150)
color_label.place(relx=0.5, rely=0.45)
# Start checking for updates
color_label.after(100, check_color_label_update)

# Ajouter le binding pour CTRL+G
app.bind('<Control-g>', lambda event: choose_color())

# Bouton pour commencer le traitement
start_button = ctk.CTkButton(palette_frame, image=icon_start, text="Commencer le traitement", width=350, command=process_images)
start_button.place(relx=0.5, rely=0.82, anchor=ctk.CENTER)
# Fonction pour commencer le traitement
def start_processing(event=None):
    if not current_process:
        process_images()  # Appeler la fonction pour commencer le traitement

# Ajouter le binding pour CTRL+A
app.bind('<Control-Return>', start_processing)

# Fonction pour lancer un traitement unique de l'élément sélectionné
def process_selected_item(event=None):
    on_treeview_double_click(None)  # Appeler la fonction existante pour lancer le traitement

# Ajouter le binding pour la touche ENTRÉE
app.bind('<Return>', process_selected_item)

# Frame pour tourner et faire des rotations
flip_rotate_frame = ctk.CTkFrame(app, width=400, height=170, corner_radius=10, border_width=1)
flip_rotate_frame.place(relx=0.33, rely=0.755, anchor="w")

# Initialisation de la variable pour le degré
degree_var = tk.IntVar()
degree_var.set(0)

# Créer les widgets pour la rotation
degree_frame = ctk.CTkFrame(flip_rotate_frame)
degree_frame.pack(pady=10, anchor="w")

degree_label = ctk.CTkLabel(degree_frame, text="Rotation : ")
degree_label.pack(side="left", padx=5)

decrement_button = ctk.CTkButton(degree_frame, image=icon_rotate_moins, text='', fg_color="transparent", bg_color="transparent", width=5, command=decrement_degree)
decrement_button.pack(side="left", padx=5)

degree_entry = ctk.CTkEntry(degree_frame, textvariable=degree_var, width=50, state="readonly")
degree_entry.pack(side="left", padx=5)

increment_button = ctk.CTkButton(degree_frame, image=icon_rotate_plus, text='', fg_color="transparent", bg_color="transparent", width=5, command=increment_degree)
increment_button.pack(side="left", padx=5)

# Ajouter le binding pour CTRL+U (diminuer la rotation)
app.bind('<Control-u>', lambda event: decrement_degree())
# Ajouter le binding pour CTRL+I (augmenter la rotation)
app.bind('<Control-i>', lambda event: increment_degree())

effect_3d_var = tk.BooleanVar()
# Activer effet 3d
effect_3d_checkbox = ctk.CTkCheckBox(degree_frame, text="Effet 3D", variable=effect_3d_var, command=update_3d_effect)
effect_3d_checkbox.pack(side="left", padx=25)
app.bind('<Control-e>', lambda event: toggle_3d_effect())

# Initialisation des variables pour flip vertical et horizontal
vertical_flip_var = tk.BooleanVar()
horizontal_flip_var = tk.BooleanVar()

# Frame pour le flip vertical et horizontal
flip_frame = ctk.CTkFrame(flip_rotate_frame)
flip_frame.pack(pady=10, anchor="w")

flip_label = ctk.CTkLabel(flip_frame, text="Retournement : ")
flip_label.pack(side="left", padx=5)

vertical_flip_label = ctk.CTkLabel(flip_frame, fg_color="transparent", bg_color="transparent", image=icon_flipv, text="", width=20)
vertical_flip_label.pack(side="left", padx=5)
vertical_flip_checkbox = ctk.CTkCheckBox(flip_frame, text="Verticale", variable=vertical_flip_var, command=update_vertical_flip)
vertical_flip_checkbox.pack(side="left", padx=5)

horizontal_flip_label = ctk.CTkLabel(flip_frame, fg_color="transparent", bg_color="transparent", image=icon_fliph, text="", width=20)
horizontal_flip_label.pack(side="left", padx=5)
horizontal_flip_checkbox = ctk.CTkCheckBox(flip_frame, text="Horizontale", variable=horizontal_flip_var, command=update_horizontal_flip)
horizontal_flip_checkbox.pack(side="left", padx=5)

# Ajouter le binding pour CTRL+O (activer/désactiver le retournement vertical)
app.bind('<Control-o>', lambda event: toggle_vertical_flip())
# Ajouter le binding pour CTRL+P (activer/désactiver le retournement horizontal)
app.bind('<Control-p>', lambda event: toggle_horizontal_flip())

# Luminosité et Ombre
luminosity_contrast_frame = ctk.CTkFrame(flip_rotate_frame, height=15)
luminosity_contrast_frame.pack(pady=5, anchor="w")

luminosity_label = ctk.CTkLabel(luminosity_contrast_frame, text="Luminosité : ")
luminosity_label.pack(side="left", padx=5)
luminosity_slider = tk.Scale(luminosity_contrast_frame, from_=-5, to=5,tickinterval=1, orient="horizontal", command=update_luminosity)
luminosity_slider.set(0)
luminosity_slider.pack(side="left", padx=5)

contrast_label = ctk.CTkLabel(luminosity_contrast_frame, text="Contraste : ")
contrast_label.pack(side="left", padx=5)
contrast_slider = tk.Scale(luminosity_contrast_frame, from_=0, to=4,tickinterval=1, orient="horizontal", command=update_contrast)
contrast_slider.set(0)
contrast_slider.pack(side="left", padx=5)

# Ajouter le binding pour CTRL+J (augmenter la luminosité)
app.bind('<Control-j>', increase_luminosity)
# Ajouter le binding pour CTRL+H (diminuer la luminosité)
app.bind('<Control-h>', decrease_luminosity)
# Ajouter le binding pour CTRL+K (augmenter l'ombre)
app.bind('<Control-l>', increase_contrast)
# Ajouter le binding pour CTRL+L (diminuer l'ombre)
app.bind('<Control-k>', decrease_contrast)

# Cadre pour la prévisualisation des images
image_frame = ctk.CTkFrame(app, width=400, height=550, corner_radius=5, border_width=1)
image_frame.place(relx=1.0, rely=0.60, anchor="e")

# Destination path and button
destination_frame = ctk.CTkFrame(app)
destination_frame.place(relx=0.0, rely=0.97, anchor="sw", y=-10, x=10)
destination_label = ctk.CTkLabel(destination_frame, text="Destination:", font=("Helvetica", 16))
destination_label.pack(side="left")
destination_entry = ctk.CTkEntry(destination_frame, textvariable=destination_path, width=350)
destination_entry.pack(side="left")
destination_button = ctk.CTkButton(destination_frame, text="Changer", command=browse_destination, width=15)
destination_button.pack(side="left", padx=5)
app.bind('<Control-d>', lambda event: browse_destination())

# Activer l'API remove.bg
remove_bg_activate_api_frame = ctk.CTkFrame(app, fg_color="transparent")
remove_bg_activate_api_frame.place(relx=0.65, rely=0.95, anchor="se")

remove_bg_api_activate = tk.BooleanVar()  # Définir la variable associée à la case à cocher

remove_bg_api_activate_checkbox = ctk.CTkCheckBox(remove_bg_activate_api_frame, text="Activer l'API remove.bg  ", variable=remove_bg_api_activate, command=remove_bg_api_activation)
remove_bg_api_activate_checkbox.pack(side="right")
# Raccourci F10 pour cocher/décocher et activer l'API
app.bind('<F10>', lambda event: toggle_remove_bg_api_activation())

# Créer le footer
footer = ctk.CTkFrame(app, height=40, corner_radius=0)
footer.pack(side="bottom", fill="x")

# Afficher les informations du développeur
footer_text = (
    f"Copyright © {developer['name']} |  "
    f"{developer['email']}"
)

footer_label = ctk.CTkLabel(footer, text=footer_text, font=("Helvetica", 10))
footer_label.pack(side="right", padx=10)

app.iconphoto(False, tk.PhotoImage(file=icon_path))

load_chosen_api()  # Load the chosen API at startup

# Boucle principale de l'application
app.mainloop()
