# Test Atleti — WebApp Base

App per accedere, visualizzare e inserire i risultati dei test fisici degli atleti (salto verticale, sprint, ecc.). I tipi di test sono **personalizzabili**: si aggiungono dalla pagina "Gestisci Tipi di Test", senza modificare il codice.

## Come avviarla sul tuo computer

1. Assicurati di avere Python installato (versione 3.9 o superiore).
2. Apri il terminale nella cartella del progetto e crea un ambiente virtuale (consigliato, ma non obbligatorio):
   ```
   python -m venv venv
   ```
   Attivalo:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
3. Installa le dipendenze:
   ```
   pip install -r requirements.txt
   ```
4. Avvia l'app:
   ```
   streamlit run app.py
   ```
5. Si aprirà automaticamente nel browser, di solito su `http://localhost:8501`.

Al primo avvio viene creato in automatico un file `test_atleti.db`: è il database, con dentro già 3 tipi di test di esempio (Salto Verticale, Salto in Lungo, Sprint 20m).

## Credenziali di accesso

Username di default: `admin`
Password di default: `cambiami123`

**Cambiale prima di usare l'app con un cliente vero.** Apri `app.py`, trova questa parte in cima al file:

```python
CREDENZIALI = {
    "admin": hashlib.sha256("cambiami123".encode()).hexdigest(),
}
```

Per generare l'hash di una nuova password, apri un terminale Python (scrivi `python` nel terminale) ed esegui:
```python
import hashlib
hashlib.sha256("la_tua_nuova_password".encode()).hexdigest()
```
Copia il risultato e sostituiscilo al posto dell'hash esistente.

## Come personalizzare per un cliente (la parte "moddabile")

Dalla pagina **⚙️ Gestisci Tipi di Test**, il cliente (o tu per conto suo) può aggiungere qualsiasi metrica voglia monitorare — nome e unità di misura — senza toccare una riga di codice. Il form di inserimento e i grafici si adattano automaticamente ai nuovi test aggiunti.

## Struttura dei file

- `app.py` — l'interfaccia dell'app (login, menu, pagine)
- `database.py` — tutte le funzioni che leggono/scrivono nel database
- `test_atleti.db` — il database (creato automaticamente al primo avvio, non lo devi toccare a mano)
- `requirements.txt` — elenco delle librerie necessarie

## Limiti di questa versione base (e prossimi passi)

Questa versione è pensata per validare l'idea in fretta con i primi clienti reali:

- **Un solo database locale per installazione** — va bene per un cliente alla volta. Se in futuro vuoi gestire più clienti da un'unica app online condivisa, andrà migrata a un database "vero" online (es. Supabase), mantenendo la stessa logica di tabelle già pensata.
- **Login semplice** — un solo utente amministratore. Se serve un login per ogni atleta o più ruoli diversi, va costruito un sistema di autenticazione più completo.
- **Deploy online** — per metterla a disposizione di un cliente senza farla girare sul tuo pc, puoi pubblicarla gratuitamente su [Streamlit Community Cloud](https://streamlit.io/cloud): basta collegare il repository GitHub del progetto.

## Prossimo passo consigliato

Prova l'app con dati finti per qualche giorno, poi mostrala a 1-2 allenatori reali e raccogli feedback prima di aggiungere altre funzionalità.
