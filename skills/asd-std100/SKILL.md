---
name: asd-std100
description: >-
  Write or rewrite clear, unambiguous technical Danish for instructions, error
  messages, tool descriptions, prompts, status reports and documentation.
  First ask Danish or English unless the user has already chosen for this task.
  Use when Danish text is dense or ambiguous, or another agent must interpret it.
  Triggers: klart teknisk dansk, teknisk dansk, forenklet dansk, omskriv på dansk,
  fjern tvetydighed, dansk version af STE100, asd-std100.
  Not for creative, marketing or persuasive copy. Do not translate English
  unless the user requests Danish output or translation.
metadata:
  version: 0.1.0
---

# Klart teknisk dansk

Skriv dansk, som en læser eller en agent kan forstå uden at gætte.
Fjern tvetydighed, ikke nødvendig information.

Denne færdighed er inspireret af klarhedsprincipperne i ASD-STE100 og
færdigheden `asd-ste100`. Navnet `asd-std100` er et lokalt færdighedsnavn.
Det betegner ikke en officiel dansk standard, en ASD-ordliste eller en
certificering. Reglerne nedenfor er praktiske regler for dansk, ikke en
oversættelse af ASD's officielle regler eller ordbog.

## Vælg sprog før teksten skrives

Denne regel går forud for standardformatet under Output.
Hvis brugeren ikke allerede har valgt dansk eller engelsk til denne opgave,
skal du spørge og vente på svaret:

**"Vil du have den tekniske beskrivelse på dansk eller engelsk?"**

Udled ikke valget af kildens eller samtalens sprog. Automatisk valg af denne
færdighed er heller ikke et sprogvalg. Et udtrykkeligt ønske om `asd-std100`
tæller som et valg af dansk. Genbrug valget ved rettelser af samme tekst.
Spørg igen ved en ny skriveopgave, medmindre brugeren har valgt for hele sessionen.

Hvis svaret er engelsk, skal du indlæse `asd-ste100` fra færdighedskataloget
og følge den færdighed i stedet. Hvis brugeren ønsker begge sprog, skal du
bruge hver færdighed til dens eget sprog. Hvis den nødvendige færdighed
mangler, skal du sige det i stedet for at påstå, at du har anvendt den.
Respektér projektets sprogkrav, før du skriver filer. Ved en konflikt skal
du forklare kravet og tilbyde en separat tekst i samtalen.

## Hvornår skal færdigheden bruges?

- Skriv eller omskriv danske procedurer, fejlmeddelelser og værktøjsbeskrivelser.
- Gør danske prompts og instruktioner til andre agenter entydige.
- Fjern tungt sprog fra statusrapporter, README-filer og teknisk dokumentation.
- Bevar alle fakta, forbehold og betingelser i en tekst, der skal forenkles.

Brug ikke reglerne til kreativ tekst eller reklamer, hvor stil og overtalelse
har et selvstændigt formål. Oversæt kun tekst til dansk, når brugeren beder
om dansk tekst eller en oversættelse. Bevar ellers kildens sprog.

## Vælg en tilstand

Vælg ud fra teksttypen, hvis brugeren ikke angiver en tilstand.
Oplys kun valget, når brugeren beder om en forklaring.

**Streng:** Procedurer, sikkerhedstekst, fejlmeddelelser, prompts og
instruktioner til værktøjer eller agenter. Anvend alle regler.
Brug højst 20 ord pr. instruktionssætning og 25 ord pr. beskrivende sætning.

**Klar prosa:** README-filer, ændringsbeskrivelser og forklaringer.
Anvend samme sætningsgrænser og regler om struktur og betydning.
Brug naturlige danske formuleringer. Undgå at gøre teksten stiv ved at
håndhæve én ordklasse pr. ord eller et kunstigt begrænset ordforråd.
Bevar faste navne på tekniske begreber i begge tilstande.

