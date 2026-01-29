# 🕸️ Social Network Bottleneck Detector

A web application that analyzes social networks to identify critical **bottleneck nodes** — users who act as bridges between communities. Remove them, and information flow breaks.

![Dashboard Preview](docs/dashboard-preview.png)

---

## 🎯 Problem Statement

### The Problem

Imagine Twitter/X as a giant spider web where each person is a node, and "follow" connections are the edges between them.

**Key Question:** If you wanted to spread information across the ENTIRE network, which specific people would you NEED to go through?

These critical people are called **"bottlenecks"** — remove them, and the network fragments into isolated pieces.

### Real-World Applications

| Use Case | Description |
|----------|-------------|
| **Viral Marketing** | Instead of paying 100 random influencers, find the 5 people who connect different communities |
| **Misinformation Control** | Bottleneck users spreading fake news affect multiple communities simultaneously |
| **Network Resilience** | Identify single points of failure before they leave the platform |
| **Community Analysis** | Understand how information flows between different groups |

### What Makes Someone a Bottleneck?

```
Regular User:              Bottleneck User:
   
   A ← B                   Community 1       Community 2
   ↓                           ↓                 ↓
   C                       A ← B ← [X] → D → E → F
                                    ↑
                              This person!
                        Connects BOTH communities
```

**User X** is a bottleneck because:
- Remove X → Communities 1 and 2 can't communicate
- Information MUST flow through X to cross community boundaries
- X has high "betweenness centrality" in graph theory terms

---

## 🧮 The Algorithm

We calculate a **Composite Bottleneck Score** using multiple graph metrics:

```python
bottleneck_score = (0.4 × betweenness_centrality) 
                 + (0.3 × bridge_score) 
                 + (0.3 × pagerank)
```

| Metric | What It Measures |
|--------|------------------|
| **Betweenness Centrality** | How many shortest paths between other users go through you? |
| **Bridge Score** | How many different communities do you connect? |
| **PageRank** | Are your followers also important/influential people? |

### Algorithms Used
- **Betweenness Centrality**: Identifies users on many shortest paths
- **PageRank**: Google's algorithm adapted for social influence
- **Louvain Community Detection**: Groups users into communities
- **Custom Bridge Detection**: Finds cross-community connectors

---

## ✨ Features

- 📊 **Interactive Dashboard** - Real-time network statistics and top bottlenecks
- 🕸️ **Graph Visualization** - Cytoscape.js powered network explorer
- 🔍 **Bottleneck Analysis** - Ranked list of critical nodes with detailed metrics
- 💬 **Natural Language Queries** - Ask questions in plain English powered by GPT-4
- 🎨 **Community Coloring** - Visual distinction between detected communities
- 📈 **Algorithm Execution** - Run PageRank, Louvain, Betweenness on demand

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Frontend** | React 18, TypeScript, Vite, TailwindCSS, Cytoscape.js |
| **Backend** | Python 3.11+, FastAPI, Pydantic, LangChain |
| **Database** | Neo4j Aura (Cloud Graph Database) |
| **AI/NLQ** | OpenAI GPT-4, LangChain Text2Cypher |
| **Caching** | Redis |
| **Deployment** | Vercel (frontend), Railway (backend) |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- Neo4j Aura account (free tier works)
- OpenAI API key

### 1. Clone the repository
```bash
git clone https://github.com/suryamidde/social-network-bottleneck-detector.git
cd social-network-bottleneck-detector
```

### 2. Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your Neo4j and OpenAI credentials
```

### 3. Frontend Setup
```bash
cd frontend
npm install
```

### 4. Import Sample Data
```bash
cd ..
python scripts/import_data.py --sample --uri "your-neo4j-uri" --user "neo4j" --password "your-password"
```

### 5. Run the Application
```bash
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

### 6. Run Graph Algorithms
```bash
# Via API or use the Dashboard buttons
curl -X POST http://localhost:8000/api/v1/algorithms/run/pagerank
curl -X POST http://localhost:8000/api/v1/algorithms/run/louvain
curl -X POST http://localhost:8000/api/v1/algorithms/run/bottleneck
```

