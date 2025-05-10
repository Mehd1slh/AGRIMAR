import matplotlib.pyplot as plt
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from dotenv import load_dotenv

load_dotenv('variables.env')

def create_soil_graph(layer, file_name):
    print(f"Creating graph for layer: {layer.get('name')}")
    
    # Renaming BEFORE filename creation
    name_mapping = {'sand': 'sable', 'clay': 'argile', 'silt': 'limon'}
    layer_name = name_mapping.get(layer['name'], layer['name'])
    
    file_name = f"agrimar/data_graphs+pdf/{layer_name}.png"
    os.makedirs(os.path.dirname(file_name), exist_ok=True)  # ensure directory exists

    depths = [d.get('label') for d in layer.get('depths', [])]
    values = [d.get('values', {}).get('mean') for d in layer.get('depths', [])]

    print(f"Depths: {depths}")
    print(f"Values: {values}")

    # ⚠️ Defensive: if data missing, skip file creation
    if not depths or not values or any(v is None for v in values):
        print(f"[WARNING] Missing or invalid data for layer {layer_name}. Graph will not be created.")
        return  # early exit!

    plt.figure(figsize=(10, 6))
    plt.plot(depths, values, marker='o', linestyle='-', color='b')
    plt.title(f"{layer_name.upper()} Niveaux par profondeur")
    plt.xlabel('Profondeur')
    plt.ylabel(f"{layer.get('unit_measure', {}).get('target_units', '')}")
    plt.grid(True)
    plt.savefig(file_name)
    plt.close()
    print(f"[INFO] Graph saved at {file_name}")


def create_weather_graphs(dates, values, title, ylabel, filename , color = 'b'):
    plt.figure(figsize=(10, 6))
    plt.plot(dates, values, marker='o', color=color)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel(ylabel)
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(filename)
    plt.close()


def get_weather_report_text():
    title = "Rapport de Météorologique"
    paragraph = (
        """Ce rapport contient les données météorologiques quotidiennes, y compris les températures, l'humidité, l'indice UV et la vitesse du vent. Chaque graphique représente une analyse détaillée des conditions météorologiques pour aider à comprendre les tendances et à prendre des décisions éclairées."""
    )
    return title, paragraph

def add_weather_properties_pages(pdf, full_weather_data):
    
    #layers = full_soil_data["properties"]["layers"]
    daily_weather_data = full_weather_data['daily']
    dates = [datetime.fromtimestamp(day['dt']).date().isoformat() for day in daily_weather_data]
    temps = [day['temp']['day'] for day in daily_weather_data] 
    humidity = [day['humidity'] for day in daily_weather_data]
    uvi = [day['uvi'] for day in daily_weather_data]
    wind_speed = [day['wind_speed'] for day in daily_weather_data]

    title, paragraph = get_weather_report_text()
    pdf.add_second_page(title, paragraph)

    pdf.add_page() #first weather page (temperature + humidity)
    create_weather_graphs(dates, temps, 'Température quotidienne', 'Temperature (°C)', "agrimar/data_graphs+pdf/daily_temperature.png", 'red')
    pdf.set_font("Arial", size=12)
    pdf.image("agrimar/data_graphs+pdf/daily_temperature.png", x=10, y=None , w=190)
    pdf.set_y(150)   
    create_weather_graphs(dates, humidity, 'Humidité quotidienne', 'Humidité (%)', "agrimar/data_graphs+pdf/daily_humidity.png", 'blue')
    pdf.set_font("Arial", size=12)
    pdf.image('agrimar/data_graphs+pdf/daily_humidity.png', x=10, y=None , w=190)

    pdf.add_page() #second weather page (uv index + wind speed)
    create_weather_graphs(dates, uvi, 'Indice UV quotidien', 'Indice UV', "agrimar/data_graphs+pdf/daily_uvi.png", 'orange')
    pdf.set_font("Arial", size=12)
    pdf.image("agrimar/data_graphs+pdf/daily_uvi.png", x=10, y=None , w=190)
    pdf.set_y(150)   
    create_weather_graphs(dates, wind_speed, 'Vitesse du vent quotidienne', 'Vitesse (m/s)', "agrimar/data_graphs+pdf/daily_wind_speed.png", 'green')
    pdf.set_font("Arial", size=12)
    pdf.image("agrimar/data_graphs+pdf/daily_wind_speed.png", x=10, y=None , w=190)

