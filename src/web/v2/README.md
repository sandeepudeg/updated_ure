# GramSetu Web Interface v2

Modern, agricultural-themed web interface for GramSetu Rural AI Assistant.

## 📁 File Structure

```
src/web/v2/
├── index.html          # Main HTML structure
├── styles.css          # All CSS styles (agricultural theme)
├── app.js              # JavaScript functionality
└── README.md           # This file
```

## 🎨 Design Features

### Color Palette
- **Primary Green**: #2E7D32, #43A047, #66BB6A (farming/growth)
- **Earth Tones**: #FFF9E6, #FFF3D6, #E8D5A8 (soil/harvest)
- **Background**: #F5F9F3, #E8F5E9 (fresh fields)
- **Accents**: #F9A825 (golden harvest)

### Layout
- **3-Column Design**: Left sidebar, center chat, right info panel
- **Responsive**: Adapts to mobile, tablet, and desktop
- **Agent Cards**: 2x3 grid showcasing 6 key features
- **Professional**: Clean, modern, enterprise-grade styling

## 🚀 Features

### User Interface
- ✅ Quick action buttons for common queries
- ✅ Agent cards for feature discovery
- ✅ Image upload for crop disease identification
- ✅ Real-time chat interface
- ✅ Chat history display
- ✅ Location and weather info
- ✅ Market prices sidebar
- ✅ Language selector (English, Hindi, Marathi)

### Functionality
- ✅ API integration with AWS Lambda
- ✅ Image upload and base64 encoding
- ✅ Local storage for user ID and chat history
- ✅ Loading indicators
- ✅ Error handling
- ✅ Responsive design
- ✅ Keyboard shortcuts (Enter to send)

## 🔧 Configuration

### API Endpoint
Update the API endpoint in `app.js`:

```javascript
const CONFIG = {
    API_ENDPOINT: 'https://8938dqxf33.execute-api.us-east-1.amazonaws.com/dev/query',
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000
};
```

### Agent Cards
Modify agent cards in `index.html`:

```html
<div class="agent-card" data-query="Your query here">
    <div class="icon">🌱</div>
    <h3>Card Title</h3>
    <p>Card description</p>
</div>
```

## 📦 Deployment

### Option 1: S3 + CloudFront (Recommended)

```powershell
# Upload all files to S3
aws s3 cp index.html s3://ure-mvp-data-us-east-1-188238313375/web/v2/index.html --content-type "text/html"
aws s3 cp styles.css s3://ure-mvp-data-us-east-1-188238313375/web/v2/styles.css --content-type "text/css"
aws s3 cp app.js s3://ure-mvp-data-us-east-1-188238313375/web/v2/app.js --content-type "application/javascript"

# Invalidate CloudFront cache
aws cloudfront create-invalidation --distribution-id E354ZTACSUHKWS --paths "/web/v2/*"
```

### Option 2: Local Testing

```bash
# Using Python
cd src/web/v2
python -m http.server 8000

# Using Node.js
npx http-server -p 8000

# Then open: http://localhost:8000
```

### Option 3: Direct File Access

Simply open `index.html` in your browser. Note: API calls may be blocked by CORS in this mode.

## 🧪 Testing

### Manual Testing Checklist
- [ ] Quick action buttons populate input field
- [ ] Agent cards populate input field
- [ ] Send button sends message
- [ ] Enter key sends message
- [ ] Image upload works
- [ ] Chat messages display correctly
- [ ] Loading indicator appears
- [ ] Error messages display
- [ ] Responsive design works on mobile
- [ ] Language selector displays (functionality TBD)

### Browser Console Testing

```javascript
// Clear chat history
GramSetu.clearHistory();

// Check current state
console.log(GramSetu.state);

// Send test message
GramSetu.sendMessage();
```

## 🔌 API Integration

### Request Format

```json
{
    "user_id": "user_1234567890_abc123",
    "query": "What disease is affecting my tomato plant?",
    "image": "base64_encoded_image_data" // optional
}
```

### Response Format

```json
{
    "agent": "Agri Expert",
    "response": "Based on the image, your tomato plant appears to have...",
    "message": "Alternative response field"
}
```

## 🎯 Customization

### Change Colors
Edit `styles.css` and update the color variables:

```css
/* Primary colors */
#2E7D32  /* Dark green */
#43A047  /* Medium green */
#66BB6A  /* Light green */

/* Earth tones */
#FFF9E6  /* Light cream */
#E8D5A8  /* Golden beige */
#F9A825  /* Harvest gold */
```

### Add New Agent Card

1. Add HTML in `index.html`:
```html
<div class="agent-card" data-query="Your query">
    <div class="icon">🎯</div>
    <h3>New Feature</h3>
    <p>Description</p>
</div>
```

2. Update grid if needed (currently 2x3):
```css
.agent-cards {
    grid-template-columns: repeat(3, 1fr); /* Change to 3 columns */
}
```

### Modify Quick Actions

Edit the quick actions in `index.html`:

```html
<button class="quick-action" data-query="Your custom query">
    🎯 Your Action Name
</button>
```

## 📱 Responsive Breakpoints

- **Desktop**: > 1200px (3-column layout)
- **Tablet**: 768px - 1200px (stacked layout)
- **Mobile**: < 768px (single column, simplified)

## 🐛 Troubleshooting

### Issue: API calls fail
- Check CORS settings on API Gateway
- Verify API endpoint URL in `app.js`
- Check browser console for errors

### Issue: Images don't upload
- Verify file size < 5MB
- Check image format (jpg, png supported)
- Ensure base64 encoding works

### Issue: Styles not loading
- Check file paths in `index.html`
- Verify CSS file is in same directory
- Clear browser cache

### Issue: Chat history not saving
- Check localStorage is enabled
- Verify browser supports localStorage
- Check for quota exceeded errors

## 📄 License

Part of the GramSetu Rural AI Assistant project.

## 🤝 Contributing

To contribute improvements:
1. Test changes locally
2. Update this README if needed
3. Document any new features
4. Ensure responsive design works

## 📞 Support

For issues or questions, refer to the main project documentation.

---

**Last Updated**: March 4, 2026  
**Version**: 2.0  
**Status**: Production Ready
