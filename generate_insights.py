import pandas as pd
import os

csv_path = "resultat_clustering.csv"

if not os.path.exists(csv_path):
    print(f"❌ Erreur : Le fichier '{csv_path}' n'existe pas. Lance d'abord l'OCR et le Clustering.")
else:
    df_cluster = pd.read_csv(csv_path)

    # Correspondance de tes 5 catégories
    dictionnaire_categories = {
        0: "Vêtements & Autres",
        1: "Matériel Informatique",
        2: "Consoles & Jeux Vidéo",
        3: "Mobilier & Bureau",
        4: "Tapis & Décoration"
    }
    df_cluster['nom_categorie'] = df_cluster['cluster_id'].map(dictionnaire_categories)

    # 🛠️ NETTOYAGE SÉCURITÉ : Si la TVA est aberrante (ex: numéro de facture confondu), 
    # on applique par défaut un taux de 20% du TTC, très classique en gestion financière.
    def corriger_tva(row):
        ttc = row['montant_ttc']
        tva = row['tva']
        if tva > ttc or tva <= 0:
            return round(ttc * 0.20, 2)  # Estimation à 20% par sécurité
        return tva

    df_cluster['tva_propre'] = df_cluster.apply(corriger_tva, axis=1)
    
    # Calcul du montant Hors Taxes (HT)
    df_cluster['montant_ht'] = (df_cluster['montant_ttc'] - df_cluster['tva_propre']).round(2)

    print("📊 =============================================================== 📊")
    print("📈       AUDIT FINANCIER & INSIGHTS ANALYTIQUES         📈")
    print("📊 =============================================================== 📊\n")

    # 1. Calcul des indicateurs poussés de gestion de trésorerie
    insights = df_cluster.groupby('nom_categorie').agg(
        Nb_Factures=('montant_ttc', 'count'),
        Total_HT=('montant_ht', 'sum'),
        Total_TVA=('tva_propre', 'sum'),
        Total_TTC=('montant_ttc', 'sum'),
        Achat_Moyen_TTC=('montant_ttc', 'mean'),
        Facture_Max_TTC=('montant_ttc', 'max')
    )

    # 2. Calcul des parts du budget global (en %)
    total_global_ttc = insights['Total_TTC'].sum()
    insights['Part_Budget_(%)'] = ((insights['Total_TTC'] / total_global_ttc) * 100).round(2)

    # Tri du tableau par le pôle qui coûte le plus cher
    insights = insights.sort_values(by='Total_TTC', ascending=False)

    # 3. Affichage propre de toutes les colonnes à l'écran (sans les "...")
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', 1000)

    affichage = insights.copy()
    for col in ['Total_HT', 'Total_TVA', 'Total_TTC', 'Achat_Moyen_TTC', 'Facture_Max_TTC']:
        affichage[col] = affichage[col].apply(lambda x: f"{x:,.2f} €")
    affichage['Part_Budget_(%)'] = affichage['Part_Budget_(%)'].apply(lambda x: f"{x} %")

    print(affichage)
    print("\n-------------------------------------------------------------------")
    
    # 4. Indicateurs clés de performance (KPIs) pour le tableau de bord
    total_global_tva = insights['Total_TVA'].sum()
    total_global_ht = insights['Total_HT'].sum()
    
    print(f"💰 VOLUME FINANCIER TOTAL : {total_global_ttc:,.2f} € TTC")
    print(f"📉 TOTAL NET HORS TAXES   : {total_global_ht:,.2f} € HT")
    print(f"🛡️ TVA À RÉCUPÉRER (20%)  : {total_global_tva:,.2f} €")
    print(f"🚨 ALERT BUDGET DIRECTION : '{insights['Total_TTC'].idxmax()}' représente {insights['Part_Budget_(%)'].max()}% des dépenses globales.")

    # Sauvegarde du registre complet enrichi pour ton API ou ton Chatbot
    df_cluster.to_csv("registre_depenses_final.csv", index=False)
    print("\n💾 Registre financier enrichi sauvegardé dans 'registre_depenses_final.csv'")