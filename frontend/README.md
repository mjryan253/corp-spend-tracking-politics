# Frontend - Corporate Spending Tracker

A modern, responsive web interface for the Corporate Spending Tracker built with Alpine.js and Tailwind CSS.

## Features

- **🔍 Advanced Search**: Search companies by name, ticker, or CIK
- **🎛️ Dynamic Filters**: Toggle filters for spending ranges and data availability
- **📊 Company Details**: View comprehensive spending summaries and breakdowns
- **📱 Responsive Design**: Works on desktop, tablet, and mobile devices
- **⚡ Fast Performance**: Lightweight with no build process required

## Technology Stack

- **Alpine.js**: Lightweight JavaScript framework for interactivity
- **Tailwind CSS**: Utility-first CSS framework for rapid UI development
- **Chart.js**: For data visualizations (ready for future use)
- **Vanilla JavaScript**: No build process, just include CDN links

## Quick Start

### Option 1: Python HTTP Server (Recommended)

1. **Start the backend server** (from the backend directory):
   ```bash
   cd backend
   python manage.py runserver
   ```

2. **Start the frontend server** (from the frontend directory):
   ```bash
   cd frontend
   python server.py
   ```

3. **Open your browser** and navigate to:
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api/

### Option 2: Live Server (VS Code Extension)

1. Install the "Live Server" extension in VS Code
2. Right-click on `index.html` and select "Open with Live Server"
3. The frontend will open in your browser

### Option 3: Direct File Opening

Simply open `index.html` in your browser (note: some features may not work due to CORS restrictions)

## Project Structure

```
frontend/
├── index.html          # Main application file
├── server.py           # Simple HTTP server
├── README.md           # This file
└── components/         # Future component files
```

## API Integration

The frontend connects to the Django REST API at `http://localhost:8000/api/` and includes:

- **Company Search**: `/api/companies/search/`
- **Company Details**: `/api/companies/{id}/`
- **Spending Summary**: `/api/companies/{id}/spending_summary/`
- **Top Spenders**: `/api/companies/top_spenders/`

## Search Features

### Basic Search
- Search by company name, ticker symbol, or CIK
- Real-time search with 300ms debounce
- Results update automatically as you type

### Advanced Filters
- **Spending Range**: Filter by minimum and maximum total spending
- **Data Availability**: Filter companies that have lobbying or charitable data
- **Toggle Filters**: Show/hide advanced filter options
- **Clear Filters**: Reset all filters with one click

## Company Details

Click on any company in the search results to view:

- **Basic Information**: Ticker, CIK, headquarters location
- **Spending Summary**: Total amounts for lobbying, charitable, and political spending
- **Charitable Breakdown**: Grants categorized by recipient type
- **Financial Context**: Latest revenue and net income data

## Future Enhancements

- **Dashboard**: Overview of top spenders and trends
- **Analytics**: Charts and visualizations using Chart.js
- **Export**: Download data in CSV/Excel format
- **Advanced Visualizations**: Interactive charts and graphs
- **Real-time Updates**: WebSocket integration for live data

## Browser Compatibility

- Chrome 88+
- Firefox 85+
- Safari 14+
- Edge 88+

## Development

### Adding New Features

1. **Components**: Add new Alpine.js components in the `<script>` section
2. **Styling**: Use Tailwind CSS utility classes for styling
3. **API Calls**: Use the existing fetch patterns for new endpoints

### Customization

- **Colors**: Modify Tailwind classes or add custom CSS
- **Layout**: Adjust the responsive grid system
- **Components**: Extend Alpine.js components for new functionality

## Troubleshooting

### CORS Issues
If you see CORS errors in the browser console:
1. Make sure the backend server is running on port 8000
2. Use the Python HTTP server (`python server.py`) instead of opening the file directly
3. Check that the API endpoints are accessible

### API Connection Issues
1. Verify the backend server is running: http://localhost:8000/api/
2. Check the browser's Network tab for failed requests
3. Ensure the API endpoints match the frontend expectations

### Styling Issues
1. Check that Tailwind CSS is loading properly
2. Verify Alpine.js is working by checking the browser console
3. Ensure all CDN links are accessible

## Contributing

1. Make changes to `index.html`
2. Test with the Python HTTP server
3. Ensure the backend API is running
4. Test all search and filter functionality
