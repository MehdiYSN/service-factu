import json
from jinja2 import Template
from weasyprint import HTML

def charger_donnees():
    with open('data.json', 'r', encoding='utf-8') as f:
        return json.load(f)

def formater_prix(valeur):
    return f"{valeur:,.2f}".replace(",", " ").replace(".", ",")

def generer_facture():
    data = charger_donnees()
    
    # Calculs automatiques
    total_ht = 0.0
    for item in data['articles']:
        qte = int(item['quantite'])
        pu = float(item['pu_ht'])
        ligne_total = qte * pu
        total_ht += ligne_total
        
        # Ajout des versions formatées pour le template
        item['pu_ht_formate'] = formater_prix(pu)
        item['total_ht_formate'] = formater_prix(ligne_total)
        
    tva_taux = data['tva_taux']
    total_tva = total_ht * (tva_taux / 100)
    total_ttc = total_ht + total_tva
    
    # Injection dans les données globales du template
    data['total_ht'] = formater_prix(total_ht)
    data['total_tva'] = formater_prix(total_tva)
    data['total_ttc'] = formater_prix(total_ttc)

    # Lecture du template HTML
    with open('template.html', 'r', encoding='utf-8') as f:
        html_template = f.read()
        
    # Rendu avec Jinja2
    template = Template(html_template)
    html_rendu = template.render(data)
    
    # Nom du fichier de sortie
    nom_fichier = f"{data['type_document']}_{data['numero']}.pdf"
    
    # Génération du PDF propre via WeasyPrint
    print(f"Génération de {nom_fichier} en cours...")
    HTML(string=html_rendu).write_pdf(nom_fichier)
    print("Félicitations, le document PDF professionnel a été généré avec succès !")

if __name__ == "__main__":
    generer_facture()
