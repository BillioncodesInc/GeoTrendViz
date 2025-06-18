# Deployment Guide for GeoTrendViz

This guide provides step-by-step instructions for deploying GeoTrendViz to various platforms.

## Table of Contents

- [Prerequisites](#prerequisites)
- [Deploying to Vercel](#deploying-to-vercel)
- [Deploying to Heroku](#deploying-to-heroku)
- [Deploying to Railway](#deploying-to-railway)
- [Environment Variables](#environment-variables)
- [Post-Deployment](#post-deployment)

## Prerequisites

Before deploying, ensure you have:

1. A Twitter Developer account with API credentials
2. The project cloned and working locally
3. All environment variables ready

## Deploying to Vercel

### Method 1: Using Vercel CLI

1. **Install Vercel CLI**

   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**

   ```bash
   vercel login
   ```

3. **Deploy**

   ```bash
   vercel
   ```

   Follow the prompts:

   - Select your account
   - Link to existing project or create new
   - Configure project settings

4. **Set Environment Variables**
   ```bash
   vercel env add TWITTER_API_KEY
   vercel env add TWITTER_API_SECRET
   vercel env add TWITTER_ACCESS_TOKEN
   vercel env add TWITTER_ACCESS_TOKEN_SECRET
   vercel env add TWITTER_BEARER_TOKEN
   vercel env add SECRET_KEY
   ```

### Method 2: Using Vercel Dashboard

1. Visit [vercel.com](https://vercel.com) and sign in
2. Click "New Project"
3. Import your GitHub repository
4. Configure environment variables in the dashboard
5. Click "Deploy"

## Deploying to Heroku

1. **Install Heroku CLI**
   Download from [heroku.com](https://devcenter.heroku.com/articles/heroku-cli)

2. **Create Procfile**

   ```
   web: gunicorn app:app
   ```

3. **Login to Heroku**

   ```bash
   heroku login
   ```

4. **Create Heroku App**

   ```bash
   heroku create geotrendviz-yourname
   ```

5. **Set Environment Variables**

   ```bash
   heroku config:set TWITTER_API_KEY=your_key
   heroku config:set TWITTER_API_SECRET=your_secret
   heroku config:set TWITTER_ACCESS_TOKEN=your_token
   heroku config:set TWITTER_ACCESS_TOKEN_SECRET=your_token_secret
   heroku config:set TWITTER_BEARER_TOKEN=your_bearer_token
   heroku config:set SECRET_KEY=your_secret_key
   ```

6. **Deploy**
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
- Set up error tracking (e.g., Sentry)

### 3. Custom Domain (Optional)

#### Vercel

```bash
vercel domains add yourdomain.com
```

#### Heroku

```bash
heroku domains:add yourdomain.com
```

### 4. Enable HTTPS

- Vercel: Automatic
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

#### Vercel

```bash
vercel logs
```

#### Heroku

```bash
heroku logs --tail
```

#### Railway

View logs in the Railway dashboard

## Security Best Practices

1. **Never commit .env files**
2. **Use strong secret keys**
3. **Enable 2FA on deployment platforms**
4. **Regularly update dependencies**
5. **Monitor for security vulnerabilities**

## Support

If you encounter issues:

1. Check the [GitHub Issues](https://github.com/BillioncodesInc/GeoTrendViz/issues)
2. Review deployment platform documentation
3. Contact support@billioncodes.com

---

Happy Deploying! 🚀
