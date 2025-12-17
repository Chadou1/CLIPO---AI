# Emplacement de la Bibliothèque de Fichiers

## 📂 Structure Recommandée  

La bibliothèque de fichiers doit être placée dans :

```
D:\SITES\clipgenius\clipo-bibliothèque\
```

## 📁 Organisation des Dossiers

### 1. **Vidéos de la Bibliothèque**
Créez un dossier pour chaque bibliothèque de vidéos. Actuellement, la bibliothèque "Keo" est configurée :

```
D:\SITES\clipgenius\clipo-bibliothèque\Keo\
```

**Formats supportés :** `.mp4`, `.mov`, `.avi`, `.mkv`

Vous avez déjà **115 fichiers vidéo** dans ce dossier.

---

### 2. **Polices (Fonts)**
Placez vos fichiers de polices TrueType/OpenType ici :

```
D:\SITES\clipgenius\clipo-bibliothèque\Fonts\
```

**Polices requises :**
1. `FUTRFW.TTF`
2. `HelveticaNeueCondensedBold.ttf`
3. `Luxerie Display.otf`
4. `Luxerie.ttf`
5. `space age.ttf`

---

### 3. **Musiques**
Placez vos fichiers audio pour la synchronisation musicale ici :

```
D:\SITES\clipgenius\clipo-bibliothèque\Werenoi_Musiques\
```

**Formats supportés :** `.mp3`, `.wav`, `.m4a`, etc.

Le système utilisera ces fichiers pour :
- Détection automatique des beats
- Synchronisation des transitions vidéo avec la musique
- Sélection aléatoire d'une musique pour chaque génération

---

### 4. **Vidéos Générées**
Les clips générés depuis la bibliothèque sont sauvegardés dans :

```
D:\SITES\clipgenius\backend\storage\library_output\
```

Ce dossier est créé automatiquement par le service.

---

## 🎯 Ajouter une Nouvelle Bibliothèque

Pour ajouter une nouvelle bibliothèque de vidéos (ex: "ThemeB") :

1. **Créez le dossier :**
   ```
   D:\SITES\clipgenius\clipo-bibliothèque\ThemeB\
   ```

2. **Ajoutez vos fichiers vidéo** dans ce dossier

3. **Mettez à jour le code backend :**
   
   Éditez `D:\SITES\clipgenius\backend\api\library.py` ligne 16 :
   ```python
   AVAILABLE_LIBRARIES = ["Keo", "ThemeB"]  # Ajoutez votre bibliothèque
   ```

4. **Redémarrez le service library** pour appliquer les changements

---

## ✅ Vérification

Pour vérifier que tout est correct :

1. **Bibliothèque Keo :** ✅ Déjà présente avec 115 vidéos
2. **Dossier Fonts :** ✅ Créé (à remplir avec les polices)
3. **Dossier Werenoi_Musiques :** ✅ Créé (à remplir avec de la musique)
4. **Dossier library_output :** ✅ Sera créé automatiquement

---

## 📊 Résumé de l'Emplacement

| Type de Fichier | Emplacement | Status |
|----------------|-------------|---------|
| **Vidéos (Keo)** | `clipo-bibliothèque\Keo\` | ✅ 115 fichiers |
| **Polices** | `clipo-bibliothèque\Fonts\` | ⚠️ À remplir |
| **Musiques** | `clipo-bibliothèque\Werenoi_Musiques\` | ⚠️ À remplir |
| **Sortie** | `backend\storage\library_output\` | ✅ Auto |

---

## 🚨 Important

> [!WARNING]
> Sans polices dans le dossier `Fonts\`, la génération de vidéos échouera car le module ne pourra pas créer le texte overlay.

> [!WARNING]
> Sans musique dans le dossier `Werenoi_Musiques\`, la génération échouera lors de la synchronisation audio.

**Assurez-vous d'ajouter au moins 1 fichier de police et 1 fichier audio avant de tester la génération !**
