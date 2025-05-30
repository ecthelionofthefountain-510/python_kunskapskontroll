# Kunskapskontroll – Python

Detta repo innehåller min inlämning för kunskapskontrollen i Python. Arbetet är uppdelat i två (eller tre) delar och inkluderar även en Streamlit-applikation för interaktiv dataanalys.

---

## Innehåll

- `part_1.ipynb` – Teoretiska frågor och Python-övningar
- `part_2.ipynb` – Dataanalys av diamantdata (data story)
- `streamlit_app.py` – Streamlit-applikation för interaktiv analys

---

## Del 1 – Teoretiska frågor och Python-övningar

I denna notebook besvaras bland annat:
- Skillnaden mellan tuple och list
- Funktioners syfte och användning
- Begrepp kopplat till klasser (instans, attribut, metod)
- Vad Streamlit är
- Skapande och test av en egen klass (`BankAccount`)
- Kodtest: räkna vokaler i en sträng, hitta gemensamma element i två listor
- Resonemang kring statistik, kausalitet och olika diagramtyper
- Självutvärdering kring arbetet

---

## Del 2 – Dataanalys av diamantdata

I denna notebook analyseras ett stort dataset med diamanter utifrån ett affärscase för Guldfynd.

Analysen innehåller:
- Datastädning och kontroll av datakvalitet
- Visualiseringar av pris, carat, färg, klarhet och samband mellan variabler
- Tolkning av korrelationsmatris
- Lärdomar och rekommendationer i en executive summary
- Data storytelling: kod, visualisering och text varvas för att skapa en röd tråd

---

## Streamlit-applikation

`streamlit_app.py` är en interaktiv webbapplikation där användaren kan:
- Filtrera diamanter på pris, carat, färg, klarhet och slipning
- Utforska de viktigaste diagrammen från analysen (prisfördelning, pris vs carat, pris per klarhet/färg, korrelationsmatris)
- Ladda ner filtrerad data
- Läsa en sammanfattning av de viktigaste insikterna

Appen fokuserar på kvalitet framför kvantitet och visar endast de mest relevanta diagrammen för beslutsfattare.

---

## Så här kör du

1. Klona repot och installera beroenden
2. Starta Jupyter Notebook för att läsa och köra `part_1.ipynb` och `part_2.ipynb`
3. Starta Streamlit-appen med:

streamlit run streamlit_app.py

4. Se till att filen `diamonds_clean.csv` finns i projektmappen (skapas automatiskt av notebooken).

---

## Om projektet

Syftet är att visa förståelse för både grundläggande Python och dataanalys, samt att kunna kommunicera insikter på ett tydligt sätt – både i kod och visuellt.  
Analysen är utformad som en "data story" och Streamlit-appen är anpassad för att ge beslutsfattare en snabb överblick av diamantmarknaden.

---