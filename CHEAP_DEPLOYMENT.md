# Budget-Friendly Deployment Options for PsychBot

Cost comparison for 24/7 operation with ~4GB RAM needed for Ollama:

| Option | Monthly Cost | Setup Difficulty | Notes |
|--------|--------------|------------------|-------|
| Oracle Cloud Free Tier | **$0** | Medium | 2 VMs free forever, ARM-based |
| DigitalOcean Droplet | **$12-24** | Easy | Simple, reliable |
| AWS EC2 Spot | **$10-15** | Medium | Can be interrupted |
| Fly.io | **$15-20** | Easy | Good for Docker |
| Railway.app | **$5-20** | Very Easy | Pay for usage |
| AWS Lightsail | **$20-40** | Easy | AWS managed, simpler than ECS |
| Render.com | **$7-25** | Very Easy | Free tier + paid |

---

## Option 1: Oracle Cloud Free Tier (RECOMMENDED - FREE!)

Oracle Cloud has a **generous free tier** that includes:
- 4 ARM-based VMs (Ampere A1) with 24GB RAM total
- Or 2 AMD VMs with 1GB RAM each
- 200GB storage
- **FREE FOREVER** (not a trial)

### Setup Steps:

```bash
# 1. Sign up at https://cloud.oracle.com/free
# 2. Create a VM instance (choose ARM for more resources)
# 3. Connect via SSH

# On the VM:
# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone your repo
git clone https://github.com/LEMSingapore/psychbot2.git
cd psychbot2

# Set up environment variables
cat > .env << 'EOF'
SENDGRID_API_KEY=your-key-here
EOF

# Put credentials.json in place
# (Upload via scp or paste content)

# Start services
docker-compose up -d

# Open firewall for port 9000
sudo iptables -I INPUT -p tcp --dport 9000 -j ACCEPT
sudo netfilter-persistent save

# Configure Oracle Cloud security list to allow port 9000
# (Do this in Oracle Cloud Console)
```

**Monthly Cost: $0**

---

## Option 2: DigitalOcean Droplet (EASIEST)

Simple, reliable, and cheap VPS hosting.

### Pricing:
- **Basic Droplet (2GB RAM)**: $12/month
- **Droplet (4GB RAM)**: $24/month (recommended for Ollama)

### Setup Steps:

```bash
# 1. Sign up at https://digitalocean.com
# 2. Create a Droplet (Ubuntu 22.04, 4GB RAM, $24/month)
# 3. SSH into your droplet

# Install Docker (same as Oracle Cloud steps above)
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
newgrp docker

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and setup
git clone https://github.com/LEMSingapore/psychbot2.git
cd psychbot2

# Setup credentials
echo "SENDGRID_API_KEY=your-key" > .env
# Upload credentials.json via scp

# Start
docker-compose up -d

# Configure firewall
sudo ufw allow 9000
sudo ufw enable
```

**Monthly Cost: $24** (or $12 if you can fit in 2GB RAM)

---

## Option 3: AWS EC2 with Spot Instances (AWS but cheaper)

Use Spot Instances for 70-90% discount on EC2.

### Pricing:
- **t3.medium Spot (2 vCPU, 4GB)**: ~$8-12/month
- **t3.large Spot (2 vCPU, 8GB)**: ~$15-20/month

### Setup:

```bash
# 1. Launch Spot Instance from AWS Console
#    - AMI: Ubuntu 22.04
#    - Type: t3.large
#    - Request type: Persistent
#    - Price: Set to max $0.03/hour (~$20/month)

# 2. SSH into instance
ssh -i your-key.pem ubuntu@ec2-instance-ip

# 3. Install Docker and Docker Compose (same as above)

# 4. Clone and run
git clone https://github.com/LEMSingapore/psychbot2.git
cd psychbot2
# Setup .env and credentials.json
docker-compose up -d

# 5. Configure Security Group to allow port 9000
```

**Monthly Cost: $10-20** (risk: can be interrupted if AWS needs capacity)

---

## Option 4: Fly.io (Easy Docker deployment)

Fly.io is designed for Docker and has good pricing.

### Pricing:
- 1 shared CPU, 256MB RAM: Free
- 1 shared CPU, 2GB RAM: ~$10/month
- 2 shared CPU, 4GB RAM: ~$20/month

