#!/bin/bash
# demo.sh - A demo script for the SRE CLI tool
#
# This script demonstrates the major functionalities of the CLI tool by running non-interactive commands
# sequentially. It prints the exact CLI command that is about to run (so your audience knows what’s happening),
# adds a 2.5-second pause between commands, and finally shows the last 30 lines of the log file (sre.log).
#
# Ensure that your Kubernetes deployment exists in the 'test-namespace' as defined below and that sre.py
# is in the same directory as this script.
#
# Kubernetes Resources:
# ---
# apiVersion: v1
# kind: Namespace
# metadata:
#   name: test-namespace
# ---
# apiVersion: apps/v1
# kind: Deployment
# metadata:
#   name: my-deployment
#   namespace: test-namespace
# spec:
#   replicas: 1
#   selector:
#     matchLabels:
#       app: myapp
#   template:
#     metadata:
#       labels:
#         app: myapp
#     spec:
#       containers:
#       - name: nginx
#         image: nginx:1.21
#         ports:
#         - containerPort: 80

echo "=========================================="
echo "Welcome to the SRE CLI Demo!"
echo "=========================================="
sleep 2.5

# 1. List Deployments
echo ""
echo "Step 1: Listing deployments in the 'test-namespace'."
echo "Command: python3 sre.py list --namespace test-namespace"
sleep 1
echo "Output:"
python3 sre.py list --namespace test-namespace
sleep 2.5

# 2. Scale Deployment
echo ""
echo "Step 2: Scaling 'my-deployment' to 3 replicas. Let's pump it up!"
echo "Command: python3 sre.py scale --deployment my-deployment --replicas 3 --namespace test-namespace"
sleep 1
echo "Output:"
python3 sre.py scale --deployment my-deployment --replicas 3 --namespace test-namespace
sleep 2.5

# 3. Display Deployment Information
echo ""
echo "Step 3: Fetching info for 'my-deployment'. Time to reveal the secrets!"
echo "Command: python3 sre.py info --deployment my-deployment --namespace test-namespace"
sleep 1
echo "Output:"
python3 sre.py info --deployment my-deployment --namespace test-namespace
sleep 2.5

# 4. Run Diagnostics
echo ""
echo "Step 4: Running diagnostics on 'my-deployment' (with pod-level details)."
echo "Let's check what's really happening under the hood..."
echo "Command: python3 sre.py diagnostic --deployment my-deployment --namespace test-namespace --pod"
sleep 1
echo "Output:"
python3 sre.py diagnostic --deployment my-deployment --namespace test-namespace --pod
sleep 2.5

# 5a. Restart Deployment (Rollout Restart)
echo ""
echo "Step 5: Restarting 'my-deployment' to trigger a rollout."
echo "Time for a fresh reboot – like turning it off and on again!"
echo "Command: python3 sre.py rollout restart --deployment my-deployment --namespace test-namespace"
sleep 1
echo "Output:"
python3 sre.py rollout restart --deployment my-deployment --namespace test-namespace
sleep 2.5

# 5b. Check Rollout Status
echo ""
echo "Step 6: Checking rollout status..."
echo "Command: python3 sre.py rollout status --deployment my-deployment --namespace test-namespace"
sleep 1
echo "Output:"
python3 sre.py rollout status --deployment my-deployment --namespace test-namespace
sleep 2.5

# 6. Fetch Logs
echo ""
echo "Step 7: Fetching logs for 'my-deployment'. Let's see the backstage drama!"
echo "Command: python3 sre.py logs --deployment my-deployment --namespace test-namespace"
sleep 1
echo "Output:"
python3 sre.py logs --deployment my-deployment --namespace test-namespace
sleep 2.5

# 7. Demonstrate Interactive Mode
echo ""
echo "Step 8: Now, let's demonstrate interactive mode!"
echo "Command: python3 sre.py info --interactive"
echo "When prompted, please enter: 'my-deployment' for deployment and 'test-namespace' for namespace."
sleep 1
python3 sre.py info --interactive
sleep 2.5

# Show the last 30 lines of the log file
echo ""
echo "=========================================="
echo "Now, let's peek at the last 30 lines of the log file (sre.log):"
echo "=========================================="
tail -n 30 sre.log

echo ""
echo "=========================================="
echo "Demo complete! Thanks for watching our CLI magic show."
echo "Have a fantastic day and happy deploying!"
echo "=========================================="
