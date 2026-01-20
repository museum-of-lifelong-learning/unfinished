/**
 * Data Service for Figurine Gallery
 * Handles all data fetching and caching from Google Sheets
 */

const DataService = (function() {
    // Configuration
    const CONFIG = {
        SHEET_URL: 'https://docs.google.com/spreadsheets/d/16Ww-LsbFi6SqtoJglpMt0UxJ1uaPNXRcYCo1aTuIYLE/export?format=csv&gid=0',
        TOTAL_FIGURES: 27000,
        CACHE_EXPIRY_MS: 60 * 1000, // 1 minute in milliseconds
        STORAGE_KEY: 'figurine_gallery_data'
    };

    // Default/placeholder values for missing data
    const DEFAULT_FIGURE_DATA = {
        UUID: null,
        FigureID: null,
        Word1: 'Unknown',
        Word2: 'Figure',
        Paragraph1: 'No description available for this figure.',
        Paragraph2: '',
        Resource_ToolsInspiration: '',
        Resource_Anlaufstellen: '',
        Resource_Programm: '',
        Footer: ''
    };

    /**
     * Extract figure ID (1-27000) from the last 5 digits of a UUID
     * @param {string} uuid - The full UUID string
     * @returns {number|null} - Figure ID or null if invalid
     */
    function extractFigureIdFromUUID(uuid) {
        if (!uuid || typeof uuid !== 'string') {
            return null;
        }

        // Remove any non-alphanumeric characters and get last 5 characters
        const cleaned = uuid.replace(/[^a-zA-Z0-9]/g, '');
        
        if (cleaned.length < 5) {
            return null;
        }

        const lastFive = cleaned.slice(-5);
        
        // Convert to number (treating as base-36 or decimal depending on content)
        let figureId;
        
        // If it's all digits, parse as decimal
        if (/^\d+$/.test(lastFive)) {
            figureId = parseInt(lastFive, 10);
        } else {
            // Otherwise, use a hash-like approach to get a number
            let hash = 0;
            for (let i = 0; i < lastFive.length; i++) {
                const char = lastFive.charCodeAt(i);
                hash = ((hash << 5) - hash) + char;
                hash = hash & hash; // Convert to 32-bit integer
            }
            figureId = Math.abs(hash);
        }

        // Ensure it's within range 1-27000
        figureId = ((figureId - 1) % CONFIG.TOTAL_FIGURES) + 1;
        
        return figureId;
    }

    /**
     * Parse the `?id=` parameter from the current URL
     * @returns {string|null} - UUID from URL or null if not present
     */
    function getUUIDFromUrl() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const id = urlParams.get('id');
            return id ? id.trim() : null;
        } catch (error) {
            console.error('Error parsing URL parameters:', error);
            return null;
        }
    }

    /**
     * Fetch and parse CSV data from Google Sheets using Papa Parse
     * @returns {Promise<Array>} - Array of row objects
     */
    async function fetchSheetData() {
        return new Promise((resolve, reject) => {
            // Check if Papa Parse is available
            if (typeof Papa === 'undefined') {
                reject(new Error('Papa Parse library is not loaded'));
                return;
            }

            Papa.parse(CONFIG.SHEET_URL, {
                download: true,
                header: true,
                skipEmptyLines: true,
                transformHeader: (header) => header.trim(),
                complete: (results) => {
                    if (results.errors && results.errors.length > 0) {
                        console.warn('CSV parsing warnings:', results.errors);
                    }
                    resolve(results.data);
                },
                error: (error) => {
                    console.error('Failed to fetch sheet data:', error);
                    reject(new Error(`Failed to fetch data from Google Sheets: ${error.message}`));
                }
            });
        });
    }

    /**
     * Get cached data from localStorage if not expired
     * @returns {Object|null} - Cached data object or null if expired/missing
     */
    function getCachedData() {
        try {
            const cached = localStorage.getItem(CONFIG.STORAGE_KEY);
            
            if (!cached) {
                return null;
            }

            const parsed = JSON.parse(cached);
            const now = Date.now();

            // Check if cache has expired
            if (parsed.timestamp && (now - parsed.timestamp) < CONFIG.CACHE_EXPIRY_MS) {
                return parsed.data;
            }

            // Cache expired, remove it
            localStorage.removeItem(CONFIG.STORAGE_KEY);
            return null;
        } catch (error) {
            console.error('Error reading cached data:', error);
            // Clear potentially corrupted cache
            localStorage.removeItem(CONFIG.STORAGE_KEY);
            return null;
        }
    }

    /**
     * Save data to localStorage with timestamp
     * @param {Array} data - Data to cache
     */
    function setCachedData(data) {
        try {
            const cacheObject = {
                timestamp: Date.now(),
                data: data
            };
            localStorage.setItem(CONFIG.STORAGE_KEY, JSON.stringify(cacheObject));
        } catch (error) {
            console.error('Error caching data:', error);
            // localStorage might be full or disabled
            // Continue without caching
        }
    }

    /**
     * Find a row by exact UUID match
     * @param {Array} data - Array of row objects
     * @param {string} uuid - UUID to search for
     * @returns {Object|null} - Matching row or null
     */
    function lookupByUUID(data, uuid) {
        if (!uuid || !data || !Array.isArray(data)) {
            console.warn('lookupByUUID: Invalid parameters', { uuid, dataIsArray: Array.isArray(data) });
            return null;
        }

        const normalizedUUID = uuid.trim().toLowerCase();
        console.log('Searching for UUID:', normalizedUUID, 'in', data.length, 'rows');
        
        const found = data.find(row => {
            const rowUUID = row.UUID || row.uuid;
            return rowUUID && rowUUID.trim().toLowerCase() === normalizedUUID;
        });
        
        if (found) {
            console.log('✅ UUID match found:', found);
        } else {
            console.warn('❌ No UUID match found for:', normalizedUUID);
        }
        
        return found || null;
    }

    /**
     * Fallback lookup by figure ID
     * @param {Array} data - Array of row objects
     * @param {number} figureId - Figure ID (1-27000)
     * @returns {Object|null} - Matching row or null
     */
    function lookupByFigureID(data, figureId) {
        if (!figureId || !data || !Array.isArray(data)) {
            console.warn('lookupByFigureID: Invalid parameters', { figureId, dataIsArray: Array.isArray(data) });
            return null;
        }

        const targetId = parseInt(figureId, 10);
        
        if (isNaN(targetId) || targetId < 1 || targetId > CONFIG.TOTAL_FIGURES) {
            console.warn('lookupByFigureID: Invalid figure ID', targetId);
            return null;
        }

        console.log('Searching for figure ID', targetId, 'in', data.length, 'rows');
        const found = data.find(row => {
            const rowFigureId = parseInt(row.FigureID || row.figureId || row.figureid, 10);
            return rowFigureId === targetId;
        });
        
        if (found) {
            console.log('Found matching row:', found);
        } else {
            console.warn('No matching row found for figure ID', targetId);
        }
        
        return found || null;
    }

    /**
     * Normalize row data to consistent format with defaults
     * @param {Object} row - Raw row data
     * @param {string} uuid - Original UUID used for lookup
     * @returns {Object} - Normalized figure data
     */
    function normalizeRowData(row, uuid) {
        return {
            UUID: row.UUID || row.uuid || uuid,
            FigureID: parseInt(row.FigureID || row.figureId || row.figureid, 10) || extractFigureIdFromUUID(uuid),
            Word1: row.Word1 || row.word1 || DEFAULT_FIGURE_DATA.Word1,
            Word2: row.Word2 || row.word2 || DEFAULT_FIGURE_DATA.Word2,
            Paragraph1: row.Paragraph1 || row.paragraph1 || DEFAULT_FIGURE_DATA.Paragraph1,
            Paragraph2: row.Paragraph2 || row.paragraph2 || DEFAULT_FIGURE_DATA.Paragraph2,
            Resource_ToolsInspiration: row.Resource_ToolsInspiration || row.resource_toolsinspiration || '',
            Resource_Anlaufstellen: row.Resource_Anlaufstellen || row.resource_anlaufstellen || '',
            Resource_Programm: row.Resource_Programm || row.resource_programm || '',
            Footer: row.Footer || row.footer || ''
        };
    }

    /**
     * Main function: Get figure data by UUID
     * Tries exact UUID lookup, falls back to figure ID derived from UUID
     * @param {string} uuid - UUID to look up
     * @returns {Promise<Object|null>} - Figure data or null
     */
    async function getFigureData(uuid) {
        if (!uuid) {
            console.warn('No UUID provided');
            return null;
        }

        try {
            // Try to get cached data first
            let data = getCachedData();

            // If no cached data, fetch fresh
            if (!data) {
                data = await fetchSheetData();
                setCachedData(data);
            }

            // Try exact UUID match first
            let row = lookupByUUID(uuid, data);

            // If no exact match, try figure ID lookup
            if (!row) {
                const figureId = extractFigureIdFromUUID(uuid);
                if (figureId) {
                    row = lookupByFigureID(figureId, data);
                }
            }

            // If still no match, return default with extracted ID
            if (!row) {
                const figureId = extractFigureIdFromUUID(uuid);
                return {
                    ...DEFAULT_FIGURE_DATA,
                    UUID: uuid,
                    FigureID: figureId
                };
            }

            return normalizeRowData(row, uuid);

        } catch (error) {
            console.error('Error getting figure data:', error);
            // Return default data with what we can extract
            const figureId = extractFigureIdFromUUID(uuid);
            return {
                ...DEFAULT_FIGURE_DATA,
                UUID: uuid,
                FigureID: figureId,
                Paragraph1: 'Unable to load figure data. Please try again later.'
            };
        }
    }

    /**
     * Clear the data cache
     */
    function clearCache() {
        localStorage.removeItem(CONFIG.STORAGE_KEY);
    }

    /**
     * Get cache status information
     * @returns {Object} - Cache status info
     */
    function getCacheStatus() {
        try {
            const cached = localStorage.getItem(CONFIG.STORAGE_KEY);
            if (!cached) {
                return { cached: false, timestamp: null, age: null, expired: true };
            }

            const parsed = JSON.parse(cached);
            const now = Date.now();
            const age = now - parsed.timestamp;
            const expired = age >= CONFIG.CACHE_EXPIRY_MS;

            return {
                cached: true,
                timestamp: new Date(parsed.timestamp).toISOString(),
                age: Math.round(age / 1000 / 60), // age in minutes
                expired: expired,
                recordCount: parsed.data ? parsed.data.length : 0
            };
        } catch (error) {
            return { cached: false, timestamp: null, age: null, expired: true, error: error.message };
        }
    }

    // Public API
    return {
        // Configuration (read-only)
        CONFIG: Object.freeze({ ...CONFIG }),
        
        // Core functions
        extractFigureIdFromUUID,
        getUUIDFromUrl,
        fetchSheetData,
        getCachedData,
        setCachedData,
        lookupByUUID,
        lookupByFigureID,
        getFigureData,
        
        // Utility functions
        clearCache,
        getCacheStatus
    };
})();
