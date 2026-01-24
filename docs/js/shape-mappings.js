/**
 * Shape Mappings - Data extracted from Excel for browser-side figurine composition.
 * This file contains all the data needed to convert a figure ID to its shape combination.
 */

// Shape mappings by question (F01-F06)
// Each question maps to an array of shape names (indexed by answer ID)
const SHAPES_BY_QUESTION = {
  "F01": [
    "semioval",
    "wide_rectangle",
    "capsule_pill",
    "flat_pyramid",
    "wide_rectangle",
    "flat_trapezoid"
  ],
  "F02": [
    "tall_pyramid",
    "rhombus_udlr",
    "upright_pill",
    "double_upright_pill",
    "stacked_circles"
  ],
  "F03": [
    "stepped_block_3",
    "stacked_circles_custom",
    "rhombus_udlr",
    "tall_trapezoid",
    "facing_bowls"
  ],
  "F04": [
    "flat_rectangle",
    "flat_rectangle",
    "flat_rectangle",
    "flat_rectangle",
    "flat_rectangle",
    "flat_rectangle"
  ],
  "F05": [
    "sphere_circle",
    "sphere_circle",
    "sphere_circle",
    "sphere_circle",
    "sphere_circle",
    "sphere_circle"
  ],
  "F06": [
    "capsule_pill",
    "semioval",
    "flat_pyramid_sockel",
    "stepped_block",
    "wide_rectangle"
  ]
};

// Number of answers per question [F01, F02, F03, F04, F05, F06]
const ANSWERS_PER_QUESTION = [6, 5, 5, 6, 6, 5];

// Width ratios for each shape (width = height * ratio)
const SHAPE_WIDTH_RATIOS = {
    "semioval": 2.5,
    "wide_rectangle": 2.2,
    "capsule_pill": 2.5,
    "tapered_trapezoid": 2.5,
    "blocky_trapezoid": 2.0,
    "stepped_block": 2.2,
    "sphere_circle": 1.0,
    "flat_pyramid": 4.0,
    "flat_rectangle": 6.0,
    "flat_pressed_oval": 4.0,
    "flat_trapezoid": 4.0,
    "tall_pyramid": 2/3,
    "rhombus_udlr": 2/3,
    "stacked_circles": 4/7,
    "stacked_circles_custom": 40/49,
    "upright_pill": 10/(Math.PI * 6),
    "flat_pyramid_sockel": 4.0,
    "tall_trapezoid": 2/3,
    "stepped_block_3": 1.0,
    "double_upright_pill": 2/3,
    "facing_bowls": 0.7
};

// Height ratios for 6 levels (top to bottom: level 1 to level 6)
// These match TOKEN_HEIGHT_RATIOS from generate_web_svgs.py
const TOKEN_HEIGHT_RATIOS = [1.5, 3, 1, 6, 6, 1.5];

// Total combinations: 6 * 5 * 5 * 6 * 6 * 5 = 27000
const TOTAL_COMBINATIONS = ANSWERS_PER_QUESTION.reduce((a, b) => a * b, 1);

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.ShapeMappings = {
        SHAPES_BY_QUESTION,
        ANSWERS_PER_QUESTION,
        SHAPE_WIDTH_RATIOS,
        TOKEN_HEIGHT_RATIOS,
        TOTAL_COMBINATIONS
    };
}
