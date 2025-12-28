# Migration to OpenAI + Render.com

## What Changed?

We switched from **Ollama (self-hosted LLM)** to **OpenAI API** to enable cheaper cloud deployment.

### Files Modified

1. **requirements.txt**
   - Added: `langchain-openai>=0.0.5`

2. **src/rag_chain.py**
   - Changed: `Ollama` → `ChatOpenAI` (uses OpenAI API)
   - Model: `llama3:8b` → `gpt-3.5-turbo`
   - Added: `OPENAI_API_KEY` environment variable requirement

3. **src/calendar_utils.py**
   - Added: Support for `GOOGLE_CREDENTIALS_JSON` environment variable
   - Now works with both file and env var credentials

### Files Created

1. **Dockerfile.render** - Simplified Docker image (no Ollama)
2. **render.yaml** - One-click deployment config for Render.com
3. **RENDER_DEPLOYMENT.md** - Complete deployment guide
4. **.env.example** - Environment variable template

---

## Before You Deploy

### 1. Test Locally First

```bash
# Install new dependencies
pip install -r requirements.txt

# Create .env file with your OpenAI key
cat > .env << 'EOF'
OPENAI_API_KEY=sk-your-key-here
SENDGRID_API_KEY=SG.your-key-here
EOF

# Make sure credentials.json is in project root

# Run document ingestion
python src/ingest.py

# Start the server
python main.py

# Test in another terminal
curl http://localhost:9000/docs
curl -X POST http://localhost:9000/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What services do you offer?"}'
```

### 2. Get API Keys

- **OpenAI**: https://platform.openai.com/api-keys
- **SendGrid**: https://app.sendgrid.com/settings/api_keys

### 3. Push to GitHub

```bash
git add .
git commit -m "Migrate to OpenAI for cloud deployment"
git push origin main
```

### 4. Deploy to Render

Follow **RENDER_DEPLOYMENT.md** for step-by-step instructions.

---

## Cost Comparison

| Deployment | Monthly Cost | Setup Difficulty |
|------------|--------------|------------------|
| **OLD: AWS ECS + Ollama** | $80-100 | Hard |
| **NEW: Render + OpenAI** | **$7-30** | Easy |

**Savings: $50-70/month!**

---

## What Didn't Change?

Everything else stays the same:
- ✅ FastAPI backend
- ✅ LangChain RAG system
- ✅ ChromaDB vector database
- ✅ Google Calendar integration
- ✅ SendGrid email
- ✅ Booking service
- ✅ Content filtering
- ✅ Quick responses (cached answers)

The user experience is **identical** - just cheaper to run!

---

## Rollback Plan

If you need to go back to Ollama:

```bash
# Restore old rag_chain.py
git checkout HEAD~1 -- src/rag_chain.py

# Remove langchain-openai from requirements.txt
# Use docker-compose.yml to run with Ollama again
```

---

## Performance Comparison

### Ollama (Local)
- ✅ Free inference
- ✅ Data stays private
- ❌ Needs 4GB+ RAM
- ❌ Expensive hosting
- ⏱️ Response time: 1-3s

### OpenAI API (Cloud)
- ✅ Super cheap ($0.002/query)
- ✅ Minimal RAM needed
- ✅ Very fast inference
- ✅ Cheap hosting
- ❌ Data goes to OpenAI
- ⏱️ Response time: 0.5-1.5s

---

## Next Steps

1. ✅ Test locally with OpenAI
2. ✅ Push to GitHub
3. ✅ Deploy to Render.com
4. 🔄 Monitor costs in OpenAI dashboard
5. 🔄 Set up UptimeRobot to keep app awake

See **RENDER_DEPLOYMENT.md** for complete deployment instructions!
