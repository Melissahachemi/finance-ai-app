import easyocr
import os
import re
import pandas as pd

print("Chargement du modèle OCR...")
reader = easyocr.Reader(['fr', 'en'])

dossier_factures = "factures"
liste_depenses = [] # Liste vide qui va stocker nos dictionnaires de dépenses

# Vérifier si le dossier existe
if not os.path.exists(dossier_factures):
    print(f"Erreur : Le dossier '{dossier_factures}' n'existe pas !")
else:
    # On liste tous les fichiers du dossier
    fichiers = os.listdir(dossier_factures)
    print(f"Trouvé {len(fichiers)} fichier(s) à analyser.\n")

    for index, nom_fichier in enumerate(fichiers):
        # On ne traite que les images pour le moment (jpg, jpeg, png)
        if nom_fichier.lower().endswith(('.png', '.jpg', '.jpeg')):
            print(f"[{index + 1}/{len(fichiers)}] Analyse de {nom_fichier}...")
            chemin_complet = os.path.join(dossier_factures, nom_fichier)
            
            try:
                # 1. OCR
                resultat = reader.readtext(chemin_complet, detail=0)
                texte_complet = " ".join(resultat)
                
                # 2. Extraction des infos (RegEx)
                motif_strict = re.search(r'(?:\$\s*(\d+[\.,]?\d*))|(?:(\d+[\.,]?\d*)\s*(?:USD|€))', texte_complet)
                motif_date = re.search(r'([A-Za-z]{3,}\.?\s*\d{1,2}\s*,\s*\d{4})', texte_complet)
                
                montant = motif_strict.group(1) if (motif_strict and motif_strict.group(1)) else (motif_strict.group(2) if motif_strict else None)
                date = motif_date.group(1) if motif_date else None
                
                # 3. On crée la dépense propre sous forme de dictionnaire
                depense = {
                    "fichier": nom_fichier,
                    "date": date,
                    "description": texte_complet[:30] + "...", # On prend le début du texte comme description temporaire
                    "montant": montant,
                    "categorie": None # Ce sera pour Scikit-Learn plus tard !
                }
                
                liste_depenses.append(depense)
                
            except Exception as e:
                print(f"❌ Erreur lors du traitement de {nom_fichier} : {e}")

    # --- ENREGISTREMENT DANS LE TABLEAU CENTRAL ---
    if liste_depenses:
        # On transforme notre liste en un magnifique tableau Pandas DataFrame
        df_final = pd.DataFrame(liste_depenses)
        
        # On l'enregistre dans un fichier CSV central
        df_final.to_csv("registre_depenses.csv", index=False)
        
        print("\n" + "="*40)
        print("🎉 ANALYSE TERMINÉE AVEC SUCCÈS !")
        print("Le fichier 'registre_depenses.csv' a été créé.")
        print("============== EXTRAIT ==============")
        print(df_final.head()) # Affiche les 5 premières lignes du tableau