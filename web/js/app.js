/**
 * Figurine Gallery App - Main Entry Point
 */
(function() {
    'use strict';

    // Extract figure ID from URL (last 5 digits of UUID)
    function getFigureIdFromUrl() {
        const params = new URLSearchParams(window.location.search);
        const uuid = params.get('id');
        if (uuid && uuid.length >= 5) {
            const last5 = uuid.slice(-5);
            const figureId = parseInt(last5, 10);
            if (figureId >= 1 && figureId <= 27000) {
                return figureId;
            }
        }
        return Math.floor(Math.random() * 27000) + 1;
    }
    
    // Get full UUID from URL
    function getUuidFromUrl() {
        const params = new URLSearchParams(window.location.search);
        return params.get('id') || null;
    }

    // Simple minimap controller
    const MinimapController = {
        container: null,
        grid: null,
        viewport: null,
        position: null,
        homeBtn: null,
        totalRows: 164,
        totalCols: 165,
        userRow: 82,
        userCol: 82,

        init(userRow, userCol) {
            this.container = document.getElementById('minimap-container');
            this.grid = document.querySelector('.minimap-grid');
            this.viewport = document.getElementById('minimap-viewport');
            this.position = document.getElementById('minimap-position');
            this.homeBtn = document.getElementById('minimap-home-btn');

            if (!this.container || !this.grid) {
                console.warn('Minimap elements not found');
                return;
            }

            this.userRow = userRow;
            this.userCol = userCol;

            // Show and position user indicator
            this.updateUserPosition(userRow, userCol);

            // Home button click
            if (this.homeBtn) {
                this.homeBtn.addEventListener('click', (e) => {
                    e.stopPropagation();
                    GridManager.scrollToUserFigure();
                });
            }

            // Click on minimap to navigate
            this.grid.addEventListener('click', (e) => {
                const rect = this.grid.getBoundingClientRect();
                const x = e.clientX - rect.left;
                const y = e.clientY - rect.top;
                const col = Math.floor((x / rect.width) * this.totalCols);
                const row = Math.floor((y / rect.height) * this.totalRows);
                GridManager.scrollToPosition(row, col);
            });

            console.log('Minimap initialized');
        },

        updateUserPosition(row, col) {
            if (!this.position || !this.grid) return;
            const rect = this.grid.getBoundingClientRect();
            const x = (col / this.totalCols) * rect.width;
            const y = (row / this.totalRows) * rect.height;
            this.position.style.left = `${x}px`;
            this.position.style.top = `${y}px`;
            this.position.style.display = 'block';
        },

        update(detail) {
            if (!this.viewport || !this.grid) return;
            const { centerRow, centerCol, totalRows, totalCols } = detail;
            this.totalRows = totalRows || this.totalRows;
            this.totalCols = totalCols || this.totalCols;

            const rect = this.grid.getBoundingClientRect();
            // Estimate visible cells (approx 3x5 on mobile)
            const visibleCols = 5;
            const visibleRows = 3;

            const vpWidth = (visibleCols / this.totalCols) * rect.width;
            const vpHeight = (visibleRows / this.totalRows) * rect.height;
            const vpX = ((centerCol - visibleCols/2) / this.totalCols) * rect.width;
            const vpY = ((centerRow - visibleRows/2) / this.totalRows) * rect.height;

            this.viewport.style.left = `${Math.max(0, vpX)}px`;
            this.viewport.style.top = `${Math.max(0, vpY)}px`;
            this.viewport.style.width = `${vpWidth}px`;
            this.viewport.style.height = `${vpHeight}px`;
            this.viewport.style.display = 'block';
        }
    };

    // Initialize the app
    async function init() {
        const loadingEl = document.getElementById('loading-indicator');
        const errorEl = document.getElementById('error-state');
        const gridContainer = document.getElementById('grid-container');

        try {
            // Get user figure
            const userFigureId = getFigureIdFromUrl();
            console.log('App: Initializing with figure', userFigureId);

            // Initialize grid manager
            GridManager.init(userFigureId);

            // Get user position from grid manager
            const userPos = GridManager.userPosition;
            
            // Initialize minimap
            MinimapController.init(userPos.row, userPos.col);

            // Listen for figure clicks (bubbles up from grid)
            gridContainer.addEventListener('figureClick', async (e) => {
                const { figureId, isUserFigure } = e.detail;
                console.log('=== Figure Click Event ===');
                console.log('Figure ID:', figureId, 'Is User Figure:', isUserFigure);
                
                // Get UUID from URL
                const uuid = getUuidFromUrl();
                console.log('UUID from URL:', uuid);
                
                // Show slip view with figure data
                if (typeof SlipView !== 'undefined' && SlipView.show) {
                    // Try to load data from Google Sheets if DataService is available
                    if (typeof DataService !== 'undefined') {
                        try {
                            console.log('=== Loading Data from Google Sheets ===');
                            
                            // Fetch data from cache or Google Sheets
                            let data = DataService.getCachedData();
                            if (!data) {
                                console.log('❌ No cache found');
                                console.log('⬇️ Fetching from Google Sheets...');
                                console.log('URL:', DataService.CONFIG.SHEET_URL);
                                data = await DataService.fetchSheetData();
                                console.log('✅ Fetched', data.length, 'rows from Google Sheets');
                                console.log('Sample row:', data[0]);
                                DataService.setCachedData(data);
                                console.log('💾 Data cached');
                            } else {
                                console.log('✅ Using cached data:', data.length, 'rows');
                            }
                            
                            // Look up figure by UUID first, then by ID
                            let figureData = null;
                            if (uuid) {
                                console.log('🔍 Looking up by UUID:', uuid);
                                figureData = DataService.lookupByUUID(data, uuid);
                            }
                            
                            if (!figureData) {
                                console.log('🔍 UUID lookup failed, trying by Figure ID:', figureId);
                                figureData = DataService.lookupByFigureID(data, figureId);
                            }
                            
                            if (figureData) {
                                console.log('✅ Found data:', figureData);
                                SlipView.show(figureData);
                            } else {
                                console.warn('❌ No data found - showing placeholder');
                                SlipView.show({ figureId, isUserFigure });
                            }
                        } catch (error) {
                            console.error('❌ Error loading figure data:', error);
                            console.error('Stack:', error.stack);
                            // Fallback to placeholder on error
                            SlipView.show({ figureId, isUserFigure });
                        }
                    } else {
                        console.warn('❌ DataService not available, showing placeholder');
                        // DataService not available, show placeholder
                        SlipView.show({ figureId, isUserFigure });
                    }
                }
            });

            // Listen for scroll updates (for minimap)
            gridContainer.addEventListener('scrollUpdate', (e) => {
                MinimapController.update(e.detail);
            });

            // Home button (additional one if exists)
            const homeBtn = document.getElementById('home-button');
            if (homeBtn) {
                homeBtn.addEventListener('click', () => {
                    GridManager.scrollToUserFigure();
                });
            }

            // Hide loading
            if (loadingEl) loadingEl.classList.add('hidden');
            
            console.log('App: Ready');
        } catch (error) {
            console.error('App: Initialization error', error);
            if (loadingEl) loadingEl.classList.add('hidden');
            if (errorEl) {
                errorEl.classList.remove('hidden');
                const msg = errorEl.querySelector('.error-state__message');
                if (msg) msg.textContent = error.message;
            }
        }
    }

    // Start when DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
