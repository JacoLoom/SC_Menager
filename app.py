"""
WebApp Test Atleti - versione base
------------------------------------
Un allenatore/preparatore accede con delle credenziali, gestisce i suoi
atleti, inserisce i risultati dei test (es. salto verticale) e vede
l'andamento nel tempo. I "tipi di test" sono personalizzabili: si possono
aggiungere nuove metriche dalla pagina "Gestisci Tipi di Test", senza
toccare il codice. Questa è la parte che rende l'app "moddabile" per
ogni cliente.
"""

import hashlib
from datetime import date

import streamlit as st

import database as db

st.set_page_config(page_title="Test Atleti", page_icon="🏃", layout="wide")

# ---------------------------------------------------------
# CREDENZIALI DI ACCESSO
# Cambia qui username e password. La password non è salvata in chiaro:
# viene confrontata come "impronta" (hash SHA256), non come testo puro.
#
# Per generare l'hash di una nuova password, apri un terminale Python
# ed esegui:
#   import hashlib
#   hashlib.sha256("la_tua_nuova_password".encode()).hexdigest()
# poi incolla il risultato qui sotto al posto dell'hash esistente.
# ---------------------------------------------------------
CREDENZIALI = {
    "admin": hashlib.sha256("admin".encode()).hexdigest(),
}


def verifica_credenziali(username: str, password: str) -> bool:
    hash_inserito = hashlib.sha256(password.encode()).hexdigest()
    return CREDENZIALI.get(username) == hash_inserito


def pagina_login():
    st.title("🔐 Accedi")
    st.caption("Usa le credenziali fornite dal tuo amministratore.")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        invia = st.form_submit_button("Accedi")

    if invia:
        if verifica_credenziali(username, password):
            st.session_state.logged_in = True
            st.session_state.username = username
            st.rerun()
        else:
            st.error("Username o password non corretti.")


def pagina_atleti():
    st.header("📋 Atleti")

    with st.expander("➕ Aggiungi un nuovo atleta"):
        with st.form("form_nuovo_atleta", clear_on_submit=True):
            nome = st.text_input("Nome")
            cognome = st.text_input("Cognome")
            data_nascita = st.date_input("Data di nascita", value=None)
            note = st.text_area("Note (opzionale)")
            submit = st.form_submit_button("Salva atleta")

        if submit:
            if nome.strip() == "" or cognome.strip() == "":
                st.warning("Nome e cognome sono obbligatori.")
            else:
                db.add_atleta(nome, cognome, str(data_nascita) if data_nascita else "", note)
                st.success(f"Atleta {nome} {cognome} aggiunto.")
                st.rerun()

    st.subheader("Elenco atleti")
    atleti_df = db.get_atleti()

    if atleti_df.empty:
        st.info("Non ci sono ancora atleti. Aggiungine uno dal pannello sopra.")
        return

    st.dataframe(atleti_df, use_container_width=True, hide_index=True)

    st.subheader("Elimina un atleta")
    opzioni = {f"{r.nome} {r.cognome} (id {r.id})": r.id for r in atleti_df.itertuples()}
    scelta = st.selectbox("Seleziona atleta da eliminare", options=list(opzioni.keys()))
    if st.button("Elimina atleta", type="primary"):
        db.delete_atleta(opzioni[scelta])
        st.success("Atleta eliminato.")
        st.rerun()


def pagina_inserisci_test():
    st.header("➕ Inserisci un risultato di test")

    atleti_df = db.get_atleti()
    tipi_df = db.get_tipi_test()

    if atleti_df.empty:
        st.warning("Aggiungi prima almeno un atleta nella sezione 'Atleti'.")
        return
    if tipi_df.empty:
        st.warning("Aggiungi prima almeno un tipo di test nella sezione 'Gestisci Tipi di Test'.")
        return

    atleti_opzioni = {f"{r.nome} {r.cognome}": r.id for r in atleti_df.itertuples()}
    tipi_opzioni = {f"{r.nome} ({r.unita_misura})": r.id for r in tipi_df.itertuples()}

    with st.form("form_risultato", clear_on_submit=True):
        atleta_scelto = st.selectbox("Atleta", options=list(atleti_opzioni.keys()))
        tipo_scelto = st.selectbox("Tipo di test", options=list(tipi_opzioni.keys()))
        valore = st.number_input("Valore misurato", step=0.1, format="%.2f")
        data_test = st.date_input("Data del test", value=date.today())
        note = st.text_area("Note (opzionale)")
        submit = st.form_submit_button("Salva risultato")

    if submit:
        db.add_risultato(
            atleta_id=atleti_opzioni[atleta_scelto],
            tipo_test_id=tipi_opzioni[tipo_scelto],
            valore=valore,
            data=str(data_test),
            note=note,
        )
        st.success("Risultato salvato.")


