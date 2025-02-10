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
- [Unit Testing](#unit-testing)

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
git clone https://github.com/yg1996/akamai-home-assignment.git
cd akamai-home-assignment
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

### Interactive Mode
This tool supports an **Interactive Mode** to simplify its use. If any required argument is missing, it will automatically prompt the user to enter the value interactively. Enable **Interactive Mode** by using the `--interactive` flag:

#### Example:
```bash
python3 sre.py scale --interactive
```

When run with `--interactive`, missing values such as deployment names, replicas, and namespaces will be requested interactively.

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

## 🧪 Unit Testing
The **SRE Kubernetes CLI Tool** includes a suite of unit tests to validate its core functionalities. These tests are located in the test_sre.py file and are designed to simulate Kubernetes API behavior using dummy API objects.

### Key Tests
| Test Case    | Description |
|------------|-------------|
| `test_list_deployments`    | Verifies that the CLI correctly lists the deployments in the given namespace. |
| `test_scale_deployment`    | Ensures that scaling a deployment updates the replica count as expected. |
| `test_info_deployment`     | Checks that detailed deployment information is displayed correctly. |
| `test_rollout_deployment_status` | Simulates a rollout and tests the status monitoring mechanism. |
| `test_fetch_logs_deployment`  | Verifies that logs for a given deployment are retrieved and displayed. |
| `test_fetch_logs_pod`     | Ensures that logs for a specific pod are fetched correctly. |


### Running the Tests
To run the unit tests, navigate to the project directory and execute:

```bash 
python3 test_sre.py 
```

This will execute the entire test suite and display the results.

---

