# Just Dosar Request

## Descriere

`just_dosar_request` este o aplicație web dezvoltată cu **Streamlit** care permite căutarea și afișarea detaliilor despre dosarele judiciare din România, utilizând portalul oficial `portal.just.ro`. Aplicația face următoarele:

- **Caută dosare** folosind API-ul SOAP al portalului just.ro, pe baza criteriilor precum numărul dosarului, obiectul dosarului, numele unei părți, instanța și intervalul de timp.
- **Extrage link-uri** pentru fiecare dosar prin web scraping de pe `portal.just.ro`, astfel încât utilizatorii să poată accesa direct pagina dosarului.
- **Afișează detaliile** dosarelor într-un tabel interactiv, cu posibilitatea de a selecta un dosar pentru a vedea informații detaliate (părți implicate, ședințe, documente).
- **Exportă rezultatele** într-un fișier CSV pentru utilizare ulterioară.

Aplicația este utilă pentru avocați, juriști sau orice persoană interesată să acceseze rapid informații despre dosarele judiciare din România.

## Cerințe

Pentru a rula aplicația, ai nevoie de următoarele:

**Python 3.12.9**

### Dependințe Python
Instalează dependințele folosind `pip`:
```bash
pip install streamlit pandas sqlite3 zeep requests beautifulsoup4 urllib3
```
**Bază de date SQLite**
Aplicația necesită o bază de date SQLite numită instante.db care conține o tabelă instante cu o coloană nume ce listează instanțele disponibile (ex. "JudecatoriaBRASOV").
Poți crea această bază de date manual sau folosi un script pentru a o popula cu instanțele de pe portal.just.ro.

**Conexiune la internet**
Aplicația face cereri SOAP către http://portalquery.just.ro/query.asmx?wsdl și cereri HTTP către https://portal.just.ro pentru web scraping.

**Instalare și Utilizare**
Clonează repository-ul:
```
git clone https://github.com/gelu-constantin/just_dosar_request.git
cd just_dosar_request
```
Instalează dependințele:
```
pip install -r requirements.txt
```
(Notă: Creează un fișier requirements.txt cu dependințele listate mai sus dacă dorești să folosești această comandă.)

Asigură-te că ai instante.db:
Plasează fișierul instante.db în același director cu main.py.

**Rulează aplicația:**
```
streamlit run main.py
```
Aplicația se va deschide în browser-ul tău implicit (de obicei la http://localhost:8501).

**Utilizare:**
Selectează o instanță sau bifează "Caută în toate instanțele" ( nu se recomanda inca - e in lucru procedura de extragere a id-ului).
Introdu criteriile de căutare (număr dosar, obiect dosar, nume parte, interval de timp).
Apasă butonul "Caută" pentru a vedea rezultatele.
Dă **click** pe un număr de dosar din tabel pentru a accesa pagina oficială a dosarului pe portal.just.ro.
Selectează un dosar din tabel pentru a vedea detaliile complete (părți, ședințe, documente).
Descarcă rezultatele ca fișier CSV dacă dorești.

**Structura Proiectului**
**main.py**: Scriptul principal care rulează aplicația Streamlit.
**instante.db**: Baza de date SQLite cu lista instanțelor (nu este inclusă în repository; trebuie creată separat).
**README.md**: Documentația proiectului.

**Note**
Performanță: Căutarea și web scraping-ul pot dura mai mult dacă sunt multe dosare sau instanțe. Aplicația include o pauză de 2 secunde între instanțe pentru a evita supraîncărcarea serverului.
Erori: Dacă apar erori la accesarea SOAP sau a portalului, acestea vor fi afișate în interfață.
Limitări: Unele dosare pot să nu aibă anumite atribute (ex. documente, ședințe), caz în care se va afișa "N/A".

**Contribuții**
Dacă dorești să contribui, te rugăm să creezi un pull request sau să raportezi probleme în secțiunea Issues a repository-ului.

Autor
Gelu Constantin (gelu-constantin)
