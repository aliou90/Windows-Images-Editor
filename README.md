# Windows Image Editor

*(CustomTkinter Edition — Background Removal & Image Enhancer)*

Application Python permettant d'éditer facilement des images : suppression d’arrière-plan (rembg), filtres, rotation, ajustements, zoom, et export.
Interface **CustomTkinter moderne**, fluide et responsive.

---

## 🚀 Fonctionnalités principales

* 🎯 **Suppression d'arrière-plan (rembg)** en un clic
* ✂️ **Recadrage, rotation, redimensionnement**
* 🎨 **Ajustements intelligents** : luminosité, contraste, netteté
* 🔍 **Prévisualisation instantanée**
* 🖼️ Support complet : **PNG / JPG / WebP**
* 💾 Sauvegarde rapide & traitement par lot
* 🧰 Outils d’amélioration basés sur **OpenCV** et **Pillow**

---

## 🧩 Technologies utilisées

* Python 3
* CustomTkinter
* PIL / Pillow
* rembg
* OpenCV
* NumPy

---

## 📁 Structure du projet

```
main.py
config/
assets/
  └── screenshots/
      ├── screenshot1.png
      └── screenshot2.png
requirements.txt
README.md
```

---

## 📸 Captures d'écran

![Screenshot](assets/screenshots/screenshot1.png)

---

## ▶️ Lancer l'application

Assurez-vous d’avoir créé le `.venv` :

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Ensuite :

```bash
python3 main.py
```

---

## 📦 Dépendances principales

```
numpy
opencv-python-headless
Pillow
rembg
customtkinter
requests
python-dotenv
```

---

## 📜 Licence

Libre d’utilisation pour projets personnels ou professionnels.

---

