import streamlit as st
import pandas as pd
from io import BytesIO
import zipfile

def check_password():
    """Gibt True zurück, wenn das Passwort korrekt ist."""
    def password_entered():
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Passwort aus Speicher löschen
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        st.text_input("Bitte Passwort eingeben", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        st.text_input("Bitte Passwort eingeben", type="password", on_change=password_entered, key="password")
        st.error("😕 Passwort falsch")
        return False
    return True

if check_password():
    # Hier folgt Ihr restlicher Code (Datei-Upload, etc.)
    st.write("Willkommen! Sie können nun Daten verarbeiten.")

    # Datei-Upload
    uploaded_file = st.file_uploader("Excel-Datei auswählen", type=["xlsx"])
    
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        
        # Buffer für das ZIP-Archiv im Speicher
        zip_buffer = BytesIO()
        
        with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_file:
            for index, row in df.iterrows():
                # vCard-Logik
                vcard = [
                    "BEGIN:VCARD", "VERSION:3.0",
                    f"N:{row.get('Name','')};{row.get('Vorname','')};;;",
                    f"FN:{row.get('Vorname','')} {row.get('Name','')}",
                    f"ORG:{row.get('Firma','')};{row.get('Abteilung','')}",
                    f"TEL;TYPE=WORK,VOICE:{row.get('Telefon','')}",
                    f"TEL;TYPE=CELL,VOICE:{row.get('Mobiltelefon','')}",
                    f"ADR;TYPE=WORK:;;{row.get('Adresse','')};;;",
                    f"EMAIL;TYPE=PREF,INTERNET:{row.get('Email','')}",
                    f"URL:{row.get('URL','')}",
                    "END:VCARD"
                ]
                vcard_content = "\n".join(vcard)
                
                # Datei dem ZIP hinzufügen
                filename = f"{row.get('Vorname','unbekannt')}_{row.get('Name','kontakt')}.vcf"
                zip_file.writestr(filename, vcard_content)

        # Download Button
        st.success(f"{len(df)} Kontakte verarbeitet!")
        st.download_button(
            label="📥 ZIP mit allen vCards herunterladen",
            data=zip_buffer.getvalue(),
            file_name="visitenkarten.zip",
            mime="application/zip"
        )
