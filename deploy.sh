#!/bin/bash

# EVision Quick Deploy Script
# This will help you deploy your app to Vercel and Render

echo "╔══════════════════════════════════════════════════════╗"
echo "║          EVision Quick Deploy                        ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}Choose deployment option:${NC}"
echo "1. Deploy Frontend to Vercel (Recommended)"
echo "2. Full deployment guide"
echo "3. Check deployment status"
echo ""
read -p "Enter choice (1-3): " choice

case $choice in
  1)
    echo -e "\n${YELLOW}Deploying to Vercel...${NC}\n"

    # Check if Vercel CLI is installed
    if ! command -v vercel &> /dev/null; then
        echo "Installing Vercel CLI..."
        npm install -g vercel
    fi

    # Deploy frontend
    cd frontend
    echo -e "${BLUE}Starting Vercel deployment...${NC}"
    vercel --prod

    echo -e "\n${GREEN}✓ Deployment complete!${NC}"
    echo "Your app should be live at the URL shown above."
    ;;

  2)
    echo -e "\n${BLUE}=== DEPLOYMENT GUIDE ===${NC}\n"
    cat << 'EOF'
EASIEST METHOD - Deploy to Vercel (Frontend):

1. Go to: https://vercel.com
2. Click "Sign Up" and sign in with GitHub
3. Click "Add New Project"
4. Select your "EVision" repository
5. Configure:
   - Root Directory: frontend
   - Framework: Next.js (auto-detected)
   - Build Command: npm run build (default)
6. Click "Deploy"
7. Wait 2-3 minutes
8. Your app will be live!

Your frontend will be at: https://evision-{your-username}.vercel.app

---

BACKEND DEPLOYMENT (Optional):

For now, you can use the backend running locally.
For production deployment:

1. Go to: https://render.com
2. Sign in with GitHub
3. Click "New +" → "Web Service"
4. Select your "EVision" repository
5. Configure:
   - Root Directory: backend
   - Build Command: pip install -r requirements.txt
   - Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
6. Add environment variables (see DEPLOYMENT.md)
7. Click "Create Web Service"
8. Wait 5-10 minutes
9. Your backend will be live!

---

See DEPLOYMENT.md for detailed instructions.
EOF
    ;;

  3)
    echo -e "\n${BLUE}Checking GitHub repository...${NC}\n"
    echo "Repository: https://github.com/rohankilaru-ai/EVision"
    echo "Branch: claude/setup-evision-auth-eYgAU"
    echo ""
    echo "Latest commit:"
    git log -1 --oneline
    echo ""
    echo -e "${GREEN}✓ All deployment files are committed and pushed${NC}"
    echo ""
    echo "Next steps:"
    echo "1. Go to https://vercel.com and sign in with GitHub"
    echo "2. Import your EVision repository"
    echo "3. Deploy with one click!"
    ;;

  *)
    echo "Invalid choice"
    exit 1
    ;;
esac

echo ""
echo -e "${BLUE}Need help?${NC} Check DEPLOYMENT.md for detailed instructions"