Visit `http://localhost:5173` 🎉

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/bottlenecks` | GET | List top bottleneck users |
| `/api/v1/bottlenecks/summary` | GET | Bottleneck statistics |
| `/api/v1/bottlenecks/bridges` | GET | Cross-community bridge users |
| `/api/v1/graph/stats` | GET | Network statistics |
| `/api/v1/graph/subgraph` | GET | Get Cytoscape-formatted subgraph |
| `/api/v1/communities` | GET | List detected communities |
| `/api/v1/nlq/query` | POST | Natural language query |
| `/api/v1/algorithms/run/{name}` | POST | Execute graph algorithm |

### Natural Language Query Examples
```bash
# Ask in plain English
curl -X POST http://localhost:8000/api/v1/nlq/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Who are the top bottlenecks?"}'

# More examples:
# "Show me bridge users"
# "Find the most influential users"
# "Which community is the largest?"
# "Show users connecting multiple communities"
```

---

## 📁 Project Structure

```
social-network-bottleneck-detector/
├── backend/
│   ├── app/
│   │   ├── api/v1/           # API route handlers
│   │   │   ├── algorithms.py
│   │   │   ├── bottlenecks.py
│   │   │   ├── communities.py
│   │   │   ├── graph.py
│   │   │   └── nlq.py
│   │   ├── services/         # Business logic
│   │   │   ├── neo4j_service.py
│   │   │   ├── cache_service.py
│   │   │   └── nlq_service.py
│   │   ├── schemas/          # Pydantic models
│   │   ├── config.py
│   │   └── main.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/       # React components
│   │   │   ├── NetworkGraph.tsx
│   │   │   ├── BottleneckCard.tsx
│   │   │   └── NaturalLanguageInput.tsx
│   │   ├── pages/            # Page components
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Explorer.tsx
│   │   │   ├── Bottlenecks.tsx
│   │   │   └── Query.tsx
│   │   └── services/api.ts
│   ├── package.json
│   └── vite.config.ts
├── scripts/
│   └── import_data.py        # Data import utilities
├── docker-compose.yml
└── README.md
```

---

## 🌐 Deployment

### Frontend (Vercel)
```bash
cd frontend
vercel --prod
```

### Backend (Railway)
```bash
cd backend
railway up
```

### Environment Variables

```env
# Neo4j Aura
NEO4J_URI=neo4j+s://xxxxx.databases.neo4j.io
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
NEO4J_DATABASE=neo4j

# OpenAI (for NLQ)
OPENAI_API_KEY=sk-...

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Frontend
VITE_API_URL=https://your-backend.railway.app
```

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 📊 Sample Results

After running on a network of 100 users with 535 connections:

| Metric | Value |
|--------|-------|
| Users Analyzed | 100 |
| Connections | 535 |
| Communities Detected | 60 |
| Bottlenecks Identified | 100 |
| Avg Bottleneck Score | 1.11 |
| Max Bottleneck Score | 1.51 |

Top bottleneck users connect 10+ different communities and sit on hundreds of shortest paths.

---

## 🎓 What I Learned

- **Graph Theory**: Betweenness centrality, PageRank, community detection
- **Neo4j**: Cypher queries, Graph Data Science algorithms
- **LangChain**: Text2Cypher for natural language database queries
- **React + TypeScript**: Modern frontend development
- **FastAPI**: High-performance Python APIs
- **Cytoscape.js**: Interactive graph visualization

---

## 🔮 Future Improvements

- [ ] Real-time Twitter/X data ingestion
- [ ] Temporal analysis (how bottlenecks change over time)
- [ ] Bottleneck prediction using ML
- [ ] Export reports as PDF
- [ ] Multi-network comparison
- [ ] WebSocket for live updates

---

## 📄 License

MIT License - feel free to use this for your own projects!

---

## 👤 Author

**Surya Midde**
- GitHub: [@suryamidde](https://github.com/suryamidde)
- LinkedIn: [Surya Midde](https://linkedin.com/in/suryamidde)

---

## ⭐ Star This Repo!

If you found this useful, please give it a star! It helps others discover the project.