def pagina_storico():
    st.header("📈 Storico e grafici")

    atleti_df = db.get_atleti()
    if atleti_df.empty:
        st.info("Non ci sono ancora atleti registrati.")
        return

    atleti_opzioni = {f"{r.nome} {r.cognome}": r.id for r in atleti_df.itertuples()}
    atleta_scelto = st.selectbox("Seleziona atleta", options=list(atleti_opzioni.keys()))
    atleta_id = atleti_opzioni[atleta_scelto]

    risultati_df = db.get_risultati(atleta_id)

    if risultati_df.empty:
        st.info("Nessun risultato registrato per questo atleta.")
        return

    st.subheader("Tabella risultati")
    st.dataframe(risultati_df, use_container_width=True, hide_index=True)

    st.subheader("Andamento nel tempo")
    tipi_presenti = risultati_df["tipo_test"].unique()
    tipo_grafico = st.selectbox("Scegli il test da visualizzare nel grafico", options=tipi_presenti)

    dati_grafico = (
        risultati_df[risultati_df["tipo_test"] == tipo_grafico]
        .sort_values("data")
        .set_index("data")[["valore"]]
    )
    st.line_chart(dati_grafico)


def pagina_gestisci_tipi_test():
    st.header("⚙️ Gestisci tipi di test")
    st.caption(
        "Questa è la parte personalizzabile dell'app: qui puoi aggiungere "
        "i test specifici che vuoi monitorare, oltre a quelli già presenti."
    )

    with st.expander("➕ Aggiungi un nuovo tipo di test"):
        with st.form("form_nuovo_tipo", clear_on_submit=True):
            nome_test = st.text_input("Nome del test (es. Salto Verticale)")
            unita = st.text_input("Unità di misura (es. cm, sec, kg)")
            submit = st.form_submit_button("Aggiungi tipo di test")

        if submit:
            if nome_test.strip() == "" or unita.strip() == "":
                st.warning("Compila entrambi i campi.")
            else:
                try:
                    db.add_tipo_test(nome_test, unita)
                    st.success(f"Tipo di test '{nome_test}' aggiunto.")
                    st.rerun()
                except Exception:
                    st.error("Esiste già un tipo di test con questo nome.")

    st.subheader("Tipi di test esistenti")
    tipi_df = db.get_tipi_test()
    st.dataframe(tipi_df, use_container_width=True, hide_index=True)

    if not tipi_df.empty:
        st.subheader("Elimina un tipo di test")
        opzioni = {f"{r.nome} ({r.unita_misura})": r.id for r in tipi_df.itertuples()}
        scelta = st.selectbox("Seleziona tipo di test da eliminare", options=list(opzioni.keys()))
        if st.button("Elimina tipo di test", type="primary"):
            db.delete_tipo_test(opzioni[scelta])
            st.success("Tipo di test eliminato.")
            st.rerun()


def app_principale():
    st.sidebar.title("🏃 Test Atleti")
    st.sidebar.write(f"Utente: **{st.session_state.username}**")

    pagina = st.sidebar.radio(
        "Menu",
        ["📋 Atleti", "➕ Inserisci Test", "📈 Storico e Grafici", "⚙️ Gestisci Tipi di Test"],
    )

    st.sidebar.divider()
    if st.sidebar.button("Esci"):
        st.session_state.logged_in = False
        st.rerun()

    if pagina == "📋 Atleti":
        pagina_atleti()
    elif pagina == "➕ Inserisci Test":
        pagina_inserisci_test()
    elif pagina == "📈 Storico e Grafici":
        pagina_storico()
    elif pagina == "⚙️ Gestisci Tipi di Test":
        pagina_gestisci_tipi_test()


def main():
    db.init_db()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        app_principale()
    else:
        pagina_login()


if __name__ == "__main__":
    main()