Længdegrænserne er lokale arbejdsregler, ikke officielle krav til dansk.
Tæl ord adskilt af mellemrum. Opdel ikke danske sammensætninger for at
påvirke ordtallet. Bevar en længere sætning, hvis en opdeling ville ændre
betydningen. Forklar undtagelsen som beskrevet under Output.

## Regler for klar struktur

| Regel | Gør sådan | Undgå |
|---|---|---|
| Synlig aktør | "Agenten sletter filen." | "Filen slettes", hvis det er vigtigt, hvem der sletter den. |
| Direkte instruktion | "Åbn filen." | "Der skal foretages åbning af filen." |
| Én handling pr. instruktion | "Åbn filen. Læs linje 3." | Flere handlinger i én lang sætning. |
| Betingelse før handling | "Hvis testen fejler, skal du stoppe udrulningen." | En betingelse gemt efter handlingen. |
| Klar rækkefølge | Brug en nummereret liste til trin, som skal udføres i rækkefølge. | En rækkefølge skjult i et afsnit. |
| Klar logik | Angiv, om alle betingelser eller mindst én betingelse skal være opfyldt. | "Og/eller" uden en klar betydning. |
| Tydelig reference | Gentag navnet, hvis "den", "det" eller "dette" kan pege på flere ting. | Et stedord med flere mulige referencer. |
| Korte afsnit | Ét emne og højst seks sætninger pr. afsnit. | Flere emner i samme afsnit. |
| Enkel tegnsætning | Brug punktum og lister. Bevar dansk komma, hvor det er nødvendigt. | Semikolon og indskud, som skjuler hovedbudskabet. |
| Tydelige lister | Angiv, om punkterne er trin, alternativer eller krav. | En liste, hvor forholdet mellem punkterne er uklart. |

Brug aktiv form, når aktøren er kendt og relevant. Bevar passiv form, hvis
aktøren er ukendt eller uden betydning. Opfind aldrig en aktør.

## Regler for danske ord og formuleringer

- Brug det samme navn for det samme begreb. Skift ikke mellem "kunde",
  "bruger" og "klient", hvis teksten kun omtaler én rolle.
  Slå heller ikke forskellige roller sammen for at spare ord.
- Brug almindelige, præcise ord. Skriv "bruge" i stedet for "gøre brug af"
  og "hjælpe" i stedet for "yde assistance".
- Brug et verbum til en handling. Skriv "Kontrollér loggen" i stedet for
  "Foretag en kontrol af loggen".
- Fjern tomme indledninger som "Det er vigtigt at bemærke, at".
  Bevar selve oplysningen og dens forbehold.
- Fjern udokumenterede kvalitetsord som "sømløs", "banebrydende" og
  "lynhurtig". Erstat dem kun med målbare oplysninger, som kilden angiver.
- Skriv danske sammensætninger korrekt: "fejlmeddelelse", ikke "fejl meddelelse".
  Omskriv tunge sammensætninger, hvis delene eller relationen er uklare.
  En ordgrænse for engelske navneordskæder passer ikke til dansk.
- Brug almindelige danske verbalforbindelser, når de er præcise.
  "Log ind" og "slå op" er ikke fejl, blot fordi de består af flere ord.
  Undgå uklare metaforer som "kigge ind i problemet".
- Bevar nødvendige fagtermer. Forklar en ukendt forkortelse ved første brug,
  når forklaringen er kendt. Gæt ikke på en forkortelses betydning.
- Bevar produktnavne, API-navne, kode, kommandoer, filstier, nøgler og
  pladsholdere nøjagtigt. Oversæt ikke et felt som `retry_count`.
- Bevar tekst, der skal matches ordret, såsom citerede fejlstrenge.
  Omskriv kun selve strengen, hvis opgaven udtrykkeligt er at ændre den.
- Brug korrekt dansk med æ, ø og å. Bevar dokumentets eksisterende
  kommapraksis, hvis den er korrekt. Et startkomma er ikke obligatorisk.

## Betydning går før korthed

En omskrivning må ikke ændre på fakta, betingelser eller sikkerhed.
Kontrollér især følgende:

