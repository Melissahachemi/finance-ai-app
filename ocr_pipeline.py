import os
import re
import pandas as pd
import easyocr

# 1. Initialisation de l'OCR (en anglais, car le dataset Kaggle est en anglais)
print("⏳ Chargement du moteur EasyOCR...")
reader = easyocr.Reader(['en'])

# Dossier contenant tes 150 images copiées
DOSSIER_FACTURES = "factures"

# Liste des mots génériques à supprimer (le "bruit" des factures)
MOTS_A_RETIRE = {
    'invoice', 'total', 'price', 'quantity', 'qty', 'tax', 'subtotal', 
    'seller', 'client', 'amount', 'date', 'number', 'no', 'items', 
    'description', 'payment', 'due', 'bank', 'account', 'statement',
    'the', 'and', 'for', 'with', 'from', 'this', 'that', 'your'
}

def nettoyer_texte(texte_brut):
    """Fonction qui nettoie le texte extrait par l'OCR"""
    # En passage en minuscules
    texte = texte_brut.lower()
    # On remplace la ponctuation, les chiffres et les symboles ($ , €) par des espaces
    texte = re.sub(r'[^a-z\s]', ' ', texte)
    # On découpe le texte mot par mot
    mots = texte.split()
    # On garde uniquement les mots importants (qui ne sont pas dans notre liste noire)
    mots_propres = [m for m in mots if m not in MOTS_A_RETIRE and len(m) > 2]
    # On rassemble les mots nettoyés en une seule ligne
    return " ".join(mots_propres)

# --- BOUCLE PRINCIPALE ---
donnees_extraites = []

if not os.path.exists(DOSSIER_FACTURES):
    print(f"❌ Le dossier '{DOSSIER_FACTURES}' n'existe pas. Crée-le et mets tes 150 images dedans.")
else:
    images = [f for f in os.listdir(DOSSIER_FACTURES) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f"📸 {len(images)} images trouvées dans le dossier. Début de l'extraction...")

    for index, nom_image in enumerate(images, 1):
        chemin_image = os.path.join(DOSSIER_FACTURES, nom_image)
        print(f"🔍 [{index}/{len(images)}] Analyse de {nom_image}...")
        
        try:
            # L'OCR lit l'image et extrait le texte
            resultat_ocr = reader.readtext(chemin_image, detail=0)
            texte_brut = " ".join(resultat_ocr)
            
            # Application de notre nettoyage sémantique
            texte_propre = nettoyer_texte(texte_brut)
            
            # On stocke le résultat temporairement
            donnees_extraites.append({
                "nom_fichier": nom_image,
                "texte_nettoye": texte_propre
            })
        except Exception as e:
            print(f"⚠️ Erreur sur l'image {nom_image} : {e}")

    # 3. Sauvegarde dans un nouveau fichier CSV pour l'étape du clustering
    df_resultat = pd.DataFrame(donnees_extraites)
    df_resultat.to_csv("dataset_clustering.csv", index=False)
    print("\n✅ Extraction et nettoyage terminés !")
    print("💾 Les données propres sont sauvegardées dans 'dataset_clustering.csv'")