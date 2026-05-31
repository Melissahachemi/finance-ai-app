import os
import re
import pandas as pd
import easyocr
from pypdf import PdfReader

# 1. Initialisation de l'OCR pour les images
print("Chargement du modèle OCR pour les images...")
reader = easyocr.Reader(['fr', 'en'])

dossier_factures = "factures"
liste_depenses = []

# 2. Dictionnaire de classification (Taxonomie métier)
def classifier_texte(texte):
    texte_lower = texte.lower()
    regles = {
        "equipement_informatique": ["desktop", "computer", "ryzen", "amd", "dell", "optiplex", "hp", "ram", "ssd"],
        "fournitures_techniques": ["epoxy", "sealant", "silicone", "lubricant", "tape", "teflon", "mask", "sponge", "adhesive", "3m"],
        "services_maintenance": ["unclogged", "disposal", "repaired", "stove", "internet", "suite", "revenue", "service"]
    }
    for categorie, mots_cles in regles.items():
        for mot in mots_cles:
            if mot in texte_lower:
                return categorie
    return "autres_depenses"

# 3. Traitement du dossier
if not os.path.exists(dossier_factures):
    print(f"Erreur : Le dossier '{dossier_factures}' n'existe pas !")
else:
    fichiers = os.listdir(dossier_factures)
    print(f"🔍 Trouvé {len(fichiers)} fichier(s) dans le dossier.\n")

    for index, nom_fichier in enumerate(fichiers):
        chemin_complet = os.path.join(dossier_factures, nom_fichier)
        ext = nom_fichier.lower()
        texte_extrait = ""

        # --- A. STRATÉGIE D'INGESTION HYBRIDE ---
        try:
            if ext.endswith(('.png', '.jpg', '.jpeg')):
                print(f"[{index + 1}/{len(fichiers)}] 📸 OCR Image sur : {nom_fichier}...")
                resultat_ocr = reader.readtext(chemin_complet, detail=0)
                texte_extrait = " ".join(resultat_ocr)

            elif ext.endswith('.pdf'):
                print(f"[{index + 1}/{len(fichiers)}] 📄 Extraction PDF sur : {nom_fichier}...")
                pdf_reader = PdfReader(chemin_complet)
                # On fusionne le texte de toutes les pages du PDF
                texte_extrait = " ".join([page.extract_text() for page in pdf_reader.pages if page.extract_text()])

            else:
                continue # Ignore les autres formats de fichiers

            if not texte_extrait.strip():
                print(f"⚠️ Texte vide pour {nom_fichier}, ignoré.")
                continue

            # --- B. PARSING REGEX ---
            motif_montant = re.search(r'(?:total|amount due)[:\s]*\$?\s*([\d\s.,]+)', texte_extrait, re.IGNORECASE)
            motif_date = re.search(r'(\b[A-Za-z]{3,}\.?\s*\d{1,2}\s*,\s*\d{4}\b)|(\b\d{2}/\d{2}/\d{4}\b)', texte_extrait)

            # Si la RegEx stricte du total échoue, on cherche un symbole monétaire simple
            if not motif_montant:
                motif_montant = re.search(r'(?:\$\s*(\d+[\.,]?\d*))|(?:(\d+[\.,]?\d*)\s*(?:USD|€))', texte_extrait)

            montant = motif_montant.group(1).strip() if motif_montant else "0.00"
            date = motif_date.group(0).strip() if motif_date else "Date inconnue"

            # Nettoyage du montant
            montant = montant.replace("USD", "").replace(" ", "").strip()

            # --- C. CLASSIFICATION ---
            categorie = classifier_texte(texte_extrait)

            # Ajout au registre
            liste_depenses.append({
                "fichier": nom_fichier,
                "date": date,
                "description": texte_extrait.replace("\n", " ")[:50] + "...",
                "montant": montant,
                "categorie": categorie
            })

        except Exception as e:
            print(f"❌ Erreur sur {nom_fichier} : {e}")

    # --- 4. ENREGISTREMENT ET INTERFACE ---
    if liste_depenses:
        df_final = pd.DataFrame(liste_depenses)
        df_final.to_csv("registre_depenses.csv", index=False)
        print("\n" + "="*40)
        print("🎉 PIPELINE HYBRIDE TERMINÉ AVEC SUCCÈS !")
        print("Le fichier 'registre_depenses.csv' regroupe toutes tes données classifiées.")
        print(df_final.head(10))