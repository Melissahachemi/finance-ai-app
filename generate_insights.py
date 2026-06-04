import pandas as pd
import os

# 1. Chemins des fichiers
FICH_CLUSTER = "resultat_clustering.csv"
FICH_ORIGINE = "depenses.csv"  # Ton fichier d'origine !

if not os.path.exists(FICH_CLUSTER):
    print(f"❌ Erreur : Le fichier '{FICH_CLUSTER}' est introuvable. Lance 'python cluster_model.py' d'abord.")
elif not os.path.exists(FICH_ORIGINE):
    print(f"❌ Erreur : Le fichier d'origine '{FICH_ORIGINE}' est introuvable à la racine du projet.")
else:
    # 2. Chargement des données
    df_cluster = pd.read_csv(FICH_CLUSTER)
    df_origine = pd.read_csv(FICH_ORIGINE)

    # 3. Mapping (Traduction des numéros en vrais noms de catégories)
    dictionnaire_categories = {
        0: "Autres & Divers",
        1: "Matériel Informatique",
        2: "Consoles & Jeux Vidéo",
        3: "Mobilier & Bureau",
        4: "Tapis & Décoration"
    }
    df_cluster['nom_categorie'] = df_cluster['cluster_id'].map(dictionnaire_categories)

    # 4. Association avec les vrais montants du fichier d'origine
    # On aligne les lignes ou on fusionne selon l'index pour récupérer la colonne 'montant'
    if 'montant' in df_origine.columns:
        df_cluster['montant'] = df_origine['montant']
    else:
        # Si la colonne s'appelle autrement (ex: 'prix' ou 'total'), on s'adapte
        col_montant = [c for c in df_origine.columns if 'mont' in c.lower() or 'prix' in c.lower() or 'total' in c.lower()]
        if col_montant:
            df_cluster['montant'] = df_origine[col_montant[0]]
        else:
            # Sécurité au cas où la colonne montant n'est pas trouvée
            print("⚠️ Colonne de montant introuvable dans depenses.csv, utilisation d'une valeur par défaut.")
            df_cluster['montant'] = 100.0

    # Nettoyage de la colonne montant (conversion en nombres si c'est du texte)
    df_cluster['montant'] = pd.to_numeric(df_cluster['montant'].astype(str).str.replace(r'[^\d.]', '', regex=True), errors='coerce').fillna(0)

    print("📊 --- LES VRAIS INSIGHTS DE COMPTABILITÉ (PANDAS) --- 📊\n")

    # KPI 1 : Répartition du budget par catégorie
    stats = df_cluster.groupby('nom_categorie')['montant'].agg(['sum', 'count'])
    stats.columns = ['Montant Total (€)', 'Nombre de Factures']
    stats = stats.sort_values(by='Montant Total (€)', ascending=False)
    
    # Affichage propre
    stats['Montant Total (€)'] = stats['Montant Total (€)'].apply(lambda x: f"{x:,.2f} €")
    print(stats)

    # KPI 2 : Total Général
    total_general = df_cluster['montant'].sum()
    print(f"\n💰 Dépense Totale Cumulée : {total_general:,.2f} €")

    # KPI 3 : Pire catégorie
    top_depense = df_cluster.groupby('nom_categorie')['montant'].sum().idxmax()
    print(f"🚨 Alerte Budget : La catégorie la plus coûteuse est '{top_depense}'.")

    # 5. Sauvegarde du registre final enrichi
    df_cluster.to_csv("registre_depenses_final.csv", index=False)
    print("\n💾 Le registre complet a été sauvegardé dans 'registre_depenses_final.csv'")