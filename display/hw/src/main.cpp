#include <Arduino.h>
#include <MD_MAX72xx.h>
#include <SPI.h>

// --- DISPLAY CONFIGURATION -------------------------------------------------
// Software SPI pins (working set)
#define HARDWARE_TYPE MD_MAX72XX::FC16_HW
#define MAX_DEVICES 4
#define CLK_PIN   0   // D0
#define DATA_PIN  2   // D2 (DIN)
#define CS_PIN    1   // D1

MD_MAX72XX mx = MD_MAX72XX(HARDWARE_TYPE, DATA_PIN, CLK_PIN, CS_PIN, MAX_DEVICES);

// --- STATE & HELPERS -------------------------------------------------------
enum Pattern { PATTERN_NONE, PATTERN_BORED, PATTERN_THINKING, PATTERN_FINISH };

struct PatternState {
  Pattern current = PATTERN_NONE;
  uint8_t stage = 0;       // sub-state inside a pattern
  int16_t scrollX = 0;     // scroll position for text
  int16_t var1 = 0;        // reusable (e.g., HI y-pos)
  int16_t var2 = 0;        // reusable
  unsigned long lastStep = 0;
};

PatternState ps;
uint8_t gSpeed = 5;        // 0-10 (higher = faster)
uint8_t gBrightness = 7;   // 0-15

// Simple 5x7 font (MSB is top row). Only needed chars are defined.
struct Glyph { char c; uint8_t data[5]; };
const Glyph FONT[] = {
  {' ', {0x00,0x00,0x00,0x00,0x00}},
  {'!', {0x00,0x00,0x5F,0x00,0x00}},
  {'B', {0x7F,0x49,0x49,0x49,0x36}},
  {'E', {0x7F,0x49,0x49,0x49,0x41}},
  {'G', {0x3E,0x41,0x49,0x49,0x7A}},
  {'H', {0x7F,0x08,0x08,0x08,0x7F}},
  {'I', {0x00,0x41,0x7F,0x41,0x00}},
  {'K', {0x7F,0x08,0x14,0x22,0x41}},
  {'N', {0x7F,0x04,0x08,0x10,0x7F}},
  {'O', {0x3E,0x41,0x41,0x41,0x3E}},
  {'S', {0x26,0x49,0x49,0x49,0x32}},
  {'T', {0x01,0x01,0x7F,0x01,0x01}},
  {'Y', {0x07,0x08,0x70,0x08,0x07}},
};

int textWidth(const String &s) { return s.length() * 6; }

const uint8_t* glyphFor(char c) {
  for (auto &g : FONT) if (g.c == c) return g.data;
  return FONT[0].data; // space fallback
}

void drawChar5x7(int x, int y, char c) {
  const uint8_t* g = glyphFor(c);
  for (int col = 0; col < 5; col++) {
    uint8_t bits = g[col];
    for (int row = 0; row < 7; row++) {
      bool on = bits & (1 << row);
      int xx = x + col;
      int yy = y + row;
      if (xx >= 0 && xx < (MAX_DEVICES * 8) && yy >= 0 && yy < 8) {
        mx.setPoint(yy, xx, on);
      }
    }
  }
}

void drawText(int x, int y, const String &s) {
  int cursor = x;
  for (int i = 0; i < s.length(); i++) {
    drawChar5x7(cursor, y, s[i]);
    cursor += 6; // 5px + 1px space
  }
}

void drawCentered(const String &s) {
  int w = textWidth(s);
  int x = ((MAX_DEVICES * 8) - w) / 2;
  if (x < 0) x = 0;
  mx.clear();
  drawText(x, 0, s);
  mx.update();
}

int adjustedInterval(int baseMs) {
  // Map speed 0..10 to factor 1.6..0.4
  float factor = 1.6f - (gSpeed * 0.12f);
  int v = (int)(baseMs * factor);
  return v < 15 ? 15 : v;
}

