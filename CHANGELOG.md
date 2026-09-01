# Changelog

## v20.3.2

- Lokale Sicherungshistorie pro Held von 10 auf 5 Stände reduziert.
- Sicherungsstände in IndexedDB verschoben; der aktuelle Companion-Datensatz bleibt für die stabile v1-Endphase weiterhin im bewährten `localStorage`.
- Bestehende v20.3.1-Sicherungen werden beim ersten Zugriff automatisch nach IndexedDB migriert und auf die fünf neuesten Stände begrenzt.
- Falls IndexedDB nicht verfügbar ist, bleibt ein auf fünf Stände begrenzter `localStorage`-Fallback aktiv.
- Wiederherstellen und vollständiges Zurücksetzen brechen ab, wenn der aktuelle Stand vorher nicht erfolgreich gesichert werden konnte.

## v20.3.1

- Bis zu 10 automatische lokale Sicherungsstände je Held ergänzt; vor Änderungen wird der vorherige persistierte Stand gesichert.
- Sicherungen können in der Oberfläche manuell erzeugt, wiederhergestellt und als JSON exportiert werden.
- Ein vollständiges Zurücksetzen legt vorher zwingend eine lokale Sicherung an.
- Bei knappem Browser-Speicher werden zuerst alte Sicherungen verworfen, bevor ein aktueller Spielstand verloren gehen kann.
- Zeitpunkt des letzten erfolgreichen OneDrive-Syncs ist in den Daten- und Sync-Informationen sichtbar.

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
