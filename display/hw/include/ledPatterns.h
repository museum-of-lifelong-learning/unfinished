#ifndef LED_PATTERNS_H
#define LED_PATTERNS_H

#include <MD_MAX72xx.h>

extern MD_MAX72XX mx;
extern const int MAX_DEVICES;

void testAllSingleLEDs() {
  Serial.println("\n>>> TEST 1: Single LED Scan (All 256 LEDs)");
  Serial.println("Each LED will light individually for 50ms");
  
  int ledCount = 0;
  for (int row = 0; row < 8; row++) {
    for (int col = 0; col < MAX_DEVICES * 8; col++) {
      mx.clear();
      mx.setPoint(row, col, true);
      mx.update();
      
      ledCount++;
      if (col % 8 == 0 && col > 0) {
        Serial.print("  Module ");
        Serial.print(col / 8);
        Serial.println();
      }
      
      delay(50);
    }
    Serial.print("Row ");
    Serial.print(row);
    Serial.print(" complete (");
    Serial.print(ledCount);
    Serial.println(" LEDs tested)");
  }
  
  mx.clear();
  mx.update();
  Serial.println("Single LED test complete!\n");
  delay(2000);
}

void testAllLEDsOn() {
  Serial.println("\n>>> TEST 2: All LEDs ON");
  
  for (int r = 0; r < 8; r++) {
    for (int c = 0; c < MAX_DEVICES * 8; c++) {
      mx.setPoint(r, c, true);
    }
  }
  mx.update();
  
  Serial.print("All ");
  Serial.print(8 * MAX_DEVICES * 8);
  Serial.println(" LEDs should be ON");
  delay(3000);
  
  mx.clear();
  mx.update();
  delay(500);
}

void testRows() {
  Serial.println("\n>>> TEST 3: Row-by-Row Test");
  
  for (int row = 0; row < 8; row++) {
    mx.clear();
    
    for (int col = 0; col < MAX_DEVICES * 8; col++) {
      mx.setPoint(row, col, true);
    }
    mx.update();
    
    Serial.print("Row ");
    Serial.print(row);
    Serial.println(" ON");
    delay(500);
  }
  
  mx.clear();
  mx.update();
  Serial.println("Row test complete\n");
  delay(500);
}

void testColumns() {
  Serial.println("\n>>> TEST 4: Column-by-Column Test");
  
  for (int col = 0; col < MAX_DEVICES * 8; col++) {
    mx.clear();
    
    for (int row = 0; row < 8; row++) {
      mx.setPoint(row, col, true);
    }
    mx.update();
    
    if (col % 8 == 0) {
      Serial.print("Module ");
      Serial.print(col / 8);
      Serial.print(": ");
    }
    Serial.print(col % 8);
    Serial.print(" ");
    
    if (col % 8 == 7) {
      Serial.println();
    }
    
    delay(50);
  }
  
  mx.clear();
  mx.update();
  Serial.println("Column test complete\n");
  delay(500);
}

void testModules() {
  Serial.println("\n>>> TEST 5: Module-by-Module Test");
  
  for (int module = 0; module < MAX_DEVICES; module++) {
    mx.clear();
    
    int startCol = module * 8;
    int endCol = startCol + 8;
    
    for (int row = 0; row < 8; row++) {
      for (int col = startCol; col < endCol; col++) {
        mx.setPoint(row, col, true);
      }
    }
    mx.update();
    
    Serial.print("Module ");
    Serial.print(module);
    Serial.println(" ON (columns ");
    Serial.print(startCol);
    Serial.print("-");
    Serial.print(endCol - 1);
    Serial.println(")");
    
    delay(1000);
  }
  
  mx.clear();
  mx.update();
  Serial.println("Module test complete\n");
  delay(500);
}

void testCheckerboard() {
  Serial.println("\n>>> TEST 6: Checkerboard Pattern");
  
  mx.clear();
  int onCount = 0;
  
  for (int row = 0; row < 8; row++) {
    for (int col = 0; col < MAX_DEVICES * 8; col++) {
      if ((row + col) % 2 == 0) {
        mx.setPoint(row, col, true);
        onCount++;
      }
    }
  }
  mx.update();
  
  Serial.print("Checkerboard: ");
  Serial.print(onCount);
  Serial.println(" LEDs ON");
  delay(2000);
  
  mx.clear();
  mx.update();
  delay(500);
}

void testCorners() {
  Serial.println("\n>>> TEST 7: Four Corners");
  
  mx.clear();
  mx.setPoint(0, 0, true);                          // Top-Left
  mx.setPoint(0, MAX_DEVICES * 8 - 1, true);        // Top-Right
  mx.setPoint(7, 0, true);                          // Bottom-Left
  mx.setPoint(7, MAX_DEVICES * 8 - 1, true);        // Bottom-Right
  mx.update();
  
  Serial.println("All 4 corners should be lit");
  delay(2000);
  
  mx.clear();
  mx.update();
  delay(500);
}

#endif // LED_PATTERNS_H
