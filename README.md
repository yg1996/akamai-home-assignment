# SRE Kubernetes CLI Tool

![Python](https://img.shields.io/badge/python-3.8%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

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

777bash
pip install -r requirements.txt
777bash

**Sample `requirements.txt`**
777
kubernetes
argcomplete
777

### 3. Clone the Repository
777bash
git clone https://github.com/yourusername/sre-cli-tool.git
cd sre-cli-tool
777bash

### 4. Ensure Your Kubernetes Context is Set
Make sure you can access your Kubernetes cluster using:

777bash
kubectl get nodes
777bash

---

## 💻 Usage

### Basic Commands
Run the CLI tool using:

777bash
python3 sre.py [command] [options]
777bash

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
   777bash
   python3 sre.py list --namespace production
   777bash

2. **Scale a deployment interactively:**
   777bash
   python3 sre.py scale --interactive
   777bash

3. **Display deployment info:**
   777bash
   python3 sre.py info --deployment my-app --namespace default
   777bash

4. **Run diagnostics with pod-level details:**
   777bash
   python3 sre.py diagnostic --deployment my-app --pod --namespace default
   777bash

5. **Restart and monitor a deployment rollout:**
   777bash
   python3 sre.py rollout restart --deployment my-app --namespace staging
   777bash

6. **Fetch logs for all pods in a deployment:**
   777bash
   python3 sre.py logs --deployment my-app --namespace default
   777bash

---

## ⚡ Autocomplete Setup

To enable autocomplete for this tool on a client’s terminal:

1. Install **argcomplete** (already included in `requirements.txt`):
   777bash
   pip install argcomplete
   777bash

2. Enable autocomplete for the tool:
   777bash
   activate-global-python-argcomplete --user
   777bash

3. Add this line to your shell configuration file (`~/.bashrc`, `~/.zshrc`, or equivalent):
   777bash
   eval "$(register-python-argcomplete python3 sre.py)"
   777bash

4. Reload the shell:
   777bash
   source ~/.bashrc  # or `source ~/.zshrc` for Zsh users
   777bash

5. Test autocomplete:
   777bash
   python3 sre.py <TAB><TAB>
   777bash

---

## 🛠️ Troubleshooting

- **Kubernetes Configuration Issues:**  
  If the tool cannot connect to Kubernetes, ensure your `kubeconfig` is properly set up:
  777bash
  kubectl config view
  777bash

- **Missing Dependencies:**  
  Make sure you have installed all required dependencies:
  777bash
  pip install -r requirements.txt
  777bash

- **Permission Issues:**  
  If you encounter permission errors, verify you have sufficient access to the Kubernetes cluster:
  777bash
  kubectl auth can-i <verb> <resource>
  777bash

- **Autocomplete Not Working:**  
  Ensure that `argcomplete` is installed and properly registered with your shell:
  777bash
  activate-global-python-argcomplete --user
  eval "$(register-python-argcomplete python3 sre.py)"
  777bash

---

