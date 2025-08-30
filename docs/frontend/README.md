# Corporate Spending Tracker - Frontend

A modern, responsive frontend for tracking corporate spending across lobbying, political contributions, and charitable grants. Built with modern web technologies and designed for both development and production environments.

## ✨ Features

### 🔍 **Company Search**
- **Advanced Search**: Search companies by name, ticker, or CIK
- **Smart Filtering**: Filter by spending amounts, data availability, and categories
- **Real-time Results**: Live search with debounced API calls
- **Detailed Views**: Comprehensive spending breakdowns with interactive charts

### 📊 **Dashboard**
- **Overview Statistics**: Total companies, spending summaries, recent activity
- **Top Spenders**: Dynamic rankings by category with real-time data
- **Visual Analytics**: Interactive charts powered by Chart.js
- **Responsive Design**: Optimized for desktop, tablet, and mobile

### 📈 **Analytics**
- **Spending Comparison**: Compare companies across all categories
- **Trend Analysis**: Historical spending patterns and projections
- **Category Breakdown**: Detailed analysis by lobbying, political, and charitable spending
- **Export Ready**: Data formatted for reports and further analysis

### 🎨 **Modern UI/UX**
- **Dark Mode Design**: Professional dark theme optimized for extended use
- **Responsive Layout**: Seamless experience across all device sizes
- **Loading States**: Elegant loading indicators and error handling
- **Accessibility**: ARIA labels and keyboard navigation support

## 🚀 Quick Start

### Prerequisites

- **Node.js 16+** (recommended for package management)
- **Python 3.7+** (for development server alternative)

### Development Setup

1. **Install dependencies**:
   ```bash
   cd frontend
   npm install
   ```

2. **Start development server**:
   ```bash
   npm run dev
   ```

3. **Open your browser**: http://localhost:3000

### Alternative Development Methods

#### Option 1: Python HTTP Server
   ```bash
   cd frontend
python -m http.server 3000
```

#### Option 2: Node.js Server
```bash
npm run serve:alt
```

#### Option 3: VS Code Live Server
1. Install "Live Server" extension
2. Right-click `index.html` → "Open with Live Server"

## 📦 Production Build

### Build for Production

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Build CSS and JavaScript**:
   ```bash
   npm run build
   ```

3. **Generated files**:
   - `index.prod.html` - Production-ready HTML
   - `dist/app.bundle.js` - Bundled JavaScript
   - `dist/tailwind.css` - Compiled CSS
   - `dist/build-info.json` - Build metadata

### Deployment

1. Upload `index.prod.html` and `dist/` folder to your web server
2. Configure server to serve `index.prod.html` as the main page
3. Ensure backend API is accessible from production domain

## 🔧 Configuration

### Environment Configuration

The frontend automatically detects environment and configures API endpoints:

```javascript
// Development: uses localhost:8000
// Production: uses relative paths /api/

// In config.js - easily customizable
window.APP_CONFIG = {
    API: {
        BASE_URL: window.location.hostname === 'localhost' 
            ? 'http://127.0.0.1:8000/api'
            : '/api',
    }
};
```

### Customization

- **API Endpoints**: Edit `config.js` to change backend URLs
- **Colors**: Modify `tailwind.config.js` for theme customization
- **Features**: Add new tabs and components in `index.html`

## 🛠️ Technology Stack

### Core Technologies
- **Framework**: Vanilla JavaScript with Alpine.js for reactivity
- **Styling**: Tailwind CSS with custom design system
- **Charts**: Chart.js for interactive data visualization
- **Build**: Custom Node.js build system with dependency bundling

### Dependencies
- **Alpine.js**: `^3.13.3` - Lightweight reactive framework
- **Chart.js**: `^4.4.0` - Modern charting library
- **Tailwind CSS**: `^3.3.6` - Utility-first CSS framework

### Development Tools
- **PostCSS**: CSS processing and optimization
- **Autoprefixer**: Automatic vendor prefixing
- **Build System**: Custom bundling for production optimization

## 📁 Project Structure

```
frontend/
├── 📄 index.html              # Main application file
├── ⚙️ config.js               # Configuration and environment settings
├── 📊 logger.js               # Frontend logging utility
├── 🎨 src/
│   └── input.css              # Tailwind CSS source
├── 🔧 build.js                # Production build script
├── 📦 package.json            # Dependencies and scripts
├── 🎨 tailwind.config.js      # Tailwind configuration
├── 🐍 server.py              # Python development server
├── 📋 dist/                   # Production build output
│   ├── app.bundle.js          # Bundled JavaScript
│   ├── tailwind.css           # Compiled CSS
│   └── build-info.json        # Build metadata
└── 📖 README.md               # This file
```

