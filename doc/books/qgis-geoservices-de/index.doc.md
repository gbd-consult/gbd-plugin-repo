# GeoServices :/qgis-geoservices-de

Das GBD GeoServices QGIS-Plugin bindet die Karten- und Suchdienste von GBD direkt in QGIS ein. Über ein eigenes Dock können Grundkarten hinzugefügt, Orte und Objekte gesucht, Treffer auf der Karte geprüft sowie Verbindung und Dienstdaten kontrolliert werden.

Dieses Handbuch beschreibt ausschließlich die Funktionen des **GBD GeoServices Plugins**. Allgemeine QGIS-Funktionen werden nur dort erwähnt, wo das Plugin unmittelbar mit der Karte oder einer Auswahl in QGIS zusammenarbeitet.

%info
    Die Abbildungen der Funktionsbereiche zeigen nur das Plugin-Dock. Lediglich im Praxisbeispiel **„Altstadt suchen“** wird die vollständige Kartenansicht gezeigt, damit Treffer, Kartenmarker und Details gemeinsam sichtbar sind.
%end

## Inhalt ::

%toc depth=2
    /qgis-geoservices-de/start
    /qgis-geoservices-de/aufbau
    /qgis-geoservices-de/karten
    /qgis-geoservices-de/suche
    /qgis-geoservices-de/suchmodi
    /qgis-geoservices-de/raumfilter
    /qgis-geoservices-de/sortierung
    /qgis-geoservices-de/treffer
    /qgis-geoservices-de/praxis-altstadt
    /qgis-geoservices-de/status
    /qgis-geoservices-de/arbeitsablaeufe
    /qgis-geoservices-de/fehler
    /qgis-geoservices-de/begriffe
%end

## Voraussetzungen und Start :start

Für die Verwendung werden benötigt:

- QGIS ab Version 3.34,
- eine HTTPS-Verbindung zum GBD GeoServices Dienst,
- je nach Serverkonfiguration ein gültiger API-Schlüssel,
- Netzwerkzugriff auf die konfigurierte Basis-URL.

Das Plugin wird über das Symbol **GBD GeoServices** oder den entsprechenden Eintrag im QGIS-Menü geöffnet. Das Dock kann am linken oder rechten Rand von QGIS angedockt oder als eigenes Fenster gelöst werden.

Die Sprache richtet sich nach der in QGIS eingestellten Oberfläche. Bei einer deutschen QGIS-Oberfläche verwendet das Plugin deutsche Bezeichnungen, andernfalls Englisch.

## Aufbau des Plugin-Docks :aufbau

Der Kopfbereich enthält das GBD-Logo, den Namen **gbd · geoservices** und die Hilfe-Schaltfläche. Darunter liegen drei Register:

- **Karten:** Auswahl und Hinzufügen einer GBD-Grundkarte.
- **Suche:** Suche nach Namen, Adressen, freien Suchausdrücken oder einer Kartenposition.
- **Status:** Serveradresse, API-Schlüssel, Verbindungstest und technische Dienstdaten.

Die Schaltfläche mit dem Fragezeichen öffnet die Dokumentations- bzw. Hilfeseite des Dienstes.

## Karten hinzufügen :karten

Im Register **Karten** wird festgelegt, welche Variante der Grundkarte in das aktuelle QGIS-Projekt eingefügt wird.

![Register Karten des GBD GeoServices Plugins](/qgis-geoservices-images/01-karten.png){border=4 width=380px .md-image-narrow-right}

*Das Register Karten zeigt ausschließlich die Einstellungen und Aktionen des Plugins.*

### Farbschema ::

Das Auswahlfeld **Farbschema** enthält die vom verbundenen Dienst angebotenen Paletten. Je nach Server können beispielsweise folgende Varianten verfügbar sein:

- **Standard** für die allgemeine Kartendarstellung,
- **Dunkel** für eine dunkle Hintergrundkarte,
- **Hell** für eine zurückhaltende Hintergrundkarte,
- **Hoher Kontrast** für eine besonders deutliche Darstellung.

