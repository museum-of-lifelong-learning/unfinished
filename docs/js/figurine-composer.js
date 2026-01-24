/**
 * Figurine Composer - Dynamically compose figurines from individual shape SVGs.
 * Converts figure IDs to shape combinations and renders them as inline SVGs.
 */
const FigurineComposer = (function() {
    'use strict';

    // Configuration
    const CONFIG = {
        shapePath: 'assets/shapes/',
        defaultFigurineHeight: 240,  // Total height for figurine stack (matches FIGURINE_HEIGHT in Python)
        padding: 2
    };

    // Cache for loaded shape SVGs (shape name -> SVG content string)
    const shapeCache = new Map();
    
    // Cache for composed figurine SVGs (figure ID -> SVG data URL)
    const figurineCache = new Map();
    
    // Loading promise for shape preloading
    let shapesLoadedPromise = null;

    /**
     * Get all unique shape names used across all questions.
     */
    function getAllShapeNames() {
        const shapes = new Set();
        const mappings = window.ShapeMappings.SHAPES_BY_QUESTION;
        for (const question of Object.values(mappings)) {
            for (const shape of question) {
                shapes.add(shape);
            }
        }
        return Array.from(shapes);
    }

    /**
     * Preload all shape SVGs into cache.
     * Returns a promise that resolves when all shapes are loaded.
     */
    async function preloadShapes() {
        if (shapesLoadedPromise) return shapesLoadedPromise;

        const shapeNames = getAllShapeNames();
        console.log(`FigurineComposer: Preloading ${shapeNames.length} shapes...`);

        shapesLoadedPromise = Promise.all(
            shapeNames.map(async (name) => {
                try {
                    const response = await fetch(`${CONFIG.shapePath}${name}.svg`);
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    const svgText = await response.text();
                    shapeCache.set(name, svgText);
                } catch (error) {
                    console.error(`Failed to load shape: ${name}`, error);
                }
            })
        ).then(() => {
            console.log(`FigurineComposer: Loaded ${shapeCache.size} shapes`);
        });

        return shapesLoadedPromise;
    }

    /**
     * Convert a figure ID (1-27000) to its shape combination.
     * Returns array of 6 shape names in visual order (top to bottom).
     */
    function idToShapes(figureId) {
        const { SHAPES_BY_QUESTION, ANSWERS_PER_QUESTION, TOTAL_COMBINATIONS } = window.ShapeMappings;

        if (figureId < 1 || figureId > TOTAL_COMBINATIONS) {
            console.error(`Figure ID ${figureId} out of range [1, ${TOTAL_COMBINATIONS}]`);
            return null;
        }

        // Convert to 0-indexed
        let idValue = figureId - 1;

        // Decode using mixed-radix system (same as Python implementation)
        // Indices are in F01-F06 order
        const questionIndices = [0, 0, 0, 0, 0, 0];
        for (let i = 5; i >= 0; i--) {
            questionIndices[i] = idValue % ANSWERS_PER_QUESTION[i];
            idValue = Math.floor(idValue / ANSWERS_PER_QUESTION[i]);
        }

        // Convert indices to shapes in visual order (top=F06 to bottom=F01)
        const shapes = [];
        for (let level = 1; level <= 6; level++) {
            // Level 1 (top) = F06, Level 6 (bottom) = F01
            const questionIdx = 6 - level;  // Level 1 → 5 (F06), Level 6 → 0 (F01)
            const questionKey = `F${String(questionIdx + 1).padStart(2, '0')}`;
            const shapeIdx = questionIndices[questionIdx];
            shapes.push(SHAPES_BY_QUESTION[questionKey][shapeIdx]);
        }

        return shapes;
    }

    /**
     * Extract the inner content of an SVG (everything inside the root <svg> tag).
     * Also extracts width/height from the original SVG.
     */
    function parseSvgContent(svgText) {
        // Parse the SVG to extract dimensions and inner content
        const parser = new DOMParser();
        const doc = parser.parseFromString(svgText, 'image/svg+xml');
        const svgElement = doc.querySelector('svg');
        
        if (!svgElement) return null;

        const width = parseFloat(svgElement.getAttribute('width')) || 100;
        const height = parseFloat(svgElement.getAttribute('height')) || 100;
        
        // Get inner content (all child elements)
        let innerContent = '';
        for (const child of svgElement.children) {
            innerContent += child.outerHTML;
        }

        return { width, height, innerContent };
    }

    /**
     * Compose a figurine SVG from its shape names.
     * Returns SVG content as a string.
     */
    function composeFigurineSvg(shapes, totalHeight = CONFIG.defaultFigurineHeight) {
        const { TOKEN_HEIGHT_RATIOS, SHAPE_WIDTH_RATIOS } = window.ShapeMappings;

        // Calculate individual shape heights using token_height_ratios
        const totalRatio = TOKEN_HEIGHT_RATIOS.reduce((a, b) => a + b, 0);
        const shapeHeights = TOKEN_HEIGHT_RATIOS.map(ratio => totalHeight * ratio / totalRatio);

        // Calculate max width needed for any shape in this figurine
        let maxWidth = 0;
        for (let i = 0; i < shapes.length; i++) {
            const shapeName = shapes[i];
            const widthRatio = SHAPE_WIDTH_RATIOS[shapeName] || 2.5;
            const shapeWidth = shapeHeights[i] * widthRatio;
            maxWidth = Math.max(maxWidth, shapeWidth);
        }

        // Calculate exact content dimensions
        const contentHeight = shapeHeights.reduce((a, b) => a + b, 0);
        const contentWidth = maxWidth;

        // Add minimal padding
        const padding = CONFIG.padding;
        const viewWidth = contentWidth + 2 * padding;
        const viewHeight = contentHeight + 2 * padding;

        // Build SVG content
        let svgContent = `<svg xmlns="http://www.w3.org/2000/svg" width="${viewWidth}" height="${viewHeight}" viewBox="0 0 ${viewWidth} ${viewHeight}">`;

        // Draw shapes from top to bottom (level 1 at top, level 6 at bottom)
        let currentY = padding;
        for (let i = 0; i < shapes.length; i++) {
            const shapeName = shapes[i];
            const targetHeight = shapeHeights[i];
            const widthRatio = SHAPE_WIDTH_RATIOS[shapeName] || 2.5;
            const shapeWidth = targetHeight * widthRatio;

            // Get cached shape SVG
            const shapeSvg = shapeCache.get(shapeName);
            if (!shapeSvg) {
                console.warn(`Shape not cached: ${shapeName}`);
                currentY += targetHeight;
                continue;
            }

            // Parse the shape SVG
            const parsed = parseSvgContent(shapeSvg);
            if (!parsed) {
                currentY += targetHeight;
                continue;
            }

            // Calculate scale factor (shape SVGs are at standardized 100px height)
            const scale = targetHeight / parsed.height;

            // Center horizontally
            const shapeX = (viewWidth - shapeWidth) / 2;

            // Add transformed group
            svgContent += `<g transform="translate(${shapeX}, ${currentY}) scale(${scale})">`;
            svgContent += parsed.innerContent;
            svgContent += `</g>`;

            currentY += targetHeight;
        }

        svgContent += '</svg>';
        return svgContent;
    }

    /**
     * Get a figurine SVG as a data URL (cached).
     */
    function getFigurineSvgDataUrl(figureId, height = CONFIG.defaultFigurineHeight) {
        const cacheKey = `${figureId}_${height}`;
        
        if (figurineCache.has(cacheKey)) {
            return figurineCache.get(cacheKey);
        }

        const shapes = idToShapes(figureId);
        if (!shapes) return null;

        const svgContent = composeFigurineSvg(shapes, height);
        const dataUrl = `data:image/svg+xml;charset=utf-8,${encodeURIComponent(svgContent)}`;
        
        figurineCache.set(cacheKey, dataUrl);
        return dataUrl;
    }

    /**
     * Get a figurine SVG as raw SVG string.
     */
    function getFigurineSvg(figureId, height = CONFIG.defaultFigurineHeight) {
        const shapes = idToShapes(figureId);
        if (!shapes) return null;
        return composeFigurineSvg(shapes, height);
    }

    /**
     * Create an inline SVG element for a figurine.
     */
    function createFigurineSvgElement(figureId, height = CONFIG.defaultFigurineHeight) {
        const svgContent = getFigurineSvg(figureId, height);
        if (!svgContent) return null;

        const parser = new DOMParser();
        const doc = parser.parseFromString(svgContent, 'image/svg+xml');
        return doc.querySelector('svg');
    }

    /**
     * Set an img element's src to a composed figurine.
     */
    function setImgSrc(imgElement, figureId, height = CONFIG.defaultFigurineHeight) {
        const dataUrl = getFigurineSvgDataUrl(figureId, height);
        if (dataUrl) {
            imgElement.src = dataUrl;
        }
    }

    /**
     * Check if all shapes are loaded.
     */
    function isReady() {
        return shapeCache.size > 0;
    }

    /**
     * Clear the figurine cache (useful if memory is a concern).
     */
    function clearFigurineCache() {
        figurineCache.clear();
    }

    /**
     * Get cache statistics.
     */
    function getCacheStats() {
        return {
            shapesLoaded: shapeCache.size,
            figurinesCached: figurineCache.size
        };
    }

    // Public API
    return {
        preloadShapes,
        idToShapes,
        getFigurineSvg,
        getFigurineSvgDataUrl,
        createFigurineSvgElement,
        setImgSrc,
        isReady,
        clearFigurineCache,
        getCacheStats,
        CONFIG
    };
})();

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.FigurineComposer = FigurineComposer;
}
