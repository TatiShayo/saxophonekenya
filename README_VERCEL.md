# Deploying Frederic Sax Ke to Vercel (Instant 1-Click / CLI)

This package contains everything configured for **Vercel** (`vercel.json`, `index.html`, `rate-card.html`, assets, and media).

---

## Method 1: Instant Deployment via Vercel CLI (Recommended)

1. Open PowerShell or Terminal in this folder:
   ```bash
   cd "C:\Users\TATI\Desktop\Clients\October\Fred\Website Antigravity\SAX\SAX"
   ```
2. Run the Vercel login command:
   ```bash
   vercel login
   ```
   *(Select your email or GitHub to authenticate)*
3. Run the deploy command:
   ```bash
   vercel --prod
   ```
4. Follow the 3 prompts:
   - *Set up and deploy?* **Y**
   - *Which scope?* (Select your Vercel account)
   - *Link to existing project?* **N**
   - *What's your project's name?* **frederic-sax-ke** (or press Enter)
   - *In which directory is your code located?* **./** (press Enter)
   - *Want to modify settings?* **N** (press Enter)

Within 30 seconds, Vercel will output your live URL:
```
✅ Production: https://frederic-sax-ke.vercel.app
```

---

## Method 2: Deploy via Vercel Web Dashboard (Drag & Drop or GitHub)

1. Log in to [vercel.com](https://vercel.com).
2. Click **Add New...** -> **Project**.
3. **If connecting GitHub**: Push this repository to GitHub and click **Import**.
4. **If uploading directly**:
   - Install Vercel CLI (`npm i -g vercel`), run `vercel login`, and type `vercel --prod`.
5. Your custom domain (e.g. `fredericsax.com` or `fredericsax.co.ke`) can be added under **Project Settings -> Domains** with automatic free SSL!