- **Krav:** "Skal" er et krav. "Bør" er en anbefaling.
  Erstat ikke det ene med det andet.
- **Tilladelse og mulighed:** "Må" kan angive tilladelse.
  "Kan" kan angive evne eller mulighed. Gør kun betydningen mere eksplicit,
  hvis kilden eller konteksten gør den klar.
- **Usikkerhed:** Bevar "muligvis", "sandsynligvis", "kan have" og lignende
  forbehold. "Jobbet kan have fejlet" betyder ikke "Jobbet fejlede".
- **Tid og tilstand:** Bevar forskellen mellem en tidligere hændelse og en
  tilstand, der gælder nu. Dansk førnutid er tilladt. Omskriv ikke automatisk
  "Jobbet er afsluttet" eller "Vi har modtaget filen" til datid.
- **Afgrænsning:** Bevar negationer, undtagelser, tal, enheder, tidsfrister,
  sammenligninger og kvantorer som "kun", "alle" og "mindst én".
- **Årsag:** Tilføj ikke en forklaring, diagnose eller hyppighed, som kilden
  ikke angiver. "Efter" betyder ikke nødvendigvis "på grund af".

Hvis kildeteksten er tvetydig, og betydningen ikke kan udledes sikkert,
skal du stille ét konkret spørgsmål. Gæt ikke for at levere en glat tekst.
Hvis et udsagn mangler indhold eller dokumentation, må du ikke opfinde det.

## Arbejdsgang

1. Afklar sproget. Læs hele teksten og identificér formål, læser og tilstand.
2. Notér fakta, aktører, krav, usikkerhed og tekst, der skal bevares ordret.
3. Find lange sætninger, skjulte aktører, uklare referencer, skiftende
   betegnelser, navneordsstil og tomme formuleringer.
4. Omskriv uden at tilføje oplysninger eller ændre styrken af et udsagn.
5. Sammenlign omskrivningen med kilden. Kontrollér især betingelser,
   negationer, tal, tidsformer og forbehold.
6. Kontrollér dansk grammatik, sætningslængde og den logiske rækkefølge.
7. Returnér teksten i det format, der er beskrevet nedenfor.

Reglerne kræver sproglig vurdering. Denne færdighed indeholder ikke en
automatisk dansk linter og bruger ikke den engelske linters ordlister.

## Output

**Som standard:** Returnér kun den danske tekst, klar til at blive indsat.
Tilføj ikke en indledning, en tilstandsangivelse, en optælling eller et
stående tilbud om mere hjælp. Hvis teksten allerede er klar, returnér den
uændret. Bevar relevant formatering og struktur.

Hvis du bevidst bevarer en lang eller tung formulering for at beskytte
betydningen, må du tilføje én kort linje efter teksten:

`Bevaret: "[formulering]" — [den præcision, som ellers ville gå tabt].`

Et nødvendigt afklaringsspørgsmål går forud for standardformatet.

**På anmodning:** Vis før/efter eller forklar ændringerne med en tabel:

| Regel | Original | Omskrevet |
|---|---|---|
| Verbum frem for navneord | Foretag en kontrol af loggen. | Kontrollér loggen. |
| Betingelse før handling | Stop jobbet, hvis testen fejler. | Hvis testen fejler, skal du stoppe jobbet. |

Angiv tilstanden efter tabellen. Forklar kort eventuelle bevidste undtagelser.
Hvis brugeren beder om både en forklaring og en færdig tekst, skal du levere
begge dele.

## Grænser og eksempler

Færdigheden forbedrer tekstens form. Den kontrollerer ikke, om indholdet er
teknisk korrekt, og garanterer ikke overholdelse af en officiel standard.
Kortest mulig tekst er ikke målet. Entydig tekst er målet.

Se [før/efter-eksempler](examples/before-after.md) for danske instruktioner,
statusmeddelelser, logiske betingelser og tilfælde, der kræver afklaring.
