#include <Arduino.h>
#include <MD_MAX72xx.h>
#include <SPI.h>

// --- DISPLAY CONFIGURATION -------------------------------------------------
#define HARDWARE_TYPE MD_MAX72XX::FC16_HW
#define MAX_DEVICES 4
#define CLK_PIN   0   // D0
#define DATA_PIN  2   // D2 (DIN)
#define CS_PIN    1   // D1

MD_MAX72XX mx = MD_MAX72XX(HARDWARE_TYPE, DATA_PIN, CLK_PIN, CS_PIN, MAX_DEVICES);
constexpr int DISPLAY_WIDTH = MAX_DEVICES * 8;

// --- STATE & HELPERS -------------------------------------------------------
enum Pattern { PATTERN_NONE, PATTERN_BORED, PATTERN_THINKING, PATTERN_FINISH, PATTERN_REMOVE_FIGURE, PATTERN_ERROR };

struct Point { int8_t x, y; };

struct SnakeState {
  Point body[5];
  Point food;
  int8_t dirX, dirY;
};

struct PatternState {
  Pattern current = PATTERN_NONE;
  uint8_t stage = 0;       // sub-state inside a pattern
  int16_t scrollX = 0;     // scroll position for text
  int16_t var1 = 0;        // reusable
  int16_t var2 = 0;        // reusable
  unsigned long lastStep = 0;
  SnakeState snake;        // For BORED state
};

PatternState ps;
uint8_t gSpeed = 5;        // 0-10 (higher = faster)
uint8_t gBrightness = 7;   // 0-15

