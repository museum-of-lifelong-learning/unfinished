/**
 * Grid Manager - Simplified version with runtime figurine composition
 */
const GridManager = (function() {
    'use strict';

    const CONFIG = {
        totalFigures: 27000,
        gridCols: 165,
        gridRows: 164,
        bufferZone: 10,  // Increased for more aggressive preloading
        cellGap: 8
    };

    let state = {
        userFigureId: 1,
        userGridRow: 82,
        userGridCol: 82,
        figureMapping: new Map(),
        visibleCells: new Map(),
        cellPool: [],
        scrollContainer: null,
        gridElement: null,
        cellWidth: 150,
        cellHeight: 300,
        isInitialized: false,
        scrollRAF: null
    };

    function mulberry32(seed) {
        return function() {
            let t = seed += 0x6D2B79F5;
            t = Math.imul(t ^ t >>> 15, t | 1);
            t ^= t + Math.imul(t ^ t >>> 7, t | 61);
            return ((t ^ t >>> 14) >>> 0) / 4294967296;
        };
    }

    function wrapPosition(row, col) {
        let r = row % CONFIG.gridRows;
        let c = col % CONFIG.gridCols;
        if (r < 0) r += CONFIG.gridRows;
        if (c < 0) c += CONFIG.gridCols;
        return { row: r, col: c };
    }

    function getKey(row, col) {
        return `${row},${col}`;
    }

    function generateMapping(seed) {
        const random = mulberry32(seed);
        state.figureMapping.clear();
        
        const figures = [];
        for (let i = 1; i <= CONFIG.totalFigures; i++) {
            if (i !== state.userFigureId) figures.push(i);
        }
        
        // Shuffle
        for (let i = figures.length - 1; i > 0; i--) {
            const j = Math.floor(random() * (i + 1));
            [figures[i], figures[j]] = [figures[j], figures[i]];
        }
        
        // Center position for user
        state.userGridRow = Math.floor(CONFIG.gridRows / 2);
        state.userGridCol = Math.floor(CONFIG.gridCols / 2);
        state.figureMapping.set(getKey(state.userGridRow, state.userGridCol), state.userFigureId);
        
        let idx = 0;
        for (let r = 0; r < CONFIG.gridRows; r++) {
            for (let c = 0; c < CONFIG.gridCols; c++) {
                const key = getKey(r, c);
                if (!state.figureMapping.has(key)) {
                    state.figureMapping.set(key, figures[idx % figures.length]);
                    idx++;
                }
            }
        }
    }

    function getFigureAt(row, col) {
        const w = wrapPosition(row, col);
        return state.figureMapping.get(getKey(w.row, w.col)) || 1;
    }

    function getVisibleRange() {
        if (!state.scrollContainer) return null;
        const sl = state.scrollContainer.scrollLeft;
        const st = state.scrollContainer.scrollTop;
        const vw = state.scrollContainer.clientWidth;
        const vh = state.scrollContainer.clientHeight;
        
        const cw = state.cellWidth + CONFIG.cellGap;
        const ch = state.cellHeight + CONFIG.cellGap;
        
        return {
            startCol: Math.floor(sl / cw) - CONFIG.bufferZone,
            endCol: Math.ceil((sl + vw) / cw) + CONFIG.bufferZone,
            startRow: Math.floor(st / ch) - CONFIG.bufferZone,
            endRow: Math.ceil((st + vh) / ch) + CONFIG.bufferZone
        };
    }

    function getCellFromPool() {
        if (state.cellPool.length > 0) return state.cellPool.pop();
        
        const cell = document.createElement('div');
        cell.className = 'figure-cell';
        const img = document.createElement('img');
        img.className = 'figure-cell__image';
        img.decoding = 'async';  // Non-blocking decode
        cell.appendChild(img);
        
        cell.addEventListener('click', (e) => {
            const fid = parseInt(cell.dataset.figureId, 10);
            const isUser = fid === state.userFigureId;
            // Only allow clicks on the user's figure
            if (isUser) {
                state.gridElement.dispatchEvent(new CustomEvent('figureClick', {
                    detail: { figureId: fid, isUserFigure: isUser },
                    bubbles: true
                }));
            }
        });
        
        return cell;
    }

    function renderCell(row, col, figureId, isUser) {
        const key = getKey(row, col);
        let cell = state.visibleCells.get(key);
        
        if (!cell) {
            cell = getCellFromPool();
            state.visibleCells.set(key, cell);
            state.gridElement.appendChild(cell);
        }
        
        const cw = state.cellWidth + CONFIG.cellGap;
        const ch = state.cellHeight + CONFIG.cellGap;
        
        cell.style.cssText = `position:absolute;left:${col*cw}px;top:${row*ch}px;width:${state.cellWidth}px;height:${state.cellHeight}px`;
        cell.dataset.row = row;
        cell.dataset.col = col;
        cell.dataset.figureId = figureId;
        
        const img = cell.querySelector('img');
        // Use FigurineComposer to generate the figurine at runtime
        const currentFigureId = parseInt(img.dataset.figureId, 10);
        if (currentFigureId !== figureId) {
            img.dataset.figureId = figureId;
            FigurineComposer.setImgSrc(img, figureId, state.cellHeight);
            img.alt = `Figure ${figureId}`;
        }
        
        cell.classList.toggle('figure-cell--user', isUser);
        return cell;
    }

    function updateCells() {
        const range = getVisibleRange();
        if (!range) return;
        
        const newKeys = new Set();
        
        for (let r = range.startRow; r <= range.endRow; r++) {
            for (let c = range.startCol; c <= range.endCol; c++) {
                // Skip cells outside the grid boundaries
                if (r < 0 || r >= CONFIG.gridRows || c < 0 || c >= CONFIG.gridCols) {
                    continue;
                }
                
                const fid = getFigureAt(r, c);
                const isUser = (r === state.userGridRow && c === state.userGridCol);
                renderCell(r, c, fid, isUser);
                newKeys.add(getKey(r, c));
            }
        }
        
        // Remove old cells
        for (const [key, cell] of state.visibleCells) {
            if (!newKeys.has(key)) {
                cell.remove();
                cell.classList.remove('figure-cell--user');
                state.cellPool.push(cell);
                state.visibleCells.delete(key);
            }
        }
        
        emitScrollUpdate();
    }

    function emitScrollUpdate() {
        if (!state.scrollContainer || !state.gridElement) return;
        const cw = state.cellWidth + CONFIG.cellGap;
        const ch = state.cellHeight + CONFIG.cellGap;
        const centerCol = Math.floor((state.scrollContainer.scrollLeft + state.scrollContainer.clientWidth/2) / cw);
        const centerRow = Math.floor((state.scrollContainer.scrollTop + state.scrollContainer.clientHeight/2) / ch);
        
        // Calculate if user figure is visible and direction to it
        const userVisibility = getUserFigureVisibility();
        
        state.gridElement.dispatchEvent(new CustomEvent('scrollUpdate', {
            detail: { 
                centerRow, 
                centerCol, 
                totalRows: CONFIG.gridRows, 
                totalCols: CONFIG.gridCols,
                userVisible: userVisibility.visible,
                userAngle: userVisibility.angle
            },
            bubbles: true
        }));
    }
    
    function getUserFigureVisibility() {
        if (!state.scrollContainer) return { visible: true, angle: null };
        
        const cw = state.cellWidth + CONFIG.cellGap;
        const ch = state.cellHeight + CONFIG.cellGap;
        
        // User figure position in pixels
        const userX = state.userGridCol * cw + cw / 2;
        const userY = state.userGridRow * ch + ch / 2;
        
        // Current viewport
        const viewLeft = state.scrollContainer.scrollLeft;
        const viewTop = state.scrollContainer.scrollTop;
        const viewRight = viewLeft + state.scrollContainer.clientWidth;
        const viewBottom = viewTop + state.scrollContainer.clientHeight;
        
        // Check if user is in viewport (with some margin)
        const margin = Math.min(cw, ch) * 0.5;
        const inViewX = userX > viewLeft + margin && userX < viewRight - margin;
        const inViewY = userY > viewTop + margin && userY < viewBottom - margin;
        
        if (inViewX && inViewY) {
            return { visible: true, angle: null };
        }
        
        // Calculate exact angle to user figure
        const viewCenterX = viewLeft + state.scrollContainer.clientWidth / 2;
        const viewCenterY = viewTop + state.scrollContainer.clientHeight / 2;
        
        const dx = userX - viewCenterX;
        const dy = userY - viewCenterY;
        // Calculate angle in degrees (0° = right, 90° = down, -90° = up, ±180° = left)
        const angle = Math.atan2(dy, dx) * 180 / Math.PI;
        
        return { visible: false, angle: angle };
    }

    function handleScroll() {
        if (state.scrollRAF) cancelAnimationFrame(state.scrollRAF);
        state.scrollRAF = requestAnimationFrame(() => {
            clampScrollPosition();
            updateCells();
        });
    }
    
    function clampScrollPosition() {
        if (!state.scrollContainer) return;
        
        const cw = state.cellWidth + CONFIG.cellGap;
        const ch = state.cellHeight + CONFIG.cellGap;
        
        // Calculate the actual grid dimensions (single grid, no tiling)
        const gridWidth = CONFIG.gridCols * cw;
        const gridHeight = CONFIG.gridRows * ch;
        
        // Calculate max scroll positions (grid size minus viewport size)
        const maxScrollLeft = Math.max(0, gridWidth - state.scrollContainer.clientWidth);
        const maxScrollTop = Math.max(0, gridHeight - state.scrollContainer.clientHeight);
        
        let sl = state.scrollContainer.scrollLeft;
        let st = state.scrollContainer.scrollTop;
        let needsClamp = false;
        
        // Clamp to boundaries
        if (sl < 0) {
            sl = 0;
            needsClamp = true;
        } else if (sl > maxScrollLeft) {
            sl = maxScrollLeft;
            needsClamp = true;
        }
        
        if (st < 0) {
            st = 0;
            needsClamp = true;
        } else if (st > maxScrollTop) {
            st = maxScrollTop;
            needsClamp = true;
        }
        
        if (needsClamp) {
            state.scrollContainer.scrollTo({ left: sl, top: st, behavior: 'auto' });
        }
    }

    function setupDimensions() {
        if (!state.scrollContainer) return;
        const vw = state.scrollContainer.clientWidth;
        const vh = state.scrollContainer.clientHeight;
        
        // Cell takes ~50% viewport height on mobile
        state.cellHeight = Math.min(vh * 0.5, 400);
        state.cellWidth = state.cellHeight * 0.5;
        
        const cw = state.cellWidth + CONFIG.cellGap;
        const ch = state.cellHeight + CONFIG.cellGap;
        
        // Single grid (no tiling) - finite boundaries
        state.gridElement.style.width = `${CONFIG.gridCols * cw}px`;
        state.gridElement.style.height = `${CONFIG.gridRows * ch}px`;
    }

    function scrollToPosition(row, col, smooth = true) {
        if (!state.scrollContainer) return;
        const cw = state.cellWidth + CONFIG.cellGap;
        const ch = state.cellHeight + CONFIG.cellGap;
        
        // Calculate target position (center the cell in viewport)
        const x = col * cw - state.scrollContainer.clientWidth / 2 + cw / 2;
        const y = row * ch - state.scrollContainer.clientHeight / 2 + ch / 2;
        
        // Clamp to valid scroll range
        const gridWidth = CONFIG.gridCols * cw;
        const gridHeight = CONFIG.gridRows * ch;
        const maxScrollLeft = Math.max(0, gridWidth - state.scrollContainer.clientWidth);
        const maxScrollTop = Math.max(0, gridHeight - state.scrollContainer.clientHeight);
        
        const clampedX = Math.max(0, Math.min(x, maxScrollLeft));
        const clampedY = Math.max(0, Math.min(y, maxScrollTop));
        
        state.scrollContainer.scrollTo({ left: clampedX, top: clampedY, behavior: smooth ? 'smooth' : 'auto' });
    }

    function scrollToUserFigure() {
        scrollToPosition(state.userGridRow, state.userGridCol);
    }

    function init(userFigureId) {
        if (state.isInitialized) return Promise.resolve();
        
        state.userFigureId = userFigureId || 1;
        state.scrollContainer = document.getElementById('grid-container');
        
        if (!state.scrollContainer) {
            throw new Error('Grid container not found');
        }
        
        // Create grid element
        state.gridElement = document.createElement('div');
        state.gridElement.className = 'figure-grid';
        state.gridElement.style.position = 'relative';
        state.scrollContainer.appendChild(state.gridElement);
        
        generateMapping(Date.now());
        setupDimensions();
        
        state.scrollContainer.addEventListener('scroll', handleScroll, { passive: true });
        window.addEventListener('resize', () => { setupDimensions(); updateCells(); });
        
        // Preload shapes before rendering
        return FigurineComposer.preloadShapes().then(() => {
            // Initial render and scroll to user
            updateCells();
            setTimeout(() => scrollToPosition(state.userGridRow, state.userGridCol, false), 50);
            
            state.isInitialized = true;
            console.log(`GridManager: User figure ${state.userFigureId} at (${state.userGridRow}, ${state.userGridCol})`);
        });
    }

    return {
        init,
        scrollToUserFigure,
        scrollToPosition,
        get userPosition() { return { row: state.userGridRow, col: state.userGridCol }; },
        get config() { return CONFIG; }
    };
})();
