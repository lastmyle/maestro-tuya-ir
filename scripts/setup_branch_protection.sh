#!/bin/bash
# Setup branch protection for main branch using GitHub CLI
# Run this once to configure branch protection rules

set -e

echo "🔒 Setting up branch protection for main branch..."

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI (gh) is not installed"
    echo "Install it with: brew install gh"
    exit 1
fi

# Check if authenticated
if ! gh auth status &> /dev/null; then
    echo "❌ Not authenticated with GitHub"
    echo "Run: gh auth login"
    exit 1
fi

# Get repository info
REPO=$(gh repo view --json nameWithOwner -q .nameWithOwner)
echo "📦 Repository: $REPO"

# Set up branch protection using GitHub API
echo "⚙️  Configuring branch protection rules..."

gh api \
  --method PUT \
  -H "Accept: application/vnd.github+json" \
  -H "X-GitHub-Api-Version: 2022-11-28" \
  "/repos/$REPO/branches/main/protection" \
  -f required_status_checks[strict]=true \
  -f required_status_checks[contexts][]=test \
  -f required_status_checks[contexts][]=lint \
  -f required_status_checks[contexts][]='Vercel – maestro-tuya-ir' \
  -f enforce_admins=false \
  -f required_pull_request_reviews[dismiss_stale_reviews]=true \
  -f required_pull_request_reviews[require_code_owner_reviews]=false \
  -f required_pull_request_reviews[required_approving_review_count]=0 \
  -f required_pull_request_reviews[require_last_push_approval]=false \
  -f restrictions=null \
  -f required_linear_history=false \
  -f allow_force_pushes=false \
  -f allow_deletions=false \
  -f block_creations=false \
  -f required_conversation_resolution=false \
  -f lock_branch=false \
  -f allow_fork_syncing=false

echo ""
echo "✅ Branch protection configured successfully!"
echo ""
echo "📋 Configuration:"
echo "   - Required status checks: test, lint, Vercel"
echo "   - Strict status checks: enabled (must be up to date)"
echo "   - Require PR reviews: disabled (solo dev)"
echo "   - Admins can bypass: yes"
echo "   - Force push: disabled"
echo "   - Delete branch: disabled"
echo ""
echo "🔍 View settings: https://github.com/$REPO/settings/branches"