// Full 5x7 Font
const uint8_t FONT_5x7[][5] = {
  {0x00, 0x00, 0x00, 0x00, 0x00}, // space
  {0x00, 0x00, 0x5F, 0x00, 0x00}, // !
  {0x00, 0x07, 0x00, 0x07, 0x00}, // "
  {0x14, 0x7F, 0x14, 0x7F, 0x14}, // #
  {0x24, 0x2A, 0x7F, 0x2A, 0x12}, // $
  {0x23, 0x13, 0x08, 0x64, 0x62}, // %
  {0x36, 0x49, 0x55, 0x22, 0x50}, // &
  {0x00, 0x05, 0x03, 0x00, 0x00}, // '
  {0x00, 0x1C, 0x22, 0x41, 0x00}, // (
  {0x00, 0x41, 0x22, 0x1C, 0x00}, // )
  {0x14, 0x08, 0x3E, 0x08, 0x14}, // *
  {0x08, 0x08, 0x3E, 0x08, 0x08}, // +
  {0x00, 0x50, 0x30, 0x00, 0x00}, // ,
  {0x08, 0x08, 0x08, 0x08, 0x08}, // -
  {0x00, 0x60, 0x60, 0x00, 0x00}, // .
  {0x20, 0x10, 0x08, 0x04, 0x02}, // /
  {0x3E, 0x51, 0x49, 0x45, 0x3E}, // 0
  {0x00, 0x42, 0x7F, 0x40, 0x00}, // 1
  {0x42, 0x61, 0x51, 0x49, 0x46}, // 2
  {0x21, 0x41, 0x45, 0x4B, 0x31}, // 3
  {0x18, 0x14, 0x12, 0x7F, 0x10}, // 4
  {0x27, 0x45, 0x45, 0x45, 0x39}, // 5
  {0x3C, 0x4A, 0x49, 0x49, 0x30}, // 6
  {0x01, 0x71, 0x09, 0x05, 0x03}, // 7
  {0x36, 0x49, 0x49, 0x49, 0x36}, // 8
  {0x06, 0x49, 0x49, 0x29, 0x1E}, // 9
  {0x00, 0x36, 0x36, 0x00, 0x00}, // :
  {0x00, 0x56, 0x36, 0x00, 0x00}, // ;
  {0x08, 0x14, 0x22, 0x41, 0x00}, // <
  {0x14, 0x14, 0x14, 0x14, 0x14}, // =
  {0x00, 0x41, 0x22, 0x14, 0x08}, // >
  {0x02, 0x01, 0x51, 0x09, 0x06}, // ?
  {0x32, 0x49, 0x79, 0x41, 0x3E}, // @
  {0x7E, 0x11, 0x11, 0x11, 0x7E}, // A
  {0x7F, 0x49, 0x49, 0x49, 0x36}, // B
  {0x3E, 0x41, 0x41, 0x41, 0x22}, // C
  {0x7F, 0x41, 0x41, 0x22, 0x1C}, // D
  {0x7F, 0x49, 0x49, 0x49, 0x41}, // E
  {0x7F, 0x09, 0x09, 0x09, 0x01}, // F
  {0x3E, 0x41, 0x49, 0x49, 0x7A}, // G
  {0x7F, 0x08, 0x08, 0x08, 0x7F}, // H
  {0x00, 0x41, 0x7F, 0x41, 0x00}, // I
  {0x20, 0x40, 0x41, 0x3F, 0x01}, // J
  {0x7F, 0x08, 0x14, 0x22, 0x41}, // K
  {0x7F, 0x40, 0x40, 0x40, 0x40}, // L
  {0x7F, 0x02, 0x0C, 0x02, 0x7F}, // M
  {0x7F, 0x04, 0x08, 0x10, 0x7F}, // N
  {0x3E, 0x41, 0x41, 0x41, 0x3E}, // O
  {0x7F, 0x09, 0x09, 0x09, 0x06}, // P
  {0x3E, 0x41, 0x51, 0x21, 0x5E}, // Q
  {0x7F, 0x09, 0x19, 0x29, 0x46}, // R
  {0x46, 0x49, 0x49, 0x49, 0x31}, // S
  {0x01, 0x01, 0x7F, 0x01, 0x01}, // T
  {0x3F, 0x40, 0x40, 0x40, 0x3F}, // U
  {0x1F, 0x20, 0x40, 0x20, 0x1F}, // V
  {0x3F, 0x40, 0x38, 0x40, 0x3F}, // W
  {0x63, 0x14, 0x08, 0x14, 0x63}, // X
  {0x07, 0x08, 0x70, 0x08, 0x07}, // Y
  {0x61, 0x51, 0x49, 0x45, 0x43}, // Z
  {0x00, 0x7F, 0x41, 0x41, 0x00}, // [
  {0x02, 0x04, 0x08, 0x10, 0x20}, // \ (backslash)
  {0x00, 0x41, 0x41, 0x7F, 0x00}, // ]
  {0x04, 0x02, 0x01, 0x02, 0x04}, // ^
  {0x40, 0x40, 0x40, 0x40, 0x40}  // _
};

int textWidth(const String &s) { return s.length() * 6; }

const uint8_t* glyphFor(char c) {
  if (c < 32 || c > 95) return FONT_5x7[0];
  return FONT_5x7[c - 32];
}