## 💻 Development

### Available Scripts

```bash
# Development
npm run dev                    # Start development server with watch
npm run serve                  # Start Python HTTP server
npm run serve:alt              # Start Node.js server

# Building
npm run build                  # Full production build
npm run build:css              # Compile Tailwind CSS only
npm run build:js               # Bundle JavaScript only

# Utilities
npm run watch                  # Watch CSS changes
npm run clean                  # Clean build artifacts
```

### API Integration Pattern

```javascript
// Using the configuration system
const url = CONFIG_HELPERS.getApiUrl('companies/search/');

try {
    const response = await fetch(url);
    const data = await response.json();
    
    // Handle success
    frontendLogger.info('API request successful', { url, data });
    return data;
} catch (error) {
    // Handle error
    frontendLogger.error('API request failed', { url, error });
    throw error;
}
```

### Adding New Features

1. **New Tab**: Add navigation button and content section
2. **API Endpoint**: Create function using `CONFIG_HELPERS.getApiUrl()`
3. **Alpine Component**: Add reactive data and methods
4. **Styling**: Use Tailwind classes following the design system

### Logging System

Comprehensive logging for debugging and monitoring:

```javascript
// User interactions
frontendLogger.logUserAction('Search performed', { query: 'apple' });

// API requests (automatically logged)
frontendLogger.logApiRequest(url, method, params, response);

// Custom events
frontendLogger.info('Custom event', { data: {...} });
frontendLogger.warning('Warning message', { context: 'search' });
frontendLogger.error('Error occurred', { error: error.message });
```

## 🎨 Design System

### Color Palette

```css
/* Spending Categories */
--color-lobbying: #ef4444     /* Red */
--color-charitable: #10b981   /* Green */
--color-political: #3b82f6    /* Blue */
--color-total: #f59e0b        /* Amber */

/* UI Colors */
--color-primary: #3b82f6      /* Blue */
--color-success: #10b981      /* Green */
--color-warning: #f59e0b      /* Amber */
--color-error: #ef4444        /* Red */
```

### Component Classes

```css
/* Custom components */
.card                          /* Standard card layout */
.btn, .btn-primary            /* Button variants */
.input                        /* Form inputs */
.spinner                      /* Loading indicators */
.nav-item                     /* Navigation items */
```

### Responsive Design

- **Mobile First**: Designed for mobile, enhanced for desktop
- **Breakpoints**: Follows Tailwind's responsive system
- **Touch Friendly**: Optimized for touch interactions
- **Accessibility**: WCAG 2.1 AA compliant

## 🔍 Troubleshooting

### Common Issues

#### **API Connection Errors**
```bash
# Check backend server
curl http://localhost:8000/api/companies/

# Verify CORS configuration
# Check browser console for CORS errors
```

#### **Build Issues**
```bash
# Clear node modules and reinstall
rm -rf node_modules package-lock.json
npm install

# Clear build cache
npm run clean
npm run build
```

#### **Styling Problems**
- Verify Tailwind CSS is compiled: `npm run build:css`
- Check browser console for CSS loading errors
- Ensure classes exist in Tailwind configuration

### Performance Optimization

- **API Calls**: Debounced search, cached responses
- **Bundle Size**: Production build minifies all assets
- **Loading**: Lazy loading for non-critical components
- **Images**: Optimized for web delivery

### Browser Support

| Browser | Version | Status |
|---------|---------|--------|
| Chrome  | 80+     | ✅ Full Support |
| Firefox | 75+     | ✅ Full Support |
| Safari  | 13+     | ✅ Full Support |
| Edge    | 80+     | ✅ Full Support |

## 📊 Monitoring & Analytics

### Performance Metrics
- First Contentful Paint (FCP)
- Largest Contentful Paint (LCP)
- Cumulative Layout Shift (CLS)
- Time to Interactive (TTI)

### Error Tracking
- JavaScript errors logged to backend
- API failures tracked and reported
- User interaction logging for UX insights

## 🤝 Contributing

1. **Code Style**: Follow existing patterns and ESLint rules
2. **Testing**: Test across all supported browsers
3. **Documentation**: Update README for new features
4. **Performance**: Ensure additions don't impact load times

### Development Workflow

1. Create feature branch from `main`
2. Make changes and test locally
3. Run production build: `npm run build`
4. Test production build
5. Submit pull request with detailed description

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](../LICENSE) file for details.

---

**Built with ❤️ for transparency in corporate spending**