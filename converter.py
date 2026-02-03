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
        # header=None ist wichtig, da keine Überschriften existieren
        df = pd.read_excel(uploaded_file, header=None)
        
        st.write("### Vorschau der erkannten Daten:")
        st.dataframe(df.head()) # Zeigt die ersten Zeilen zur Kontrolle
        
        zip_buffer = BytesIO()
        contact_count = 0
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for index, row in df.iterrows():
                # Funktion zur sicheren Datenextraktion
                def get_v(col_index):
                    try:
                        val = row[col_index]
                        return str(val).strip() if pd.notna(val) else ""
                    except:
                        return ""

                # Spalten-Mapping basierend auf Ihrer Beschreibung (A=0, B=1, ...)
                firma    = get_v(0) # Spalte A
                name     = get_v(1) # Spalte B
                vorname  = get_v(2) # Spalte C
                abt      = get_v(3) # Spalte D
                adr      = get_v(4) # Spalte E
                tel      = get_v(5) # Spalte F
                mobil    = get_v(6) # Spalte G
                email    = get_v(7) # Spalte H
                url      = get_v(8) # Spalte I

                # Wir erstellen eine vCard, solange IRGENDETWAS in der Zeile steht
                if any([name, vorname, firma, email]):
                    vcard = [
                        "BEGIN:VCARD",
                        "VERSION:3.0",
                        f"N:{name};{vorname};;;",
                        f"FN:{vorname} {name}".strip(),
                        f"ORG:{firma};{abt}",
                        f"TEL;TYPE=WORK,VOICE:{tel}",
                        f"TEL;TYPE=CELL,VOICE:{mobil}",
                        f"ADR;TYPE=WORK:;;{adr};;;",
                        f"EMAIL;TYPE=PREF,INTERNET:{email}",
                        f"URL:{url}",
                        "END:VCARD"
                    ]
                    vcard_str = "\n".join(vcard)
                    
                    # Dateiname: Nutze Name oder Index falls Name fehlt
                    display_name = f"{vorname}_{name}".strip() or f"Kontakt_{index+1}"
                    filename = f"{display_name}.vcf".replace("/", "-")
                    
                    zip_file.writestr(filename, vcard_str)
                    contact_count += 1

        if contact_count > 0:
            st.success(f"✅ {contact_count} vCards wurden erfolgreich erstellt!")
            st.download_button(
                label="📥 ZIP-Archiv herunterladen",
                data=zip_buffer.getvalue(),
                file_name="visitenkarten_export.zip",
                mime="application/zip"
            )
        else:
            st.warning("⚠️ Keine Daten gefunden. Prüfen Sie, ob die Excel-Datei in den Spalten A bis I Daten enthält.")