void clearAll() {
  mx.clear();
  mx.update();
}

// --- PATTERN START ---------------------------------------------------------
void startPattern(Pattern p) {
  ps.current = p;
  ps.stage = 0;
  ps.scrollX = MAX_DEVICES * 8;
  ps.var1 = 0;
  ps.var2 = 0;
  ps.lastStep = 0;
  clearAll();
  switch (p) {
    case PATTERN_BORED:
      Serial.println("Pattern=BORED");
      break;
    case PATTERN_THINKING:
      Serial.println("Pattern=THINKING");
      break;
    case PATTERN_FINISH:
      Serial.println("Pattern=FINISH");
      break;
    default:
      Serial.println("Pattern=NONE");
      break;
  }
}

// --- PATTERN UPDATES -------------------------------------------------------
void updateBored(unsigned long now) {
  int interval = adjustedInterval(140);
  if (now - ps.lastStep < (unsigned long)interval) return;
  ps.lastStep = now;
  // Gentle sparkle: toggle a few random pixels
  for (int i = 0; i < 3; i++) {
    int r = random(0, 8);
    int c = random(0, MAX_DEVICES * 8);
    bool cur = mx.getPoint(r, c);
    mx.setPoint(r, c, !cur);
  }
  // Light drift bar occasionally
  if (random(0, 8) == 0) {
    int col = random(0, MAX_DEVICES * 8);
    for (int r = 0; r < 8; r++) mx.setPoint(r, col, true);
  }
  mx.update();
}

void updateThinking(unsigned long now) {
  if (ps.stage == 0) {
    // Show "OH!" only once to avoid redraw flicker
    if (ps.var2 == 0) {
      drawCentered("OH!");
      ps.var2 = 1;
      ps.lastStep = now;
    }
    if (now - ps.lastStep > 1200) {
      ps.stage = 1;
      ps.var1 = 8; // start HI off-screen vertically
      ps.lastStep = now;
      ps.var2 = 0; // reuse flag
    }
    return;
  }

  if (ps.stage == 1) {
    int interval = adjustedInterval(120);
    if (now - ps.lastStep < (unsigned long)interval) return;
    ps.lastStep = now;
    mx.clear();
    drawText((MAX_DEVICES * 8 - textWidth("HI")) / 2, ps.var1, "HI");
    mx.update();
    ps.var1--; // move up
    if (ps.var1 <= 0) {
      ps.stage = 2;
      ps.scrollX = -textWidth("thinking   ");
      ps.lastStep = now;
    }
    return;
  }

  if (ps.stage == 2) {
    int interval = adjustedInterval(80);
    if (now - ps.lastStep < (unsigned long)interval) return;
    ps.lastStep = now;
    mx.clear();
    drawText(ps.scrollX, 0, "thinking   ");
    mx.update();
    ps.scrollX++;
    if (ps.scrollX > (MAX_DEVICES * 8)) {
      ps.scrollX = -textWidth("thinking   ");
    }
  }
}

void updateFinish(unsigned long now) {
  if (ps.stage == 0) {
    if (ps.var2 == 0) {
      drawCentered("THIS IS IT");
      ps.var2 = 1;
      ps.lastStep = now;
    }
    if (now - ps.lastStep > 1800) {
      ps.stage = 1;
      ps.scrollX = -textWidth("BYE   ");
      ps.lastStep = now;
      ps.var2 = 0; // reuse
    }
    return;
  }

  if (ps.stage == 1) {
    int interval = adjustedInterval(90);
    if (now - ps.lastStep < (unsigned long)interval) return;
    ps.lastStep = now;
    mx.clear();
    drawText(ps.scrollX, 0, "BYE   ");
    mx.update();
    ps.scrollX++;
    if (ps.scrollX > (MAX_DEVICES * 8)) {
      // done once
      ps.stage = 2;
      ps.lastStep = now;
    }
    return;
  }

  if (ps.stage == 2) {
    clearAll();
    ps.current = PATTERN_NONE;
    Serial.println("Pattern FINISH complete.");
  }
}