def get_soil_report_text():
    title = "Rapport de données du sol"
    paragraph = (
        "Ce rapport contient les données du sol pour différentes profondeurs. "
        "Chaque graphique représente une propriété du sol en fonction de la profondeur, "
        "permettant une analyse détaillée des caractéristiques du sol."
    )
    property_descriptions = '''
    WV1500(Teneur en eau à 1500 kPa) : Indique la capacité du sol à retenir l'eau sous haute tension.
    WV0033(Teneur en eau à 33 kPa) : Reflète la capacité du sol à retenir l'eau sous tension modérée.
    WV0010(Teneur en eau à 10 kPa) : Indique la capacité du sol à retenir l'eau sous faible tension.
    SOC(Carbone organique du sol) : Mesure la quantité de carbone organique dans le sol, un composant essentiel pour la fertilité et la structure du sol.
    LIMON(Teneur en limon) : Représente la proportion de particules fines dans le sol, influençant la texture du sol et la rétention d'eau.
    SABLE(Teneur en sable) : Indique la proportion de particules grossières dans le sol, affectant le drainage et l'aération.
    PHH2O(pH dans H2O) : Mesure l'acidité ou l'alcalinité de l'eau du sol, influençant la disponibilité des nutriments et l'activité microbienne.
    OCS(Stock de carbone organique) : Représente la quantité totale de carbone stockée dans le sol, crucial pour la santé du sol et la régulation climatique.
    OCD(Densité de carbone organique) : Reflète la concentration de carbone organique par unité de volume de sol, un indicateur de la fertilité du sol.
    NITROGEN(Teneur en azote) : Mesure la disponibilité de l'azote dans le sol, essentiel pour la croissance et le développement des plantes.
    ARGILE(Teneur en argile) : Indique la proportion de particules d'argile dans le sol, affectant la structure du sol et la rétention des nutriments.
    CFVO(Capacité d'échange cationique) : Reflète la capacité du sol à retenir et à échanger des cations, essentielle pour la disponibilité des nutriments pour les plantes.
    CEC(Capacité d'échange cationique) : Représente la capacité totale du sol à retenir des cations échangeables, influençant la disponibilité des nutriments.
    BDOD(Densité apparente du sol) : Mesure la masse de sol par unité de volume, influençant la porosité du sol et la croissance des racines.
    '''
    return title, paragraph, property_descriptions


def add_soil_report_pages(pdf, layers):
    title, paragraph, property_descriptions = get_soil_report_text()
    pdf.add_second_page(title, paragraph, property_descriptions)

    num_layers = len(layers)

    # Generate all graphs in parallel
    with ThreadPoolExecutor() as executor:
        futures = []
        for layer in layers:
            file_name = f"agrimar/data_graphs+pdf/{layer['name']}.png"
            futures.append(executor.submit(create_soil_graph, layer, file_name))
        for f in futures:
            f.result()  # wait for all to finish

    # Now insert into PDF (still sequential)
    for i in range(0, num_layers, 2):
        pdf.add_page()
        for layer in layers[i:i + 2]:
            file_name = f"agrimar/data_graphs+pdf/{layer['name']}.png"
            pdf.set_font("Arial", size=12)
            if os.path.exists(file_name):
                pdf.image(file_name, x=10, y=None, w=190)
            else:
                print(f"[WARNING] File {file_name} does not exist; skipping image insertion.")
            pdf.set_y(150)


def send_report_email(recipient_email, report_path):
    msg = MIMEMultipart()
    msg['From'] = os.getenv('MAIL_ADRESSE')
    msg['To'] = recipient_email
    msg['Subject'] = 'Your AGRIMAR Report'

    part = MIMEBase('application', "octet-stream")
    with open(report_path, 'rb') as file:
        part.set_payload(file.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(report_path)}')
    msg.attach(part)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
        server.login(os.getenv('MAIL_ADRESSE'), os.getenv('MAIL_PASSWORD'))
        server.sendmail(msg['From'], [msg['To']], msg.as_string())
