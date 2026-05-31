import os
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score
import joblib

csv_path = "registre_depenses.csv"

if not os.path.exists(csv_path):
    print("❌ Fichier registre_depenses.csv introuvable !")
else:
    df = pd.read_csv(csv_path).dropna(subset=['description', 'categorie'])
    
    # ÉTAPE CRUCIALE : On sépare en Train (80%) et Test (20%)
    X_train, X_test, y_train, y_test = train_test_split(
        df['description'], df['categorie'], test_size=0.2, random_state=42, stratify=df['categorie']
    )
    
    # Vectorisation
    vectorizer = TfidfVectorizer(stop_words='english')
    X_train_num = vectorizer.fit_transform(X_train)
    X_test_num = vectorizer.transform(X_test)
    
    # Entraînement
    model = LogisticRegression(class_weight='balanced')
    model.fit(X_train_num, y_train)
    
    # ÉVALUATION
    y_pred = model.predict(X_test_num)
    precision = accuracy_score(y_test, y_pred)
    
    print(f"📊 Nombre d'exemples d'entraînement : {len(X_train)}")
    print(f"🧪 Nombre d'exemples de test : {len(X_test)}")
    print(f"🎯 Précision globale (Accuracy) : {precision * 100:.2f}%\n")
    print("📋 Rapport détaillé de classification :")
    print(classification_report(y_test, y_pred, zero_division=0))
    
    # Sauvegarde
    joblib.dump(model, "modele_classification.pkl")
    joblib.dump(vectorizer, "vectorizer.pkl")