void updatePattern() {
  unsigned long now = millis();
  switch (ps.current) {
    case PATTERN_BORED:    updateBored(now); break;
    case PATTERN_THINKING: updateThinking(now); break;
    case PATTERN_FINISH:   updateFinish(now); break;
    default: break;
  }
}

// --- SERIAL COMMANDS -------------------------------------------------------
void handleCommand(const String &line) {
  String cmd = line;
  cmd.trim();
  cmd.toUpperCase();
  if (cmd.length() == 0) return;

  if (cmd.startsWith("PATTERN ")) {
    String arg = cmd.substring(8);
    arg.trim();
    if (arg == "BORED")      startPattern(PATTERN_BORED);
    else if (arg == "THINKING") startPattern(PATTERN_THINKING);
    else if (arg == "FINISH")   startPattern(PATTERN_FINISH);
    else {
      Serial.println("ERR UNKNOWN PATTERN");
      return;
    }
    Serial.println("OK");
    return;
  }

  if (cmd == "STOP") {
    startPattern(PATTERN_NONE);
    Serial.println("OK");
    return;
  }

  if (cmd.startsWith("SPEED ")) {
    int v = cmd.substring(6).toInt();
    if (v < 0) v = 0; if (v > 10) v = 10;
    gSpeed = v;
    Serial.print("OK SPEED="); Serial.println(gSpeed);
    return;
  }

  if (cmd.startsWith("BRIGHT ")) {
    int v = cmd.substring(7).toInt();
    if (v < 0) v = 0; if (v > 15) v = 15;
    gBrightness = v;
    mx.control(MD_MAX72XX::INTENSITY, gBrightness);
    Serial.print("OK BRIGHT="); Serial.println(gBrightness);
    return;
  }

  if (cmd == "STATUS") {
    Serial.print("OK PATTERN=");
    switch (ps.current) {
      case PATTERN_BORED:    Serial.print("BORED"); break;
      case PATTERN_THINKING: Serial.print("THINKING"); break;
      case PATTERN_FINISH:   Serial.print("FINISH"); break;
      default: Serial.print("NONE"); break;
    }
    Serial.print(" SPEED="); Serial.print(gSpeed);
    Serial.print(" BRIGHT="); Serial.println(gBrightness);
    return;
  }

  if (cmd == "HELP") {
    Serial.println("OK COMMANDS: PATTERN <BORED|THINKING|FINISH>, STOP, SPEED <0-10>, BRIGHT <0-15>, STATUS, HELP");
    return;
  }

  Serial.println("ERR UNKNOWN COMMAND");
}

void readSerialCommands() {
  static String buf;
  while (Serial.available()) {
    char ch = (char)Serial.read();
    if (ch == '\n' || ch == '\r') {
      if (buf.length() > 0) {
        handleCommand(buf);
        buf = "";
      }
    } else {
      buf += ch;
      if (buf.length() > 64) buf.remove(0, 32); // prevent runaway
    }
  }
}

// --- SETUP / LOOP ----------------------------------------------------------
void setup() {
  Serial.begin(115200);
  delay(500);
  Serial.println("\n=== LED Controller Ready ===");
  Serial.println("Commands: PATTERN <BORED|THINKING|FINISH>, STOP, SPEED <0-10>, BRIGHT <0-15>, STATUS, HELP");

  if (!mx.begin()) {
    Serial.println("Error initializing MD_MAX72XX library!");
    while (1) {}
  }
  // Batch updates to reduce flicker; we call mx.update() manually
  mx.control(MD_MAX72XX::UPDATE, MD_MAX72XX::OFF);
  mx.control(MD_MAX72XX::INTENSITY, gBrightness);
  clearAll();
}

void loop() {
  readSerialCommands();
  updatePattern();
}
