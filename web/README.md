# Figurine Gallery - Web Application

Interactive web gallery displaying 27,000 unique figurine characters from "Unfinished by Design - The Museum of Lifelong Learning".

## Local Development

### Quick Start

```bash
# Navigate to docs directory
cd /home/jp/repositories/figurine/docs

# Start local server
python3 -m http.server 8000

# Open in browser
# http://localhost:8000/?id=550e8400-e29b-41d4-a716-446655412345
```

### Test URLs

- **Default Test**: `http://localhost:8000/?id=550e8400-e29b-41d4-a716-446655412345` (Figure 12345)
- **Random Figure**: `http://localhost:8000/` (Generates random on localhost)
- **Specific Figure**: `http://localhost:8000/?id=550e8400-e29b-41d4-a716-446655400042` (Figure 42)

### Generate SVG Assets

Before testing, generate the figure SVGs:

```bash
# Generate all 27,000 figures (takes ~1-2 minutes)
cd /home/jp/repositories/figurine
python3 generate_web_svgs.py --workers 8

# Generate just a sample (for quick testing)
python3 generate_web_svgs.py --start 1 --end 100

# Generate a specific figure
python3 generate_web_svgs.py --single 12345
```

## File Structure

```
/docs
├── index.html              # Main HTML page
├── README.md               # This file
├── css/
│   └── styles.css          # All styles
├── js/
│   ├── data-service.js     # Google Sheets data fetching
│   ├── grid-manager.js     # Infinite scroll grid
│   ├── slip-view.js        # Detail overlay
│   ├── minimap.js          # Navigation minimap
│   └── app.js              # Main application
└── assets/
    └── figures/
        ├── figure-00001.svg
        ├── figure-00002.svg
        └── ... (27,000 SVG files)
```

## Configuration

### Google Sheets

The app fetches data from a published Google Sheet:
- **Sheet URL**: https://docs.google.com/spreadsheets/d/16Ww-LsbFi6SqtoJglpMt0UxJ1uaPNXRcYCo1aTuIYLE/edit
- **CSV Export**: Configured in `js/data-service.js`

To publish the sheet:
1. Open Google Sheet
2. File → Share → Publish to web
3. Select CSV format
4. Enable "Automatically republish when changes are made"
5. Use the generated URL in `data-service.js`

### Expected Sheet Columns

| Column | Description |
|--------|-------------|
| UUID | Full UUID from QR code |
| FigureID | Number 1-27000 |
| Word1 | First title word |
| Word2 | Second title word |
| Paragraph1 | First paragraph of text |
| Paragraph2 | Second paragraph of text |
| Resource_ToolsInspiration | Tools & Inspiration content |
| Resource_Anlaufstellen | Anlaufstellen & Angebote content |
| Resource_Programm | Programm-Empfehlung content |

## Features

- **Infinite Scrolling Grid**: Navigate through 27,000 figures
- **Edge Wrapping**: Seamless infinite scroll (Pac-Man effect)
- **Random Arrangement**: Each session shuffles figure positions
- **Virtual Scrolling**: Only renders visible cells for performance
- **Minimap Navigation**: Always see your position, click to return home
- **Slip Overlay**: Detailed view for your figure with personalized content
- **Mobile-First**: Optimized for touch devices
- **Accessibility**: Keyboard navigation, ARIA labels, screen reader support

## Keyboard Shortcuts

- **Arrow Keys**: Scroll the grid
- **Enter**: Open detail view for your figure
- **Escape**: Close detail view
- **Home**: Return to your figure

## Browser Support

- Chrome/Edge (last 2 versions)
- Firefox (last 2 versions)
- Safari (last 2 versions)
- Mobile Safari (iOS 14+)
- Chrome Mobile (Android 10+)

## Deployment (GitHub Pages)

1. Push changes to repository
2. Go to Settings → Pages
3. Set source: Deploy from branch `main`, folder `/docs`
4. Wait for deployment
5. Access at: `https://[username].github.io/[repo]/`

### Custom Domain (figurati.ch)

1. In GitHub Pages settings, add custom domain
2. Configure DNS:
   - CNAME: `www.figurati.ch` → `[username].github.io`
   - A records for apex domain to GitHub's IPs
3. Enable HTTPS

## Troubleshooting

### SVGs not loading
- Check if files exist in `assets/figures/`
- Verify file naming: `figure-00001.svg` (5-digit zero-padded)
- Check browser console for 404 errors

### Data not loading
- Verify Google Sheet is published
- Check browser console for CORS errors
- Try clearing localStorage: `DataService.clearCache()`

### Grid not scrolling
- Check browser console for JavaScript errors
- Verify all JS files loaded in correct order
- Check if figure elements are being created
