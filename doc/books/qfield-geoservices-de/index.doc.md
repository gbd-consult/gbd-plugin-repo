# GeoServices :/qfield-geoservices-de

Mit dem GBD GeoServices QField-Plugin fügen Sie GBD-Hintergrundkarten in die laufende QField-Sitzung ein, suchen Orte und Adressen und prüfen Suchtreffer auf der Karte. Die Oberfläche ist für die Bedienung mit dem Finger ausgelegt und öffnet sich als seitliches Bedienfeld.

Dieses Handbuch beschreibt die QField-Ausführung des Plugins. Die Anleitung für QGIS Desktop finden Sie im [GeoServices-QGIS-Handbuch](/qgis-geoservices-de).

%info
    Hintergrundkarten aus diesem Plugin gelten für die laufende QField-Sitzung. Wenn eine Hintergrundkarte dauerhaft zum Projekt gehören soll, richten Sie diese im QGIS-Projekt ein. Die verfügbaren Kartenstile, Kategorien und Inhalte hängen vom verbundenen GeoServices-Dienst ab.
%end

## Inhalt ::

%toc depth=1
    /qfield-geoservices-de/start
    /qfield-geoservices-de/oberflaeche
    /qfield-geoservices-de/verbindung
    /qfield-geoservices-de/karten
    /qfield-geoservices-de/suche
    /qfield-geoservices-de/raumfilter
    /qfield-geoservices-de/sortierung
    /qfield-geoservices-de/punktsuche
    /qfield-geoservices-de/treffer
    /qfield-geoservices-de/status
    /qfield-geoservices-de/arbeitsablaeufe
    /qfield-geoservices-de/fehler
%end

## Voraussetzungen, Installation und Start :start

Sie benötigen eine QField-Ausführung mit Unterstützung für Anwendungsplugins, ein geöffnetes Kartenprojekt und eine Netzwerkverbindung zum GBD GeoServices-Dienst. Halten Sie die HTTPS-Adresse des Dienstes und einen für den Zugriff vorgesehenen API-Schlüssel bereit.

### Plugin installieren ::

