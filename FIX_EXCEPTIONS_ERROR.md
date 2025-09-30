# Fix: "No module named exceptions" sur Linux

## 🔴 Problème

Vous obtenez l'erreur suivante lors du démarrage de l'application :
```
ModuleNotFoundError: No module named 'exceptions'
```

## 🎯 Cause

Cette erreur est généralement causée par :
1. Des dépendances système manquantes pour `reportlab` ou `lxml`
2. Une version incompatible de Python
3. Des bibliothèques C manquantes

## ✅ Solution rapide (3 étapes)

### Étape 1 : Installer les dépendances système

**Sur Ubuntu/Debian :**
```bash
sudo apt-get update
sudo apt-get install -y python3-dev libxml2-dev libxslt1-dev build-essential
```

**Sur CentOS/RHEL/Fedora :**
```bash
sudo yum install -y python3-devel libxml2-devel libxslt-devel gcc gcc-c++ make
```

### Étape 2 : Réinstaller les packages Python

```bash
pip3 uninstall reportlab lxml -y
pip3 install --upgrade pip
pip3 install reportlab lxml
```

### Étape 3 : Vérifier l'installation

```bash
python3 -c "import reportlab; print('✓ reportlab OK')"
python3 -c "import lxml; print('✓ lxml OK')"
```

## 🚀 Solution automatique (recommandée)

Utilisez le script d'installation automatique :

```bash
chmod +x install_linux.sh
./install_linux.sh
```

## 🔧 Solutions alternatives

### Option 1 : Utiliser un environnement virtuel

```bash
# Créer un environnement virtuel
python3 -m venv venv

# Activer l'environnement
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Tester
python app.py
```

### Option 2 : Désactiver temporairement les exports PDF

Si le problème persiste, vous pouvez désactiver les exports PDF :

1. Ouvrez `/modules/archives.py`
2. Commentez les lignes 14-18 (imports reportlab) :

```python
# from reportlab.lib.pagesizes import letter, A4
# from reportlab.lib import colors
# from reportlab.lib.units import inch
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
# from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
```

3. Commentez la fonction `export_pdf()` (lignes ~380-450)

**Note** : Les exports Excel et DOCX continueront de fonctionner.

### Option 3 : Installer depuis les sources

```bash
# Installer reportlab depuis les sources
pip3 install --no-binary :all: reportlab

# Ou essayer une version spécifique
pip3 install reportlab==3.6.13
```

## 📋 Vérification complète

Testez tous les modules :

```bash
python3 << EOF
try:
    import flask
    print("✓ Flask OK")
except ImportError as e:
    print(f"✗ Flask: {e}")

try:
    import openpyxl
    print("✓ openpyxl OK")
except ImportError as e:
    print(f"✗ openpyxl: {e}")

try:
    import reportlab
    print("✓ reportlab OK")
except ImportError as e:
    print(f"✗ reportlab: {e}")

try:
    import docx
    print("✓ python-docx OK")
except ImportError as e:
    print(f"✗ python-docx: {e}")

try:
    import lxml
    print("✓ lxml OK")
except ImportError as e:
    print(f"✗ lxml: {e}")

try:
    from app import app
    print("✓ Application OK")
except ImportError as e:
    print(f"✗ Application: {e}")
EOF
```

## 🐛 Debugging avancé

Si le problème persiste, obtenez plus d'informations :

```bash
# Vérifier la version de Python
python3 --version

# Vérifier les packages installés
pip3 list | grep -E "reportlab|lxml|openpyxl|docx"

# Tester l'import avec plus de détails
python3 -c "import sys; print(sys.path)"
python3 -c "import reportlab; print(reportlab.__file__)"

# Vérifier les bibliothèques système
ldconfig -p | grep -E "xml|jpeg|z|freetype"
```

## 📚 Ressources supplémentaires

- [Documentation reportlab](https://www.reportlab.com/docs/reportlab-userguide.pdf)
- [Documentation lxml](https://lxml.de/installation.html)
- [Python packaging guide](https://packaging.python.org/en/latest/guides/installing-using-linux-tools/)

## 💡 Conseils

1. **Utilisez toujours un environnement virtuel** pour éviter les conflits
2. **Mettez à jour pip** avant d'installer les packages : `pip3 install --upgrade pip`
3. **Vérifiez votre version de Python** : minimum Python 3.7
4. **Installez les dépendances système AVANT** les packages Python

## 🆘 Besoin d'aide ?

Si aucune de ces solutions ne fonctionne :

1. Partagez la sortie complète de l'erreur
2. Partagez votre version de Python : `python3 --version`
3. Partagez votre distribution Linux : `cat /etc/os-release`
4. Partagez la liste des packages installés : `pip3 list`

Contact : support@epsjl.ht