Nur tatsächlich vom Server gemeldete Farbschemata werden angeboten.

### Detailgrad ::

Der Detailgrad steuert die in der Grundkarte enthaltene Informationsmenge:

- **Minimal:** reduzierte Darstellung,
- **Standard:** ausgewogene Darstellung,
- **Maximal:** größtmöglicher Detailumfang.

Nicht jede Kombination aus Farbschema und Detailgrad muss verfügbar sein. Das Plugin berücksichtigt die vom Dienst bereitgestellten Varianten.

### Bildformat ::

Das Feld **Bildformat** bestimmt das Format der geladenen Rasterkacheln. Abhängig vom Dienst stehen PNG, JPEG/JPG oder WebP zur Auswahl.

PNG eignet sich besonders für klare Kartengrafiken. JPEG kann bei flächigen Darstellungen kleinere Datenmengen liefern. WebP verbindet häufig eine gute Bildqualität mit einer kompakten Übertragung.

### Vorhandene OSM-Grundkarte ersetzen ::

Ist **Vorhandene OSM-Grundkarte ersetzen** aktiviert, entfernt das Plugin vorhandene OSM-Grundkarten, bevor die neue GBD-Variante hinzugefügt wird. Dadurch bleiben nicht mehrere nahezu identische Hintergrundkarten übereinander liegen.

Ist die Option deaktiviert, wird die neue Karte zusätzlich eingefügt. Bereits identisch vorhandene GBD-Layer werden nicht doppelt angelegt.

### Aktualisieren und Zur Karte hinzufügen ::

- **Aktualisieren** lädt Kartenstile, Formate, Kategorien und weitere Metadaten erneut vom Server.
- **Zur Karte hinzufügen** fügt die aktuell gewählte Variante als XYZ-Kachellayer in das Projekt ein.

Die Statuszeile unter den Schaltflächen meldet den Erfolg oder zeigt eine verständliche Fehlermeldung an.

Wenn die Grundkarte als erster Layer in ein leeres Projekt eingefügt wird, richtet das Plugin die Kartenansicht automatisch auf den verfügbaren Bereich aus. Für XYZ-Kacheln wird dabei das geeignete Web-Mercator-Koordinatensystem verwendet.

## Suche :suche

Das Register **Suche** fasst Suchart, Eingaben, räumliche Einschränkungen, Sortierung, Ergebnisliste und Details zusammen.

![Namenssuche im Plugin-Dock](/qgis-geoservices-images/02-suche-name.png){border=4 width=380px .md-image-narrow-right}

*Grundaufbau der Suche im Modus Name.*

Eine Suche kann durch die Schaltfläche **Suche** oder durch Drücken der Eingabetaste in einem Eingabefeld gestartet werden. **Leeren** entfernt Suchtext, Treffer, Details und temporäre Markierungen.

## Suchmodi :suchmodi

### Name ::

Der Modus **Name** sucht gezielt nach dem Namen eines Ortes oder Objekts. Beispiele sind „Rathaus“, „Altstadt“ oder der Name einer Einrichtung.

Zusätzlich kann eine Kategorie ausgewählt werden. Ohne Suchtext ist auch eine reine Kategoriesuche möglich, sofern eine Kategorie gewählt wurde.

### Adresse ::

Der Modus **Adresse** besitzt getrennte Felder für Straße, Hausnummer, Postleitzahl und Ort.

![Adresssuche im Plugin-Dock](/qgis-geoservices-images/03-suche-adresse.png){border=4 width=380px .md-image-narrow-right}

*Straße und Hausnummer sind erforderlich; Postleitzahl und Ort grenzen die Suche weiter ein.*

Für eine gültige Adresssuche müssen **Straße** und **Hausnummer** ausgefüllt sein. **PLZ** und **Ort** sind optional, helfen aber bei gleichnamigen Straßen und verbessern die Eindeutigkeit.

### Freitext ::

Der Modus **Freitext** verarbeitet einen kombinierten Suchausdruck. Er eignet sich, wenn Name, Kategorie und Ort gemeinsam eingegeben werden sollen.

