# SRE Kubernetes CLI Tool

![Python](https://img.shields.io/badge/python-3.8%2B-blue)

An advanced Site Reliability Engineer (SRE) CLI tool to interact with Kubernetes clusters. This tool provides enhanced logging and functionality to list, scale, monitor, and troubleshoot deployments with ease.

---

## 📖 Table of Contents
- [Features](#features)
- [Setup Instructions](#setup-instructions)
- [Usage](#usage)
- [Autocomplete Setup](#autocomplete-setup)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## ✨ Features
- **Deployment Management:** List, scale, and get detailed information about Kubernetes deployments.
- **Rollout Management:** Restart and monitor deployment rollouts.
- **Diagnostic Checks:** Run health diagnostics on deployments and their pods.
- **Logs:** Retrieve logs from pods or entire deployments.
- **Interactive Mode:** Prompt for missing arguments when run interactively.
- **Enhanced Logging:** Operations and errors are logged to `sre.log`.

---

## 🚀 Setup Instructions

### 1. Prerequisites
- **Python 3.8+**
- **Kubernetes Cluster:** A configured Kubernetes environment.
- **Kubernetes CLI Tools:** [kubectl](https://kubernetes.io/docs/tasks/tools/) installed and kubeconfig configured.

### 2. Install Required Packages
Install the required Python dependencies:

```bash
pip install -r requirements.txt
```

**Sample `requirements.txt`**
```
kubernetes
argcomplete
```

### 3. Clone the Repository
```bash
git clone https://github.com/yourusername/sre-cli-tool.git
cd sre-cli-tool
```

### 4. Ensure Your Kubernetes Context is Set
Make sure you can access your Kubernetes cluster using:

```bash
kubectl get nodes
```

---

## 💻 Usage

### Basic Commands
Run the CLI tool using:

```bash
python3 sre.py [command] [options]
```

### Commands Overview
| Command    | Description |
|------------|-------------|
| `list`     | List deployments in a cluster. |
| `scale`    | Scale a deployment to a desired number of replicas. |
| `info`     | Get detailed information about a deployment. |
| `diagnostic` | Run diagnostics on deployments and their pods. |
| `rollout`  | Restart or monitor deployment rollouts. |
| `logs`     | Fetch logs for a deployment or pod. |

### Examples
1. **List all deployments in a namespace:**
   ```bash
   python3 sre.py list --namespace production
   ```

2. **Scale a deployment interactively:**
   ```bash
   python3 sre.py scale --interactive
   ```

3. **Display deployment info:**
   ```bash
   python3 sre.py info --deployment my-app --namespace default
   ```

4. **Run diagnostics with pod-level details:**
   ```bash
   python3 sre.py diagnostic --deployment my-app --pod --namespace default
   ```

5. **Restart and monitor a deployment rollout:**
   ```bash
   python3 sre.py rollout restart --deployment my-app --namespace staging
   ```

6. **Fetch logs for all pods in a deployment:**
   ```bash
   python3 sre.py logs --deployment my-app --namespace default
   ```

---

## ⚡ Autocomplete Setup

To enable autocomplete for this tool on a client’s terminal:

1. Install **argcomplete** (already included in `requirements.txt`):
   ```bash
   pip install argcomplete
   ```

2. Enable autocomplete for the tool:
   ```bash
   activate-global-python-argcomplete --user
   ```

3. Add this line to your shell configuration file (`~/.bashrc`, `~/.zshrc`, or equivalent):
   ```bash
   eval "$(register-python-argcomplete python3 sre.py)"
   ```

4. Reload the shell:
   ```bash
   source ~/.bashrc  # or `source ~/.zshrc` for Zsh users
   ```

5. Test autocomplete:
   ```bash
   python3 sre.py <TAB><TAB>
   ```

---

## 🛠️ Troubleshooting

- **Kubernetes Configuration Issues:**  
  If the tool cannot connect to Kubernetes, ensure your `kubeconfig` is properly set up:
  ```bash
  kubectl config view
  ```

- **Missing Dependencies:**  
  Make sure you have installed all required dependencies:
  ```bash
  pip install -r requirements.txt
  ```

- **Permission Issues:**  
  If you encounter permission errors, verify you have sufficient access to the Kubernetes cluster:
  ```bash
  kubectl auth can-i <verb> <resource>
  ```

- **Autocomplete Not Working:**  
  Ensure that `argcomplete` is installed and properly registered with your shell:
  ```bash
  activate-global-python-argcomplete --user
  eval "$(register-python-argcomplete python3 sre.py)"
  ```

---

