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
        
        
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for index, row in df.iterrows():
                # Zuordnung nach Spalten-Index (A=0, B=1, C=2, ...)
                def val(idx):
                    v = row[idx] if idx in row else ""
                    return str(v).strip() if pd.notna(v) else ""

                firma   = val(0) # A
                name    = val(1) # B
                vorname = val(2) # C
                abt     = val(3) # D
                adr     = val(4) # E
                tel     = val(5) # F
                mobil   = val(6) # G
                email   = val(7) # H
                url     = val(8) # I

                if name or vorname:
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
                    vcard_content = "\n".join(vcard)
                    
                    # Dateiname generieren
                    safe_name = f"{vorname}_{name}".replace(" ", "_")
                    filename = f"Kontakt_{index+1}_{safe_name}.vcf"
                    zip_file.writestr(filename, vcard_content)

        if zip_buffer.tell() > 0:
            st.success(f"{len(df)} Kontakte im ZIP-Archiv bereit!")
            st.download_button(
                label="📥 ZIP herunterladen",
                data=zip_buffer.getvalue(),
                file_name="visitenkarten_export.zip",
                mime="application/zip"
            )

