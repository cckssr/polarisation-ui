# TODO Liste - Polarisation UI Vervollständigung

## ✅ Abgeschlossen (Phase 0 - Grundarchitektur)

1. **Device Manager** - Zentrale Verwaltung von Encoder-Hardware
2. **Connection Dialog** - Dialog zur Geräteverbindung mit Portauswahl (vor Hauptfenster)
3. **Main Window mit Qt Designer UI** - Verwendet vorhandene ui_mainwindow.py
   - LCD-Displays für Encoder-Werte (Sample Stage, Detector Stage)
   - Status-LEDs für Verbindungsstatus
   - Zero-Buttons für beide Encoder
   - Start/Stop/Reset Buttons für Messung
   - Save-Funktionalität mit Gruppe/Suffix
   - Plot-Bereiche (noch leer)
4. **Data Controller** - Threading und kontinuierliche Datenakquise (10 Hz)
5. **Common UI Utilities** - Dialoge und Statusbar-Management
6. **Save Service** - Grundgerüst für Datenspeicherung
7. **Main Entry Point** - Connection Dialog vor Hauptfenster, Device Manager Übergabe

---

## 🔧 Zu behebende Fehler

### Kritisch (vor erstem Hardware-Test)

- [ ] **Arduino-Kommunikation testen**: Erste Verbindung mit echter Hardware
- [ ] **Type Hints**: Response-Handling in dual_encoder.py (str | bytes → str)

### Warnings (nicht kritisch, später beheben)

- [ ] Exception-Handling zu spezifisch machen (statt generisches `Exception`)
- [ ] F-Strings ohne Interpolation bereinigen
- [ ] `__package__` Warning in main.py

---

## 📋 Nächste Schritte (Funktionalität)

### Phase 1: Grundfunktionen vervollständigen

#### Hardware-Integration

- [ ] **Arduino-Firmware validieren**: Kommunikation mit Hardware testen
- [ ] **Photodetector-Adapter**: Adapter für Photodetektor hinzufügen
  - `PhotodetectorAdapter` (Abstract Base)
  - `PhotodetectorSerial` oder `PhotodetectorAnalog` (für Arduino ADC)
  - Integration in Device Manager
  - LCD-Display in UI verbinden (bereits vorhanden: detector_voltage)

#### Messdaten-Management

- [ ] **Measurement Service erweitern**:
  - `MeasurementPoint` aus core/models.py verwenden
  - Datenpunkte während Messung aufzeichnen
  - Session-Verwaltung implementieren
  - Datenhistorie verwalten
- [ ] **Save/Export Funktionalität**:
  - Save Dialog mit Dateiauswahl
  - CSV Export mit save_service vervollständigen
  - Metadaten erfassen (Datum, Sample-Info, Gruppe, Suffix)
  - Automatisches Backup bei laufender Messung

#### UI-Verbesserungen

- [ ] **Measurement Data Recording**:
  - Liste/Tabelle der aufgezeichneten Datenpunkte
  - Live-Counter für Anzahl Messpunkte
  - Zeitstempel-Anzeige
- [ ] **Settings Dialog**:
  - Polling-Intervall konfigurierbar
  - Speicherorte festlegen
  - Encoder-Konfiguration (z.B. Toleranzen)
- [ ] **Toolbar hinzufügen**: Schnellzugriff auf häufige Aktionen

---

### Phase 2: Datenvisualisierung

- [ ] **Plot-Integration**: PyQtGraph für Echtzeit-Plots
  - Intensität vs. Winkel (plot_measurement Widget verwenden)
  - Zeitreihen-Darstellung (plot_detector Widget verwenden)
  - Export von Plots
  - Zoom, Pan, Cursor-Funktionalität
- [ ] **Goniometer Graphics**: Visualisierung der Goniometer-Geometrie
  - 2D-Schematik des Aufbaus
  - Live-Update der Winkelpositionen
  - Validierungsanzeige für 2:1 Geometrie

---

### Phase 3: Erweiterte Features

#### Automatisierung

- [ ] **Automatische Messreihen**:
  - Winkelbereich definieren (Start, Ende, Schrittweite)
  - Dialog für manuelle Positionierung mit Warte-Prompt
  - Automatische Datenpunkt-Aufnahme nach Bestätigung
  - Fortschrittsanzeige

#### Analyse

- [ ] **Datenanalyse-Tools**:
  - Peak-Detektion
  - Fit-Funktionen (Gauss, Lorentz, etc.)
  - Polarisationsgrad-Berechnung
  - Export von Analyse-Ergebnissen

