# HeldenMobil

DSA 4.1 Heldentool fuer HLD-Dateien mit lokalen Begleitdaten und optionalem OneDrive-Sync.

## Quellstruktur ab v20

- `index.html` - HTML/CSS und statische Oberflaeche
- `vendor/jszip-3.10.1.min.js` - vendorte ZIP-Bibliothek fuer HLD-Dateien
- `js/app.js` - HeldenMobil-Anwendungslogik (wird in den folgenden v20-Schritten weiter modularisiert)
- `tests/smoke.mjs` - regressionskritische Struktur- und Syntaxpruefungen

## Tests

```bash
npm test
```

Die CI fuehrt diese Tests bei jedem Push und Pull Request aus.
