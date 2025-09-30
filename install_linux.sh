#!/bin/bash

# Script d'installation pour Linux - Section Archives EPSJL
# Ce script installe toutes les dépendances nécessaires

set -e  # Arrêter en cas d'erreur

echo "================================================"
echo "Installation des dépendances - Section Archives"
echo "================================================"
echo ""

# Détection de la distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
else
    echo "❌ Impossible de détecter la distribution Linux"
    exit 1
fi

echo "Distribution détectée: $OS"
echo ""

# Installation des dépendances système
echo "📦 Installation des dépendances système..."

case $OS in
    ubuntu|debian|linuxmint)
        echo "Installation pour Debian/Ubuntu..."
        sudo apt-get update
        sudo apt-get install -y \
            python3-dev \
            python3-pip \
            python3-venv \
            libxml2-dev \
            libxslt1-dev \
            libjpeg-dev \
            zlib1g-dev \
            libfreetype6-dev \
            build-essential \
            pkg-config
        ;;
    
    centos|rhel|fedora)
        echo "Installation pour CentOS/RHEL/Fedora..."
        sudo yum install -y \
            python3-devel \
            python3-pip \
            libxml2-devel \
            libxslt-devel \
            libjpeg-devel \
            zlib-devel \
            freetype-devel \
            gcc \
            gcc-c++ \
            make
        sudo yum groupinstall -y "Development Tools" || true
        ;;
    
    arch|manjaro)
        echo "Installation pour Arch Linux..."
        sudo pacman -S --noconfirm \
            python-pip \
            base-devel \
            libxml2 \
            libxslt \
            libjpeg-turbo \
            zlib \
            freetype2
        ;;
    
    *)
        echo "⚠️  Distribution non reconnue: $OS"
        echo "Veuillez installer manuellement les dépendances suivantes:"
        echo "  - python3-dev/devel"
        echo "  - libxml2-dev/devel"
        echo "  - libxslt-dev/devel"
        echo "  - libjpeg-dev/devel"
        echo "  - zlib-dev/devel"
        echo "  - freetype-dev/devel"
        echo "  - build-essential/gcc/make"
        exit 1
        ;;
esac

echo "✅ Dépendances système installées"
echo ""

# Mise à jour de pip
echo "🔄 Mise à jour de pip..."
python3 -m pip install --upgrade pip setuptools wheel
echo "✅ pip mis à jour"
echo ""

# Installation des dépendances Python
echo "🐍 Installation des dépendances Python..."
if [ -f requirements.txt ]; then
    python3 -m pip install -r requirements.txt
    echo "✅ Dépendances Python installées"
else
    echo "❌ Fichier requirements.txt introuvable"
    exit 1
fi
echo ""

# Vérification de l'installation
echo "🔍 Vérification de l'installation..."
echo ""

check_module() {
    if python3 -c "import $1" 2>/dev/null; then
        echo "  ✅ $1"
        return 0
    else
        echo "  ❌ $1 - ERREUR"
        return 1
    fi
}

ERRORS=0

check_module "flask" || ((ERRORS++))
check_module "openpyxl" || ((ERRORS++))
check_module "reportlab" || ((ERRORS++))
check_module "docx" || ((ERRORS++))
check_module "werkzeug" || ((ERRORS++))
check_module "sqlalchemy" || ((ERRORS++))

echo ""

if [ $ERRORS -eq 0 ]; then
    echo "✅ Tous les modules sont correctement installés!"
    echo ""
    echo "================================================"
    echo "Installation terminée avec succès! 🎉"
    echo "================================================"
    echo ""
    echo "Pour démarrer l'application:"
    echo "  python3 app.py"
    echo ""
    echo "Pour tester la section Archives:"
    echo "  python3 test_archives.py"
    echo ""
    echo "Accès: http://localhost:8000/archives"
    echo "================================================"
    exit 0
else
    echo "❌ $ERRORS module(s) n'ont pas pu être installés"
    echo ""
    echo "Consultez INSTALL_LINUX.md pour plus d'informations"
    exit 1
fi
