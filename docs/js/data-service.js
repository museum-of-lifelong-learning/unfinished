/**
 * Data Service for Figurine Gallery
 * Handles all data fetching from Google Sheets via API
 */

const DataService = (function() {
    // Configuration
    const CONFIG = {
        TOTAL_FIGURES: 27000,
        // Google Sheets API configuration
        // TODO: Replace YOUR_API_KEY_HERE with your restricted API key
        // Will be moved to Supabase later
        API_KEY: 'AIzaSyDhyLNCEn_mA5RCTYfDGNOSzPAlpY_1bIo',
        DEFAULT_SHEET_ID: '16Ww-LsbFi6SqtoJglpMt0UxJ1uaPNXRcYCo1aTuIYLE',
        SHEET_RANGE: 'A:H' // Columns: data_id, figure_id, title, Paragraph1, Paragraph2, Resource_ToolsInspiration, Resource_Anlaufstellen, Resource_Programm
    };

    // Default/placeholder values for missing data
    const DEFAULT_FIGURE_DATA = {
        data_id: null,
        figure_id: null,
        title: 'Unknown Figure',
        Paragraph1: 'No description available for this figure.',
        Paragraph2: '',
        Resource_ToolsInspiration: '',
        Resource_Anlaufstellen: '',
        Resource_Programm: ''
    };

    /**
     * Set the API key for Google Sheets API
     * @param {string} key - The API key
     */
    function setApiKey(key) {
        CONFIG.API_KEY = key;
    }

    /**
     * Get the figure_id from URL parameter
     * @returns {number|null} - Figure ID or null
     */
    function getFigureIdFromUrl() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const figureId = urlParams.get('figure_id');
            if (figureId) {
                const parsed = parseInt(figureId, 10);
                if (!isNaN(parsed) && parsed >= 1 && parsed <= CONFIG.TOTAL_FIGURES) {
                    return parsed;
                }
            }
            return null;
        } catch (error) {
            console.error('Error getting figure_id from URL:', error);
            return null;
        }
    }

    /**
     * Get the data_id from URL parameter
     * @returns {string|null} - Data ID (UUID) or null
     */
    function getDataIdFromUrl() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            const dataId = urlParams.get('data_id');
            return dataId ? dataId.trim() : null;
        } catch (error) {
            console.error('Error getting data_id from URL:', error);
            return null;
        }
    }

    /**
     * Get the sheet ID from URL parameter (optional override)
     * @returns {string} - Sheet ID (default if not provided)
     */
    function getSheetIdFromUrl() {
        try {
            const urlParams = new URLSearchParams(window.location.search);
            return urlParams.get('sheet') || urlParams.get('sheetId') || CONFIG.DEFAULT_SHEET_ID;
        } catch (error) {
            console.error('Error getting sheet ID from URL:', error);
            return CONFIG.DEFAULT_SHEET_ID;
        }
    }

    /**
     * Build Google Sheets API URL
     * @param {string} sheetId - The Google Sheet ID
     * @param {string} apiKey - The API key
     * @returns {string} - The API URL
     */
    function buildApiUrl(sheetId, apiKey) {
        const range = encodeURIComponent(CONFIG.SHEET_RANGE);
        return 'https://sheets.googleapis.com/v4/spreadsheets/' + sheetId + '/values/' + range + '?key=' + apiKey;
    }

    /**
     * Fetch data from Google Sheets API
     * @param {string} sheetId - The Google Sheet ID (optional, uses URL param or default)
     * @returns {Promise<Array>} - Array of row objects
     */
    async function fetchSheetData(sheetId) {
        const apiKey = CONFIG.API_KEY;
        const finalSheetId = sheetId || getSheetIdFromUrl();

        if (!apiKey || apiKey === 'YOUR_API_KEY_HERE') {
            throw new Error('Google Sheets API key is not configured. Please add your API key to data-service.js');
        }

        const url = buildApiUrl(finalSheetId, apiKey);
        console.log('Fetching from Google Sheets API...');

        try {
            const response = await fetch(url);
            
            if (!response.ok) {
                const errorData = await response.json().catch(function() { return {}; });
                const errorMsg = errorData.error ? errorData.error.message : response.statusText;
                throw new Error('API Error ' + response.status + ': ' + errorMsg);
            }

            const data = await response.json();
            
            if (!data.values || data.values.length < 2) {
                console.warn('No data found in sheet');
                return [];
            }

            // First row is headers
            const headers = data.values[0].map(function(h) { return h.trim(); });
            const rows = data.values.slice(1);

            // Convert to array of objects
            const result = rows.map(function(row) {
                const obj = {};
                headers.forEach(function(header, index) {
                    obj[header] = row[index] || '';
                });
                return obj;
            }).filter(function(row) { 
                return Object.values(row).some(function(v) { return v; }); 
            });

            console.log('Fetched ' + result.length + ' rows from Google Sheets');
            return result;

        } catch (error) {
            console.error('Failed to fetch sheet data:', error);
            throw error;
        }
    }

    /**
     * Find a row by exact data_id match
     * @param {Array} data - Array of row objects
     * @param {string} dataId - data_id (UUID) to search for
     * @returns {Object|null} - Matching row or null
     */
    function lookupByDataId(data, dataId) {
        if (!dataId || !data || !Array.isArray(data)) {
            console.warn('lookupByDataId: Invalid parameters', { dataId: dataId, dataIsArray: Array.isArray(data) });
            return null;
        }

        const normalizedDataId = dataId.trim().toLowerCase();
        console.log('Searching for data_id:', normalizedDataId, 'in', data.length, 'rows');
        
        const found = data.find(function(row) {
            const rowDataId = row.data_id || row.dataId || row.DataId;
            return rowDataId && rowDataId.trim().toLowerCase() === normalizedDataId;
        });
        
        if (found) {
            console.log('data_id match found:', found);
        } else {
            console.warn('No data_id match found for:', normalizedDataId);
        }
        
        return found || null;
    }

    /**
     * Find a row by figure_id
     * @param {Array} data - Array of row objects
     * @param {number} figureId - Figure ID (1-27000)
     * @returns {Object|null} - Matching row or null
     */
    function lookupByFigureId(data, figureId) {
        if (!figureId || !data || !Array.isArray(data)) {
            console.warn('lookupByFigureId: Invalid parameters', { figureId: figureId, dataIsArray: Array.isArray(data) });
            return null;
        }

        const targetId = parseInt(figureId, 10);
        
        if (isNaN(targetId) || targetId < 1 || targetId > CONFIG.TOTAL_FIGURES) {
            console.warn('lookupByFigureId: Invalid figure ID', targetId);
            return null;
        }

        console.log('Searching for figure_id', targetId, 'in', data.length, 'rows');
        const found = data.find(function(row) {
            const rowFigureId = parseInt(row.figure_id || row.figureId || row.FigureId, 10);
            return rowFigureId === targetId;
        });
        
        if (found) {
            console.log('Found matching row:', found);
        } else {
            console.warn('No matching row found for figure_id', targetId);
        }
        
        return found || null;
    }

    /**
     * Normalize row data to consistent format with defaults
     * @param {Object} row - Raw row data
     * @returns {Object} - Normalized figure data
     */
    function normalizeRowData(row) {
        // Parse title into two words if it contains a space
        const title = row.title || row.Title || '';
        const titleParts = title.split(' ');
        const word1 = titleParts[0] || 'Unknown';
        const word2 = titleParts.slice(1).join(' ') || 'Figure';
        
        return {
            data_id: row.data_id || row.dataId || null,
            figure_id: parseInt(row.figure_id || row.figureId || 0, 10),
            title: title,
            Word1: word1,
            Word2: word2,
            Paragraph1: row.Paragraph1 || row.paragraph1 || DEFAULT_FIGURE_DATA.Paragraph1,
            Paragraph2: row.Paragraph2 || row.paragraph2 || DEFAULT_FIGURE_DATA.Paragraph2,
            Resource_ToolsInspiration: row.Resource_ToolsInspiration || row.resource_toolsinspiration || '',
            Resource_Anlaufstellen: row.Resource_Anlaufstellen || row.resource_anlaufstellen || '',
            Resource_Programm: row.Resource_Programm || row.resource_programm || ''
        };
    }

    /**
     * Main function: Get figure data by data_id
     * Always fetches fresh data from API (no caching)
     * @param {string} dataId - data_id (UUID) to look up
     * @returns {Promise<Object|null>} - Figure data or null
     */
    async function getFigureData(dataId) {
        if (!dataId) {
            console.warn('No data_id provided');
            return null;
        }

        try {
            // Always fetch fresh data
            const data = await fetchSheetData();

            // Look up by data_id
            const row = lookupByDataId(data, dataId);

            // If no match, return default
            if (!row) {
                console.warn('No data found for data_id:', dataId);
                return Object.assign({}, DEFAULT_FIGURE_DATA, { data_id: dataId });
            }

            return normalizeRowData(row);

        } catch (error) {
            console.error('Error getting figure data:', error);
            return Object.assign({}, DEFAULT_FIGURE_DATA, { 
                data_id: dataId,
                Paragraph1: 'Unable to load figure data. Please try again later.'
            });
        }
    }

    // Public API
    return {
        // Configuration (read-only)
        CONFIG: Object.freeze(Object.assign({}, CONFIG)),
        
        // Setup
        setApiKey: setApiKey,
        
        // URL parameter getters
        getFigureIdFromUrl: getFigureIdFromUrl,
        getDataIdFromUrl: getDataIdFromUrl,
        getSheetIdFromUrl: getSheetIdFromUrl,
        
        // Core functions
        fetchSheetData: fetchSheetData,
        lookupByDataId: lookupByDataId,
        lookupByFigureId: lookupByFigureId,
        normalizeRowData: normalizeRowData,
        getFigureData: getFigureData
    };
})();
