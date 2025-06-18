# Deployment Guide for GeoTrendViz

This guide provides step-by-step instructions for deploying GeoTrendViz to various platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Deploying to Render (Recommended)](#deploying-to-render-recommended)
- [Deploying to Heroku](#deploying-to-heroku)
- [Deploying to Railway](#deploying-to-railway)
- [Environment Variables](#environment-variables)
- [Post-Deployment](#post-deployment)

## Prerequisites

Before deploying, ensure you have:

1. A Twitter Developer account with API credentials
2. The project pushed to GitHub
3. All environment variables ready

## Deploying to Render (Recommended)

Render is the recommended platform for deploying Python Flask applications.

### Method 1: One-Click Deploy

1. **Click Deploy to Render Button**

   [![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/BillioncodesInc/GeoTrendViz)

2. **Configure Your Service**

   - Service name: Choose a unique name
   - Region: Select closest to your users
   - Branch: main

3. **Set Environment Variables**
   Add these in the Render dashboard:
   - `TWITTER_API_KEY`
   - `TWITTER_API_SECRET`
   - `TWITTER_ACCESS_TOKEN`
   - `TWITTER_ACCESS_TOKEN_SECRET`
   - `TWITTER_BEARER_TOKEN`

### Method 2: Manual Deploy via Dashboard

1. **Create Render Account**
   Visit [render.com](https://render.com) and sign up

2. **New Web Service**

   - Click "New +" → "Web Service"
   - Connect your GitHub account
   - Select the GeoTrendViz repository

3. **Configure Service**

   - Name: `geotrendviz` (or your choice)
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`

4. **Add Environment Variables**
   In the Environment tab, add:

   ```
   TWITTER_API_KEY=your_key
   TWITTER_API_SECRET=your_secret
   TWITTER_ACCESS_TOKEN=your_token
   TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
   TWITTER_BEARER_TOKEN=your_bearer_token
   SECRET_KEY=<leave blank for auto-generation>
   ```

5. **Deploy**
   Click "Create Web Service"

### Method 3: Using render.yaml

The project includes a `render.yaml` file for automatic configuration.

1. Push to GitHub
2. Connect repository to Render
3. Render will automatically detect and use the configuration

## Deploying to Heroku

1. **Install Heroku CLI**
   Download from [heroku.com](https://devcenter.heroku.com/articles/heroku-cli)

2. **Login to Heroku**

   ```bash
   heroku login
   ```

3. **Create Heroku App**

   ```bash
   heroku create geotrendviz-yourname
   ```

4. **Set Environment Variables**

   ```bash
   heroku config:set TWITTER_API_KEY=your_key
   heroku config:set TWITTER_API_SECRET=your_secret
   heroku config:set TWITTER_ACCESS_TOKEN=your_token
   heroku config:set TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
   heroku config:set TWITTER_BEARER_TOKEN=your_bearer_token
   heroku config:set SECRET_KEY=your_secret_key
   ```

5. **Deploy**
   ```bash
   git push heroku main
   ```

## Deploying to Railway

1. **Visit Railway**
   Go to [railway.app](https://railway.app)

2. **New Project**
   Click "New Project" → "Deploy from GitHub repo"

3. **Select Repository**
   Choose your GeoTrendViz repository

4. **Add Variables**
   Click on the deployment → Variables → Add all required environment variables

5. **Deploy**
   Railway will automatically deploy your app

## Environment Variables

Required environment variables for all platforms:

```env
TWITTER_API_KEY=your_twitter_api_key
TWITTER_API_SECRET=your_twitter_api_secret
TWITTER_ACCESS_TOKEN=your_twitter_access_token
TWITTER_ACCESS_TOKEN_SECRET=your_twitter_access_token_secret
TWITTER_BEARER_TOKEN=your_twitter_bearer_token
SECRET_KEY=generate_random_string_here
```

### Getting Twitter API Credentials

1. Visit [developer.twitter.com](https://developer.twitter.com)
2. Create a new app
3. Generate API keys and tokens
4. Copy all credentials

### Generating a Secret Key

Python method:

```python
import secrets
print(secrets.token_hex(32))
```

Or use online generator: [randomkeygen.com](https://randomkeygen.com/)

## Post-Deployment

### 1. Test Your Deployment

- Visit your deployed URL
- Test searching for different locations
- Verify word cloud generation
- Check tweet fetching functionality

### 2. Monitor Performance

- Check application logs
- Monitor API rate limits
- Set up uptime monitoring

### 3. Custom Domain (Optional)

#### Render

1. Go to Settings → Custom Domains
2. Add your domain
3. Update DNS records

#### Heroku

```bash
heroku domains:add yourdomain.com
```

#### Railway

Configure in the Railway dashboard

### 4. Enable HTTPS

- Render: Automatic with free SSL
- Heroku: Automatic with custom domains
- Railway: Automatic

## Troubleshooting

### Common Issues

1. **Application Error**

   - Check environment variables are set correctly
   - Review application logs
   - Ensure all dependencies are installed

2. **Twitter API Errors**

   - Verify API credentials
   - Check rate limits
   - Ensure Twitter Developer account is active

3. **Build Failures**
   - Check Python version compatibility
   - Verify requirements.txt is complete
   - Check for syntax errors

### Viewing Logs

#### Render

- Dashboard → Logs tab
- Real-time log streaming

#### Heroku

```bash
heroku logs --tail
```

#### Railway

View logs in the Railway dashboard

## Performance Tips

1. **Render Specific**

   - Use Render's auto-scaling features
   - Enable health checks
   - Configure custom domains for better performance

2. **Caching**

   - Consider adding Redis for caching
   - Render offers managed Redis instances

3. **Static Files**
   - Consider using a CDN for static assets
   - Render serves static files efficiently

## Security Best Practices

1. **Never commit .env files**
2. **Use strong secret keys**
3. **Enable 2FA on deployment platforms**
4. **Regularly update dependencies**
5. **Monitor for security vulnerabilities**
6. **Use Render's built-in DDoS protection**

## Cost Considerations

### Render (Recommended)

- **Free Tier**: Perfect for getting started
  - 750 hours/month
  - Automatic SSL
  - Custom domains
- **Paid Plans**: Start at $7/month for always-on service

### Heroku

- **Free Tier**: Discontinued
- **Basic**: $7/month
- **Additional costs**: Add-ons like databases

### Railway

- **Free Trial**: $5 credit
- **Usage-based**: Pay for what you use
- **Estimated**: ~$5-10/month for small apps

## Support

If you encounter issues:

1. Check the [GitHub Issues](https://github.com/BillioncodesInc/GeoTrendViz/issues)
2. Review deployment platform documentation
3. Contact support@billioncodes.com

---

Happy Deploying! 🚀