![Freitextsuche im Plugin-Dock](/qgis-geoservices-images/04-suche-freitext.png){border=4 width=380px .md-image-narrow-right}

*Beispiel einer kombinierten Anfrage mit aktuellem Kartenausschnitt und angepasster Unschärfe.*

Mögliche Eingaben sind beispielsweise:

- `Café nahe Rathaus Kiel`
- `Apotheke Lübeck`
- `Altstadt`
- `Schule in Flensburg`

Wenn der Dienst den Ausdruck in einzelne Bestandteile zerlegt, erscheint unter dem Trefferstatus eine Zeile **Interpretiert als**. Sie zeigt beispielsweise erkannte Namen, Kategorien, Orte oder Adressbestandteile.

### Was ist hier ::

Der Modus **Was ist hier** sucht an einer direkt in der Karte gewählten Position.

![Modus Was ist hier im Plugin-Dock](/qgis-geoservices-images/05-was-ist-hier.png){border=4 width=380px .md-image-narrow-right}

*Nach der Wahl des Radius wird die Position durch einen Klick in die QGIS-Karte festgelegt.*

Der Ablauf ist:

1. **Was ist hier** auswählen.
2. Einen Radius festlegen oder **Automatisch** verwenden.
3. In der QGIS-Karte auf die gewünschte Position klicken.
4. Trefferliste und Kartenmarkierungen prüfen.

Bei einem Wert von `0 m` bestimmt der Dienst bzw. das Plugin einen passenden automatischen Suchradius. Manuell sind Radien bis 10.000 Meter möglich.

Während dieser Modus aktiv ist, ist die normale Schaltfläche **Suche** deaktiviert, da der Kartenklick die Suche auslöst.

## Räumliche Suchfilter :raumfilter

Die Suchmodi können mit räumlichen Filtern kombiniert werden.

### Nur im aktuellen Kartenausschnitt ::

Diese Option beschränkt die Anfrage auf den aktuell sichtbaren Bereich der QGIS-Karte. Sie ist hilfreich, wenn ein häufig vorkommender Name nur in der näheren Umgebung gesucht werden soll.

### Ausgewählte Objekte als Suchgebiet verwenden ::

Diese Option verwendet ausgewählte Polygonobjekte des aktiven Vektorlayers als Suchgebiet. Vor dem Start müssen ein geeigneter Layer aktiv und mindestens ein Polygon ausgewählt sein.

Sobald diese Option aktiviert wird, wird **Nur im aktuellen Kartenausschnitt** automatisch deaktiviert. Beide Einschränkungen werden nicht gleichzeitig verwendet.

### Auswahlfläche: vollständig innerhalb ::

Ist diese Option aktiviert, werden nur Treffer berücksichtigt, die vollständig innerhalb der gewählten Polygonfläche liegen. Ohne diese strenge Einschränkung können je nach Suchdienst auch räumlich schneidende Ergebnisse berücksichtigt werden.

## Sortierung und Unschärfe :sortierung

### Sortierung ::

Die Treffer können nach unterschiedlichen Kriterien angefordert werden:

- **Relevanz:** passendste Treffer zuerst,
- **Entfernung:** räumlich nächste Treffer zuerst,
- **Name:** alphabetische Sortierung nach Name,
- **Adresse:** Sortierung nach Adressangaben.

Die Entfernungssortierung ist besonders sinnvoll, wenn die Suche einen räumlichen Bezug besitzt, etwa einen Kartenausschnitt oder einen gewählten Punkt.

### Unschärfe ::

Der Regler **Unschärfe** steuert, wie tolerant die Suche gegenüber abweichenden Schreibweisen ist. Ein niedriger Wert bevorzugt exakte Übereinstimmungen. Ein höherer Wert kann Tippfehler und ähnlich geschriebene Begriffe besser berücksichtigen, liefert aber möglicherweise mehr weniger genaue Treffer.

Empfohlener Ablauf:

1. Mit dem Standardwert beginnen.
2. Bei zu wenigen Treffern die Unschärfe schrittweise erhöhen.
3. Bei zu vielen ungenauen Treffern den Wert reduzieren oder Kategorie und Raumfilter ergänzen.

