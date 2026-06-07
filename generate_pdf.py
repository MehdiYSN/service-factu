import json
from jinja2 import Template
from weasyprint import HTML

def charger_donnees():
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def formater_prix(valeur):
    if valeur == 0:
        return ""  # Reste vide si le prix calculé est à 0
    return f"{valeur:,.2f}".replace(",", " ").replace(".", ",")

def generer_facture():
    data = charger_donnees()
    
    total_ht = 0.0
    for item in data['articles']:
        # Récupération de la quantité brute
        qte_brute = str(item.get('quantite', '')).strip()
        try:
            qte = int(qte_brute) if qte_brute != "" else 0
        except ValueError:
            qte = 0
            
        # Récupération du prix unitaire brut
        pu_brut = str(item.get('pu_ht', '')).strip()
        try:
            pu = float(pu_brut) if pu_brut != "" else 0.0
        except ValueError:
            pu = 0.0
        
        # Calcul du montant de la ligne
        ligne_total = qte * pu
        total_ht += ligne_total
        
        # GESTION DES CASES VIDES : 
        # Si vous n'avez pas mis de prix ou de quantité, on laisse la case 100% vide
        if pu_brut == "":
            item['pu_ht_formate'] = ""
        else:
            item['pu_ht_formate'] = formater_prix(pu) + " €"

        if qte_brute == "" or qte == 0:
            item['quantite'] = ""
            item['total_ht_formate'] = "" # Le total de la ligne reste vide aussi
        else:
            if pu_brut == "":
                item['total_ht_formate'] = ""
            else:
                item['total_ht_formate'] = formater_prix(ligne_total) + " €"

    # Calculs de la TVA et du TTC global
    try:
        tva_taux = float(data.get('tva_taux', 0))
    except ValueError:
        tva_taux = 0.0
        
    total_tva = total_ht * (tva_taux / 100)
    total_ttc = total_ht + total_tva
    
    # Formatage des totaux (si le total est 0, on affiche quand même 0,00 € ou vide selon vos préférences)
    # Ici, on affiche 0,00 € si rien n'est calculé pour éviter un bug visuel sur les totaux du bas
    data['total_ht'] = formater_prix(total_ht) + " €" if total_ht > 0 else ""
    data['total_tva'] = formater_prix(total_tva) + " €" if total_tva > 0 else ""
    data['total_ttc'] = formater_prix(total_ttc) + " €" if total_ttc > 0 else ""
    data['tva_taux'] = int(tva_taux) if tva_taux.is_integer() else tva_taux

    # Lecture du template HTML
    with open('template.html', 'r', encoding='utf-8') as f:
        html_template = f.read()
        
    # Rendu du document
    template = Template(html_template)
    html_rendu = template.render(data)
    
    # Nom du fichier final
    nom_fichier = f"{data.get('type_document', 'DOCUMENT')}_{data.get('numero', '0000')}.pdf"
    
    print(f"Génération de {nom_fichier} (cases vides respectées)...")
    HTML(string=html_rendu).write_pdf(nom_fichier)
    print("Fait !")

if __name__ == "__main__":
    generer_facture()
