# Deployment Guide - Social Network Bottleneck Detector

## 🚀 Quick Deploy

### Backend (Railway)

1. **Login to Railway:**
   ```bash
   railway login
   ```
   This opens a browser for authentication.

2. **Create a new project:**
   ```bash
   cd backend
   railway init
   ```
   Select "Empty Project" when prompted.

3. **Set environment variables:**
   ```bash
   railway variables set NEO4J_URI="neo4j+s://adb1a905.databases.neo4j.io"
   railway variables set NEO4J_USER="neo4j"
   railway variables set NEO4J_PASSWORD="WiyeDT9DsU3k7tdKTKJePuoXGN9Qs5M9ok31qsPBo94"
   railway variables set OPENAI_API_KEY="your-openai-key"  # Optional for NLQ
   ```

4. **Deploy:**
   ```bash
   railway up
   ```

5. **Get your backend URL:**
   ```bash
   railway domain
   ```
   Copy this URL (e.g., `https://your-app.railway.app`)

### Frontend (Vercel) - Update API URL

1. **Update vercel.json:**
   Replace `https://your-backend.railway.app` with your actual Railway URL:
   ```json
   {
     "rewrites": [
       {
         "source": "/api/:path*",
         "destination": "https://YOUR-RAILWAY-URL/api/:path*"
       }
     ]
   }
   ```

2. **Redeploy:**
   ```bash
   cd frontend
   vercel --prod
   ```

## 📊 Current Status

- **Frontend:** https://frontend-sigma-eight-20.vercel.app ✅
- **Backend:** Needs Railway deployment
- **Database:** Neo4j Aura ✅ (2,761 users, 50K edges, 105 communities)

## 🔧 Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
set NEO4J_URI=neo4j+s://adb1a905.databases.neo4j.io
set NEO4J_USER=neo4j
set NEO4J_PASSWORD=WiyeDT9DsU3k7tdKTKJePuoXGN9Qs5M9ok31qsPBo94
uvicorn app.main:app --reload --port 8000

# Frontend (separate terminal)
cd frontend
npm install
npm run dev
```

## 🧪 API Endpoints

| Endpoint | Description |
|----------|-------------|
| GET /api/v1/graph/stats | Network statistics |
| GET /api/v1/bottlenecks | List bottleneck nodes |
| GET /api/v1/graph/subgraph | Get graph for visualization |
| POST /api/v1/algorithms/run/{name} | Run PageRank, Betweenness, etc. |
| POST /api/v1/nlq/query | Natural language queries |
