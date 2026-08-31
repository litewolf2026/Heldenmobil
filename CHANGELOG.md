# Changelog

## v20.3

- Kampf-Kernberechnungen aus `app.js` entkoppelt und als Regressionstests eingefroren.
- Passive magische Wirkungen können keine Ladungen mehr verbrauchen und werden als passiv dargestellt.
- Löschen von Wirkungen bzw. allen magischen Daten erfordert Bestätigung.
- Wunden/Statusereignisse sind wieder manuell bearbeitbar und werden nicht wie automatische Energieereignisse behandelt.
- Zauberliste in die generische, persistente Einklapplogik aufgenommen.

## v20.2

- Companion-Normalisierung und Energieereignis-Aggregation in `js/companion-core.js` ausgelagert.
- Normalisierte Altbestände werden ohne Änderung des Zeitstempels zurückgespeichert.
- Persistente OneDrive-Sync-Baseline ergänzt: parallele lokale und entfernte Änderungen führen zu einem Konflikt statt zu stillem Überschreiben.

## v20.1

- HLD-Parser und HLD-spezifische Liturgie-/Ausrüstungssemantik in `js/hld-parser.js` ausgelagert.
- Erste gezielte HLD-Regressionstests ergänzt.

## v20.0

- Monolithische `index.html` in HTML, `js/app.js` und vendorte JSZip-Datei aufgeteilt.
- Dauerhafte CI und Smoke-Tests eingeführt.
