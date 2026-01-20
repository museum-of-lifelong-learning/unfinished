/**
 * Grid Manager - Simplified version
 */
const GridManager = (function() {
    'use strict';

    const CONFIG = {
        totalFigures: 27000,
        gridCols: 165,
        gridRows: 164,
        bufferZone: 10,  // Increased for more aggressive preloading
        cellGap: 8,
        figurePath: 'assets/figures/figure-{id}.svg'
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

    function getFigurePath(id) {
        return CONFIG.figurePath.replace('{id}', String(id).padStart(5, '0'));
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
        img.loading = 'lazy';
        img.decoding = 'async';  // Non-blocking decode
        img.fetchPriority = 'low';  // Don't block other resources
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
        const src = getFigurePath(figureId);
        if (img.getAttribute('src') !== src) {
            img.src = src;
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
                // Map infinite grid position to logical grid position
                const logicalRow = ((r % CONFIG.gridRows) + CONFIG.gridRows) % CONFIG.gridRows;
                const logicalCol = ((c % CONFIG.gridCols) + CONFIG.gridCols) % CONFIG.gridCols;
                
                const fid = getFigureAt(logicalRow, logicalCol);
                const isUser = (logicalRow === state.userGridRow && logicalCol === state.userGridCol);
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
        const w = wrapPosition(centerRow, centerCol);
        
        state.gridElement.dispatchEvent(new CustomEvent('scrollUpdate', {
            detail: { centerRow: w.row, centerCol: w.col, totalRows: CONFIG.gridRows, totalCols: CONFIG.gridCols },
            bubbles: true
        }));
    }

    function handleScroll() {
        if (state.scrollRAF) cancelAnimationFrame(state.scrollRAF);
        state.scrollRAF = requestAnimationFrame(() => {
            handleScrollWrap();
            updateCells();
        });
    }
    
    function handleScrollWrap() {
        if (!state.scrollContainer) return;
        
        const cw = state.cellWidth + CONFIG.cellGap;
        const ch = state.cellHeight + CONFIG.cellGap;
        const gridWidth = CONFIG.gridCols * cw;
        const gridHeight = CONFIG.gridRows * ch;
        const maxWidth = gridWidth * 3;
        const maxHeight = gridHeight * 3;
        
        let sl = state.scrollContainer.scrollLeft;
        let st = state.scrollContainer.scrollTop;
        let needsWrap = false;
        
        // Wrap when going beyond the middle grid section boundaries
        // Left boundary: wrap from left section to right section
        if (sl < gridWidth * 0.5) {
            sl += gridWidth;
            needsWrap = true;
        }
        // Right boundary: wrap from right section to left section  
        else if (sl > gridWidth * 2.5) {
            sl -= gridWidth;
            needsWrap = true;
        }
        
        // Top boundary: wrap from top section to bottom section
        if (st < gridHeight * 0.5) {
            st += gridHeight;
            needsWrap = true;
        }
        // Bottom boundary: wrap from bottom section to top section
        else if (st > gridHeight * 2.5) {
            st -= gridHeight;
            needsWrap = true;
        }
        
        if (needsWrap) {
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
        
        // Make grid 3x larger in each dimension for seamless wrapping
        state.gridElement.style.width = `${CONFIG.gridCols * cw * 3}px`;
        state.gridElement.style.height = `${CONFIG.gridRows * ch * 3}px`;
    }

    function scrollToPosition(row, col, smooth = true) {
        if (!state.scrollContainer) return;
        const cw = state.cellWidth + CONFIG.cellGap;
        const ch = state.cellHeight + CONFIG.cellGap;
        
        // Get current scroll position in grid coordinates
        const currentCol = (state.scrollContainer.scrollLeft + state.scrollContainer.clientWidth / 2) / cw;
        const currentRow = (state.scrollContainer.scrollTop + state.scrollContainer.clientHeight / 2) / ch;
        
        // Find the closest instance of the target position in the 3x3 tiled grid
        // Target can appear at: col, col+gridCols, col+2*gridCols (and same for rows)
        let bestCol = col + CONFIG.gridCols;
        let bestRow = row + CONFIG.gridRows;
        let minDist = Infinity;
        
        for (let tileRow = 0; tileRow < 3; tileRow++) {
            for (let tileCol = 0; tileCol < 3; tileCol++) {
                const candidateCol = col + tileCol * CONFIG.gridCols;
                const candidateRow = row + tileRow * CONFIG.gridRows;
                const dist = Math.sqrt(
                    Math.pow(candidateCol - currentCol, 2) + 
                    Math.pow(candidateRow - currentRow, 2)
                );
                if (dist < minDist) {
                    minDist = dist;
                    bestCol = candidateCol;
                    bestRow = candidateRow;
                }
            }
        }
        
        const x = bestCol * cw - state.scrollContainer.clientWidth / 2 + cw / 2;
        const y = bestRow * ch - state.scrollContainer.clientHeight / 2 + ch / 2;
        state.scrollContainer.scrollTo({ left: Math.max(0,x), top: Math.max(0,y), behavior: smooth ? 'smooth' : 'auto' });
    }

    function scrollToUserFigure() {
        scrollToPosition(state.userGridRow, state.userGridCol);
    }

    function init(userFigureId) {
        if (state.isInitialized) return;
        
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
        
        // Initial render and scroll to user
        updateCells();
        setTimeout(() => scrollToPosition(state.userGridRow, state.userGridCol, false), 50);
        
        state.isInitialized = true;
        console.log(`GridManager: User figure ${state.userFigureId} at (${state.userGridRow}, ${state.userGridCol})`);
    }

    return {
        init,
        scrollToUserFigure,
        scrollToPosition,
        get userPosition() { return { row: state.userGridRow, col: state.userGridCol }; },
        get config() { return CONFIG; }
    };
})();
