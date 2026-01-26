# Smart Fashion Trends - Web UI

A modern, responsive web interface for the Smart Fashion Trends AI recommendation system.

## Features

- **User Authentication**: Register and login with secure JWT authentication
- **Personalized Recommendations**: View AI-powered fashion recommendations
- **Interactive Feedback**: Like, add to cart, or wishlist items to improve recommendations
- **Fashion Trends**: Explore trending items across different time periods
- **Seasonal Trends**: View trends for specific seasons (Spring, Summer, Fall, Winter)
- **User Preferences**: View your learned preferences based on interactions

## Getting Started

### Prerequisites

Make sure the backend API server is running:

```bash
# From the project root
python src/api/app.py
```

The API should be running on `http://localhost:5000`

### Accessing the UI

Once the API server is running, open your browser and navigate to:

```
http://localhost:5000
```

The UI will be served from the root endpoint.

## Usage

### 1. Authentication

When you first visit the UI, you'll see the authentication screen:

- **Register**: Create a new account with username, email, and password
- **Login**: Sign in with your existing credentials

After successful authentication, you'll be automatically logged in and redirected to the main application.

### 2. Recommendations

The **Recommendations** tab shows personalized fashion items selected by the AI:

- Each item displays details: name, category, style, color, brand, and price
- A recommendation score indicates how well it matches your preferences
- Interact with items using action buttons:
  - ❤️ **Like**: Mark items you find interesting
  - 🛒 **Cart**: Items you'd consider purchasing
  - ⭐ **Wishlist**: Save items for later

Your interactions are recorded and used to improve future recommendations!

### 3. Trends

The **Trends** tab displays current fashion trends:

- Select a time period (7, 30, or 90 days)
- View trends organized by:
  - Categories (dresses, shirts, pants, etc.)
  - Styles (casual, formal, sporty, etc.)
  - Colors (popular color choices)
  - Brands (trending brands)

**Seasonal Trends** section allows you to explore trends for specific seasons:
- 🌸 Spring
- ☀️ Summer
- 🍂 Fall
- ❄️ Winter

### 4. Preferences

The **Preferences** tab shows your learned preferences:

- View all preferences extracted from your interactions
- Each preference has a weight indicating its importance
- Preferences are automatically updated as you interact with items

## Technical Details

### Architecture

The UI is built with:
- **HTML5**: Semantic markup
- **CSS3**: Modern styling with CSS Grid and Flexbox
- **Vanilla JavaScript**: No frameworks, lightweight and fast

### API Integration

The UI communicates with the Flask backend API using:
- **REST API**: Standard HTTP methods (GET, POST)
- **JWT Authentication**: Secure token-based auth stored in localStorage
- **JSON**: Data exchange format

### Responsive Design

The interface is fully responsive and works on:
- Desktop computers
- Tablets
- Mobile devices

### Browser Compatibility

Tested and working on:
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)

## File Structure

```
ui/
├── index.html              # Main HTML file
├── static/
│   ├── css/
│   │   └── styles.css      # All styling
│   └── js/
│       └── app.js          # Application logic
└── README.md               # This file
```

## Customization

### Changing API URL

If your API is running on a different host/port, update the `API_BASE_URL` in `ui/static/js/app.js`:

```javascript
const API_BASE_URL = 'http://your-host:your-port';
```

### Styling

All styles are in `ui/static/css/styles.css`. The design uses CSS custom properties (variables) for easy theming:

```css
:root {
    --primary-color: #6366f1;
    --secondary-color: #8b5cf6;
    --background: #f8fafc;
    /* ... */
}
```

## Security

- Passwords are never stored in the browser
- JWT tokens are stored in localStorage
- All API calls include authentication headers
- CORS is enabled on the backend for security

## Development

### Making Changes

1. Edit the HTML in `ui/index.html`
2. Update styles in `ui/static/css/styles.css`
3. Modify logic in `ui/static/js/app.js`
4. Refresh the browser to see changes (no build step required!)

### Debugging

Open browser developer tools (F12) to:
- View console logs
- Inspect network requests
- Debug JavaScript code

## Future Enhancements

Potential improvements for the UI:

- [ ] Image uploads for fashion items
- [ ] Outfit visualization
- [ ] Social sharing features
- [ ] Dark mode toggle
- [ ] Advanced filtering options
- [ ] Search functionality
- [ ] User profile editing
- [ ] Purchase history
- [ ] Rating system for items

## Troubleshooting

### UI not loading

- Make sure the API server is running
- Check that you're accessing `http://localhost:5000`
- Check browser console for errors

### Can't log in

- Verify the API server is running
- Check network tab in browser dev tools
- Ensure you're using correct credentials

### No recommendations showing

- You may need to interact with some items first
- Try running `python src/train_model.py` to generate sample data

### CORS errors

- The Flask app should have CORS enabled
- Check that `flask-cors` is installed
- Verify the API is running on the expected port

## Support

For issues or questions:
- Check the main [README.md](../README.md)
- Review the [QUICKSTART.md](../QUICKSTART.md) guide
- Check API documentation at `http://localhost:5000/api`