## Trefferliste und Details :treffer

Nach einer erfolgreichen Suche zeigt das Plugin die Gesamtzahl, die auf der aktuellen Seite dargestellte Anzahl und gegebenenfalls die Interpretation der Anfrage.

![Trefferliste im Plugin-Dock](/qgis-geoservices-images/06-suchergebnisse.png){border=4 width=380px .md-image-narrow-right}

*Trefferkarten, Interpretation der Freitextsuche und Seitennavigation.*

Jede Trefferkarte kann Name, Kategorie und räumlichen Kontext enthalten. Mit **Zurück** und **Weiter** wird zwischen Ergebnisseiten gewechselt. Die aktuelle Seitennummer steht in der Mitte.

### Darstellung auf der Karte ::

Die Treffer werden gleichzeitig als temporäre Markierungen in der QGIS-Karte dargestellt:

- nicht ausgewählte Treffer erscheinen blau,
- der ausgewählte Treffer wird rot hervorgehoben,
- flächige oder linienförmige Geometrien werden zusätzlich hervorgehoben.

Die Markierungen sind temporär und werden beim Leeren der Suche oder beim Schließen des Plugin-Docks entfernt.

### Einen Treffer auswählen ::

Ein Klick auf eine Trefferkarte führt zum Objekt, markiert es in der Karte und öffnet den Abschnitt **Details**.

![Details eines ausgewählten Treffers](/qgis-geoservices-images/07-trefferdetails.png){border=4 width=380px .md-image-narrow-right}

*Der ausgewählte Treffer wird blau hinterlegt; darunter erscheinen die vom Dienst gelieferten Eigenschaften.*

Bei Punktobjekten verwendet das Plugin für die Navigation typischerweise einen Maßstab von 1:15.000. Bei Linien und Flächen wird auf die räumliche Ausdehnung des Objekts gezoomt.

Der Detailbereich enthält abhängig vom Ergebnis unter anderem:

- Name und Zusammenfassung,
- Kategorie und Kategorienpfad,
- Adresse oder räumliche Zuordnung,
- Objekt-ID,
- Geometrietyp und Ausdehnung,
- weitere vom GeoServices Dienst gelieferte Eigenschaften.

Verschachtelte Werte werden vollständig dargestellt und nicht stillschweigend verworfen.

## Praxisbeispiel Altstadt :praxis-altstadt

Dieses Beispiel zeigt bewusst die vollständige QGIS-Kartenansicht, weil hier das Zusammenspiel zwischen Plugin und Karte erklärt wird.

### Altstadt suchen und Treffer vergleichen ::

1. Das Register **Suche** öffnen.
2. Den Modus **Freitext** wählen.
3. `Altstadt` als Suchanfrage eingeben.
4. Bei Bedarf Kategorie, Kartenausschnitt oder Unschärfe anpassen.
5. **Suche** auswählen.
6. Trefferkarten im Plugin mit den blauen Markierungen auf der Karte vergleichen.

![Altstadt-Suche mit Trefferliste und Kartenmarkierungen](/qgis-geoservices-images/09-altstadt-ergebnisse-qgis.webp){border=4 width=100% .md-image-wide}

*Praxisansicht: Die Suche nach „Altstadt“ liefert mehrere Treffer; ihre Positionen werden als blaue Kreise auf der Karte angezeigt.*

Die Ergebnisanzahl kann hoch sein, weil der Name „Altstadt“ in vielen Gemeinden vorkommt. Eine Eingrenzung über den aktuellen Kartenausschnitt, eine Ortsangabe im Freitext oder eine Kategorie führt schneller zum gewünschten Treffer.

### Treffer auswählen und Details prüfen ::

Nach der Auswahl einer Trefferkarte zoomt das Plugin auf den Treffer. Die gewählte Position wird rot dargestellt und der Detailbereich wird geöffnet.

![Ausgewählter Altstadt-Treffer mit Details](/qgis-geoservices-images/10-altstadt-details-qgis.webp){border=4 width=100% .md-image-wide}