1. Öffnen Sie die Plugin-Verwaltung in den QField-Einstellungen.
2. Wählen Sie **Install plugin from URL** beziehungsweise die entsprechende übersetzte Option zum Installieren über eine URL.
3. Tragen Sie die direkte Download-Adresse des QField-Plugin-ZIPs ein. Verwenden Sie die QField-Ausführung aus dem [QField-Plugin-Katalog](//qfield).
4. Aktivieren Sie **GBD GeoServices** in der Plugin-Verwaltung.
5. Öffnen Sie ein Kartenprojekt und tippen Sie auf das GeoServices-Symbol in der Plugin-Werkzeugleiste.

Der Download-Link führt direkt zum ZIP und nicht zur Beschreibungsseite des Plugins.

### Erstmalig verbinden ::

Öffnen Sie im Plugin das Register **Einstellungen**, tragen Sie die Dienstadresse und den API-Schlüssel ein und wählen Sie **Speichern und testen**. Anschließend stehen die vom Dienst gelieferten Kartenstile und Kategorien zur Verfügung.

Die Sprache des Plugins richtet sich nach der Spracheinstellung von QField: Deutsch bei deutscher Spracheinstellung, ansonsten Englisch. Die englischen Registernamen lauten **Maps**, **Search** und **Settings**.

## Aufbau des Bedienfelds :oberflaeche

Das Bedienfeld enthält drei Register:

| Register | Aufgabe |
| --- | --- |
| **Karten** | Einen Kartenstil und ein Bildformat wählen, eine Hintergrundkarte hinzufügen und zur Service-Abdeckung zoomen. |
| **Suche** | Nach Namen, Adressen und Freitext suchen, Filter verwenden und Treffer prüfen. |
| **Einstellungen** | Dienstadresse und API-Schlüssel speichern sowie Verbindung und Dienstdaten kontrollieren. |

Auf schmalen Geräten nutzt das Bedienfeld die verfügbare Breite. Auf größeren Ansichten bleibt daneben ein Teil der Karte sichtbar. Längere Inhalte lassen sich im jeweiligen Register scrollen.

Mit **×** schließen Sie das Bedienfeld. Über das GeoServices-Symbol öffnen Sie es erneut. Zusätzliche Filter sind zunächst unter **Weitere Suchoptionen** eingeklappt.

## Verbindung einrichten :verbindung

Im Register **Einstellungen** befindet sich der Bereich **Service-Verbindung**.

### Basis-URL ::

Die **Basis-URL** ist die HTTPS-Adresse des GeoServices-Dienstes, zum Beispiel `https://geoservices.gbd-consult.de`. Tragen Sie die Dienstadresse ohne einen zusätzlichen Such- oder Kachelpfad ein. Eine Adresse ohne HTTPS wird vom Plugin abgelehnt.

### API-Schlüssel ::

Geben Sie den zu Ihrem Dienst gehörenden Schlüssel in **API-Schlüssel** ein. Bei einer neuen Installation ist das Feld leer. Standardmäßig ist der Wert verdeckt; **API-Schlüssel anzeigen** macht ihn sichtbar.

Der Schlüssel wird nach **Speichern und testen** in den QField-Einstellungen dieses Geräts gespeichert. Für eine Hintergrundkarte ist in dieser Plugin-Fassung ein gespeicherter, nicht leerer API-Schlüssel erforderlich, auch wenn andere Anfragen an den Dienst ohne Schlüssel möglich sein sollten.

%warn
    Lassen Sie den API-Schlüssel bei Bildschirmfreigaben und für Abbildungen verdeckt. Geben Sie ihn nicht in Suchtexte oder öffentliche Download-Links ein.
%end

### Speichern und testen ::

1. Prüfen Sie die **Basis-URL**.
2. Tragen Sie den **API-Schlüssel** ein.
3. Tippen Sie auf **Speichern und testen**.
4. Kontrollieren Sie die Rückmeldung zum Verbindungstest.

**Erneut testen** lädt die Dienstdaten mit den bereits gespeicherten Einstellungen erneut. Änderungen in den Eingabefeldern übernehmen Sie dagegen mit **Speichern und testen**.

## Hintergrundkarten hinzufügen :karten

Im Register **Karten** wählen Sie die Hintergrundkarte für die aktuelle Sitzung.

### Stil und Bildformat ::

Das Feld **Stil** enthält die vom Dienst angebotenen Varianten. Die Bezeichnungen können beispielsweise Farbschema und Detailumfang kombinieren, etwa **Standard — Maximum** oder **Dunkel — Minimum**. Es werden nur tatsächlich vom Dienst gelieferte Stile angeboten.

Unter **Bildformat** wählen Sie eines der verfügbaren Formate. Je nach Dienst können beispielsweise PNG, JPEG oder WebP angeboten werden.

### Karte hinzufügen ::

1. Stellen Sie sicher, dass unter **Einstellungen** ein API-Schlüssel gespeichert wurde.
2. Öffnen Sie **Karten** und wählen Sie **Aktualisieren**, falls noch keine Stile geladen wurden.
3. Wählen Sie einen **Stil** und ein **Bildformat**.
4. Lassen Sie **Aktive GBD-Hintergrundkarte ersetzen** eingeschaltet, wenn die bisher über dieses Plugin hinzugefügte Karte ausgetauscht werden soll.
5. Tippen Sie auf **Zur Karte hinzufügen**.

Die Erfolgsmeldung bestätigt, dass die Hintergrundkarte für diese QField-Sitzung hinzugefügt wurde. Wenn der Dienst eine Abdeckung liefert, richtet das Plugin den Kartenausschnitt darauf aus.

Die neue Hintergrundkarte wird in dieser Fassung oben in die Kartenansicht eingefügt. Dadurch kann sie andere Projektlayer überdecken. Das Plugin fügt sie nicht als dauerhaft gespeicherte Ebene zum Projekt hinzu.

Wenn bereits eine GBD-Hintergrundkarte aktiv und die Ersetzungsoption ausgeschaltet ist, fügt das Plugin keine zweite hinzu und zeigt eine entsprechende Meldung.

### Zur Abdeckung zurückkehren ::

Mit **Auf Service-Abdeckung zoomen** richten Sie die Kartenansicht erneut auf das vom Dienst gemeldete Gebiet aus. **Aktualisieren** lädt Kartenstile, Bildformate, Kategorien und Statusinformationen neu.

## Nach Orten und Adressen suchen :suche

Im Register **Suche** befindet sich der Bereich **Orte finden**. Über das Auswahlfeld wechseln Sie zwischen **Name**, **Adresse** und **Freitext**.

### Name ::

Geben Sie den Namen eines Ortes oder Objekts ein, beispielsweise `Rathaus`. Wählen Sie bei Bedarf zusätzlich eine Kategorie und tippen Sie auf **Suche**. Im Suchtextfeld können Sie die Suche auch mit der Eingabetaste starten.

### Adresse ::

Im Modus **Adresse** erscheinen getrennte Eingabefelder:

- **Straße** und **Hausnummer** sind erforderlich.
- **Postleitzahl (optional)** und **Ort (optional)** grenzen die Suche weiter ein.

Tragen Sie die Adresse ein und tippen Sie auf **Suche**. Fehlen Straße oder Hausnummer, zeigt das Plugin eine entsprechende Meldung.

### Freitext ::

Im Modus **Freitext** können Sie Namen, Kategorien und Ortsangaben kombinieren, zum Beispiel `Café nahe Rathaus Kiel`. Ob und welche Treffer gefunden werden, hängt von den Daten und der Verarbeitung des verbundenen Dienstes ab.

Wenn der Dienst eine Interpretation des Suchausdrucks zurückliefert, wird diese unter **Interpretiert als** angezeigt.

### Kategorien verwenden ::

Mit **Kategorien filtern…** begrenzen Sie die Liste der Kategorien. Wählen Sie anschließend die gewünschte Kategorie im Auswahlfeld **Kategorie**. **Alle Kategorien** hebt diese Einschränkung auf.

In den Modi **Name** und **Freitext** ist auch eine Suche ohne Suchtext möglich, wenn eine Kategorie ausgewählt wurde. Die Adresssuche verwendet dagegen ihre getrennten Adressfelder.

### Eingaben und Treffer leeren ::

**Leeren** entfernt die Text- und Adressfelder, die Trefferliste, die Interpretation und die temporären Suchmarkierungen auf der Karte. Die gewählte Kategorie und die zusätzlichen Suchoptionen werden dabei nicht automatisch zurückgesetzt. Prüfen Sie diese vor einer neuen Suche.

## Räumliche Suchfilter :raumfilter

Öffnen Sie im Register **Suche** die **Weiteren Suchoptionen**.

### Nur im aktuellen Kartenausschnitt ::

Aktivieren Sie **Nur im aktuellen Kartenausschnitt**, wenn die Suche auf das gerade sichtbare Gebiet begrenzt werden soll. Stellen Sie den gewünschten Kartenausschnitt vor dem Start der Suche ein.

### Ausgewählte Objekte als Suchgebiet ::

Wenn eine aktive Projektebene ausgewählte Polygonobjekte bereitstellt, können Sie **Ausgewählte Objekte als Suchgebiet verwenden** aktivieren.

1. Wählen Sie ein oder mehrere Polygonobjekte in der aktiven Ebene aus.
2. Öffnen Sie die **Weiteren Suchoptionen**.
3. Aktivieren Sie **Ausgewählte Objekte als Suchgebiet verwenden**.
4. Starten Sie die Suche.

Beim Einschalten wird der Filter **Nur im aktuellen Kartenausschnitt** ausgeschaltet. Solange das ausgewählte Suchgebiet verwendet wird, ist der Kartenausschnitt-Filter nicht auswählbar.

%info
    Ob ausgewählte Objekte für das Plugin verfügbar sind, hängt von der verwendeten QField-Ausführung und der aktiven Ebene ab. Bei einer nicht verfügbaren oder ungeeigneten Auswahl zeigt das Plugin eine Fehlermeldung. Verwenden Sie dann den Filter für den aktuellen Kartenausschnitt.
%end

### Vollständig innerhalb der Fläche ::

**Treffer müssen vollständig innerhalb der gewählten Fläche liegen** wird beim Aktivieren des ausgewählten Suchgebiets zunächst eingeschaltet. Die Option ist nur zusammen mit diesem Suchgebiet verfügbar. Schalten Sie sie aus, wenn der Dienst auch Treffer berücksichtigen soll, die nicht vollständig innerhalb liegen.

## Sortierung und Unschärfe :sortierung

Die **Weiteren Suchoptionen** enthalten die **Sortierung** und die **Unschärfe**.

| Sortierung | Verwendung |
| --- | --- |
| **Relevanz** | Treffer nach der vom Dienst ermittelten Relevanz ordnen. |
| **Entfernung** | Entfernungsbezogene Reihenfolge mit der Kartenmitte als Bezugspunkt anfordern. |
| **Name** | Eine Sortierung nach Namen anfordern. |
| **Adresse** | Eine Sortierung nach Adressangaben anfordern. |

Die **Unschärfe** ist zwischen 1 und 10 einstellbar; voreingestellt ist 4. Die genaue Auswertung übernimmt der Dienst. Bei zu wenigen Treffern können Sie einen höheren Wert versuchen und anschließend die Treffer prüfen.

Mit **Suchoptionen ausblenden** klappen Sie die zusätzlichen Einstellungen wieder ein. Die eingestellten Werte bleiben dabei erhalten.

## An einer Kartenposition suchen :punktsuche

Der Bereich **Was ist hier?** ist eine eigene Punktsuche. Er ist unabhängig vom Auswahlfeld für **Name**, **Adresse** und **Freitext**.

1. Stellen Sie im Feld neben **Auf Karte wählen** den Suchradius ein. **Automatischer Radius** überlässt die Vorgabe dem Dienst; alternativ wählen Sie einen Wert in Metern bis 10.000 m.
2. Tippen Sie auf **Auf Karte wählen**. Das Bedienfeld schließt sich und eine Meldung fordert zum Tippen auf die Karte auf.
3. Tippen Sie auf die gewünschte Position.
4. Prüfen Sie die zurückgelieferten Treffer im erneut geöffneten Register **Suche**.

Die Punktsuche übermittelt die gewählte Position und gegebenenfalls den Radius. Textsuche, Kategorien, Sortierung und die räumlichen Filter aus den weiteren Suchoptionen werden für diese Anfrage nicht übernommen.

Die Treffer dieser Punktsuche werden als eine Ergebnisliste angezeigt; es gibt dafür keine weitere Ergebnisseite.

## Trefferliste, Details und Kartenansicht :treffer

Nach einer Suche zeigt das Plugin die vom Dienst gemeldete Trefferzahl und die Anzahl der aktuell angezeigten Ergebnisse. Bei einer Text- oder Adresssuche werden bis zu 20 Treffer je Seite angefordert.

### Einen Treffer öffnen ::

Tippen Sie auf einen Eintrag in der Trefferliste. Das Plugin richtet den Kartenausschnitt auf den Treffer aus und versucht, dessen Geometrie hervorzuheben. Die Hervorhebung hängt von den in Ihrer QField-Ausführung verfügbaren Kartenfunktionen ab.

Zu jedem Treffer werden Name, gegebenenfalls weitere Angaben, der Geometrietyp und eine vorhandene Kennung angezeigt. Mit **Details** blenden Sie die gelieferten Objektattribute ein; **Details ausblenden** klappt sie wieder zu.

### Markierungen auf der Karte ::

Das Plugin stellt die Ergebnisse nach Möglichkeit als temporäre Punktmarkierungen auf der Karte dar. Bei flächigen oder linienförmigen Treffern dient die Mitte des jeweiligen Trefferbereichs als Position der Markierung. Die Markierung ist daher nicht mit der vollständigen Objektgeometrie gleichzusetzen.

Wenn die Karteninteraktion in Ihrer QField-Ausführung verfügbar ist, öffnet ein Tippen auf eine Trefferposition den zugehörigen Listeneintrag. Überlappende Treffer prüfen Sie am besten über die Liste.

### Zwischen Ergebnisseiten wechseln ::

Mit **Weiter** und **Zurück** wechseln Sie bei Text- und Adresssuchen zwischen den verfügbaren Ergebnisseiten. Die Seitenanzeige nennt die aktuelle Seite. Die Schaltflächen sind während einer laufenden Anfrage beziehungsweise am Anfang oder Ende der Ergebnisliste deaktiviert.

Eine neue Suche oder **Leeren** ersetzt beziehungsweise entfernt die bisherige Ergebnisdarstellung.

## Dienststatus und Metadaten :status

Im Register **Einstellungen** sehen Sie die Rückmeldung zum Verbindungstest und die **Service-Metadaten**.

Je nach Dienst werden folgende Angaben angezeigt:

- API-Version,
- Abdeckung,
- Datenstand,
- Anzahl der Kategorien,
- Quellenangabe.

Eine erfolgreiche Statusabfrage meldet außerdem die Anzahl der geladenen Stilgenerationen. **Technischen Status anzeigen** blendet die vom Dienst gelieferten Statusdaten ein; **Technischen Status ausblenden** schließt diesen Bereich wieder.

Mit **Erneut testen** aktualisieren Sie die Angaben für die gespeicherte Verbindung. Wenn Sie zuvor die Dienstadresse oder den Schlüssel im Eingabefeld geändert haben, wählen Sie **Speichern und testen**.

## Typische Arbeitsabläufe :arbeitsablaeufe

### Eine Hintergrundkarte für die Sitzung einrichten ::

1. Öffnen Sie **Einstellungen** und speichern Sie die Verbindung mit **Speichern und testen**.
2. Wechseln Sie zu **Karten**.
3. Wählen Sie **Stil** und **Bildformat**.
4. Tippen Sie auf **Zur Karte hinzufügen**.
5. Prüfen Sie die Darstellung und richten Sie bei Bedarf den Ausschnitt mit **Auf Service-Abdeckung zoomen** aus.

### Ein Objekt im Arbeitsgebiet finden ::

1. Stellen Sie den Kartenausschnitt auf Ihr Arbeitsgebiet ein.
2. Öffnen Sie **Suche** und wählen Sie **Name** oder **Freitext**.
3. Tragen Sie einen Suchbegriff ein und wählen Sie bei Bedarf eine Kategorie.
4. Aktivieren Sie unter **Weitere Suchoptionen** den Filter **Nur im aktuellen Kartenausschnitt**.
5. Tippen Sie auf **Suche** und öffnen Sie einen Treffer in der Liste.
6. Prüfen Sie bei Bedarf die **Details** oder wechseln Sie zur nächsten Ergebnisseite.

### Einen Ort auf der Karte untersuchen ::

1. Öffnen Sie **Suche** und den Bereich **Was ist hier?**.
2. Stellen Sie den Radius ein oder lassen Sie **Automatischer Radius** ausgewählt.
3. Tippen Sie auf **Auf Karte wählen** und anschließend auf die gewünschte Kartenposition.
4. Prüfen Sie die Treffer und deren Attribute über **Details**.

## Fehler einordnen :fehler

### Zur Karte hinzufügen ist nicht verfügbar ::

Prüfen Sie, ob ein API-Schlüssel gespeichert wurde und ob ein Kartenstil und Bildformat gewählt werden können. Laden Sie die Daten mit **Aktualisieren** neu. Auch während des Ladens ist die Schaltfläche deaktiviert.

### Eine GBD-Hintergrundkarte ist bereits aktiv ::

Aktivieren Sie **Aktive GBD-Hintergrundkarte ersetzen**, wenn Sie eine andere Variante über die aktuelle Hintergrundkarte des Plugins laden möchten.

### Authentifizierung fehlgeschlagen ::

Prüfen Sie den Schlüssel unter **Einstellungen** und speichern Sie ihn mit **Speichern und testen**. Ein nicht leerer Schlüssel ist keine Bestätigung dafür, dass der Dienst ihn akzeptiert.

### HTTPS-Adresse wird abgelehnt ::

Tragen Sie eine gültige HTTPS-Dienstadresse als **Basis-URL** ein. Verwenden Sie nicht die Adresse einer einzelnen Suchanfrage oder Kachel.

### Verbindung fehlgeschlagen oder Zeitüberschreitung ::

Prüfen Sie die Netzwerkverbindung und die gespeicherte Dienstadresse. Versuchen Sie **Erneut testen**. Bei einer unerwarteten Serverantwort kann das Plugin die Daten nicht weiterverarbeiten; prüfen Sie dann die Verfügbarkeit des Dienstes.

### Keine Treffer ::

Prüfen Sie die Kategorie und die räumlichen Filter. Versuchen Sie einen allgemeineren Suchbegriff, einen größeren Kartenausschnitt oder eine höhere Unschärfe. Bei Adressen müssen Straße und Hausnummer ausgefüllt sein.

### Ausgewählte Fläche kann nicht verwendet werden ::

Prüfen Sie die aktive Vektorebene und die Auswahl von Polygonobjekten. Wenn Ihre QField-Ausführung die Auswahl nicht bereitstellt, verwenden Sie **Nur im aktuellen Kartenausschnitt**.

### Treffer oder Hintergrundkarte werden nicht dargestellt ::

Die Kartenfunktionen hängen von der verwendeten QField-Ausführung ab. Prüfen Sie zunächst die Rückmeldung im Bedienfeld. Eine erfolgreiche Suchanfrage und die Darstellung ihrer temporären Markierungen sind getrennte Schritte; nutzen Sie die Trefferliste zur Prüfung der gelieferten Ergebnisse.

Wenn eine Hintergrundkarte andere Projektlayer verdeckt, beachten Sie, dass diese Fassung sie oben in die laufende Kartenansicht einfügt. Für eine dauerhaft festgelegte Layer-Reihenfolge bereiten Sie die Hintergrundkarte im QGIS-Projekt vor.
