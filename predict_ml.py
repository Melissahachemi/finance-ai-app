import os
import joblib

# 1. Chargement des fichiers de l'I.A.
if not os.path.exists("modele_classification.pkl") or not os.path.exists("vectorizer.pkl"):
    print("❌ Erreur : Les fichiers de l'I.A. sont introuvables. Lance d'abord 'train_model.py' !")
else:
    print("🧠 Chargement du modèle de Machine Learning Scikit-Learn...")
    model = joblib.load("modele_classification.pkl")
    vectorizer = joblib.load("vectorizer.pkl")
    
    print("✅ Modèle prêt pour l'analyse.\n")
    print("="*60)
    print("🔮 PRÉDICTIONS DE L'I.A. SUR DE NOUVELLES FACTURES INCONNUES")
    print("="*60)

    # 2. Nouvelles factures de test (sans aucun mot-clé identique à ton dictionnaire de base)
    nouvelles_factures = [
        "Purchased five high-performance computing setups with extra RAM memory and internal SSD storage.",
        "Order batch of 3M vinyl adhesive solutions, tesa tape and liquid silicone tubes for lab engineering.",
        "The technician unclogged the facility water line and completed the stove knob replacement."
    ]

    # 3. Traitement mathématique par le Vectorizer
    # On transforme le texte brut en fréquences de mots compréhensibles par l'I.A.
    textes_numerises = vectorizer.transform(nouvelles_factures)

    # 4. Calcul de la prédiction statistique par Scikit-Learn
    predictions = model.predict(textes_numerises)

    # 5. Affichage des résultats
    for facture, categorie_predite in zip(nouvelles_factures, predictions):
        print(f"\n📄 Facture Reçue : '{facture}'")
        print(f"🤖 Décision de l'I.A. : ⭐ {categorie_predite} ⭐")