*Praxisansicht: ausgewählter Altstadt-Treffer, roter Kartenmarker und vollständige vom Dienst gelieferte Details.*

![Detailbereich des ausgewählten Altstadt-Treffers](/qgis-geoservices-images/11-altstadt-details-plugin.png){border=4 width=380px .md-image-narrow-right}

*Nahansicht ausschließlich aus dem Plugin: Der Detailbereich bewahrt auch verschachtelte Kategorien, Ortszuordnungen, OSM-Angaben, Trefferwerte, Objekt-ID und Geometrie.*

Vor der weiteren Verwendung sollten mindestens Name, Kategorie, übergeordnete Orte und räumliche Position geprüft werden. Gleichnamige Treffer lassen sich dadurch zuverlässig unterscheiden.

## Status und Verbindung :status

Das Register **Status** verwaltet die Verbindung zum GeoServices Dienst und zeigt die aktuell geladenen Metadaten.

![Status und Verbindung im Plugin-Dock](/qgis-geoservices-images/08-status.png){border=4 width=380px .md-image-narrow-right}

*Basis-URL, geschützter API-Schlüssel, Verbindungstest und Dienstinformationen.*

### Basis-URL ::

Die **Basis-URL** ist die Adresse des GeoServices Servers. Aus Sicherheitsgründen akzeptiert das Plugin ausschließlich HTTPS-Adressen.

### API-Schlüssel ::

Der **API-Schlüssel** ist bei offenen Servern optional. Bei geschützten Diensten wird er für Karten-, Metadaten- und Suchanfragen benötigt.

Der Wert wird standardmäßig verdeckt dargestellt. **API-Schlüssel anzeigen** macht ihn vorübergehend lesbar.

%warn
    API-Schlüssel nicht in Screenshots, Projektnotizen oder öffentlich zugänglichen Dokumenten offen anzeigen.
%end

### Einstellungen speichern ::

**Einstellungen speichern** übernimmt Basis-URL und API-Schlüssel in die Plugin-Konfiguration. Nach einem Serverwechsel sollten die Metadaten im Register **Karten** erneut aktualisiert werden.

### Verbindung testen ::

**Verbindung testen** prüft, ob der konfigurierte Dienst erreichbar ist und die Antwort verarbeitet werden kann. Eine erfolgreiche Prüfung wird direkt unter den Schaltflächen bestätigt.

### Dienstinformationen ::

Der Informationsbereich kann folgende Angaben enthalten:

- **Gebiet:** Kennung des bereitgestellten Datenbereichs,
- **Datenstand:** Datum des Datenbestands,
- **Kategorien:** Anzahl verfügbarer Suchkategorien,
- **Quellenangabe:** vorgeschriebene Datenattribution,
- **Build:** Server-Build,
- **Schema:** verwendete Datenbankschema- oder Generationskennung,
- **Authentifizierung:** offener oder geschützter Zugriff.

## Typische Arbeitsabläufe :arbeitsablaeufe

### Eine Grundkarte einrichten ::

1. Im Register **Status** die Basis-URL prüfen.
2. Falls erforderlich den API-Schlüssel eintragen und speichern.
3. **Verbindung testen** auswählen.
4. Zum Register **Karten** wechseln und **Aktualisieren** auswählen.
5. Farbschema, Detailgrad und Bildformat festlegen.
6. Entscheiden, ob eine vorhandene OSM-Grundkarte ersetzt werden soll.
7. **Zur Karte hinzufügen** auswählen.
8. Meldung und Layernamen kontrollieren.

### Einen Ort oder ein Objekt finden ::

1. Zum Register **Suche** wechseln.
2. Einen passenden Suchmodus wählen.
3. Suchdaten eingeben und gegebenenfalls eine Kategorie auswählen.
4. Optional einen räumlichen Filter setzen.
5. Sortierung und Unschärfe prüfen.
6. Suche starten.
7. Treffer auf Karte und in der Liste vergleichen.
8. Einen Treffer auswählen und seine Details prüfen.
9. Mit **Leeren** die temporären Ergebnisse entfernen.

