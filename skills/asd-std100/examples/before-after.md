# Før/efter: klart teknisk dansk

Eksemplerne viser lokale klarhedsregler, ikke officiel ASD-overholdelse.

## Skjult aktør og navneordsstil

**Før:**
Der skal af agenten foretages en kontrol af konfigurationsfilen inden
igangsættelse af jobbet.

**Efter:**
Agenten skal kontrollere konfigurationsfilen, før agenten starter jobbet.

**Hvorfor:** Aktøren og handlingerne er synlige. Kravet med "skal" er bevaret.

## Trin i en bestemt rækkefølge

**Før:**
Åbn filen og læs linje 3, og kontrollér derefter, om værdien er 10.

**Efter:**
1. Åbn filen.
2. Læs linje 3.
3. Kontrollér, om værdien er 10.

**Hvorfor:** Hvert trin indeholder én handling. Rækkefølgen og tallet er bevaret.

## Usikkerhed er information

**Før:**
Det er vigtigt at bemærke, at anmodningen muligvis kan være fejlet på grund
af en timeout.

**Efter:**
Anmodningen kan være fejlet på grund af en timeout.

**Hvorfor:** Den tomme indledning og det dobbelte forbehold er fjernet.
Fejlen og årsagen er stadig muligheder, ikke fastslåede fakta.

**Forkert omskrivning:**
Anmodningen fejlede på grund af en timeout.

Denne version gør en mulighed til en sikker diagnose.

## Krav og anbefalinger er forskellige

**Før:**
Det anbefales, at operatøren foretager en sikkerhedskopiering før opdateringen.

**Efter:**
Operatøren bør sikkerhedskopiere før opdateringen.

**Hvorfor:** Handlingen står som et verbum. Anbefalingen bliver ikke et krav.
"Operatøren skal sikkerhedskopiere" ville ændre betydningen.

## En kendt logisk betingelse

**Før:**
Hvis testen fejler, eller hvis konfigurationsfilen mangler, skal du stoppe udrulningen.

**Efter:**
Hvis mindst én af følgende betingelser er opfyldt, skal du stoppe udrulningen:

- Testen fejler.
- Konfigurationsfilen mangler.

**Hvorfor:** Listen betyder mindst én betingelse, ikke begge betingelser.
Betingelserne er samlet, så læseren kan afgøre dem, før læseren handler.

## Teknisk tekst, der skal bevares ordret

**Før:**
Du skal gøre brug af `retry_count` for at foretage konfiguration af antallet
af genforsøg, og værdien skal sættes til `3`.

**Efter:**
Du skal angive antallet af genforsøg med `retry_count`.
Du skal sætte værdien til `3`.

**Hvorfor:** Feltnavnet, værdien og begge krav er bevaret.

## Ukendt aktør og relevant tidsform

**Før og efter:**
Filen er blevet slettet.

**Hvorfor:** Teksten angiver ikke, hvem der slettede filen.
Tilføj ikke "Agenten", og ændr ikke tidsformen alene for at forkorte teksten.
Passiv og førnutid kan være nødvendige på dansk.

## Dansk verbalforbindelse og sammensætning

**Før:**
Foretag login for at få vist fejl meddelelsen.

**Efter:**
Log ind for at se fejlmeddelelsen.

**Hvorfor:** "Log ind" er en almindelig, præcis dansk verbalforbindelse.
"Fejlmeddelelse" er ét sammensat ord. Engelske regler om flerordsverber
og navneordskæder skal ikke anvendes mekanisk på dansk.

## Tvetydighed, der kræver et spørgsmål

**Kilde:**
Agenten sendte filen til serveren, da den var klar.

**Svar:**
Henviser "den var klar" til agenten, filen eller serveren?

**Hvorfor:** En omskrivning må ikke vælge en reference uden grundlag.

## Klar tekst kræver ingen ændring

**Før og efter:**
Hvis testen fejler, skal du stoppe jobbet.

**Hvorfor:** Aktøren, betingelsen og kravet er tydelige.
Returnér teksten uden forklaring, medmindre brugeren beder om en forklaring.
