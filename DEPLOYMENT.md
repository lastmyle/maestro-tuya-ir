# Deployment Guide

This guide covers deploying the Maestro Tuya IR Bridge.

## Vercel Deployment (Recommended)

Vercel provides serverless deployment with zero configuration.

### Prerequisites

- [Vercel account](https://vercel.com/signup)
- [Vercel CLI](https://vercel.com/docs/cli) (optional, for CLI deployment)
- Git repository (GitHub, GitLab, or Bitbucket)

### Method 1: Deploy via Vercel Dashboard (Easiest)

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Import to Vercel**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Click "Import Project"
   - Select your repository
   - Vercel will auto-detect the FastAPI application

3. **Configure (if needed)**
   - Framework Preset: **Other**
   - Build Command: (leave empty)
   - Output Directory: (leave empty)
   - Install Command: `pip install -r requirements.txt`

4. **Deploy**
   - Click "Deploy"
   - Wait for deployment to complete
   - Your API will be live at `https://your-project.vercel.app`

### Method 2: Deploy via Vercel CLI

```bash
# Install Vercel CLI
npm i -g vercel

# Login to Vercel
vercel login

# Deploy to preview
vercel

# Deploy to production
vercel --prod
```

### Testing Your Deployment

Once deployed, test your endpoints:

```bash
# Health check
curl https://your-project.vercel.app/api/health

# Encode command
curl -X POST https://your-project.vercel.app/api/encode \
  -H "Content-Type: application/json" \
  -d '{
    "manufacturer": "Fujitsu",
    "protocol": "fujitsu_ac",
    "command": {
      "power": "on",
      "mode": "cool",
      "temperature": 24,
      "fan": "auto",
      "swing": "off"
    }
  }'
```

### Vercel Configuration Files

The project includes these Vercel-specific files:

- **vercel.json**: Deployment configuration
- **requirements.txt**: Python dependencies (production only)
- **.vercelignore**: Files to exclude from deployment
- **.python-version**: Specifies Python 3.14

### Important Notes

- **Function Timeout**: Free tier has 10s timeout, Pro has 60s
- **Bundle Size**: Must be under 250MB
- **Cold Starts**: First request after inactivity may be slower
- **Environment Variables**: Set in Vercel dashboard if needed

### Limitations on Vercel

- Maximum function duration: 10s (Hobby), 60s (Pro)
- No persistent file storage
- Runs as serverless functions (not long-running processes)

---

## Traditional Server Deployment

### Using uv (Recommended)

```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# Clone repository
git clone <your-repo>
cd maestro-tuya-ir

# Install dependencies
uv sync

# Run with multiple workers
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Systemd Service Example

Create `/etc/systemd/system/maestro-tuya-ir.service`:

```ini
[Unit]
Description=Maestro Tuya IR Bridge
After=network.target

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/maestro-tuya-ir
ExecStart=/root/.cargo/bin/uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable maestro-tuya-ir
sudo systemctl start maestro-tuya-ir
sudo systemctl status maestro-tuya-ir
```

### Nginx Reverse Proxy

Create `/etc/nginx/sites-available/maestro-tuya-ir`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Enable and reload:
```bash
sudo ln -s /etc/nginx/sites-available/maestro-tuya-ir /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

## Cloud Platforms (Serverless)

### AWS Lambda

Use [Mangum](https://mangum.io/) to wrap FastAPI for Lambda:

1. Install Mangum:
   ```bash
   uv add mangum
   ```

2. Update `main.py`:
   ```python
   from mangum import Mangum

   # At the end of main.py
   handler = Mangum(app)
   ```

3. Deploy using AWS SAM, Serverless Framework, or Zappa

### Google Cloud Run

```bash
# Deploy directly from source (no Docker needed)
gcloud run deploy maestro-tuya-ir \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8000
```

### Azure Functions

Use [Azure Functions for Python](https://docs.microsoft.com/en-us/azure/azure-functions/functions-reference-python):

1. Install Azure Functions Core Tools
2. Create function app
3. Deploy using Azure CLI

---

## Environment Variables

No environment variables are required for basic operation. Optional:

```bash
# CORS configuration
ALLOWED_ORIGINS=https://yourdomain.com,https://app.yourdomain.com

# Rate limiting (if implemented)
RATE_LIMIT_PER_MINUTE=100

# Redis caching (if implemented)
REDIS_URL=redis://localhost:6379
```

Set environment variables in Vercel:
1. Go to Project Settings → Environment Variables
2. Add key-value pairs
3. Redeploy for changes to take effect

---

## Monitoring and Logs

### Vercel
- View logs in Vercel Dashboard → Your Project → Logs
- Real-time logs: `vercel logs <deployment-url>`
- Enable [Vercel Analytics](https://vercel.com/analytics)

### Server
```bash
# View systemd logs
sudo journalctl -u maestro-tuya-ir -f

# View last 100 lines
sudo journalctl -u maestro-tuya-ir -n 100
```

---

## Performance Optimization

1. **Enable HTTP/2**: Supported automatically on Vercel
2. **Caching**: Implement Redis for frequently generated codes
3. **CDN**: Use Vercel's CDN for static assets
4. **Compression**: Enable gzip/brotli (automatic on Vercel)

---

## Security Considerations

1. **CORS**: Configure `ALLOWED_ORIGINS` properly
2. **Rate Limiting**: Implement rate limiting for production
3. **API Keys**: Add authentication if needed
4. **HTTPS**: Always use HTTPS (automatic on Vercel)

---

## Rollback

### Vercel
- Go to Deployments in Vercel Dashboard
- Click on a previous deployment
- Click "Promote to Production"

### Server
```bash
# Rollback using git
cd /opt/maestro-tuya-ir
git checkout <previous-commit>
uv sync
sudo systemctl restart maestro-tuya-ir
```

---

## Troubleshooting

### Vercel: "No Python Version Specified"
- Ensure `.python-version` file exists with `3.14`

### Vercel: "Module not found"
- Ensure all dependencies are in `requirements.txt`
- Check import paths are correct
- Verify Python version compatibility

### Vercel: "Function timeout"
- Upgrade to Pro plan for 60s timeout
- Optimize slow operations
- Consider caching for expensive computations

### Server: "Port already in use"
```bash
# Find and stop the process
sudo lsof -i :8000
sudo kill -9 <PID>
```

### Server: "Permission denied"
```bash
# Fix file permissions
sudo chown -R www-data:www-data /opt/maestro-tuya-ir
sudo chmod -R 755 /opt/maestro-tuya-ir
```

---

## Support

For deployment issues:
- Vercel: [Vercel Support](https://vercel.com/support)
- General: [GitHub Issues](https://github.com/yourusername/maestro-tuya-ir-bridge/issues)
