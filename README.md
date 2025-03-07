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

### Dependințe Python
Instalează dependințele folosind `pip`:
```bash
pip install streamlit pandas sqlite3 zeep requests beautifulsoup4 urllib3