### Setup:

```bash
# 1. Install flyctl
curl -L https://fly.io/install.sh | sh

# 2. Sign up and login
flyctl auth signup
flyctl auth login

# 3. Create fly.toml in your project
cat > fly.toml << 'EOF'
app = "psychbot"

[build]
  dockerfile = "Dockerfile"

[env]
  OLLAMA_BASE_URL = "http://localhost:11434"

[[services]]
  internal_port = 9000
  protocol = "tcp"

  [[services.ports]]
    handlers = ["http"]
    port = 80

  [[services.ports]]
    handlers = ["tls", "http"]
    port = 443

[mounts]
  source = "psychbot_data"
  destination = "/app/docs"
EOF

# 4. Create secrets
flyctl secrets set SENDGRID_API_KEY=your-key
flyctl secrets set GOOGLE_CREDENTIALS_JSON="$(cat credentials.json)"

# 5. Deploy
flyctl launch
flyctl deploy
```

**Note:** Running Ollama on Fly.io can be tricky due to resource limits. Consider using 4GB+ RAM.

**Monthly Cost: $15-25**

---

## Option 5: Railway.app (Simplest, Pay as you go)

Railway has a simple interface and GitHub integration.

### Pricing:
- $5 starter credit/month
- Additional usage: ~$0.02/hour for 2GB RAM container

### Setup:

```bash
# 1. Go to https://railway.app
# 2. Connect your GitHub repo
# 3. Add environment variables in Railway dashboard:
#    - SENDGRID_API_KEY
#    - GOOGLE_CREDENTIALS_JSON (paste full JSON)
#    - OLLAMA_BASE_URL=http://ollama:11434

# 4. Create two services:
#    Service 1: Ollama (use ollama/ollama:latest image)
#    Service 2: PsychBot (use your Dockerfile)

# 5. Railway auto-deploys from your repo
```

**Monthly Cost: $5-20** depending on usage

---

## Option 6: Switch to Cloud LLM (Remove Ollama Completely)

The cheapest option might be to **remove Ollama** and use a cloud LLM API:

### Options:
- **OpenAI API**: ~$0.002 per 1K tokens (GPT-3.5 Turbo)
- **AWS Bedrock**: ~$0.0008-0.003 per 1K tokens (Claude Haiku)
- **Groq**: FREE tier, very fast inference

With low traffic (1000 queries/month, ~100 tokens each), this could cost **$0.20-2/month** for the LLM alone.

Then you can deploy PsychBot alone on:
- **Render.com Free Tier**: $0
- **Fly.io Free Tier**: $0
- **Railway.app**: $5/month
- **DigitalOcean App Platform**: $5/month

### To switch to OpenAI:

```bash
# 1. Update requirements.txt
echo "openai>=1.0.0" >> requirements.txt

# 2. Update src/rag_chain.py
# Replace the Ollama import and get_llm() function with:
```

```python
from langchain_openai import ChatOpenAI
import os

@lru_cache(maxsize=1)
def get_llm():
    """Cached LLM - OpenAI instead of Ollama"""
    return ChatOpenAI(
        model="gpt-3.5-turbo",
        temperature=0.1,
        max_tokens=80,
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
```

**Total Monthly Cost with Cloud LLM: $0-10** (depending on platform)

---

## My Recommendation

For your use case, I recommend **one of these**:

### 🥇 Best Free Option: Oracle Cloud Free Tier
- **Cost: $0/month**
- Reliable, generous resources
- Requires some setup but well-documented

### 🥈 Best Paid Option: DigitalOcean Droplet
- **Cost: $24/month** (or $12 for 2GB)
- Very simple, reliable
- Great documentation and support

### 🥉 Best Budget Option: Switch to Cloud LLM + Render.com
- **Cost: $0-7/month**
- Remove Ollama dependency
- Use OpenAI/Groq for LLM
- Deploy PsychBot on Render free tier

---

## Quick Cost Reduction Summary

Your current plan costs: **$80-100/month**

Cheaper alternatives:
1. Oracle Cloud Free Tier: **$0** ⚡
2. DigitalOcean Droplet: **$12-24**
3. EC2 Spot Instance: **$10-20**
4. Switch to OpenAI + Render: **$0-7** ⚡

Would you like me to help you set up any of these cheaper options?
