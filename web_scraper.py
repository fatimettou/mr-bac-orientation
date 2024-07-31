import pandas as pd
import streamlit as st
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from webdriver_manager.chrome import ChromeDriverManager

# Fonction pour exécuter le scraping
def scrape_data(matricule):
    # URL de la page web
    url = f"https://dec.education.gov.mr/bac-21/{matricule}/info"

    # Chemin vers votre ChromeDriver
    service = Service(ChromeDriverManager().install())

    # Initialiser le driver Chromium
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.binary_location = '/usr/bin/chromium-browser'

    driver = webdriver.Chrome(service=service, options=options)

    # Ouvrir la page web
    driver.get(url)

    try:
        # Attendre que le tableau soit chargé
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, "table"))
        )

        # Obtenir le contenu de la page et l'analyser avec BeautifulSoup
        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Trouver le tableau contenant les informations
        table = soup.find("table")

        # Trouver la valeur du span
        result_span = soup.find("span", class_="result")

        if table:
            # Extraire les en-têtes du tableau
            headers = [header.text.strip() for header in table.find_all("th")]

            # Extraire les lignes du tableau
            rows = []
            for row in table.find_all("tr"):
                cols = [col.text.strip() for col in row.find_all("td")]
                if cols:
                    rows.append(cols)

            # Créer un DataFrame
            df = pd.DataFrame(rows, columns=headers)

            # Extraire la valeur du span et la convertir en float
            moyenne = float(result_span.text.strip()) if result_span else 0.0

            # Calculer moyenne_orientation
            if len(df) >= 3:
                moyenne_orientation = (
                    (float(df['النتيجة'][0]) * 3) +
                    (float(df['النتيجة'][1]) * 2) +
                    (float(df['النتيجة'][2]) * 1) +
                    moyenne
                ) / 7
            else:
                moyenne_orientation = None  # Gérer le cas où il y a moins de 3 lignes

            # Ajouter moyenne_orientation au DataFrame
            df['moyenne_orientation'] = moyenne_orientation

            return df, moyenne_orientation
        else:
            return None, None
    finally:
        # Fermer le navigateur
        driver.quit()

# Interface Streamlit
st.title('Extraction des Informations du Site Web')
matricule = st.text_input('Entrez votre matricule :')

if matricule:
    df, moyenne_orientation = scrape_data(matricule)
    if df is not None:
        st.write(df)
        st.write(f'Moyenne Orientation: {moyenne_orientation}')
    else:
        st.write("Table non trouvée sur la page web.")
