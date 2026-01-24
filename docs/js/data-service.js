/**
 * Data Service for Figurine Gallery
 * Handles all data fetching from Supabase
 */

const DataService = (function() {
    // Configuration
    const CONFIG = {
        TOTAL_FIGURES: 27000,
        // Supabase configuration
        // The anon key is safe to expose - it only allows public read access via RLS
        SUPABASE_URL: 'https://iokujvdtoswwmhkbefwb.supabase.co',  // e.g., 'https://xxxxx.supabase.co'
        SUPABASE_ANON_KEY: 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imlva3VqdmR0b3N3d21oa2JlZndiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjkyMjgyMTYsImV4cCI6MjA4NDgwNDIxNn0.iymLJroQUUtRo30JCZbOdgb08ecCtpRWLbrO0dv06E0',  // Safe to expose with RLS
        TABLE_NAME: 'slips'
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
     * Set Supabase configuration
     * @param {string} url - Supabase project URL
     * @param {string} anonKey - Supabase anon/public key
     */
    function setSupabaseConfig(url, anonKey) {
        CONFIG.SUPABASE_URL = url;
        CONFIG.SUPABASE_ANON_KEY = anonKey;
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
     * Build Supabase REST API URL for fetching data
     * @param {string} tableName - The table name
     * @param {Object} filters - Optional filters (e.g., { data_id: 'xxx' })
     * @returns {string} - The API URL
     */
    function buildSupabaseUrl(tableName, filters) {
        let url = CONFIG.SUPABASE_URL + '/rest/v1/' + tableName + '?select=*';
        
        if (filters) {
            Object.keys(filters).forEach(function(key) {
                url += '&' + key + '=eq.' + encodeURIComponent(filters[key]);
            });
        }
        
        return url;
    }

    /**
     * Fetch data from Supabase
     * @param {Object} filters - Optional filters for the query
     * @returns {Promise<Array>} - Array of row objects
     */
    async function fetchSupabaseData(filters) {
        if (!CONFIG.SUPABASE_URL || CONFIG.SUPABASE_URL === 'YOUR_SUPABASE_URL') {
            throw new Error('Supabase URL is not configured. Please update data-service.js');
        }

        if (!CONFIG.SUPABASE_ANON_KEY || CONFIG.SUPABASE_ANON_KEY === 'YOUR_SUPABASE_ANON_KEY') {
            throw new Error('Supabase anon key is not configured. Please update data-service.js');
        }

        const url = buildSupabaseUrl(CONFIG.TABLE_NAME, filters);
        console.log('Fetching from Supabase...');

        try {
            const response = await fetch(url, {
                headers: {
                    'apikey': CONFIG.SUPABASE_ANON_KEY,
                    'Authorization': 'Bearer ' + CONFIG.SUPABASE_ANON_KEY,
                    'Content-Type': 'application/json'
                }
            });
            
            if (!response.ok) {
                const errorData = await response.json().catch(function() { return {}; });
                const errorMsg = errorData.message || errorData.error || response.statusText;
                throw new Error('API Error ' + response.status + ': ' + errorMsg);
            }

            const data = await response.json();
            console.log('Fetched ' + data.length + ' rows from Supabase');
            return data;

        } catch (error) {
            console.error('Failed to fetch Supabase data:', error);
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
            const rowDataId = row.data_id;
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
            const rowFigureId = parseInt(row.figure_id, 10);
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
     * @param {Object} row - Raw row data from Supabase
     * @returns {Object} - Normalized figure data
     */
    function normalizeRowData(row) {
        // Parse title into two words if it contains a space
        const title = row.title || '';
        const titleParts = title.split(' ');
        const word1 = titleParts[0] || 'Unknown';
        const word2 = titleParts.slice(1).join(' ') || 'Figure';
        
        return {
            data_id: row.data_id || null,
            figure_id: parseInt(row.figure_id || 0, 10),
            title: title,
            Word1: word1,
            Word2: word2,
            Paragraph1: row.paragraph1 || DEFAULT_FIGURE_DATA.Paragraph1,
            Paragraph2: row.paragraph2 || DEFAULT_FIGURE_DATA.Paragraph2,
            Resource_ToolsInspiration: row.resource_tools_inspiration || '',
            Resource_Anlaufstellen: row.resource_anlaufstellen || '',
            Resource_Programm: row.resource_programm || ''
        };
    }

    /**
     * Main function: Get figure data by data_id
     * Fetches data directly from Supabase with filter
     * @param {string} dataId - data_id (UUID) to look up
     * @returns {Promise<Object|null>} - Figure data or null
     */
    async function getFigureData(dataId) {
        if (!dataId) {
            console.warn('No data_id provided');
            return null;
        }

        try {
            // Fetch directly with data_id filter for efficiency
            const data = await fetchSupabaseData({ data_id: dataId });

            // If no match, return default
            if (!data || data.length === 0) {
                console.warn('No data found for data_id:', dataId);
                return Object.assign({}, DEFAULT_FIGURE_DATA, { data_id: dataId });
            }

            return normalizeRowData(data[0]);

        } catch (error) {
            console.error('Error getting figure data:', error);
            return Object.assign({}, DEFAULT_FIGURE_DATA, { 
                data_id: dataId,
                Paragraph1: 'Unable to load figure data. Please try again later.'
            });
        }
    }

    /**
     * Get figure data by figure_id
     * @param {number} figureId - Figure ID (1-27000)
     * @returns {Promise<Object|null>} - Figure data or null
     */
    async function getFigureDataByFigureId(figureId) {
        if (!figureId) {
            console.warn('No figure_id provided');
            return null;
        }

        try {
            const data = await fetchSupabaseData({ figure_id: figureId });

            if (!data || data.length === 0) {
                console.warn('No data found for figure_id:', figureId);
                return Object.assign({}, DEFAULT_FIGURE_DATA, { figure_id: figureId });
            }

            return normalizeRowData(data[0]);

        } catch (error) {
            console.error('Error getting figure data:', error);
            return Object.assign({}, DEFAULT_FIGURE_DATA, { 
                figure_id: figureId,
                Paragraph1: 'Unable to load figure data. Please try again later.'
            });
        }
    }

    // Public API
    return {
        // Configuration (read-only)
        CONFIG: Object.freeze(Object.assign({}, CONFIG)),
        
        // Setup
        setSupabaseConfig: setSupabaseConfig,
        
        // URL parameter getters
        getFigureIdFromUrl: getFigureIdFromUrl,
        getDataIdFromUrl: getDataIdFromUrl,
        
        // Core functions
        fetchSupabaseData: fetchSupabaseData,
        lookupByDataId: lookupByDataId,
        lookupByFigureId: lookupByFigureId,
        normalizeRowData: normalizeRowData,
        getFigureData: getFigureData,
        getFigureDataByFigureId: getFigureDataByFigureId
    };
})();
