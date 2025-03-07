import streamlit as st
import pandas as pd
import sqlite3
from zeep import Client
from datetime import datetime
import unicodedata
import re
import requests
from bs4 import BeautifulSoup
import time
import urllib3

# Dezactivare avertismente SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 📌 Funcție pentru a citi și formata instanțele din SQLite
def get_instante():
    conn = sqlite3.connect("instante.db")
    cursor = conn.cursor()
    query = "SELECT nume FROM instante ORDER BY nume"
    cursor.execute(query)
    instante = [normalize_name(row[0]) for row in cursor.fetchall()]
    conn.close()
    return instante

# 📌 Funcție pentru eliminarea diacriticelor și a spațiilor din nume
def normalize_name(nume):
    nume_fara_diacritice = ''.join(
        c for c in unicodedata.normalize('NFD', nume)
        if unicodedata.category(c) != 'Mn'
    )
    nume_formatat = re.sub(r'\s+', '', nume_fara_diacritice)
    return nume_formatat

# 📌 Funcție pentru a căuta link-ul unui dosar pe portal.just.ro
def get_dosar_link(numar_dosar):
    search_url = f"https://portal.just.ro/SitePages/cautare.aspx?k={numar_dosar}"
    try:
        response = requests.get(search_url, verify=False)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        for link_tag in soup.find_all('a', href=True, string=re.compile(numar_dosar)):
            dosar_number = link_tag.text.strip()
            if dosar_number == numar_dosar:  # Verificăm exact numărul dosarului
                # Construim link-ul corect, eliminând orice `..`
                href = link_tag['href']
                if ".." in href:
                    href = href.replace("..", "")
                full_link = "https://portal.just.ro" + href
                return full_link
    except Exception as e:
        st.warning(f"Eroare la accesarea link-ului pentru dosar {numar_dosar}: {e}")
    return "#"

# 📌 Inițializare client SOAP
wsdl_url = "http://portalquery.just.ro/query.asmx?wsdl"
try:
    client = Client(wsdl_url)
except Exception as e:
    st.error(f"Eroare la inițializarea clientului SOAP: {e}")
    st.stop()

# 📌 Interfață Streamlit
st.title("Căutare Dosare Justiție România")

# 📌 Obținem lista de instanțe
instante_lista = get_instante()

# Selectăm instanța (dropdown cu search activat)
if instante_lista:
    toate_instantele = st.checkbox("Caută în toate instanțele")
    if toate_instantele:
        institutie_nume = None
    else:
        institutie_nume = st.selectbox("Selectează instanța", instante_lista)
else:
    st.warning("⚠️ Nicio instanță găsită!")
    institutie_nume = None

# 📌 Formular pentru parametri de căutare
numar_dosar = st.text_input("Număr Dosar (ex. 123/2023)", "").strip()
obiect_dosar = st.text_input("Obiect Dosar (opțional)", "").strip()
nume_parte = st.text_input("Nume Parte (opțional)", "").strip()
data_start = st.date_input("Data Început", datetime(2020, 1, 1))
data_stop = st.date_input("Data Sfârșit", datetime.now())

