/**
 * SlipView Module
 * Manages the slip overlay that shows figure details
 */

const SlipView = (function() {
    // DOM element references
    let overlay = null;
    let closeBtn = null;
    let figureImage = null;
    let word1El = null;
    let word2El = null;
    let characterNumberEl = null;
    let paragraph1El = null;
    let paragraph2El = null;
    let resourceToolsEl = null;
    let resourceAnlaufstellenEl = null;
    let resourceProgrammEl = null;

    /**
     * Initialize the slip view module
     * Sets up DOM references and event listeners
     */
    function init() {
        // Cache DOM elements
        overlay = document.getElementById('slip-overlay');
        closeBtn = document.getElementById('slip-close-btn');
        figureImage = document.getElementById('slip-figure-image');
        word1El = document.getElementById('slip-word1');
        word2El = document.getElementById('slip-word2');
        characterNumberEl = document.getElementById('slip-character-number');
        paragraph1El = document.getElementById('slip-paragraph1');
        paragraph2El = document.getElementById('slip-paragraph2');
        resourceToolsEl = document.getElementById('slip-resource-tools');
        resourceAnlaufstellenEl = document.getElementById('slip-resource-anlaufstellen');
        resourceProgrammEl = document.getElementById('slip-resource-programm');

        if (!overlay) {
            console.error('SlipView: #slip-overlay element not found');
            return;
        }

        // Set initial state
        overlay.setAttribute('aria-hidden', 'true');
        overlay.classList.remove('hidden');

        // Set up event listeners
        setupEventListeners();
        
        console.log('SlipView: Initialized');
    }

    /**
     * Set up all event listeners for the slip overlay
     */
    function setupEventListeners() {
        // Close button click
        if (closeBtn) {
            closeBtn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                hide();
            });
        }

        // Backdrop click (click on overlay but not on content)
        overlay.addEventListener('click', function(e) {
            if (e.target === overlay) {
                hide();
            }
        });

        // Escape key press
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && isOpen()) {
                hide();
            }
        });

        // Prevent scroll propagation when slip is open
        overlay.addEventListener('wheel', function(e) {
            const slipContent = overlay.querySelector('.slip-content');
            if (slipContent) {
                const isScrollable = slipContent.scrollHeight > slipContent.clientHeight;
                const isAtTop = slipContent.scrollTop === 0;
                const isAtBottom = slipContent.scrollTop + slipContent.clientHeight >= slipContent.scrollHeight;

                // Allow scrolling within the slip content
                if (isScrollable) {
                    if ((e.deltaY < 0 && isAtTop) || (e.deltaY > 0 && isAtBottom)) {
                        e.preventDefault();
                    }
                } else {
                    e.preventDefault();
                }
            }
        }, { passive: false });
    }

    /**
     * Check if the slip overlay is currently open
     * @returns {boolean}
     */
    function isOpen() {
        return overlay && overlay.getAttribute('aria-hidden') === 'false';
    }

    /**
     * Show the slip overlay with figure data
     * @param {Object} figureData - Data from Google Sheets
     */
    function show(figureData) {
        if (!overlay) {
            console.error('SlipView: Cannot show - overlay not initialized');
            return;
        }

        // Populate content - check for both old and new field names
        if (figureData && (figureData.figure_id || figureData.FigureID || figureData.figureId)) {
            populateContent(figureData);
        } else {
            console.error('SlipView: No figure data provided');
            return;
        }

        // Show the overlay
        overlay.setAttribute('aria-hidden', 'false');
        document.body.classList.add('slip-open');

        // Focus management for accessibility
        if (closeBtn) {
            closeBtn.focus();
        }
    }

    /**
     * Hide the slip overlay
     */
    function hide() {
        if (!overlay) return;

        overlay.setAttribute('aria-hidden', 'true');
        document.body.classList.remove('slip-open');
    }

    /**
     * Populate all DOM elements with figure data
     * @param {Object} data - Figure data from Google Sheets
     */
    function populateContent(data) {
        // Get figure ID from various possible field names
        const figureId = data.figure_id || data.FigureID || data.figureId;
        
        // Set figure image
        setFigureImage(figureId);

        // Set title words
        if (word1El) {
            word1El.textContent = data.Word1 || '';
        }
        if (word2El) {
            word2El.textContent = data.Word2 || '';
        }

        // Set character number
        if (characterNumberEl) {
            characterNumberEl.textContent = `${figureId}`;
        }

        // Set paragraphs
        if (paragraph1El) {
            paragraph1El.textContent = data.Paragraph1 || '';
        }
        if (paragraph2El) {
            paragraph2El.textContent = data.Paragraph2 || '';
        }

        // Set resource sections (using innerHTML to support HTML links)
        if (resourceToolsEl) {
            const toolsContent = data.Resource_ToolsInspiration || '';
            resourceToolsEl.innerHTML = toolsContent;
            ensureLinksOpenInNewWindow(resourceToolsEl);
        }
        if (resourceAnlaufstellenEl) {
            const anlaufstellenContent = data.Resource_Anlaufstellen || '';
            resourceAnlaufstellenEl.innerHTML = anlaufstellenContent;
            ensureLinksOpenInNewWindow(resourceAnlaufstellenEl);
        }
        if (resourceProgrammEl) {
            const programmContent = data.Resource_Programm || '';
            resourceProgrammEl.innerHTML = programmContent;
            ensureLinksOpenInNewWindow(resourceProgrammEl);
        }
    }

    /**
     * Set the figure SVG image source
     * @param {number|string} figureId - The figure ID
     */
    function setFigureImage(figureId) {
        if (!figureImage) return;

        const id = parseInt(figureId, 10);
        
        // Use FigurineComposer to generate the figure at runtime
        if (typeof FigurineComposer !== 'undefined' && FigurineComposer.isReady()) {
            FigurineComposer.setImgSrc(figureImage, id, 400);  // Larger size for slip view
        } else {
            // Fallback: try to load precomposed image (for backwards compatibility)
            const paddedId = String(figureId).padStart(5, '0');
            const imagePath = `assets/figures/figure-${paddedId}.svg`;
            figureImage.src = imagePath;
        }
        
        figureImage.alt = `Figure ${id}`;

        // Handle image load error
        figureImage.onerror = function() {
            console.warn(`SlipView: Failed to load image for figure ${figureId}`);
        };
    }

    /**
     * Ensure all links within an element open in a new window
     * Adds target="_blank" and rel="noopener noreferrer" for security
     * @param {HTMLElement} element - The element containing links
     */
    function ensureLinksOpenInNewWindow(element) {
        if (!element) return;
        
        const links = element.querySelectorAll('a');
        links.forEach(link => {
            link.setAttribute('target', '_blank');
            link.setAttribute('rel', 'noopener noreferrer');
        });
    }

    // Public API
    return {
        init: init,
        show: show,
        hide: hide,
        populateContent: populateContent,
        setFigureImage: setFigureImage,
        isOpen: isOpen
    };
})();

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', SlipView.init);
} else {
    SlipView.init();
}
