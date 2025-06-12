# Manual d'Usuari - Bot de Preus de Combustible de Menorca

## Índex
1. [Introducció](#introducció)
2. [Començar a Utilitzar el Bot](#començar-a-utilitzar-el-bot)
3. [Funcionalitats Principals](#funcionalitats-principals)
4. [Funcionalitats Avançades](#funcionalitats-avançades)
5. [Sistema d'Alertes](#sistema-dalertes)
6. [Consultes en Línia](#consultes-en-línia)
7. [Secció d'Administració](#secció-dadministració)
8. [Comandaments Disponibles](#comandaments-disponibles)
9. [Resolució de Problemes](#resolució-de-problemes)

---

## Introducció

El **Bot de Preus de Combustible de Menorca** és un bot de Telegram que proporciona informació actualitzada sobre els preus dels combustibles a totes les estacions de servei de Menorca. Les dades s'actualitzen cada 10 minuts i provenen del Ministerio de Industria, Comercio y Turismo d'Espanya.

### Característiques Principals:
- ⛽️ Preus en temps real de totes les estacions de Menorca
- 📍 Cerca d'estacions per ubicació
- 🔔 Sistema d'alertes personalitzades
- 📊 Gràfics d'evolució de preus
- 🏘️ Filtratge per municipis
- 🚗 Informació de tots els tipus de combustible

---

## Començar a Utilitzar el Bot

### 1. Iniciar el Bot
- Cerca `@menorca_fuel_bot` a Telegram (nom d'exemple)
- Prem **Start** o envia `/start`
- Rebràs un missatge de benvinguda amb el menú principal

### 2. Menú Principal
El menú principal ofereix les següents opcions:

| Botó | Funcionalitat |
|------|---------------|
| 💶 **Per PREU** | Veure estacions més barates/cares |
| 🚗🚜 **Per COMBUSTIBLE** | Filtrar per tipus de combustible |
| 🏘 **Per MUNICIPI** | Veure estacions per municipi |
| 👁‍🗨 **+INFO** | Informació del bot i última actualització |
| 📊 **Gràfics de preus** | Veure evolució històrica de preus |
| 📍 **Aprop meu** | Trobar estacions properes |
| 🔔 **Alertes de preu** | Gestionar alertes personalitzades |

---

## Funcionalitats Principals

### 💶 Consulta per Preu

#### Estacions Més Barates
- Selecciona **💶 Per PREU** → **✅ 5 més barates**
- Mostra les 5 estacions amb els preus més baixos
- Per defecte mostra preus de Benzina 95 E5

#### Estacions Més Cares
- Selecciona **💶 Per PREU** → **‼️ 5 més cares**
- Mostra les 5 estacions amb els preus més alts

### 🚗🚜 Consulta per Combustible

El bot suporta els següents tipus de combustible:

| Combustible | Descripció |
|-------------|------------|
| 🟢 **Benzina 95 E5** | Gasolina estàndard |
| 🌟 **Benzina 95 E5 Premium** | Gasolina premium |
| ⚫️ **Gasoli A** | Dièsel estàndard |
| 🟡 **Gasoli B** | Dièsel agrícola |
| 🟠 **Gasoli Premium** | Dièsel premium |
| ⚪️ **GLP** | Gas liquat del petroli |

**Com utilitzar:**
1. Selecciona **🚗🚜 Per COMBUSTIBLE**
2. Tria el tipus de combustible desitjat
3. Veuràs les 5 estacions més barates per aquest combustible

### 🏘 Consulta per Municipi

#### Municipis Disponibles:
- **Maó** (Capital)
- **Ciutadella** 
- **Alaior**
- **Es Mercadal**
- **Ferreries**
- **Sant Lluís**
- **Fornells**

**Com utilitzar:**
1. Selecciona **🏘 Per MUNICIPI**
2. Tria el municipi desitjat
3. Veuràs totes les estacions del municipi amb preus de tots els combustibles disponibles
4. Pots crear una alerta directament des d'aquesta pantalla

---

## Funcionalitats Avançades

### 📊 Gràfics de Preus

Visualitza l'evolució històrica dels preus:

**Com generar un gràfic:**
1. Selecciona **📊 Gràfics de preus**
2. Tria el tipus de combustible
3. Selecciona el període:
   - **📅 Darrera setmana** (7 dies)
   - **📅 Darrer mes** (30 dies)
4. El bot generarà i enviarà un gràfic amb:
   - Preu mitjà diari
   - Rang mínim-màxim
   - Nombre d'estacions incloses

### 📍 Cerca per Ubicació

Troba estacions properes a la teva ubicació:

**Com utilitzar:**
1. Selecciona **📍 Aprop meu**
2. Comparteix la teva ubicació quan se't demani
3. El bot mostrarà les estacions en un radi de 10km
4. Les estacions es mostren ordenades per distància

**Informació mostrada:**
- Nom de l'estació i adreça
- Distància en quilòmetres
- Preus dels combustibles principals
- Enllaç a Google Maps

---

## Sistema d'Alertes

### 🔔 Crear Alertes

Les alertes t'avisen quan el preu d'un combustible baixa del llindar que defineixes.

**Crear una alerta:**
1. Selecciona **🔔 Alertes de preu** → **✅ Crear alerta**
2. Tria el tipus de combustible
3. Selecciona l'àmbit:
   - Un municipi específic
   - **🏝️ Tota Menorca**
4. Introdueix el preu objectiu (exemple: 1.45)
5. Confirma la creació

**Limitacions:**
- Preu mínim: 0.50€/L
- Preu màxim: 3.00€/L
- Només es mostren combustibles disponibles al municipi seleccionat

### 📋 Gestionar Alertes

**Veure les teves alertes:**
- Selecciona **🔔 Alertes de preu** → **📋 Les meves alertes**
- Veuràs totes les alertes actives amb:
  - Tipus de combustible
  - Municipi o àmbit
  - Preu objectiu
  - Data de creació

**Eliminar alertes:**
1. Selecciona **🔔 Alertes de preu** → **❌ Eliminar alerta**
2. Tria l'alerta que vols eliminar
3. Confirma l'eliminació

### 🔔 Funcionament de les Alertes

- **Freqüència de comprovació:** Cada 10 minuts
- **Notificació:** Rebràs un missatge quan es compleixi la condició
- **Desactivació automàtica:** ⚠️ **Important!** Una vegada s'envia una alerta, aquesta es desactiva automàticament per evitar spam. Si vols continuar rebent alertes per aquest combustible, hauràs de crear una nova alerta.
- **Informació inclosa:**
  - Estació amb el preu més baix
  - Preu actual
  - Detalls de l'estació
  - Enllaç a Google Maps

---

## Consultes en Línia

### Ús d'Inline Queries

Pots utilitzar el bot en qualsevol xat sense afegir-lo:

**Com utilitzar:**
1. En qualsevol xat, escriu `@menorca_fuel_bot` (segueix d'un espai)
2. Apareixeran opcions predefinides:
   - **✅ Més Barates** - 5 estacions més econòmiques
   - **💸 Més Cares** - 5 estacions més cares
3. Selecciona una opció per enviar la informació al xat

---

## Secció d'Administració

### Accés d'Administrador

L'accés d'administrador està restringit a usuaris específics configurats al sistema. Els administradors tenen accés a funcionalitats especials per gestionar i monitoritzar el bot.

### Comandaments d'Administració

#### `/stats` - Estadístiques del Bot
Mostra estadístiques detallades d'ús:
- **Usuaris totals:** Nombre total d'usuaris registrats
- **Usuaris actius:** Usuaris que han utilitzat el bot en els últims 30 dies
- **Interaccions d'avui:** Nombre d'interaccions del dia actual
- **Alertes actives:** Nombre total d'alertes configurades

#### `/debug_historical` - Debug de Dades Històriques
Comandament de diagnòstic per verificar i reparar dades històriques:
- Neteja registres NULL de la base de dades
- Analitza la disponibilitat de dades històriques
- Emmagatzema una instantània del dia actual
- Prova la generació de gràfics
- Proporciona informació detallada sobre l'estat del sistema

#### `/debug_municipality` - Debug de Municipis
Verifica el funcionament del sistema de municipis:
- Prova els mapejos de municipis
- Comprova la disponibilitat de combustibles per municipi
- Identifica problemes de configuració
- Mostra estadístiques per municipi

#### `/debug_datamanager` - Debug del Gestor de Dades
Prova directament les consultes del gestor de dades:
- Verifica les consultes de municipis
- Comprova la integritat de les dades
- Identifica problemes de rendiment
- Proporciona informació detallada dels logs

#### `/debug_investigation` - Investigació de Dades
Investiga discrepàncies en les dades:
- Analitza noms de municipis en la base de dades
- Compara amb els valors esperats
- Identifica inconsistències
- Suggereix correccions

### Funcionalitats Automàtiques d'Administració

#### Monitorització Automàtica
- **Logs detallats:** Tots els errors i activitats es registren
- **Seguiment d'usuaris:** Estadístiques automàtiques d'ús
- **Gestió d'errors:** Recuperació automàtica d'errors temporals

#### Manteniment de Dades
- **Neteja automàtica:** Eliminació de registres invàlids
- **Instantànies diàries:** Emmagatzematge automàtic per a gràfics
- **Validació de dades:** Verificació de la integritat de les dades

---

## Comandaments Disponibles

### Comandaments Públics

| Comandament | Descripció |
|-------------|------------|
| `/start` | Inicia el bot i mostra el menú principal |
| `/status` | Mostra informació de debug personal |
| `/id` | Mostra la teva informació de Telegram (útil per configurar administradors) |

### Comandaments d'Administrador

| Comandament | Descripció |
|-------------|------------|
| `/stats` | Estadístiques d'ús del bot |
| `/debug_historical` | Debug i reparació de dades històriques |
| `/debug_municipality` | Verificació del sistema de municipis |
| `/debug_datamanager` | Proves del gestor de dades |
| `/debug_investigation` | Investigació de discrepàncies de dades |

### Informació Mostrada per Estació

Cada estació mostra:
- **🔸 Nom de l'estació** (amb enllaç a Google Maps si hi ha coordenades)
- **📍 Adreça completa**
- **🏘️ Municipi**
- **Preus per combustible** (només els disponibles):
  - 🟢 Benzina 95 E5: *preu*€
  - 🌟 Benzina 95 E5 Premium: *preu*€
  - ⚫️ Gasoli A: *preu*€
  - 🟡 Gasoli B: *preu*€
  - 🟠 Gasoli Premium: *preu*€
  - ⚪️ GLP: *preu*€
- **⏰ Horari** (si està disponible)

---

## Resolució de Problemes

### Problemes Comuns

#### "No disponible en aquests moments"
- **Causa:** Problemes temporals amb la base de dades o dades no disponibles
- **Solució:** Espera uns minuts i torna-ho a provar

#### "Error en les dades"
- **Causa:** Problema amb les dades enviades
- **Solució:** Torna al menú principal i intenta-ho de nou

#### "Preu no vàlid"
- **Causa:** Format incorrecte en introduir el preu per alertes
- **Solució:** Utilitza format decimal (exemple: 1.45, no 1,45)

#### No rebo alertes
- **Possibles causes:**
  - L'alerta està configurada amb un preu massa baix
  - No hi ha estacions que compleixin els criteris
  - Problemes temporals del sistema
- **Solució:** Revisa les teves alertes i ajusta els preus si cal

### Contacte i Suport

- **Desenvolupador:** Damià Sintes
- **Codi font:** [GitHub](https://github.com/Damiasroca/Bot_Menorca_EESS)
- **Dades oficials:** Ministerio de Industria, Comercio y Turismo

### Informació Tècnica

- **Actualització de dades:** Cada 10 minuts
- **Comprovació d'alertes:** Cada 10 minuts
- **Persistència:** Les converses es guarden automàticament
- **Idioma:** Català (interfície) / Castellà (dades oficials)

---

## Notes Importants

1. **Precisió de dades:** Algunes dades d'ubicació poden ser imprecises segons la font oficial
2. **Disponibilitat:** No totes les estacions ofereixen tots els tipus de combustible
3. **Horaris:** La informació d'horaris pot no estar sempre disponible
4. **Fornells:** Tractat com a municipi independent perque som un poble.
5. **Privacitat:** El bot només emmagatzema dades necessàries per al funcionament (ID d'usuari, alertes, estadístiques d'ús)

---

*Última actualització del manual: Desembre 2024* 