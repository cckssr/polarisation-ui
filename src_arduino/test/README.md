# Arduino Firmware Testing

Unit-Tests für die SCPI-Firmware ohne physische Hardware.

## Überblick

- **Framework**: PlatformIO Unit Testing (Unity)
- **Platform**: Native (Dein Computer, nicht Arduino)
- **Tests befinden sich in**: `test/test_*.cpp`

## Tests ausführen

```bash
cd src_arduino

# Alle Tests ausführen
pio test -e native_test

# Spezifischen Test ausführen
pio test -e native_test --filter test_scpi_parser

# Verbose Output
pio test -e native_test -v
```

## Aktuelle Tests

### `test_scpi_parser.cpp`

Testet die SCPI-Befehlsanalyse:

- Query-Befehle (`*IDN?`)
- Commands mit Parametern (`CONF:ADC:GAIN 16`)
- Case-Insensitivität
- Whitespace-Handling
- Multiple Parameter (`CONF:SRC ENC:A,ADC,PDTIA`)

## Wie Tests funktionieren

1. **PlatformIO native environment** kompiliert den Code für Deinen Computer (macOS/Linux/Windows)
2. **Mock-Objekte** ersetzen Arduino-spezifische Typen (z.B. `String`)
3. **Unity Framework** führt die Tests aus und gibt Ergebnisse aus

## Neue Tests hinzufügen

### Schritt 1: Neue Test-Datei erstellen

```bash
touch test/test_my_feature.cpp
```

### Schritt 2: Test schreiben

```cpp
#include <unity.h>

void test_my_feature() {
  // Arrange
  int result = myFunction(5);

  // Assert
  TEST_ASSERT_EQUAL(10, result);
}

void setUp(void) {}
void tearDown(void) {}
```

### Schritt 3: Ausführen

```bash
pio test -e native_test
```

## Test-Makros (Unity)

```cpp
TEST_ASSERT_TRUE(condition)
TEST_ASSERT_FALSE(condition)
TEST_ASSERT_EQUAL(expected, actual)
TEST_ASSERT_EQUAL_STRING(expected_str, actual_str)
TEST_ASSERT_NOT_NULL(pointer)
TEST_ASSERT_NULL(pointer)
TEST_ASSERT_GREATER_THAN(threshold, actual)
// ... und viele mehr (siehe unity.h)
```

## Testen des echten Quellcodes (`.inc`-Pattern)

`scpiParse()` lebt in `src/scpi_parse.inc` und wird per `#include` sowohl von
`src/scpi.cpp` (Firmware, `String` = Arduinos echte Klasse) als auch von
`test_scpi_parser.cpp` (nativer Test, `String` = `StringMock`) eingebunden.
So testet der native Test exakt denselben Quellcode wie die Firmware, statt
einer separat gepflegten Kopie, die unbemerkt abweichen könnte. Für weitere
Funktionen, die ohne Hardware-Zugriff testbar sind, denselben Ansatz nutzen:
Logik in eine `.inc`-Datei auslagern und von beiden Seiten einbinden.

## Mock-Objekte

Die `StringMock`-Klasse in `test_scpi_parser.cpp` simuliert Arduino's `String` Klasse.

Weitere Mock-Beispiele:

```cpp
// Für Testing ohne ADS1220
class ADS1220Mock {
  float lastVoltage() { return 1.234; }
  bool adcPresent() { return true; }
};
```

## Nächste Schritte

1. Tests für `handleConfAdcGain()`, `handleMeasAdcVolt()` schreiben
2. Mock für ADC-Session erstellen
3. Integration-Tests für komplette Command-Sequenzen

## Troubleshooting

**"native_test environment not found"**

```bash
pio platform install native
```

**Compile-Fehler wegen Arduino-Dependencies**
→ Nutze `#ifdef UNIT_TEST` um Hardware-Code auszuschließen
