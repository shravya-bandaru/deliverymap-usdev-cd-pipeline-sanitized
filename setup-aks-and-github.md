# AKS Cluster Setup and GitHub Actions Configuration (Azure Portal Guide)

## Prerequisites
- Azure Portal access (https://portal.azure.com)
- Owner/Contributor access to Azure subscription
- Access to your GitHub repository settings

## Step 1: Login to Azure Portal

1. Go to https://portal.azure.com
2. Sign in with your Azure credentials
3. Note your **Subscription ID** and **Tenant ID**:
   - Click on **Subscriptions** in the left menu
   - Find your subscription and click on it
   - Copy the **Subscription ID** (save this for later)
   - The **Tenant ID** is shown on the Overview page

## Step 2: Create Resource Group

1. In Azure Portal, search for **Resource groups** in the top search bar
2. Click **+ Create**
3. Fill in:
   - **Subscription**: Select your subscription
   - **Resource group**: `concourse-rg-usdev`
   - **Region**: `East US` (or your preferred region)
4. Click **Review + create**
5. Click **Create**



**Save these values:**
- Resource Group Name: `concourse-rg-usdev`
- Region: `East US` (or whatever you chose)

## Step 3: Create AKS Cluster (takes 10-15 minutes)

1. Search for **Kubernetes services** in the top search bar
2. Click **+ Create** → **Create a Kubernetes cluster**

### Basics Tab:
- **Subscription**: Select your subscription
- **Resource group**: `concourse-rg-usdev` (the one you just created)
- **Cluster preset configuration**: `Dev/Test`
- **Kubernetes cluster name**: `concourse-aks-usdev`
- **Region**: Same as your resource group
- **Availability zones**: None (for dev)
- **AKS pricing tier**: `Free`
- **Kubernetes version**: Default (latest stable)
- **Automatic upgrade**: `Disabled`
- **Node size**: Click **Choose a size** → Select `D2s_v3` (2 vCPUs, 8GB RAM)
- **Scale method**: `Manual`
- **Node count**: `2`

### Node pools Tab:
- Leave default settings

### Access Tab:
- **Authentication and Authorization**: `Local accounts with Kubernetes RBAC`
- Leave other defaults

### Networking Tab:
- **Network configuration**: `Azure CNI`
- Leave other defaults

### Integrations Tab:
- **Container monitoring**: `Enabled` (recommended)
- **Azure Policy**: `Disabled` (for dev)

### Advanced Tab:
- Leave defaults

### Tags Tab:
- (Optional) Add tags like `Environment: Development`

### Review + Create:
- Click **Review + create**
- Click **Create**

⏰ **Wait 10-15 minutes** for the cluster to be created. You'll see "Deployment is in progress"

**Save these values:**
- AKS Cluster Name: `concourse-aks-usdev`
- Resource Group: `concourse-rg-usdev`

## Step 4: Create Kubernetes Namespace

1. Once AKS cluster is created, go to your cluster `concourse-aks-usdev`
2. Click **Connect** at the top
3. You'll see Azure Cloud Shell commands. Click **Open Cloud Shell** 
4. In Cloud Shell, run these commands:

```bash
# Get credentials
az aks get-credentials --resource-group concourse-rg-usdev --name concourse-aks-usdev

# Create namespace
kubectl create namespace co-mesh-test

# Verify
kubectl get namespaces
```

You should see `co-mesh-test` in the list.

## Step 5: Create Azure Key Vault

1. Search for **Key vaults** in the top search bar
2. Click **+ Create**
3. Fill in:
   - **Subscription**: Your subscription
   - **Resource group**: `concourse-rg-usdev`
   - **Key vault name**: `concourse-kv-usdev` (must be globally unique - if taken, try `concourse-kv-usdev-123`)
   - **Region**: Same as your resource group
   - **Pricing tier**: `Standard`
4. Click **Next: Access policy**
5. Keep defaults (Vault access policy)
6. Click **Review + create**
7. Click **Create**

**Save this value:**
- Key Vault Name: `concourse-kv-usdev` (or whatever you used)

## Step 6: Create App Registration (Service Principal)

1. Search for **Azure Active Directory** (or **Microsoft Entra ID**) in the top search bar
2. Click **App registrations** in the left menu
3. Click **+ New registration**
4. Fill in:
   - **Name**: `github-actions-concourse-deployment`
   - **Supported account types**: `Accounts in this organizational directory only`
   - **Redirect URI**: Leave blank
5. Click **Register**

**After creation:**

### Get Application (Client) ID:
- You'll see the **Application (client) ID** on the Overview page
- **Save this as AZURE_CLIENT_ID**

### Create Client Secret:
1. Click **Certificates & secrets** in the left menu
2. Click **+ New client secret**
3. Description: `GitHub Actions Secret`
4. Expires: `24 months` (or your preference)
5. Click **Add**
6. **IMMEDIATELY COPY** the secret **Value** (you won't see it again!)
7. **Save this value** (you'll need it later, but NOT for the workflow - see note below)

**Note:** Your workflow uses OpenID Connect (OIDC), so you actually don't need the client secret for the workflow itself, but save it anyway for other Azure CLI operations.

**Saved values so far:**
- AZURE_CLIENT_ID: (the Application/Client ID)
- Client Secret: (saved for reference)

## Step 7: Grant Permissions to Service Principal

### A. Grant Contributor Role to Resource Group

1. Go back to **Resource groups** → `concourse-rg-usdev`
2. Click **Access control (IAM)** in the left menu
3. Click **+ Add** → **Add role assignment**
4. **Role** tab: Select `Contributor` → Click **Next**
5. **Members** tab:
   - Click **+ Select members**
   - Search for `github-actions-concourse-deployment`
   - Select it → Click **Select**
   - Click **Next**
6. **Review + assign** → Click **Review + assign**

### B. Grant AKS Cluster User Role

1. Go to your AKS cluster `concourse-aks-usdev`
2. Click **Access control (IAM)**
3. Click **+ Add** → **Add role assignment**
4. **Role** tab: Search for `Azure Kubernetes Service Cluster User Role` → Select it → **Next**
5. **Members** tab:
   - Click **+ Select members**
   - Search for `github-actions-concourse-deployment`
   - Select it → **Select**
   - Click **Next**
6. **Review + assign**

### C. Grant Key Vault Permissions

1. Go to your Key Vault `concourse-kv-usdev`
2. Click **Access control (IAM)**
3. Click **+ Add** → **Add role assignment**
4. **Role** tab: Select `Key Vault Secrets Officer` → **Next**
5. **Members** tab:
   - Click **+ Select members**
   - Search for `github-actions-concourse-deployment`
   - Select it → **Select**
   - Click **Next**
6. **Review + assign**

## Step 8: Add Sample Secrets to Key Vault

1. Go to your Key Vault `concourse-kv-usdev`
2. Click **Secrets** in the left menu under Objects
3. Click **+ Generate/Import**
4. Add a test secret:
   - **Upload options**: `Manual`
   - **Name**: `TestSecret`
   - **Value**: `test-value-123`
   - Click **Create**

**Note:** Later, you'll need to add your actual application secrets here based on what your deployment manifests require.

## Step 9: Get All Required Values

Before moving to GitHub, gather all these values from Azure Portal:

| Value Needed | Where to Find It |
|-------------|------------------|
| **AZURE_TENANT_ID** | Subscriptions → Your Subscription → Tenant ID |
| **AZURE_SUBSCRIPTION_ID** | Subscriptions → Your Subscription ID |
| **AZURE_CLIENT_ID** | Azure AD → App registrations → github-actions-concourse-deployment → Application (client) ID |
| **AKS_CLUSTER_NAME** | `concourse-aks-usdev` (what you named it) |
| **AKS_RESOURCE_GROUP** | `concourse-rg-usdev` (what you named it) |
| **AZ_KEY_VAULT** | `concourse-kv-usdev` (or your Key Vault name) |

**Write these down or keep the Azure Portal tabs open!**

## Step 10: Create GitHub Personal Access Tokens

You need 2 GitHub Personal Access Tokens for accessing other repositories.

1. Go to **GitHub.com** → Click your profile picture → **Settings**
2. Scroll to bottom → **Developer settings**
3. **Personal access tokens** → **Tokens (classic)**
4. Click **Generate new token** → **Generate new token (classic)**
5. Fill in:
   - **Note**: `GitHub Actions - Concourse Repos`
   - **Expiration**: `90 days` (or No expiration for CI/CD)
   - **Select scopes**: Check **`repo`** (Full control of private repositories)
6. Click **Generate token**
7. **COPY THE TOKEN IMMEDIATELY** (you won't see it again!)
8. **Save this token** - you'll use it for both:
   - TECH_ENABLEMENT_PAT
   - ADMIN_REPO_PAT

## Step 11: Configure GitHub Repository Secrets

1. Go to your GitHub repository: `https://github.com/YOUR_USERNAME/YOUR_REPO`
2. Click **Settings** tab
3. In left sidebar, click **Secrets and variables** → **Actions**
4. Click **New repository secret** button

### Add Each Secret:

**Click "New repository secret" for each of these:**

| Name | Value | From Where |
|------|-------|------------|
| `AZURE_CLIENT_ID` | Your Application (client) ID | Azure AD App Registration |
| `AZURE_TENANT_ID` | Your Tenant ID | Azure Subscription page |
| `AZURE_SUBSCRIPTION_ID` | Your Subscription ID | Azure Subscription page |
| `AKS_CLUSTER_NAME` | `concourse-aks-usdev` | What you named your cluster |
| `AKS_RESOURCE_GROUP` | `concourse-rg-usdev` | What you named your resource group |
| `AZ_KEY_VAULT` | `concourse-kv-usdev` | Your Key Vault name |
| `TECH_ENABLEMENT_PAT` | Your GitHub token | From Step 10 |
| `ADMIN_REPO_PAT` | Same GitHub token | From Step 10 |
| `WAYDEV_API_HOST` | (Optional) Leave empty for now | If you have WayDev |
| `WAYDEV_API_KEY` | (Optional) Leave empty for now | If you have WayDev |

After adding all secrets, you should see 10 secrets listed (or 8 if you skip WayDev ones).

## Step 12: Create GitHub Environment (Optional but Recommended)

For environment-specific secrets:

1. In your GitHub repo, go to **Settings**
2. Click **Environments** in the left sidebar
3. Click **New environment**
4. Name: `us-dev`
5. Click **Configure environment**
6. (Optional) Add protection rules
7. Under **Environment secrets**, add the same secrets as Step 11

**Repeat for other environments if needed:**
- `us-qa`
- `us-prod`
- etc.

**Benefit:** Environment-specific values override repository-level secrets, allowing different credentials per environment.

## Step 13: Verify Everything

### Check Azure Resources:

1. **Resource Group**: Go to `concourse-rg-usdev` - should see AKS cluster and Key Vault
2. **AKS Cluster**: Go to `concourse-aks-usdev` → Overview → Status should be "Succeeded"
3. **Key Vault**: Go to `concourse-kv-usdev` → Should see your test secret
4. **App Registration**: Azure AD → App registrations → Should see `github-actions-concourse-deployment`

### Check GitHub:

1. Go to repo **Settings** → **Secrets and variables** → **Actions**
2. Should see all 8-10 secrets listed (values hidden)
3. Go to **Actions** tab → Should see your workflow "Deploy Concourse Microservices"

## Step 14: Test the Workflow

1. In GitHub, go to **Actions** tab
2. Click **Deploy Concourse Microservices**
3. Click **Run workflow** button
4. Select:
   - Branch: `main`
   - ENVIRONMENT: `us-dev`
   - Leave other inputs as defaults
5. Click **Run workflow**

The workflow should start! Monitor the progress. First run may take longer.

## Cost Estimation

**Monthly costs (approximate, may vary by region):**
- AKS cluster (2 Standard_D2s_v3 nodes): ~$140-160/month
- Azure Key Vault: ~$0.03/10,000 operations
- Storage/Networking: ~$10-20/month
- **Total: ~$150-180/month**

**To reduce costs:**
- Use fewer/smaller nodes
- Enable cluster autoscaler
- Stop cluster when not in use (dev environments)

## Cleanup (Delete Everything if Needed)

If you want to delete everything to avoid costs:

1. Go to **Resource groups** in Azure Portal
2. Find `concourse-rg-usdev`
3. Click on it
4. Click **Delete resource group** at the top
5. Type the resource group name to confirm
6. Click **Delete**

This will delete:
- AKS cluster
- Key Vault  
- All associated resources

Then delete the App Registration:
1. Azure AD → **App registrations**
2. Find `github-actions-concourse-deployment`
3. Click it → **Delete**

## Next Steps After Setup

1. ✅ **Run your first deployment** from GitHub Actions
2. Add your actual application secrets to Key Vault
3. Update `services.json` with correct build IDs
4. Set up additional environments (us-qa, us-prod)
5. Configure monitoring and alerts

## Troubleshooting Common Issues

### "Cluster creation failed"
- Check if you have enough quota in your subscription
- Try a different region
- Use smaller VM size (B2s for testing)

### "Permission denied" errors in workflow
- Verify all role assignments in Step 7
- Wait 5-10 minutes for permissions to propagate
- Check that service principal has Contributor role

### "Cannot access private repository"
- Verify GitHub PAT has `repo` scope
- Check token hasn't expired
- Make sure you used the token for both TECH_ENABLEMENT_PAT and ADMIN_REPO_PAT

### "Key Vault access denied"
- Ensure service principal has "Key Vault Secrets Officer" role
- Check Key Vault access policy settings
- Verify Key Vault name in GitHub secrets matches exactly

### Workflow doesn't appear
- Ensure `services.json` is committed and pushed
- Check `.github/workflows/deploy.yml` is at repository root
- Refresh the Actions tab

## Quick Reference - Values Checklist

Print or save this checklist:

- [ ] AZURE_TENANT_ID: __________________
- [ ] AZURE_SUBSCRIPTION_ID: __________________  
- [ ] AZURE_CLIENT_ID: __________________
- [ ] AKS_CLUSTER_NAME: `concourse-aks-usdev`
- [ ] AKS_RESOURCE_GROUP: `concourse-rg-usdev`
- [ ] AZ_KEY_VAULT: __________________
- [ ] GitHub PAT (for both PAT secrets): __________________
- [ ] All secrets added to GitHub repository ✓
- [ ] AKS cluster running ✓
- [ ] Namespace `co-mesh-test` created ✓



need no azure credentials not service principal