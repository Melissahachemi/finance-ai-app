import os
import re
import pandas as pd
import easyocr

print("⏳ Chargement du moteur EasyOCR...")
reader = easyocr.Reader(['en'])

DOSSIER_FACTURES = "factures"

MOTS_A_RETIRE = {
    'invoice', 'total', 'price', 'quantity', 'qty', 'tax', 'subtotal', 
    'seller', 'client', 'amount', 'date', 'number', 'no', 'items', 
    'description', 'payment', 'due', 'bank', 'account', 'statement',
    'the', 'and', 'for', 'with', 'from', 'this', 'that', 'your', 'worth', 'net', 'vat'
}

def nettoyer_texte_clustering(lignes_texte):
    """Garde uniquement les mots pour le K-Means (sans chiffres)"""
    texte_joint = " ".join(lignes_texte).lower()
    texte_joint = re.sub(r'[^a-z\s]', ' ', texte_joint)
    mots = texte_joint.split()
    return " ".join([m for m in mots if m not in MOTS_A_RETIRE and len(m) > 2])

def chercher_montant_regex(resultats_ocr, pattern_mot_cle):
    """
    Cherche un montant numérique dans les lignes proches d'un mot-clé (Total ou VAT)
    """
    for i, (bbox, texte, prob) in enumerate(resultats_ocr):
        texte_clean = texte.lower()
        
        # Si on trouve le mot clé (ex: "total" ou "vat")
        if re.search(pattern_mot_cle, texte_clean):
            # On regarde les blocs de texte juste après (souvent le montant est à côté ou en dessous)
            for j in range(max(0, i-1), min(len(resultats_ocr), i+4)):
                potentiel_nombre = resultats_ocr[j][1].replace(" ", "").replace(",", ".")
                # On cherche un format nombre (ex: 1250.50 ou 15)
                match = re.search(r'\d+(?:\.\d+)?', potentiel_nombre)
                if match:
                    try:
                        return float(match.group())
                    except:
                        continue
    return 0.0

donnees_extraites = []

if not os.path.exists(DOSSIER_FACTURES):
    print(f"❌ Le dossier '{DOSSIER_FACTURES}' n'existe pas.")
else:
    images = [f for f in os.listdir(DOSSIER_FACTURES) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
    print(f"📸 {len(images)} images trouvées. Début de l'extraction par OCR...")

    for index, nom_image in enumerate(images, 1):
        chemin_image = os.path.join(DOSSIER_FACTURES, nom_image)
        print(f"🔍 [{index}/{len(images)}] Analyse OCR en cours sur {nom_image}...")
        
        try:
            # On demande à EasyOCR de nous donner le texte ET sa position (detail=1)
            resultat_ocr = reader.readtext(chemin_image, detail=1)
            
            # 1. On récupère juste les textes bruts pour le nettoyage NLP
            lignes_texte = [ligne[1] for ligne in resultat_ocr]
            texte_propre = nettoyer_texte_clustering(lignes_texte)
            
            # 2. Extraction du montant TTC (On cherche le nombre proche de 'total' ou 'gross')
            montant_ttc = chercher_montant_regex(resultat_ocr, r'total|gross|worth')
            
            # 3. Extraction de la TVA (On cherche le nombre proche de 'vat' ou 'tax')
            montant_tva = chercher_montant_regex(resultat_ocr, r'vat|tax')
            
            donnees_extraites.append({
                "nom_fichier": nom_image,
                "texte_nettoye": texte_propre,
                "montant_ttc": montant_ttc,
                "tva": montant_tva
            })
            
            print(f"   ↳ 📝 Mots clés: {texte_propre[:30]}... | 💰 TTC: {montant_ttc}€ | 🛡️ TVA: {montant_tva}€")

        except Exception as e:
            print(f"⚠️ Erreur sur l'image {nom_image} : {e}")

    # Sauvegarde
    df_resultat = pd.DataFrame(donnees_extraites)
    df_resultat.to_csv("dataset_clustering.csv", index=False)
    print(f"\n✅ Extraction par OCR terminée ! Fichier 'dataset_clustering.csv' mis à jour.")
    