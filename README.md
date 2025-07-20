# Cinematic - Movie Recommendation App

A beautiful, personality-based movie recommendation system that helps users discover films that match their unique taste and preferences.

## 🌟 Features

- **Personality Quiz**: Engaging 7-question quiz to determine your cinematic personality
- **Smart Recommendations**: AI-powered movie suggestions based on your personality traits
- **Streaming Integration**: Shows where movies are available to stream (Netflix, Hulu, Prime)
- **News Integration**: Recent news and reviews for top recommendations
- **Cinematic Design**: Beautiful, dark-themed UI with smooth animations
- **Responsive**: Works perfectly on desktop, tablet, and mobile devices

## 🚀 Quick Start

### Development Mode

#### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

#### Installation

1. **Clone or download the project**
   ```bash
   # If you have git installed
   git clone <repository-url>
   cd cinematic
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**
   - Copy `config.env` to `.env`
   - Add your API keys (optional for testing - the app works with mock data)

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Open your browser**
   - Navigate to `http://localhost:5000`
   - Start exploring your cinematic personality!

### Production Deployment

#### Prerequisites
- Docker and Docker Compose installed
- API keys for full functionality




### API Keys (Optional)

The app works perfectly without API keys using mock data, but for full functionality, you can add:

1. **Trakt API** (for movie recommendations)
   - Visit [Trakt API](https://trakt.tv/oauth/applications)
   - Create a new application
   - Copy your Client ID

2. **NewsAPI** (for movie news)
   - Visit [NewsAPI](https://newsapi.org/)
   - Sign up for a free account
   - Copy your API key

3. **WatchMode API** (for streaming info)
   - Visit [WatchMode](https://api.watchmode.com/)
   - Sign up for an account
   - Copy your API key

Add these to your `.env` file:
```
TRAKT_CLIENT_ID=your_trakt_client_id
NEWS_API_KEY=your_newsapi_key
WATCHMODE_API_KEY=your_watchmode_api_key
```

## 📁 Project Structure

```
cinematic/
├── app.py                 # Main Flask application
├── config.py             # Configuration management
├── wsgi.py              # WSGI entry point for production
├── requirements.txt      # Python dependencies
├── config.env           # Environment variables template
├── Dockerfile           # Docker container configuration
├── docker-compose.yml   # Multi-service deployment
├── nginx.conf          # Nginx reverse proxy configuration
├── deploy.sh           # Production deployment script
├── README.md           # This file
├── static/
│   ├── css/
│   │   └── style.css   # Main stylesheet
│   └── js/
│       └── main.js     # JavaScript functionality
└── templates/
    ├── index.html      # Landing page
    ├── quiz.html       # Personality quiz
    ├── recommendations.html # Results page
    └── error.html      # Error page
```

## 🎯 How It Works

### 1. Personality Assessment
The app uses a carefully crafted 7-question quiz to understand your:
- Social preferences
- Creative expression
- Adventure level
- Relaxation style
- And more...

### 2. Smart Mapping
Each answer maps to specific movie genres and themes:
- "Quiet night in" → Drama, Romance, Indie
- "Wild party" → Comedy, Action, Adventure
- "Puzzle solving" → Mystery, Thriller, Sci-Fi

### 3. Recommendation Engine
- Analyzes your dominant personality traits
- Fetches trending movies from Trakt API
- Enriches with streaming availability
- Adds recent news and reviews

### 4. Beautiful Presentation
- Cinematic dark theme
- Smooth animations and transitions
- Responsive design
- Hover effects and interactions

## 🎨 Design Features

- **Dark Cinematic Theme**: Professional movie theater aesthetic
- **Smooth Animations**: Fade-ins, hover effects, and transitions
- **Responsive Layout**: Works on all screen sizes
- **Interactive Quiz**: One question at a time with progress tracking
- **Movie Cards**: Beautiful presentation with streaming info
- **Loading States**: Smooth loading animations

## 🔮 Future Enhancements

- [ ] User accounts and history
- [ ] More detailed movie information
- [ ] Social sharing features
- [ ] Movie trailer integration
- [ ] Advanced filtering options
- [ ] Personalized watchlists

## 🛠️ Development

### Running in Development Mode
```bash
python app.py
```

### Making Changes
1. The app uses Flask's auto-reload feature
2. Changes to Python files will restart the server
3. Changes to templates and static files will be reflected immediately

### Testing
The app includes mock data for testing without API keys. Simply run the app and take the quiz to see it in action!

## 🚀 Production Features

### Security & Performance
- **Rate Limiting**: Built-in rate limiting to prevent abuse
- **Error Handling**: Comprehensive error handling with custom error pages
- **Logging**: Structured logging for monitoring and debugging
- **API Timeouts**: Configurable timeouts for external API calls
- **Security Headers**: Nginx configuration with security headers

### Scalability
- **Docker Containerization**: Easy deployment and scaling
- **Nginx Reverse Proxy**: Load balancing and SSL termination
- **Redis Caching**: Ready for caching implementation
- **Multi-Worker Setup**: Gunicorn with multiple workers

### Monitoring & Maintenance
- **Health Checks**: Docker health checks for monitoring
- **Log Management**: Centralized logging with volume mounts
- **Graceful Shutdown**: Proper signal handling
- **Environment Configuration**: Separate configs for dev/prod

### Deployment Options
1. **Docker Compose**: Full stack with Nginx and Redis
2. **Standalone**: Direct Python deployment
3. **Cloud Ready**: Ready for AWS, GCP, or Azure deployment

## 📱 Browser Compatibility

- Chrome (recommended)
- Firefox
- Safari
- Edge

## 🤝 Contributing

1. Fork the project
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- Flask for the web framework
- Google Fonts for typography
- Trakt, NewsAPI, and WatchMode for APIs
- The movie community for inspiration

---

**Ready to discover your cinematic personality? Start the quiz and find your perfect movies! 🎬✨** 
