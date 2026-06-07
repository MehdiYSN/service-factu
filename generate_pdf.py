import json
from jinja2 import Template
from weasyprint import HTML

def charger_donnees():
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def formater_prix(valeur):
    if valeur == 0:
        return ""
    return f"{valeur:,.2f}".replace(",", " ").replace(".", ",")

def generer_facture():
    data = charger_donnees()
    
    # 1. Analyse et nettoyage des articles du tableau
    total_calcule_lignes = 0.0
    for item in data['articles']:
        qte_brute = str(item.get('quantite', '')).strip()
        try:
            qte = int(qte_brute) if qte_brute != "" else 0
        except ValueError:
            qte = 0
            
        pu_brut = str(item.get('pu_ht', '')).strip()
        try:
            pu = float(pu_brut) if pu_brut != "" else 0.0
        except ValueError:
            pu = 0.0
        
        ligne_total = qte * pu
        total_calcule_lignes += ligne_total
        
        # Masquage ou affichage propre des prix unitaires
        if pu_brut == "":
            item['pu_ht_formate'] = ""
        else:
            item['pu_ht_formate'] = formater_prix(pu) + " €"

        # Masquage ou affichage propre des quantités et sous-totaux de ligne
        if qte_brute == "" or qte == 0:
            item['quantite'] = ""
            item['total_ht_formate'] = ""
        else:
            if pu_brut == "":
                item['total_ht_formate'] = ""
            else:
                item['total_ht_formate'] = formater_prix(ligne_total) + " €"

    # 2. Gestion du Total HT Global (Prend le manuel en priorité si présent)
    total_ht_manuel_brut = str(data.get('total_ht_manuel', '')).strip()
    
    if total_ht_manuel_brut != "":
        try:
            total_ht = float(total_ht_manuel_brut)
        except ValueError:
            total_ht = total_calcule_lignes
    else:
        total_ht = total_calcule_lignes

    # 3. Récupération et calcul du taux de TVA
    try:
        tva_taux_brut = str(data.get('tva_taux', '0')).strip()
        tva_taux = float(tva_taux_brut) if tva_taux_brut != "" else 0.0
    except ValueError:
        tva_taux = 0.0
        
    # Gestion de la TVA (manuelle ou calculée automatiquement)
    tva_manuelle_brut = str(data.get('tva_manuelle', '')).strip()
    if tva_manuelle_brut != "":
        try:
            total_tva = float(tva_manuelle_brut)
        except ValueError:
            total_tva = total_ht * (tva_taux / 100)
    else:
        total_tva = total_ht * (tva_taux / 100)
        
    # Calcul du montant total Toutes Taxes Comprises
    total_ttc = total_ht + total_tva
    
    # 4. Préparation des variables pour l'affichage final dans le HTML
    data['total_ht'] = formater_prix(total_ht) + " €" if total_ht > 0 else "0,00 €"
    
    if total_tva > 0:
        data['total_tva'] = formater_prix(total_tva) + " €"
    elif tva_taux == 0:
        data['total_tva'] = "TVA non applicable"
    else:
        data['total_tva'] = "0,00 €"
        
    data['total_ttc'] = formater_prix(total_ttc) + " €" if total_ttc > 0 else "0,00 €"
    data['tva_taux'] = int(tva_taux) if tva_taux.is_integer() else tva_taux

    # 5. Lecture du template HTML et rendu final
    with open('template.html', 'r', encoding='utf-8') as f:
        html_template = f.read()
        
    template = Template(html_template)
    html_rendu = template.render(data)
    
    # Création du fichier PDF final
    nom_fichier = f"{data.get('type_document', 'DOCUMENT')}_{data.get('numero', '0000')}.pdf"
    print(f"Génération du document professionnel : {nom_fichier}...")
    HTML(string=html_rendu).write_pdf(nom_fichier)
    print("Document créé avec succès !")

if __name__ == "__main__":
    generer_facture()
