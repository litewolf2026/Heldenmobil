# HeldenMobil

DSA 4.1 Heldentool für HLD-Dateien mit lokalen Begleitdaten und optionalem OneDrive-Sync.

## Quellstruktur ab v20.3.2

- `index.html` – HTML/CSS und statische Oberfläche
- `vendor/jszip-3.10.1.min.js` – vendorte ZIP-Bibliothek für HLD-Dateien
- `js/hld-parser.js` – HLD-Parsing und HLD-spezifische Semantik
- `js/companion-core.js` – Begleitdaten-Normalisierung, Ereignisaggregation und Sync-Entscheidungslogik
- `js/combat-core.js` – kleine, bereits produktiv genutzte Kampfberechnungen
- `js/app.js` – UI, Orchestrierung, OneDrive/Graph und verbleibende Anwendungslogik
- `tests/smoke.mjs` – Struktur-, Lade- und Syntaxprüfungen
- `tests/core.mjs` – Regressionstests für Parser-, Companion-, Sync- und Kampfverhalten

## Stabilisierung v20.1 bis v20.3.2

- **v20.1:** HLD-Parser aus dem UI-Monolithen gelöst und HLD-Semantik testbar gemacht.
- **v20.2:** Companion-/Abenteuer-Normalisierung ausgelagert; Energieereignisse werden dauerhaft normalisiert; OneDrive erkennt mit persistenter Sync-Baseline parallele Offline-/Remote-Änderungen und blockiert fail-closed statt still zu überschreiben.
- **v20.3:** bestehende Kampfberechnung in ein testbares Core-Modul verschoben; Wundereignisse bleiben manuell, passive magische Wirkungen sind nicht auslösbar, destruktive Magie-Aktionen sind bestätigt, Zauberliste nutzt die generische Einklapplogik.
- **v20.3.1:** lokale Sicherungshistorie mit Wiederherstellung/Export ergänzt und letzten erfolgreichen OneDrive-Sync sichtbar gemacht.
- **v20.3.2:** Backup-Historie auf fünf Stände begrenzt und aus `localStorage` in IndexedDB verschoben; bestehende v20.3.1-Sicherungen werden beim ersten Zugriff automatisch übernommen.

Die Module bilden nur Verhalten ab, das HeldenMobil tatsächlich verwendet. Es wird kein vollständiges DSA-4.1-Regelwerk nachgebaut.

## Tests

```bash
npm test
```

Die CI führt die Tests bei jedem Push und Pull Request aus.
