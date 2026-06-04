import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.cluster import KMeans

# 1. On charge ton tout nouveau fichier généré par l'OCR
csv_path = "dataset_clustering.csv"
df = pd.read_csv(csv_path)

# On retire les lignes qui n'auraient pas de texte (au cas où une image était blanche)
df = df.dropna(subset=['texte_nettoye'])

print(f"📊 Chargement de {len(df)} factures lues par l'OCR...")

# 2. Vectorisation (Traduction des mots en nombres pour l'ordinateur)
vectorizer = TfidfVectorizer(max_features=1000)
X_features = vectorizer.fit_transform(df['texte_nettoye'])

# 3. L'algorithme K-Means : On lui demande de trouver 5 catégories de dépenses
print("🤖 Entraînement de l'I.A. de Clustering (K-Means)...")
nombre_de_clusters = 5
kmeans = KMeans(n_clusters=nombre_de_clusters, random_state=42, n_init=10)
df['cluster_id'] = kmeans.fit_predict(X_features)

# 4. Sauvegarde du résultat final
df.to_csv("resultat_clustering.csv", index=False)
print("✅ Clustering terminé ! Fichier 'resultat_clustering.csv' créé.")

# --- ANALYSE : Quels sont les mots clés de chaque groupe ? ---
print("\n🕵️‍♀️ ANALYSE DES CATÉGORIES DÉCOUVERTES PAR L'I.A. :")
terms = vectorizer.get_feature_names_out()
order_centroids = kmeans.cluster_centers_.argsort()[:, ::-1]

for i in range(nombre_de_clusters):
    print(f"\n📁 GROUPE (Cluster) #{i} :")
    mots_cles = [terms[ind] for ind in order_centroids[i, :8]] # On prend les 8 mots les plus importants
    print(f"   Mots-clés dominants : {', '.join(mots_cles)}")