#### Erweiterte Persistenz

- [ ] **Session-Recovery**: Automatisches Wiederherstellen bei Absturz
- [ ] **Datenbank-Integration** (optional): SQLite für Messdaten-Historie

---

## 🧪 Testing & Qualität

### Unit Tests

- [ ] Core Services testen (ohne Qt-Abhängigkeiten)
- [ ] Device Manager mit Mock-Devices testen
- [ ] Data Controller Signal-Emission testen

### Integration Tests

- [ ] End-to-End Test: Verbindung → Messung → Speicherung
- [ ] Hardware-Tests mit Arduino

### Dokumentation

- [ ] User Manual erstellen
- [ ] API-Dokumentation für Entwickler
- [ ] Hardware-Setup Dokumentation (Verkabelung, etc.)

---

## 🔍 Bekannte Einschränkungen (Design-Entscheidungen)

1. **Manueller Goniometer**: System erfordert manuelle Positionierung (keine Motorsteuerung)
2. **Plots noch nicht implementiert**: Fokus auf Live-Werte, Plots in Phase 2
3. **Single-Thread Messung**: Aktuell einfaches Timer-basiertes Polling (ausreichend für 10 Hz)
4. **Keine Kalibrierung**: Encoder-Offset muss manuell durch Zero-Funktion gesetzt werden
5. **Photodetektor noch nicht integriert**: LCD-Display vorhanden, aber keine Daten

---

## ⚙️ Architektur-Validierung

### ✅ Eingehaltene Prinzipien

- **3-Layer-Architektur**: Core → Infrastructure → UI strikt eingehalten
- **Qt Designer UI**: Verwendung der vorhandenen ui_mainwindow.py
- **Connection-First**: Dialog vor Hauptfenster (wie im GMCounter)
- **Device-Adapter-Pattern**: Mit Mock-Support für Tests
- **Signal/Slot-Kommunikation**: Lose Kopplung zwischen Komponenten
- **Type Hints**: Durchgehend (mit wenigen bekannten Ausnahmen)

### ⚠️ Zu überprüfen

- Exception-Handling-Strategie konsistent machen
- Logging-Level konfigurierbar machen (bereits in Config)
- Error-Recovery-Mechanismen erweitern

---

## 📅 Priorisierung

### Sofort (vor erstem Test)

1. ✅ Qt Designer UI integrieren
2. ✅ Connection Dialog vor Hauptfenster
3. ✅ Live-Werte-Anzeige in LCD-Displays
4. Test mit echter Arduino-Hardware

### Kurzfristig (diese Woche)

1. Photodetector-Integration
2. Messdaten-Aufzeichnung implementieren
3. Save/Export funktionsfähig machen

### Mittelfristig (nächste Woche)

1. Plot-Integration
2. Automatische Messreihen
3. Erweiterte UI-Funktionen

### Langfristig (nach Feedback)

1. Analyse-Tools
2. Erweiterte Automatisierung
3. Datenbank-Integration

---

## 📝 Notizen

- **Qt Designer UI**: Erfolgreich integriert, alle Widgets verfügbar
- **GMCounter als Referenz**: Connection-Pattern übernommen
- **Config.json**: Bereits vorhanden, evtl. für Goniometer anpassen
- **Serial-Kommunikation**: DualEncoderArduino vollständig implementiert
- **Logging**: Debug-System vollständig integriert
- **LEDs**: Grün = Connected, Rot = Error, Grau = Not implemented

---

## 🎯 Aktuelle Implementierung

### Was funktioniert:

- ✅ Connection Dialog mit Portauswahl
- ✅ Automatische Verbindung beim Start
- ✅ Live-Anzeige der Encoder-Werte (wenn Hardware angeschlossen)
- ✅ Zeroing der Encoder
- ✅ Start/Stop Measurement (UI-State, noch keine Datenaufzeichnung)
- ✅ Status-LEDs für Verbindungsstatus
- ✅ Statusbar mit Meldungen

### Was noch fehlt:

- ⏳ Tatsächliche Datenaufzeichnung bei Messung
- ⏳ Photodetector-Integration
- ⏳ Save-Funktionalität mit echten Daten
- ⏳ Plots und Visualisierung

---

**Stand**: 14. Januar 2026  
**Phase**: Phase 0 - Architektur abgeschlossen ✓  
**Nächster Meilenstein**: Hardware-Test & Datenaufzeichnung
