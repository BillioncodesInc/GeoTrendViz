# GeoTrendViz 🌍📊

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-3.0.2-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Twitter API](https://img.shields.io/badge/Twitter%20API-v2-1DA1F2.svg)](https://developer.twitter.com/)
[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/BillioncodesInc/GeoTrendViz)

GeoTrendViz is a powerful, real-time Twitter trends visualization tool that transforms location-based trending topics into beautiful, interactive word clouds. Discover what's happening around the world with just a click.

![GeoTrendViz Demo](https://via.placeholder.com/800x400?text=GeoTrendViz+Demo)

## ✨ Features

### Core Functionality

- 🌐 **Location-Based Trends**: Analyze trending topics from any location worldwide
- 🎨 **Interactive Word Cloud**: Beautiful D3.js-powered visualizations with dynamic sizing based on tweet volume
- 📱 **Responsive Design**: Seamless experience across desktop, tablet, and mobile devices
- 🌓 **Dark/Light Mode**: Automatic theme switching with persistent user preferences
- 🌍 **Multi-Language Support**: Support for 12+ languages including English, Spanish, French, German, and more

### Advanced Features

- 🔍 **Real-Time Tweet Display**: Click any word to view recent tweets instantly
- 📊 **Tweet Metrics**: View retweets, likes, and reply counts for each tweet
- 💾 **Export Functionality**: Download word clouds as SVG files
- 🔗 **Share Integration**: Built-in sharing capabilities with Web Share API
- ⚡ **Performance Optimized**: Rate limiting and caching for optimal performance
- 🔒 **Security First**: CSRF protection, input validation, and secure API handling

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Twitter Developer Account with API access
- pip (Python package manager)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/BillioncodesInc/GeoTrendViz.git
cd GeoTrendViz
```

2. **Create a virtual environment**

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set up environment variables**
   Create a `.env` file in the root directory:

```env
TWITTER_API_KEY=your_api_key_here
TWITTER_API_SECRET=your_api_secret_here
TWITTER_ACCESS_TOKEN=your_access_token_here
TWITTER_ACCESS_TOKEN_SECRET=your_access_token_secret_here
TWITTER_BEARER_TOKEN=your_bearer_token_here
SECRET_KEY=your_flask_secret_key_here
```

5. **Run the application**

```bash
python app.py
```

6. **Open your browser**
   Navigate to `http://localhost:5000`

## 🎯 Usage

1. **Search for Trends**

   - Enter any location (city, country, or region)
   - Select your preferred language
   - Click "Search Trends"

2. **Interact with the Word Cloud**

   - Hover over words to see them enlarge
   - Click on any word to view recent tweets
   - Use the action buttons to download, share, or copy the link

3. **Customize Your Experience**
   - Toggle between dark and light modes
   - Change languages for international trends
   - Export visualizations for presentations

## 🛠️ Technology Stack

### Backend

- **Flask** - Lightweight Python web framework
- **Tweepy** - Twitter API wrapper
- **Flask-Limiter** - Rate limiting
- **Flask-WTF** - CSRF protection

### Frontend

- **D3.js** - Data visualization
- **d3-cloud** - Word cloud layout
- **Font Awesome** - Icons
- **Inter Font** - Typography

### APIs

- **Twitter API v2** - Real-time trend data
- **Web Share API** - Native sharing

## 📁 Project Structure

```
GeoTrendViz/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── render.yaml        # Render deployment config
├── Procfile           # Heroku deployment config
├── runtime.txt        # Python version
├── env.example        # Environment variables template
├── README.md          # Project documentation
├── DEPLOYMENT.md      # Deployment guide
├── LICENSE            # MIT license
├── static/
│   ├── styles.css     # Application styles
│   └── script.js      # Frontend JavaScript
└── templates/
    └── wordcloud.html # Main application template
```

## 🔧 Configuration

### Environment Variables

| Variable                      | Description                     | Required |
| ----------------------------- | ------------------------------- | -------- |
| `TWITTER_API_KEY`             | Twitter API consumer key        | Yes      |
| `TWITTER_API_SECRET`          | Twitter API consumer secret     | Yes      |
| `TWITTER_ACCESS_TOKEN`        | Twitter access token            | Yes      |
| `TWITTER_ACCESS_TOKEN_SECRET` | Twitter access token secret     | Yes      |
| `TWITTER_BEARER_TOKEN`        | Twitter Bearer token for v2 API | Yes      |
| `SECRET_KEY`                  | Flask secret key for sessions   | Yes      |

### Rate Limiting

Default limits:

- 200 requests per day per IP
- 50 requests per hour per IP
- 30 requests per minute for tweet fetching

## 🚀 Deployment

### One-Click Deploy to Render

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/BillioncodesInc/GeoTrendViz)

### Manual Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed deployment instructions for:

- Render (Recommended)
- Heroku
- Railway

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use meaningful commit messages
- Add tests for new features
- Update documentation as needed

## 📊 API Reference

### Endpoints

#### `GET /`

Main application page

#### `POST /`

Submit location for trend analysis

- **Parameters**: `location` (string), `language` (string)
- **Returns**: HTML page with word cloud

#### `POST /fetch_tweets`

Fetch recent tweets for a specific word

- **Parameters**: `word` (string), `lang` (string)
- **Returns**: JSON array of tweets

## 🐛 Troubleshooting

### Common Issues

1. **Twitter API Connection Errors**

   - Verify your API credentials in `.env`
   - Check if you've exceeded rate limits
   - Ensure your Twitter Developer account is active

2. **Word Cloud Not Displaying**

   - Clear browser cache (Ctrl+F5)
   - Check browser console for JavaScript errors
   - Verify D3.js is loading correctly

3. **Tweets Not Loading**
   - Check if the word exists in recent tweets
   - Verify language settings match tweet language
   - Check network tab for API response

## 📈 Performance Optimization

- **Caching**: Implement Redis for caching trend data
- **CDN**: Use CDN for static assets
- **Compression**: Enable gzip compression
- **Database**: Add PostgreSQL for historical data

## 🔒 Security Considerations

- All user inputs are validated and sanitized
- CSRF protection enabled on all forms
- Rate limiting prevents API abuse
- Environment variables keep credentials secure
- Regular dependency updates recommended

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **BillionCodes Inc** - _Initial work_ - [BillioncodesInc](https://github.com/BillioncodesInc)

## 🙏 Acknowledgments

- Twitter for providing the API
- D3.js community for visualization tools
- Flask community for the excellent framework
- All contributors and users

## 📞 Support

- **Documentation**: [Wiki](https://github.com/BillioncodesInc/GeoTrendViz/wiki)
- **Issues**: [GitHub Issues](https://github.com/BillioncodesInc/GeoTrendViz/issues)
- **Email**: support@billioncodes.com

---

<p align="center">Made with ❤️ by BillionCodes Inc</p>
