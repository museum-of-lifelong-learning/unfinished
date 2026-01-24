/**
 * Figurine Gallery App - Main Entry Point
 */
(function() {
    'use strict';

    // Get figure_id from URL parameter (uses DataService)
    function getFigureIdFromUrl() {
        if (typeof DataService !== 'undefined') {
            const figureId = DataService.getFigureIdFromUrl();
            if (figureId) return figureId;
        }
        // Fallback: random figure if no valid figure_id provided
        return Math.floor(Math.random() * 27000) + 1;
    }
    
    // Get data_id from URL parameter (uses DataService)
    function getDataIdFromUrl() {
        if (typeof DataService !== 'undefined') {
            return DataService.getDataIdFromUrl();
        }
        return null;
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
    
    // Direction arrow controller
    const DirectionArrowController = {
        arrow: null,
        icon: null,
        
        init() {
            this.arrow = document.getElementById('direction-arrow');
            this.icon = this.arrow?.querySelector('.direction-arrow__icon');
            
            if (!this.arrow) {
                console.warn('Direction arrow element not found');
                return;
            }
            
            // Click to navigate to user figure
            this.arrow.addEventListener('click', () => {
                GridManager.scrollToUserFigure();
            });
            
            console.log('Direction arrow initialized');
        },
        
        update(userVisible, angle) {
            if (!this.arrow) return;
            
            if (userVisible || angle === null) {
                // Hide the arrow
                this.arrow.classList.remove('direction-arrow--visible');
            } else {
                // Show arrow and rotate it to point in exact direction
                // The arrow icon (↑) points up by default, which is -90° in our coordinate system
                // So we need to rotate by (angle + 90) to point in the correct direction
                const rotation = angle + 90;
                
                // Apply rotation transform
                this.arrow.style.transform = `rotate(${rotation}deg)`;
                this.arrow.classList.add('direction-arrow--visible');
                
                // Always use up arrow icon since we're rotating the whole element
                if (this.icon) {
                    this.icon.textContent = '↑';
                }
            }
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
            
            // Initialize direction arrow
            DirectionArrowController.init();

            // Listen for figure clicks (bubbles up from grid)
            gridContainer.addEventListener('figureClick', async (e) => {
                const { figureId, isUserFigure } = e.detail;
                console.log('=== Figure Click Event ===');
                console.log('Figure ID:', figureId, 'Is User Figure:', isUserFigure);
                
                // Get data_id from URL
                const dataId = getDataIdFromUrl();
                console.log('data_id from URL:', dataId);
                
                // Show slip view with figure data
                if (typeof SlipView !== 'undefined' && SlipView.show) {
                    // Try to load data from Google Sheets if DataService is available
                    if (typeof DataService !== 'undefined' && dataId) {
                        try {
                            console.log('=== Loading Data from Google Sheets API ===');
                            
                            // Always fetch fresh data from API
                            console.log('⬇️ Fetching from Google Sheets API...');
                            const data = await DataService.fetchSheetData();
                            console.log('✅ Fetched', data.length, 'rows from Google Sheets');
                            if (data.length > 0) {
                                console.log('Sample row:', data[0]);
                            }
                            
                            // Look up figure by data_id
                            console.log('🔍 Looking up by data_id:', dataId);
                            let figureData = DataService.lookupByDataId(data, dataId);
                            
                            if (figureData) {
                                figureData = DataService.normalizeRowData(figureData);
                                console.log('✅ Found data:', figureData);
                                SlipView.show(figureData);
                            } else {
                                console.warn('❌ No data found for data_id - showing placeholder');
                                SlipView.show({ figure_id: figureId, isUserFigure });
                            }
                        } catch (error) {
                            console.error('❌ Error loading figure data:', error);
                            console.error('Stack:', error.stack);
                            // Fallback to placeholder on error
                            SlipView.show({ figure_id: figureId, isUserFigure });
                        }
                    } else {
                        console.warn('❌ DataService not available or no data_id, showing placeholder');
                        // DataService not available or no data_id, show placeholder
                        SlipView.show({ figure_id: figureId, isUserFigure });
                    }
                }
            });

            // Listen for scroll updates (for minimap and direction arrow)
            gridContainer.addEventListener('scrollUpdate', (e) => {
                MinimapController.update(e.detail);
                DirectionArrowController.update(e.detail.userVisible, e.detail.userAngle);
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
