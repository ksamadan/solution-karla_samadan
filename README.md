# TicketHub

TicketHub je middleware REST servis za support tickete.

Aplikacija dohvaća početne podatke iz DummyJSON API-ja, transformira ih u vlastiti Ticket model i sprema ih u lokalnu bazu podataka. Nakon toga svi read i write endpointi rade nad lokalnom bazom, a ne direktno nad vanjskim API-jem.

## Tehnologije

Projekt koristi:

- Python 3.11
- FastAPI
- httpx
- Pydantic
- SQLAlchemy
- Alembic
- SQLite
- pytest
- Docker
- GitHub Actions

## Struktura projekta

```text
.
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── external.py
│   └── routes/
│       ├── __init__.py
│       └── tickets.py
├── tests/
│   └── test_tickets.py
├── alembic/
│   ├── env.py
│   └── versions/
│       └── 001_create_tickets.py
├── .github/
│   └── workflows/
│       └── ci.yml
├── alembic.ini
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── Makefile
├── .gitignore
└── README.md
```

## Instalacija

Prvo je potrebno napraviti virtualno okruženje.

```bash
python -m venv .venv
```

Aktivacija virtualnog okruženja na Windowsu:

```bash
.venv\Scripts\activate
```

Aktivacija virtualnog okruženja na macOS/Linuxu:

```bash
source .venv/bin/activate
```

Instalacija potrebnih paketa:

```bash
pip install -r requirements.txt
```

## Konfiguracija

Projekt koristi SQLite bazu podataka.

Zadana baza je:

```text
tickethub.db
```

Trenutno nisu potrebne dodatne environment varijable za lokalno pokretanje.

## Migracije baze

Projekt koristi Alembic migracije.

Za kreiranje tablice u bazi pokrenuti:

```bash
alembic upgrade head
```

Nakon toga će se stvoriti SQLite baza `tickethub.db`.

## Pokretanje aplikacije

Aplikacija se pokreće naredbom:

```bash
uvicorn src.main:app --reload
```

Nakon pokretanja API je dostupan na:

```text
http://127.0.0.1:8000
```

Automatska Swagger dokumentacija dostupna je na:

```text
http://127.0.0.1:8000/docs
```

ReDoc dokumentacija dostupna je na:

```text
http://127.0.0.1:8000/redoc
```

## Punjenje baze početnim podacima

Početni podaci dohvaćaju se iz DummyJSON servisa:

```text
https://dummyjson.com/todos
https://dummyjson.com/users
```

Za dohvat i spremanje početnih ticketa u lokalnu bazu koristi se endpoint:

```http
POST /sync
```

Podaci se transformiraju ovako:

- `todo` postaje `title`
- `completed == true` postaje status `closed`
- `completed == false` postaje status `open`
- `priority` se računa pomoću `id % 3`
- `assignee` se dohvaća iz korisnika preko `userId`
- originalni JSON sprema se u `source_json`

## Endpointi

### Health check

```http
GET /health
```

Provjerava radi li servis.

Primjer odgovora:

```json
{
  "status": "ok"
}
```

---

### Lista ticketa

```http
GET /tickets
```

Vraća paginiranu listu ticketa.

Primjer:

```http
GET /tickets?limit=10&offset=0
```

Lista vraća:

- `id`
- `title`
- `status`
- `priority`
- `description`, skraćen na najviše 100 znakova

---

### Filtriranje ticketa

```http
GET /tickets?status=open
GET /tickets?priority=high
GET /tickets?status=closed&priority=medium
```

Moguće vrijednosti za `status`:

```text
open
closed
```

Moguće vrijednosti za `priority`:

```text
low
medium
high
```

---

### Detalji ticketa

```http
GET /tickets/{id}
```

Vraća detalje jednog ticketa i originalni JSON iz vanjskog izvora.

Primjer:

```http
GET /tickets/1
```

---

### Pretraga ticketa

```http
GET /tickets/search?q=login
```

Pretražuje tickete po naslovu.

---

### Kreiranje novog ticketa

```http
POST /tickets
```

Primjer bodyja:

```json
{
  "title": "Problem with login",
  "description": "User cannot log in",
  "status": "open",
  "priority": "high",
  "assignee": "karla"
}
```

Ovaj endpoint validira ulazne podatke i sprema novi ticket u bazu.

---

### Izmjena ticketa

```http
PATCH /tickets/{id}
```

Primjer bodyja:

```json
{
  "status": "closed",
  "priority": "high"
}
```

Promjena se sprema u bazu i ostaje sačuvana nakon restarta servisa.

---

### Statistika

```http
GET /stats
```

Vraća agregirane statistike:

- ukupan broj ticketa
- broj otvorenih ticketa
- broj zatvorenih ticketa
- broj ticketa po prioritetu

Primjer odgovora:

```json
{
  "total": 30,
  "open": 18,
  "closed": 12,
  "low": 10,
  "medium": 10,
  "high": 10
}
```

## Pokretanje testova

Testovi se pokreću naredbom:

```bash
pytest
```

Testovi provjeravaju:

- health-check endpoint
- kreiranje ticketa
- dohvat liste ticketa
- izmjenu ticketa
- pretragu ticketa

## Makefile naredbe

Ako se koristi Makefile, dostupne su sljedeće naredbe:

```bash
make install
```

Instalira potrebne pakete.

```bash
make migrate
```

Pokreće Alembic migracije.

```bash
make run
```

Pokreće FastAPI aplikaciju.

```bash
make test
```

Pokreće testove.

```bash
make docker-build
```

Gradi Docker image.

## Docker

Build Docker imagea:

```bash
docker build -t tickethub .
```

Pokretanje aplikacije preko Docker Composea:

```bash
docker compose up --build
```

Aplikacija je nakon toga dostupna na:

```text
http://127.0.0.1:8000
```

## CI

Projekt koristi GitHub Actions workflow.

CI pokreće instalaciju dependenciesa i testove pri pushu ili pull requestu na `main` branch.

## Korištenje ChatGPT-a

ChatGPT je korišten kao pomoć pri:

- razumijevanju zadatka
- strukturiranju FastAPI projekta
- pisanju početnog kostura koda
- pisanju SQLAlchemy modela
- pisanju Pydantic shema
- pisanju osnovnih endpointova
- pisanju osnovnih testova
- pisanju README dokumentacije
