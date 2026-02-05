# Telefonbog
App til at slå medarbejder e-mail op med dq-nummer eller cpr-nummer


## Afhængigheder
Brugerstyring: keycloak, client ID telefonbog
Database: postgres database "meta" (til logning)
API: Delta api, "Delta prod (ny)" i bitwarden

## Kør lokalt
* Installer python og requirements i requirements.txt
* Opsæt en postgres database
* Kør med `python src/main.py` 