### In einer ausgewählten Fläche suchen ::

1. Einen Polygon-Vektorlayer in QGIS aktivieren.
2. Ein oder mehrere Polygonobjekte auswählen.
3. Im Plugin **Ausgewählte Objekte als Suchgebiet verwenden** aktivieren.
4. Entscheiden, ob Treffer vollständig innerhalb der Fläche liegen müssen.
5. Suchmodus und Suchbegriff festlegen.
6. Suche starten und Ergebnisse prüfen.

## Fehler einordnen :fehler

### Verbindung fehlgeschlagen ::

Mögliche Ursachen sind eine nicht erreichbare Basis-URL, fehlender Netzwerkzugriff oder eine Serverstörung. Die URL im Register **Status** prüfen und **Verbindung testen** erneut ausführen.

### Authentifizierung fehlgeschlagen ::

Der API-Schlüssel fehlt, ist ungültig oder gehört zu einer anderen Serverumgebung. Schlüssel im Register **Status** kontrollieren, speichern und anschließend die Verbindung erneut testen.

### Basis-URL wird abgelehnt ::

Das Plugin erlaubt nur HTTPS. Eine Adresse mit `http://` muss durch die korrekte sichere Serveradresse ersetzt werden.

### Keine Kartenstile verfügbar ::

Im Register **Karten** **Aktualisieren** auswählen. Bleibt die Liste leer, Status und Verbindung prüfen. Möglich ist außerdem, dass der Server keine geeigneten Themen für die gewählte Umgebung meldet.

### Keine Suchtreffer ::

- Schreibweise und Suchmodus prüfen.
- Kategorie zurück auf **Alle Kategorien** setzen.
- räumliche Einschränkungen deaktivieren oder vergrößern,
- Unschärfe erhöhen,
- bei der Adresssuche Straße und Hausnummer kontrollieren.

### Ausgewählte Fläche kann nicht verwendet werden ::

Ein aktiver Vektorlayer mit mindestens einem ausgewählten Polygon ist erforderlich. Leere Geometrien sowie ungeeignete Geometrietypen können nicht als Suchfläche verwendet werden.

### Treffer wird nicht auf der Karte dargestellt ::

Das Ergebnis enthält möglicherweise keine verwendbare Geometrie oder einen nicht unterstützten Geometrietyp. Ein anderer Treffer kann dennoch normal verwendet werden.

### Grundkarte ist bereits vorhanden ::

Das Plugin verhindert doppelte identische GBD-Grundkarten. Entweder den vorhandenen Layer weiterverwenden oder eine andere Kombination aus Farbschema, Detailgrad oder Format auswählen.

## Begriffe :begriffe

### XYZ-Kachellayer ::

Eine Rastergrundkarte, die in festen Zoomstufen aus einzelnen Bildkacheln geladen wird.

### Farbschema ::

Die grafische Farbvariante einer Grundkarte, beispielsweise Standard, Hell, Dunkel oder Hoher Kontrast.

### Detailgrad ::

Die Informationsdichte der gewählten Kartenvariante.

### Freitextsuche ::

Eine Suche, bei der Name, Kategorie, Adresse oder Ort gemeinsam in einem Ausdruck stehen können.

### Unschärfe ::

Die Toleranz der Suche gegenüber Schreibvarianten und Tippfehlern.

### Aktueller Kartenausschnitt ::

Der derzeit sichtbare geografische Bereich der QGIS-Karte.

### Suchgebiet ::

Eine aus ausgewählten Polygonobjekten gebildete räumliche Einschränkung.

### Temporäre Markierung ::

Eine nur für die aktuelle Suche erzeugte Darstellung eines Treffers. Sie ist kein dauerhaft gespeicherter Projektlayer.

### Metadaten ::

Vom Dienst gelieferte Informationen über Kartenstile, Formate, Kategorien, Datenstand, Gebiet und weitere technische Eigenschaften.

---

**Dokumentationsstand:** Plugin-Version 0.3.2 · QGIS-Mindestversion 3.34