void drawChar5x7(int x, int y, char c) {
  const uint8_t* g = glyphFor(c);
  for (int col = 0; col < 5; col++) {
    uint8_t bits = g[col];
    for (int row = 0; row < 7; row++) {
      // Standard orientation: LSB is top (row 0)
      bool on = bits & (1 << row);
      int xx = x + col;
      int yy = y + row;
      if (xx >= 0 && xx < DISPLAY_WIDTH && yy >= 0 && yy < 8) {
        mx.setPoint(7 - yy, xx, on); // flip vertically to fix orientation
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
  int x = (DISPLAY_WIDTH - w) / 2;
  if (x < 0) x = 0;
  mx.clear();
  drawText(x, 0, s);
  mx.update();
}

int adjustedInterval(int baseMs) {
  float factor = 1.6f - (gSpeed * 0.12f);
  int v = (int)(baseMs * factor);
  return v < 15 ? 15 : v;
}

void clearAll() {
  mx.clear();
  mx.update();
}

// --- SNAKE HELPERS ---------------------------------------------------------
void spawnFood() {
  while (true) {
    ps.snake.food.x = random(0, MAX_DEVICES * 8);
    ps.snake.food.y = random(0, 8);
    // Check collision with body
    bool collision = false;
    for (int i = 0; i < 5; i++) {
      if (ps.snake.body[i].x == ps.snake.food.x && ps.snake.body[i].y == ps.snake.food.y) {
        collision = true;
        break;
      }
    }
    if (!collision) break;
  }
}

void initSnake() {
  // Start in middle
  int startX = (MAX_DEVICES * 8) / 2;
  int startY = 4;
  for (int i = 0; i < 5; i++) {
    ps.snake.body[i] = { (int8_t)(startX - i), (int8_t)startY };
  }
  ps.snake.dirX = 1;
  ps.snake.dirY = 0;
  spawnFood();
}

void updateSnakeAI() {
  Point head = ps.snake.body[0];
  Point food = ps.snake.food;
  
  // Simple AI: Move towards food
  // Try X axis first
  int dx = 0, dy = 0;
  
  if (head.x < food.x) dx = 1;
  else if (head.x > food.x) dx = -1;
  
  if (head.y < food.y) dy = 1;
  else if (head.y > food.y) dy = -1;
  
  // Prevent 180 turns
  if (dx != 0 && dx == -ps.snake.dirX) dx = 0;
  if (dy != 0 && dy == -ps.snake.dirY) dy = 0;
  
  // Decide direction (randomize slightly if both valid to look organic)
  if (dx != 0 && dy != 0) {
    if (random(0, 2) == 0) dy = 0; else dx = 0;
  }
  
  // If blocked or aligned, take the other axis
  if (dx == 0 && dy == 0) {
    // Already at target? (Should be eaten)
    // Just keep moving current dir
    dx = ps.snake.dirX;
    dy = ps.snake.dirY;
  } else if (dx != 0) {
    ps.snake.dirX = dx;
    ps.snake.dirY = 0;
  } else if (dy != 0) {
    ps.snake.dirX = 0;
    ps.snake.dirY = dy;
  }
}

// --- PATTERN START ---------------------------------------------------------
void startPattern(Pattern p) {
  ps.current = p;
  ps.stage = 0;
  ps.var1 = 0;
  ps.var2 = 0;
  ps.lastStep = 0;
  clearAll();
  
  switch (p) {
    case PATTERN_BORED:
      Serial.println("Pattern=BORED");
      initSnake();
      break;
    case PATTERN_THINKING:
      Serial.println("Pattern=THINKING");
      ps.scrollX = DISPLAY_WIDTH; // Start off-screen right
      break;
    case PATTERN_FINISH:
      Serial.println("Pattern=FINISH");
      ps.scrollX = DISPLAY_WIDTH; // Start off-screen right
      break;
    case PATTERN_REMOVE_FIGURE:
      Serial.println("Pattern=REMOVE_FIGURE");
      ps.scrollX = DISPLAY_WIDTH; // Start off-screen right
      break;
    case PATTERN_ERROR:
      Serial.println("Pattern=ERROR");
      ps.var1 = 0; // blink toggle
      break;
    default:
      Serial.println("Pattern=NONE");
      break;
  }
}

// --- PATTERN UPDATES -------------------------------------------------------
void updateBored(unsigned long now) {
  // Snake moves every 300ms
  if (now - ps.lastStep < 300) return;
  ps.lastStep = now;
  
  updateSnakeAI();
  
  // Move body
  Point nextHead = { 
    (int8_t)(ps.snake.body[0].x + ps.snake.dirX), 
    (int8_t)(ps.snake.body[0].y + ps.snake.dirY) 
  };
  
  // Wrap around
  if (nextHead.x < 0) nextHead.x = (MAX_DEVICES * 8) - 1;
  if (nextHead.x >= (MAX_DEVICES * 8)) nextHead.x = 0;
  if (nextHead.y < 0) nextHead.y = 7;
  if (nextHead.y >= 8) nextHead.y = 0;
  
  // Check food
  bool ate = (nextHead.x == ps.snake.food.x && nextHead.y == ps.snake.food.y);
  
  // Shift body
  for (int i = 4; i > 0; i--) {
    ps.snake.body[i] = ps.snake.body[i-1];
  }
  ps.snake.body[0] = nextHead;
  
  if (ate) {
    spawnFood();
  }
  
  // Draw
  mx.clear();
  // Draw Food
  mx.setPoint(7 - ps.snake.food.y, ps.snake.food.x, true);
  // Draw Snake
  for (int i = 0; i < 5; i++) {
    mx.setPoint(7 - ps.snake.body[i].y, ps.snake.body[i].x, true);
  }
  mx.update();
}

void updateThinking(unsigned long now) {
  int interval = adjustedInterval(80);
  if (now - ps.lastStep < (unsigned long)interval) return;
  ps.lastStep = now;
  
  String text = "THINKING   ";
  mx.clear();
  drawText(ps.scrollX, 0, text);
  mx.update();
  
  ps.scrollX--;
  if (ps.scrollX < -textWidth(text)) {
    ps.scrollX = DISPLAY_WIDTH;
  }
}

void updateFinish(unsigned long now) {
  int interval = adjustedInterval(80);
  if (now - ps.lastStep < (unsigned long)interval) return;
  ps.lastStep = now;
  
  String text = "- THANK YOU FOR THE VISIT -   ";
  mx.clear();
  drawText(ps.scrollX, 0, text);
  mx.update();
  
  ps.scrollX--;
  if (ps.scrollX < -textWidth(text)) {
    ps.scrollX = DISPLAY_WIDTH;
  }
}

void updateRemoveFigure(unsigned long now) {
  int interval = adjustedInterval(80);
  if (now - ps.lastStep < (unsigned long)interval) return;
  ps.lastStep = now;
  
  String text = "PLEASE REMOVE FIGURE   ";
  mx.clear();
  drawText(ps.scrollX, 0, text);
  mx.update();
  
  ps.scrollX--;
  if (ps.scrollX < -textWidth(text)) {
    ps.scrollX = DISPLAY_WIDTH;
  }
}

void updateError(unsigned long now) {
  int interval = adjustedInterval(200);
  if (now - ps.lastStep < (unsigned long)interval) return;
  ps.lastStep = now;
  ps.var1 = !ps.var1; // blink

  mx.clear();
  if (ps.var1) {
    drawCentered("ERROR");
  }
  mx.update();
}

void updatePattern() {
  unsigned long now = millis();
  switch (ps.current) {
    case PATTERN_BORED:    updateBored(now); break;
    case PATTERN_THINKING: updateThinking(now); break;
    case PATTERN_FINISH:   updateFinish(now); break;
    case PATTERN_REMOVE_FIGURE: updateRemoveFigure(now); break;
    case PATTERN_ERROR:    updateError(now); break;
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
    else if (arg == "REMOVE_FIGURE") startPattern(PATTERN_REMOVE_FIGURE);
    else if (arg == "PRINTING") startPattern(PATTERN_THINKING); // Reuse thinking for printing
    else if (arg == "ERROR")    startPattern(PATTERN_ERROR);
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
  
  if (cmd == "CLEAR") {
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
      case PATTERN_REMOVE_FIGURE: Serial.print("REMOVE_FIGURE"); break;
      case PATTERN_ERROR:    Serial.print("ERROR"); break;
      default: Serial.print("NONE"); break;
    }
    Serial.print(" SPEED="); Serial.print(gSpeed);
    Serial.print(" BRIGHT="); Serial.println(gBrightness);
    return;
  }

  if (cmd == "HELP") {
    Serial.println("OK COMMANDS: PATTERN <BORED|THINKING|FINISH|REMOVE_FIGURE|ERROR>, STOP, CLEAR, SPEED <0-10>, BRIGHT <0-15>, STATUS, HELP");
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
  Serial.println("Commands: PATTERN <BORED|THINKING|FINISH|REMOVE_FIGURE>, STOP, CLEAR, SPEED <0-10>, BRIGHT <0-15>, STATUS, HELP");

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
