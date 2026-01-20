/**
 * Minimap Navigation for Figurine Gallery
 * Manages the minimap in the top-right corner for grid navigation
 */

const Minimap = (function() {
    'use strict';

    // ==================== Configuration ====================
    const CONFIG = {
        defaultTotalCols: 165,
        defaultTotalRows: 164,
        padding: 8,  // Inner padding from minimap edge
    };

    // ==================== State ====================
    let state = {
        container: null,
        viewport: null,
        positionIndicator: null,
        homeButton: null,
        minimapGrid: null,
        totalCols: CONFIG.defaultTotalCols,
        totalRows: CONFIG.defaultTotalRows,
        userRow: null,
        userCol: null,
        currentRow: 0,
        currentCol: 0,
        viewportRows: 0,
        viewportCols: 0,
        minimapWidth: 0,
        minimapHeight: 0,
        isInitialized: false,
    };

    // ==================== Coordinate Conversion ====================
    /**
     * Convert grid position to minimap pixel coordinates
     * @param {number} gridRow - Grid row position
     * @param {number} gridCol - Grid column position
     * @returns {{x: number, y: number}} Minimap pixel coordinates
     */
    function gridToMinimapCoords(gridRow, gridCol) {
        if (!state.minimapWidth || !state.minimapHeight) {
            updateMinimapDimensions();
        }

        // Calculate available space (excluding padding)
        const availableWidth = state.minimapWidth - (CONFIG.padding * 2);
        const availableHeight = state.minimapHeight - (CONFIG.padding * 2);

        // Calculate scale factors
        const scaleX = availableWidth / state.totalCols;
        const scaleY = availableHeight / state.totalRows;

        // Convert grid position to pixel position
        const x = CONFIG.padding + (gridCol * scaleX);
        const y = CONFIG.padding + (gridRow * scaleY);

        return { x, y };
    }

    /**
     * Convert minimap pixel coordinates to grid position
     * @param {number} minimapX - X pixel position on minimap
     * @param {number} minimapY - Y pixel position on minimap
     * @returns {{row: number, col: number}} Grid position
     */
    function minimapToGridCoords(minimapX, minimapY) {
        // Calculate available space (excluding padding)
        const availableWidth = state.minimapWidth - (CONFIG.padding * 2);
        const availableHeight = state.minimapHeight - (CONFIG.padding * 2);

        // Clamp to available area
        const clampedX = Math.max(0, Math.min(minimapX - CONFIG.padding, availableWidth));
        const clampedY = Math.max(0, Math.min(minimapY - CONFIG.padding, availableHeight));

        // Calculate scale factors
        const scaleX = state.totalCols / availableWidth;
        const scaleY = state.totalRows / availableHeight;

        // Convert pixel position to grid position
        const col = Math.floor(clampedX * scaleX);
        const row = Math.floor(clampedY * scaleY);

        // Clamp to valid grid range
        return {
            row: Math.max(0, Math.min(row, state.totalRows - 1)),
            col: Math.max(0, Math.min(col, state.totalCols - 1)),
        };
    }

    // ==================== Dimension Management ====================
    /**
     * Update cached minimap dimensions from CSS
     */
    function updateMinimapDimensions() {
        if (!state.minimapGrid) return;

        const rect = state.minimapGrid.getBoundingClientRect();
        state.minimapWidth = rect.width;
        state.minimapHeight = rect.height;
    }

    // ==================== Visual Updates ====================
    /**
     * Update the position indicator (red dot) for user's figure
     * @param {number} row - Grid row of user's figure
     * @param {number} col - Grid column of user's figure
     */
    function setUserPosition(row, col) {
        state.userRow = row;
        state.userCol = col;

        if (!state.positionIndicator) return;

        const coords = gridToMinimapCoords(row, col);
        
        // Position the red dot
        state.positionIndicator.style.left = `${coords.x}px`;
        state.positionIndicator.style.top = `${coords.y}px`;
        state.positionIndicator.style.display = 'block';
    }

    /**
     * Update the viewport rectangle showing visible area
     * @param {number} row - Center row of visible area
     * @param {number} col - Center column of visible area
     * @param {number} visibleRows - Number of visible rows
     * @param {number} visibleCols - Number of visible columns
     */
    function updateViewportIndicator(row, col, visibleRows, visibleCols) {
        if (!state.viewport) return;

        // Calculate available space
        const availableWidth = state.minimapWidth - (CONFIG.padding * 2);
        const availableHeight = state.minimapHeight - (CONFIG.padding * 2);

        // Calculate scale factors
        const scaleX = availableWidth / state.totalCols;
        const scaleY = availableHeight / state.totalRows;

        // Calculate viewport rectangle dimensions
        const viewportWidth = Math.max(4, visibleCols * scaleX);
        const viewportHeight = Math.max(4, visibleRows * scaleY);

        // Calculate top-left corner (center position - half dimensions)
        const topLeftCol = col - Math.floor(visibleCols / 2);
        const topLeftRow = row - Math.floor(visibleRows / 2);

        const coords = gridToMinimapCoords(topLeftRow, topLeftCol);

        // Update viewport rectangle position and size
        state.viewport.style.left = `${Math.max(CONFIG.padding, coords.x)}px`;
        state.viewport.style.top = `${Math.max(CONFIG.padding, coords.y)}px`;
        state.viewport.style.width = `${Math.min(viewportWidth, availableWidth)}px`;
        state.viewport.style.height = `${Math.min(viewportHeight, availableHeight)}px`;
        state.viewport.style.display = 'block';
    }

    /**
     * Update the entire minimap display
     * @param {number} currentRow - Current center row position
     * @param {number} currentCol - Current center column position
     * @param {number} viewportRows - Number of visible rows
     * @param {number} viewportCols - Number of visible columns
     */
    function updatePosition(currentRow, currentCol, viewportRows, viewportCols) {
        state.currentRow = currentRow;
        state.currentCol = currentCol;
        state.viewportRows = viewportRows;
        state.viewportCols = viewportCols;

        // Update viewport indicator
        updateViewportIndicator(currentRow, currentCol, viewportRows, viewportCols);
    }

    // ==================== Event Handlers ====================
    /**
     * Handle click on minimap grid
     * @param {MouseEvent|TouchEvent} event
     */
    function handleMinimapClick(event) {
        event.preventDefault();
        event.stopPropagation();

        if (!state.minimapGrid) return;

        // Get click/touch coordinates relative to minimap grid
        const rect = state.minimapGrid.getBoundingClientRect();
        let clientX, clientY;

        if (event.touches && event.touches.length > 0) {
            clientX = event.touches[0].clientX;
            clientY = event.touches[0].clientY;
        } else if (event.changedTouches && event.changedTouches.length > 0) {
            clientX = event.changedTouches[0].clientX;
            clientY = event.changedTouches[0].clientY;
        } else {
            clientX = event.clientX;
            clientY = event.clientY;
        }

        const minimapX = clientX - rect.left;
        const minimapY = clientY - rect.top;

        // Convert to grid coordinates
        const gridPos = minimapToGridCoords(minimapX, minimapY);

        // Add visual feedback
        state.container.classList.add('minimap-container--clicked');
        setTimeout(() => {
            state.container.classList.remove('minimap-container--clicked');
        }, 150);

        // Emit custom event for grid navigation
        const customEvent = new CustomEvent('minimapClick', {
            detail: {
                row: gridPos.row,
                col: gridPos.col,
            },
            bubbles: true,
        });

        state.container.dispatchEvent(customEvent);
    }

    /**
     * Handle home button click
     * @param {MouseEvent|TouchEvent} event
     */
    function handleHomeClick(event) {
        event.preventDefault();
        event.stopPropagation();

        // Add visual feedback
        state.homeButton.classList.add('minimap-home-btn--clicked');
        setTimeout(() => {
            state.homeButton.classList.remove('minimap-home-btn--clicked');
        }, 150);

        // Emit custom event to return to user's figure
        const customEvent = new CustomEvent('goHome', {
            detail: {
                userRow: state.userRow,
                userCol: state.userCol,
            },
            bubbles: true,
        });

        state.container.dispatchEvent(customEvent);
    }

    /**
     * Handle scroll update event from GridManager
     * @param {CustomEvent} event
     */
    function handleScrollUpdate(event) {
        const detail = event.detail;

        if (detail) {
            updatePosition(
                detail.centerRow,
                detail.centerCol,
                detail.viewportRows,
                detail.viewportCols
            );

            // Update grid dimensions if provided
            if (detail.totalRows && detail.totalCols) {
                state.totalRows = detail.totalRows;
                state.totalCols = detail.totalCols;
            }
        }
    }

    /**
     * Handle window resize
     */
    function handleResize() {
        updateMinimapDimensions();

        // Re-render current state
        if (state.userRow !== null && state.userCol !== null) {
            setUserPosition(state.userRow, state.userCol);
        }

        updateViewportIndicator(
            state.currentRow,
            state.currentCol,
            state.viewportRows,
            state.viewportCols
        );
    }

    // ==================== Initialization ====================
    /**
     * Initialize the minimap module
     * @param {Object} gridConfig - Grid configuration
     * @param {number} gridConfig.totalCols - Total number of columns in grid
     * @param {number} gridConfig.totalRows - Total number of rows in grid
     * @param {number} gridConfig.userRow - User's figure row position
     * @param {number} gridConfig.userCol - User's figure column position
     */
    function init(gridConfig = {}) {
        if (state.isInitialized) {
            console.warn('Minimap already initialized');
            return;
        }

        // Get DOM elements
        state.container = document.getElementById('minimap-container');
        state.viewport = document.getElementById('minimap-viewport');
        state.positionIndicator = document.getElementById('minimap-position');
        state.homeButton = document.getElementById('minimap-home-btn');
        state.minimapGrid = state.container?.querySelector('.minimap-grid');

        if (!state.container) {
            console.error('Minimap: Required DOM elements not found');
            return;
        }

        // Apply configuration
        state.totalCols = gridConfig.totalCols || CONFIG.defaultTotalCols;
        state.totalRows = gridConfig.totalRows || CONFIG.defaultTotalRows;

        // Update dimensions from CSS
        updateMinimapDimensions();

        // Set user position if provided
        if (gridConfig.userRow !== undefined && gridConfig.userCol !== undefined) {
            setUserPosition(gridConfig.userRow, gridConfig.userCol);
        }

        // Attach event listeners
        if (state.minimapGrid) {
            state.minimapGrid.addEventListener('click', handleMinimapClick);
            state.minimapGrid.addEventListener('touchend', handleMinimapClick, { passive: false });
        }

        if (state.homeButton) {
            state.homeButton.addEventListener('click', handleHomeClick);
            state.homeButton.addEventListener('touchend', handleHomeClick, { passive: false });
        }

        // Listen for scroll updates from grid
        document.addEventListener('scrollUpdate', handleScrollUpdate);

        // Listen for window resize
        window.addEventListener('resize', handleResize, { passive: true });

        state.isInitialized = true;

        console.log('Minimap initialized with grid:', state.totalCols, 'x', state.totalRows);
    }

    /**
     * Clean up and destroy the minimap
     */
    function destroy() {
        if (!state.isInitialized) return;

        // Remove event listeners
        if (state.minimapGrid) {
            state.minimapGrid.removeEventListener('click', handleMinimapClick);
            state.minimapGrid.removeEventListener('touchend', handleMinimapClick);
        }

        if (state.homeButton) {
            state.homeButton.removeEventListener('click', handleHomeClick);
            state.homeButton.removeEventListener('touchend', handleHomeClick);
        }

        document.removeEventListener('scrollUpdate', handleScrollUpdate);
        window.removeEventListener('resize', handleResize);

        // Reset state
        state.container = null;
        state.viewport = null;
        state.positionIndicator = null;
        state.homeButton = null;
        state.minimapGrid = null;
        state.userRow = null;
        state.userCol = null;
        state.isInitialized = false;

        console.log('Minimap destroyed');
    }

    // ==================== Public API ====================
    return {
        // Core methods
        init,
        destroy,

        // Position updates
        updatePosition,
        setUserPosition,
        updateViewportIndicator,

        // Coordinate conversion
        gridToMinimapCoords,

        // Getters
        get isInitialized() { return state.isInitialized; },
        get userPosition() {
            return { row: state.userRow, col: state.userCol };
        },
        get currentPosition() {
            return { row: state.currentRow, col: state.currentCol };
        },
        get gridDimensions() {
            return { rows: state.totalRows, cols: state.totalCols };
        },

        // For debugging/testing
        _state: state,
        _CONFIG: CONFIG,
    };
})();

// Export for module systems if available
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Minimap;
}
