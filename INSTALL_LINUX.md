# Installation sur Linux - Section Archives

## Problème : "No module named exceptions"

Ce problème survient généralement avec les bibliothèques de génération de documents (reportlab, python-docx) sur Linux.

## Solution

### 1. Installer les dépendances système

#### Sur Ubuntu/Debian :
```bash
sudo apt-get update
sudo apt-get install -y python3-dev python3-pip
sudo apt-get install -y libxml2-dev libxslt1-dev
sudo apt-get install -y libjpeg-dev zlib1g-dev libfreetype6-dev
sudo apt-get install -y build-essential
```

#### Sur CentOS/RHEL/Fedora :
```bash
sudo yum install -y python3-devel python3-pip
sudo yum install -y libxml2-devel libxslt-devel
sudo yum install -y libjpeg-devel zlib-devel freetype-devel
sudo yum groupinstall -y "Development Tools"
```

#### Sur Arch Linux :
```bash
sudo pacman -S python-pip base-devel
sudo pacman -S libxml2 libxslt
sudo pacman -S libjpeg-turbo zlib freetype2
```

### 2. Installer les dépendances Python

```bash
# Mise à jour de pip
pip3 install --upgrade pip setuptools wheel

# Installation des dépendances
pip3 install -r requirements.txt
```

### 3. Si le problème persiste

Si vous avez toujours l'erreur "no module named exceptions", essayez :

```bash
# Désinstaller et réinstaller reportlab
pip3 uninstall reportlab -y
pip3 install reportlab==4.0.7

# Ou essayer une version plus récente
pip3 install reportlab --upgrade
```

### 4. Alternative : Installation sans reportlab

Si reportlab pose toujours problème, vous pouvez désactiver temporairement les exports PDF en commentant les imports dans `/modules/archives.py` :

```python
# Commentez ces lignes (lignes 14-18) :
# from reportlab.lib.pagesizes import letter, A4
# from reportlab.lib import colors
# from reportlab.lib.units import inch
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
```

Et commentez la fonction `export_pdf()` (lignes ~380-450).

**Note** : Les exports Excel et DOCX continueront de fonctionner.

## Vérification de l'installation

Testez que tout fonctionne :

```bash
python3 -c "import openpyxl; print('✓ openpyxl OK')"
python3 -c "import reportlab; print('✓ reportlab OK')"
python3 -c "import docx; print('✓ python-docx OK')"
python3 -c "from app import app; print('✓ Application OK')"
```

## Installation complète (script automatique)

Créez un fichier `install_linux.sh` :

```bash
#!/bin/bash

echo "Installation des dépendances système..."
if [ -f /etc/debian_version ]; then
    # Debian/Ubuntu
    sudo apt-get update
    sudo apt-get install -y python3-dev python3-pip libxml2-dev libxslt1-dev libjpeg-dev zlib1g-dev libfreetype6-dev build-essential
elif [ -f /etc/redhat-release ]; then
    # CentOS/RHEL/Fedora
    sudo yum install -y python3-devel python3-pip libxml2-devel libxslt-devel libjpeg-devel zlib-devel freetype-devel
    sudo yum groupinstall -y "Development Tools"
elif [ -f /etc/arch-release ]; then
    # Arch Linux
    sudo pacman -S --noconfirm python-pip base-devel libxml2 libxslt libjpeg-turbo zlib freetype2
fi

echo "Mise à jour de pip..."
pip3 install --upgrade pip setuptools wheel

echo "Installation des dépendances Python..."
pip3 install -r requirements.txt

echo "Vérification de l'installation..."
python3 -c "import openpyxl; print('✓ openpyxl OK')"
python3 -c "import reportlab; print('✓ reportlab OK')"
python3 -c "import docx; print('✓ python-docx OK')"

echo "Installation terminée !"
```

Rendez-le exécutable et lancez-le :

```bash
chmod +x install_linux.sh
./install_linux.sh
```

## Problèmes courants et solutions

### Erreur : "command 'gcc' failed"
**Solution** : Installez les outils de compilation
```bash
sudo apt-get install build-essential  # Ubuntu/Debian
sudo yum groupinstall "Development Tools"  # CentOS/RHEL
```

### Erreur : "Python.h: No such file or directory"
**Solution** : Installez python3-dev
```bash
sudo apt-get install python3-dev  # Ubuntu/Debian
sudo yum install python3-devel  # CentOS/RHEL
```

### Erreur : "libxml/xmlversion.h: No such file"
**Solution** : Installez libxml2-dev
```bash
sudo apt-get install libxml2-dev libxslt1-dev  # Ubuntu/Debian
sudo yum install libxml2-devel libxslt-devel  # CentOS/RHEL
```

### Erreur : "jpeg.h: No such file"
**Solution** : Installez libjpeg-dev
```bash
sudo apt-get install libjpeg-dev  # Ubuntu/Debian
sudo yum install libjpeg-devel  # CentOS/RHEL
```

## Environnement virtuel (recommandé)

Pour éviter les conflits, utilisez un environnement virtuel :

```bash
# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer l'application
python app.py
```

## Support

Si le problème persiste après avoir suivi ces étapes :

1. Vérifiez votre version de Python : `python3 --version` (minimum 3.7)
2. Vérifiez les logs d'erreur complets
3. Essayez d'installer les packages un par un pour identifier le problème
4. Consultez les issues GitHub des bibliothèques concernées

## Contact

Pour toute assistance : support@epsjl.ht