# 📌 Buton de căutare
if st.button("Caută"):
    if not numar_dosar and not obiect_dosar and not nume_parte:
        st.warning("Introdu cel puțin un criteriu de căutare (Număr Dosar, Obiect Dosar sau Nume Parte).")
    elif toate_instantele and not instante_lista:
        st.warning("Nu există instanțe disponibile!")
    else:
        dosare_data = []
        instante_de_cautat = instante_lista if toate_instantele else [institutie_nume]
        
        for instanta in instante_de_cautat:
            params = {
                "numarDosar": numar_dosar if numar_dosar else None,
                "obiectDosar": obiect_dosar if obiect_dosar else None,
                "numeParte": nume_parte if nume_parte else None,
                "institutie": instanta,
                "dataStart": datetime.combine(data_start, datetime.min.time()),
                "dataStop": datetime.combine(data_stop, datetime.min.time())
            }
            
            with st.spinner(f"Se caută în {instanta}..."):
                try:
                    response = client.service.CautareDosare(**params)
                    if response:
                        for dosar in response:
                            # Obținem link-ul pentru fiecare dosar individual
                            dosar_link = get_dosar_link(dosar.numar)

                            # Gestionăm părțile
                            parti_details = []
                            parti = getattr(dosar, 'parti', None)
                            if parti and hasattr(parti, 'DosarParte'):
                                for parte in parti.DosarParte:
                                    parte_info = (
                                        f"Nume: {parte.nume}\n"
                                        f"Calitate: {parte.calitateParte}\n"
                                        f"ID Parte: {getattr(parte, 'idParte', 'N/A')}"
                                    )
                                    parti_details.append(parte_info)
                            parti_text = "\n\n".join(parti_details) if parti_details else "N/A"

                            # Gestionăm ședințele
                            sedinte_details = []
                            sedinte = getattr(dosar, 'sedinte', None)
                            if sedinte and hasattr(sedinte, 'DosarSedinta'):
                                for sedinta in sedinte.DosarSedinta:
                                    sedinta_info = (
                                        f"Data: {sedinta.data.strftime('%Y-%m-%d %H:%M:%S')}\n"
                                        f"Complet: {sedinta.complet}\n"
                                        f"Ora: {getattr(sedinta, 'ora', 'N/A')}\n"
                                        f"Tip Soluție: {getattr(sedinta, 'tipSolutie', 'N/A')}\n"
                                        f"Soluție: {sedinta.solutie}\n"
                                        f"Soluție Sumar: {getattr(sedinta, 'solutieSumar', 'N/A')}\n"
                                        f"Data Modificare: {getattr(sedinta, 'dataModificare', 'N/A')}"
                                    )
                                    sedinte_details.append(sedinta_info)
                            sedinte_text = "\n\n".join(sedinte_details) if sedinte_details else "N/A"

                            # Gestionăm documentele
                            documente_details = []
                            documente = getattr(dosar, 'documente', None)
                            if documente and hasattr(documente, 'DosarDocument'):
                                for doc in documente.DosarDocument:
                                    doc_info = (
                                        f"ID: {doc.id}\n"
                                        f"Data: {doc.data.strftime('%Y-%m-%d %H:%M:%S') if doc.data else 'N/A'}\n"
                                        f"Categorie: {doc.categorieDoc}\n"
                                        f"Descriere: {doc.descriere}"
                                    )
                                    documente_details.append(doc_info)
                            documente_text = "\n\n".join(documente_details) if documente_details else "N/A"

                            # Adăugăm datele dosarului, cu "Număr Dosar" ca text simplu, dar păstrăm link-ul separat
                            dosare_data.append({
                                "Număr Dosar": dosar.numar,  # Doar numărul dosarului, fără link vizibil
                                "Link Dosar": dosar_link,  # Link-ul este stocat separat
                                "Data Dosar": dosar.data.strftime('%Y-%m-%d') if dosar.data else "N/A",
                                "Instanța": dosar.institutie,
                                "Obiect Dosar": dosar.obiect,
                                "Categorie Caz": dosar.categorieCaz,
                                "Stadiu Procesual": dosar.stadiuProcesual,
                                "Data Modificare": getattr(dosar, 'dataModificare', 'N/A'),
                                "Număr Vechi": getattr(dosar, 'numarVechi', 'N/A'),
                                "Părți": parti_text,
                                "Ședințe": sedinte_text,
                                "Documente": documente_text
                            })
                except Exception as e:
                    st.error(f"Eroare la căutarea în instanța {instanta}: {e}")
                
            if toate_instantele:
                time.sleep(2)
        
        if not dosare_data:
            st.info("Nu s-au găsit dosare pentru criteriile specificate.")
        else:
            df = pd.DataFrame(dosare_data)

            # Transformăm "Număr Dosar" într-un link clicabil, dar afișăm doar numărul
            df_display = df.copy()
            df_display["Număr Dosar"] = df.apply(
                lambda row: f"[{row['Număr Dosar']}]({row['Link Dosar']})", axis=1
            )
            
            st.subheader("Rezultate")
            
            # Afișăm tabelul
            selected_row = st.dataframe(df_display, use_container_width=True, selection_mode="single-row", on_select="rerun")
            
            if selected_row.selection and "rows" in selected_row.selection and selected_row.selection["rows"]:
                selected_index = selected_row.selection["rows"][0]
                selected_dosar = df.iloc[selected_index]  # Folosim df original pentru detalii

                with st.expander(f"Detalii Dosar: {selected_dosar['Număr Dosar']}", expanded=True):
                    st.markdown("### Informații Generale")
                    st.write(f"**Număr Dosar**: [{selected_dosar['Număr Dosar']}]({selected_dosar['Link Dosar']})")
                    st.write(f"**Link Dosar**: [{selected_dosar['Link Dosar']}]({selected_dosar['Link Dosar']})")
                    st.write(f"**Data Dosar**: {selected_dosar['Data Dosar']}")
                    st.write(f"**Instanța**: {selected_dosar['Instanța']}")
                    st.write(f"**Obiect Dosar**: {selected_dosar['Obiect Dosar']}")
                    st.write(f"**Categorie Caz**: {selected_dosar['Categorie Caz']}")
                    st.write(f"**Stadiu Procesual**: {selected_dosar['Stadiu Procesual']}")
                    st.write(f"**Data Modificare**: {selected_dosar['Data Modificare']}")
                    st.write(f"**Număr Vechi**: {selected_dosar['Număr Vechi']}")

                    st.markdown("### Părți Implicate")
                    st.text(selected_dosar['Părți'])

                    st.markdown("### Ședințe")
                    st.text(selected_dosar['Ședințe'])

                    st.markdown("### Documente")
                    st.text(selected_dosar['Documente'])

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button("Descarcă rezultatele ca CSV", data=csv, file_name="dosare.csv", mime="text/csv")