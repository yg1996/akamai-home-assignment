#!/usr/bin/env python3
# PYTHON_ARGCOMPLETE_OK

"""
sre.py - An SRE CLI tool to interact with a Kubernetes cluster with enhanced logging.

Features:
  1. sre list
     Lists deployments in the cluster.
     Optional Argument:
       --namespace: List deployments in the specified namespace.
  
  2. sre scale
     Scales a deployment to the desired number of replicas.
     Required Arguments (if not provided interactively):
       --deployment: Name of the deployment to scale.
       --replicas: Number of replicas to scale to.
     Optional Argument:
       --namespace: Namespace of the deployment. If omitted, the tool searches
                    for the deployment across all namespaces (must be unique).

  3. sre info
     Displays detailed information about a deployment.
     Required Argument (if not provided interactively):
       --deployment: Name of the deployment.
     Optional Argument:
       --namespace: Namespace of the deployment. If omitted, the first deployment
                    matching the name is shown.
  
  4. sre diagnostic
     Checks the health of a deployment and lists issues with pods.
     Required Argument (if not provided interactively):
       --deployment: Name of the deployment.
     Optional Arguments:
       --namespace: Namespace of the deployment.
       --pod: Include detailed pod-level diagnostics.
       
  5. sre rollout
     Restarts or monitors deployment rollouts.
     Positional Argument:
       action: The action to perform. Must be either "restart" or "status".
               - restart: Triggers a rollout restart of the deployment and then automatically monitors the rollout status until completion.
               - status:  Monitors the rollout status of the deployment.
     Required Argument (if not provided interactively):
       --deployment: Name of the deployment.
     Optional Argument:
       --namespace: Namespace of the deployment.
       
  6. sre logs
     Fetches logs for a specific deployment or pod.
     One of the following is required (if not provided interactively):
       --deployment: Fetch logs for all pods in the deployment.
       --pod: Fetch logs for a specific pod.
     Optional Argument:
       --namespace: Namespace of the deployment or pod (defaults to "default" for pod logs).

This version logs both operations and errors to a log file (sre.log).
"""

import argparse
import datetime
import logging
import sys
import time

from kubernetes import client, config
from kubernetes.client.rest import ApiException

# -----------------------------------------------------------------------------
# Optional: Enable argcomplete for auto-completion support.
# -----------------------------------------------------------------------------
try:
    import argcomplete
except ImportError:
    argcomplete = None
    logging.warning("argcomplete is not installed; auto-completion is disabled.")


# -----------------------------------------------------------------------------
# Helper Function: Prompt for missing arguments in interactive mode
# -----------------------------------------------------------------------------
def ensure_arg(arg_value, prompt, interactive, conversion_func=lambda x: x):
    """
    If arg_value is None and interactive mode is enabled, prompt the user.
    Otherwise, exit with an error if the argument is missing.
    """
    if arg_value is None:
        if interactive:
            value = input(prompt)
            try:
                return conversion_func(value)
            except Exception as e:
                print(f"Error converting input: {e}")
                sys.exit(1)
        else:
            print(f"Error: {prompt.strip(': ')} is required.")
            sys.exit(1)
    else:
        return arg_value


# -----------------------------------------------------------------------------
# Kubernetes Client Initialization
# -----------------------------------------------------------------------------
def init_kube_client():
    """
    Initializes and returns Kubernetes API clients.
    """
    try:
        config.load_kube_config()
        logging.info("Successfully loaded kubeconfig.")
    except Exception as e:
        logging.error("Failed to load kubeconfig: %s", e)
        print("Error: Could not load kubeconfig. Ensure you have a valid kubeconfig file.")
        sys.exit(1)
    
    apps_v1 = client.AppsV1Api()
    core_v1 = client.CoreV1Api()
    custom_objects_api = client.CustomObjectsApi()
    logging.info("Kubernetes clients initialized successfully.")
    return apps_v1, core_v1, custom_objects_api


# -----------------------------------------------------------------------------
# Helper Function: Find Deployment
# -----------------------------------------------------------------------------
def find_deployment(apps_v1, deployment_name, namespace=None):
    """
    Finds and returns a deployment object given its name and (optionally) namespace.
    """
    logging.info("Searching for deployment '%s' in namespace '%s'.", deployment_name, namespace if namespace else "all namespaces")
    if namespace:
        try:
            dep = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace)
            logging.info("Found deployment '%s' in namespace '%s'.", deployment_name, namespace)
            return dep
        except ApiException as e:
            if e.status == 404:
                logging.error("Deployment '%s' not found in namespace '%s'.", deployment_name, namespace)
                return None
            else:
                logging.error("APIException when reading deployment: %s", e)
                print("Error: Could not retrieve deployment information.")
                sys.exit(1)
    else:
        try:
            deployments = apps_v1.list_deployment_for_all_namespaces(field_selector=f"metadata.name={deployment_name}")
            if len(deployments.items) == 0:
                logging.error("Deployment '%s' not found in any namespace.", deployment_name)
                return None
            elif len(deployments.items) > 1:
                logging.error("Multiple deployments found for '%s'. Namespace must be specified.", deployment_name)
                print(f"Multiple deployments found with name '{deployment_name}'. Please specify a namespace using --namespace.")
                sys.exit(1)
            else:
                logging.info("Found deployment '%s' in namespace '%s'.", deployment_name, deployments.items[0].metadata.namespace)
                return deployments.items[0]
        except ApiException as e:
            logging.error("APIException when searching for deployment: %s", e)
            print("Error: Unable to search for deployment.")
            sys.exit(1)


# -----------------------------------------------------------------------------
# Command Implementations
# -----------------------------------------------------------------------------
def list_deployments(args, apps_v1):
    """
    Lists deployments in the specified namespace or across all namespaces.
    """
    ns = args.namespace if args.namespace is not None else (
        input("Enter namespace (or leave blank for all namespaces): ") if args.interactive else None)
    logging.info("Listing deployments. Namespace: %s", ns if ns else "all namespaces")
    try:
        if ns:
            deployments = apps_v1.list_namespaced_deployment(namespace=ns)
        else:
            deployments = apps_v1.list_deployment_for_all_namespaces()
    except ApiException as e:
        logging.error("Error listing deployments: %s", e)
        print("Error: Unable to list deployments. Check your Kubernetes cluster connectivity.")
        sys.exit(1)
    
    if not deployments.items:
        logging.info("No deployments found.")
        print("No deployments found.")
        return

    print("Deployments:")
    for dep in deployments.items:
        print(f"  Name: {dep.metadata.name}, Namespace: {dep.metadata.namespace}")
    logging.info("Listed %d deployments.", len(deployments.items))


def scale_deployment(args, apps_v1):
    """
    Scales a deployment to the desired number of replicas.
    """
    interactive = args.interactive
    deployment_name = ensure_arg(args.deployment, "Enter deployment name: ", interactive)
    replicas = ensure_arg(args.replicas, "Enter number of replicas: ", interactive, int)
    ns = args.namespace if args.namespace is not None else (
        input("Enter namespace (or leave blank to search all namespaces): ") if interactive else None)

    logging.info("Scaling deployment '%s'. Target replicas: %d. Namespace: %s", deployment_name, replicas, ns if ns else "unspecified")
    deployment = find_deployment(apps_v1, deployment_name, ns)
    if not deployment:
        logging.error("Deployment '%s' not found. Aborting scale operation.", deployment_name)
        print(f"Error: Deployment '{deployment_name}' not found.")
        sys.exit(1)
    ns = deployment.metadata.namespace

    body = {"spec": {"replicas": replicas}}
    try:
        apps_v1.patch_namespaced_deployment_scale(name=deployment_name, namespace=ns, body=body)
        logging.info("Successfully scaled deployment '%s' in namespace '%s' to %d replicas.", deployment_name, ns, replicas)
        print(f"Deployment '{deployment_name}' in namespace '{ns}' scaled to {replicas} replicas.")
    except ApiException as e:
        logging.error("Failed to scale deployment '%s': %s", deployment_name, e)
        print("Error: Scaling operation failed. Verify that the deployment exists and you have permission to modify it.")
        sys.exit(1)


def info_deployment(args, apps_v1):
    """
    Prints detailed information about a deployment.
    """
    interactive = args.interactive
    deployment_name = ensure_arg(args.deployment, "Enter deployment name: ", interactive)
    ns = args.namespace if args.namespace is not None else (
        input("Enter namespace (or leave blank to search all): ") if interactive else None)

    logging.info("Fetching info for deployment '%s'. Namespace: %s", deployment_name, ns if ns else "unspecified")
    deployment = find_deployment(apps_v1, deployment_name, ns)
    if not deployment:
        logging.error("Deployment '%s' not found.", deployment_name)
        print(f"Error: Deployment '{deployment_name}' not found.")
        sys.exit(1)

    info_lines = [
        "Deployment Information:",
        f"  Name: {deployment.metadata.name}",
        f"  Namespace: {deployment.metadata.namespace}",
        f"  Desired Replicas: {deployment.spec.replicas}",
        f"  Available Replicas: {deployment.status.available_replicas if deployment.status.available_replicas is not None else 0}",
        "  Labels:"
    ]
    if deployment.metadata.labels:
        for key, value in deployment.metadata.labels.items():
            info_lines.append(f"    {key}: {value}")
    else:
        info_lines.append("    None")
    info_lines.append(f"  Creation Timestamp: {deployment.metadata.creation_timestamp}")

    for line in info_lines:
        print(line)
    logging.info("Displayed information for deployment '%s'.", deployment_name)


def diagnostic_deployment(args, apps_v1, core_v1, custom_objects_api):
    """
    Checks the health of a deployment and optionally provides pod-level diagnostics.
    """
    interactive = args.interactive
    deployment_name = ensure_arg(args.deployment, "Enter deployment name: ", interactive)
    ns = args.namespace if args.namespace is not None else (
        input("Enter namespace (or leave blank to search all): ") if interactive else None)

    logging.info("Starting diagnostics for deployment '%s'. Namespace: %s", deployment_name, ns if ns else "unspecified")
    deployment = find_deployment(apps_v1, deployment_name, ns)
    if not deployment:
        logging.error("Deployment '%s' not found during diagnostics.", deployment_name)
        print(f"Error: Deployment '{deployment_name}' not found.")
        sys.exit(1)
    ns = deployment.metadata.namespace

    if deployment.spec.selector.match_labels:
        label_selector = ",".join([f"{k}={v}" for k, v in deployment.spec.selector.match_labels.items()])
        logging.info("Using label selector '%s' for deployment '%s'.", label_selector, deployment_name)
    else:
        logging.error("No label selector found for deployment '%s'.", deployment_name)
        print("Error: No label selector found for the deployment.")
        sys.exit(1)

    try:
        pods = core_v1.list_namespaced_pod(namespace=ns, label_selector=label_selector)
        logging.info("Found %d pods for deployment '%s'.", len(pods.items), deployment_name)
    except ApiException as e:
        logging.error("Error listing pods: %s", e)
        print("Error: Unable to list pods for the deployment.")
        sys.exit(1)

    if not pods.items:
        logging.warning("No pods found for deployment '%s'.", deployment_name)
        print("No pods found for this deployment.")
        return

    # Attempt to fetch pod metrics (if Metrics Server is installed)
    pod_metrics = {}
    try:
        metrics = custom_objects_api.list_namespaced_custom_object(
            group="metrics.k8s.io",
            version="v1beta1",
            namespace=ns,
            plural="pods"
        )
        for item in metrics.get("items", []):
            pod_name = item["metadata"]["name"]
            if item.get("containers"):
                cpu_usage = item["containers"][0]["usage"].get("cpu", "N/A")
                memory_usage = item["containers"][0]["usage"].get("memory", "N/A")
            else:
                cpu_usage, memory_usage = "N/A", "N/A"
            pod_metrics[pod_name] = {"cpu": cpu_usage, "memory": memory_usage}
        logging.info("Pod metrics collected for deployment '%s'.", deployment_name)
    except ApiException as e:
        logging.warning("Metrics API not available: %s", e)

    healthy_count = 0
    issues_count = 0

    if args.pod:
        print("Pod-level Diagnostics:")
    for pod in pods.items:
        pod_name = pod.metadata.name
        phase = pod.status.phase
        ready = all(cs.ready for cs in pod.status.container_statuses) if pod.status.container_statuses else False

        diag_msg = f"  Pod: {pod_name} | Phase: {phase} | Ready: {ready}"
        if pod_name in pod_metrics:
            diag_msg += f" | CPU: {pod_metrics[pod_name]['cpu']} | Memory: {pod_metrics[pod_name]['memory']}"
        else:
            diag_msg += " | CPU: N/A | Memory: N/A"

        issue_reasons = []
        if pod.status.container_statuses:
            for cs in pod.status.container_statuses:
                if cs.state.waiting:
                    issue_reasons.append(cs.state.waiting.reason)
                elif cs.state.terminated:
                    issue_reasons.append(cs.state.terminated.reason)
        if issue_reasons or phase != "Running" or not ready:
            diag_msg += f" | Issues: {', '.join(issue_reasons) if issue_reasons else 'Pod not running/ready'}"
            issues_count += 1
        else:
            healthy_count += 1

        if args.pod:
            print(diag_msg)
    logging.info("Diagnostics for deployment '%s': Total pods=%d, Healthy=%d, Issues=%d",
                 deployment_name, len(pods.items), healthy_count, issues_count)

    print(f"\nOverall Diagnostics for Deployment '{deployment_name}' (Namespace: {ns}):")
    print(f"  Total Pods: {len(pods.items)}")
    print(f"  Healthy Pods: {healthy_count}")
    print(f"  Pods with Issues: {issues_count}")


def monitor_rollout_status(apps_v1, deployment_name, namespace, timeout=300, interval=5):
    """
    Monitors the rollout status of a deployment until it is complete or until a timeout is reached.
    """
    logging.info("Monitoring rollout status for deployment '%s' in namespace '%s'.", deployment_name, namespace)
    start_time = time.time()
    while True:
        try:
            deployment = apps_v1.read_namespaced_deployment(name=deployment_name, namespace=namespace)
        except ApiException as e:
            logging.error("Error fetching deployment status for '%s': %s", deployment_name, e)
            print("Error: Could not fetch deployment status.")
            sys.exit(1)
        spec_replicas = deployment.spec.replicas if deployment.spec.replicas is not None else 0
        updated_replicas = deployment.status.updated_replicas if deployment.status.updated_replicas is not None else 0
        available_replicas = deployment.status.available_replicas if deployment.status.available_replicas is not None else 0

        # Check if rollout is complete
        if (deployment.status.observed_generation >= deployment.metadata.generation and 
            updated_replicas == spec_replicas and 
            available_replicas == spec_replicas):
            logging.info("Rollout status: Deployment '%s' rollout completed successfully.", deployment_name)
            print("Rollout successful: all replicas updated and available.")
            break

        # Timeout check
        if time.time() - start_time > timeout:
            logging.error("Rollout status: Timeout waiting for deployment '%s' to complete rollout.", deployment_name)
            print("Timeout waiting for rollout to complete.")
            sys.exit(1)

        logging.info("Rollout progress: Deployment '%s': %d/%d updated, %d/%d available.",
                     deployment_name, updated_replicas, spec_replicas, available_replicas, spec_replicas)
        print(f"Rollout in progress: {updated_replicas}/{spec_replicas} updated, {available_replicas}/{spec_replicas} available. Waiting...")
        time.sleep(interval)


def rollout_deployment(args, apps_v1, core_v1):
    """
    Restarts or monitors the rollout status of a deployment.
    """
    interactive = args.interactive
    deployment_name = ensure_arg(args.deployment, "Enter deployment name: ", interactive)
    ns = args.namespace if args.namespace is not None else (
        input("Enter namespace (or leave blank to search all): ") if interactive else None)

    logging.info("Rollout command received. Action: %s, Deployment: %s, Namespace: %s",
                 args.action, deployment_name, ns if ns else "unspecified")
    
    deployment = find_deployment(apps_v1, deployment_name, ns)
    if not deployment:
        logging.error("Deployment '%s' not found for rollout action.", deployment_name)
        print(f"Error: Deployment '{deployment_name}' not found.")
        sys.exit(1)
    ns = deployment.metadata.namespace

    if args.action == 'restart':
        logging.info("Initiating rollout restart for deployment '%s' in namespace '%s'.", deployment_name, ns)
        # Use timezone-aware datetime and trigger restart.
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        body = {"spec": {"template": {"metadata": {"annotations": {"kubectl.kubernetes.io/restartedAt": timestamp}}}}}
        try:
            apps_v1.patch_namespaced_deployment(name=deployment_name, namespace=ns, body=body)
            logging.info("Deployment '%s' successfully restarted at %s.", deployment_name, timestamp)
            print(f"Deployment '{deployment_name}' in namespace '{ns}' restarted successfully.")
        except ApiException as e:
            logging.error("Error restarting deployment '%s': %s", deployment_name, e)
            print(f"Error: Failed to restart deployment '{deployment_name}'.")
            sys.exit(1)
        # After restarting, monitor the rollout status.
        print("Monitoring rollout status...")
        monitor_rollout_status(apps_v1, deployment_name, ns)

    elif args.action == 'status':
        monitor_rollout_status(apps_v1, deployment_name, ns)


def fetch_logs(args, apps_v1, core_v1):
    """
    Fetches logs for a specific deployment or pod.
    """
    interactive = args.interactive
    logging.info("Logs command received. Arguments: %s", args)
    if args.deployment is None and args.pod is None:
        if interactive:
            choice = input("Fetch logs from a deployment or a pod? (Enter 'deployment' or 'pod'): ").strip().lower()
            if choice == "deployment":
                args.deployment = input("Enter deployment name: ")
            elif choice == "pod":
                args.pod = input("Enter pod name: ")
            else:
                print("Invalid choice. Exiting.")
                sys.exit(1)
        else:
            print("Error: Either --deployment or --pod must be specified.")
            sys.exit(1)
            
    if args.deployment:
        deployment_name = args.deployment
        ns = args.namespace if args.namespace is not None else (
            input("Enter namespace (or leave blank to search all): ") if interactive else None)
        logging.info("Fetching logs for deployment '%s' in namespace '%s'.", deployment_name, ns if ns else "unspecified")
        deployment = find_deployment(apps_v1, deployment_name, ns)
        if not deployment:
            logging.error("Deployment '%s' not found for fetching logs.", deployment_name)
            print(f"Error: Deployment '{deployment_name}' not found.")
            sys.exit(1)
        ns = deployment.metadata.namespace
        if deployment.spec.selector.match_labels:
            label_selector = ",".join([f"{k}={v}" for k, v in deployment.spec.selector.match_labels.items()])
            logging.info("Using label selector '%s' to fetch logs for deployment '%s'.", label_selector, deployment_name)
        else:
            logging.error("No label selector found for deployment '%s'.", deployment_name)
            print("Error: No label selector found for the deployment.")
            sys.exit(1)
        try:
            pods = core_v1.list_namespaced_pod(namespace=ns, label_selector=label_selector)
        except ApiException as e:
            logging.error("Error listing pods for deployment '%s': %s", deployment_name, e)
            print("Error: Unable to list pods for the deployment.")
            sys.exit(1)
        if not pods.items:
            logging.warning("No pods found for deployment '%s'.", deployment_name)
            print("No pods found for this deployment.")
            return
        for pod in pods.items:
            pod_name = pod.metadata.name
            try:
                logs_data = core_v1.read_namespaced_pod_log(name=pod_name, namespace=ns, tail_lines=100)
                logging.info("Fetched logs for pod '%s' in deployment '%s'.", pod_name, deployment_name)
                print(f"Logs for pod '{pod_name}':\n{logs_data}\n{'-'*60}")
            except ApiException as e:
                logging.error("Error fetching logs for pod '%s': %s", pod_name, e)
                print(f"Error: Could not fetch logs for pod '{pod_name}'.")
    elif args.pod:
        pod_name = args.pod
        ns = args.namespace if args.namespace is not None else (
            input("Enter namespace (default is 'default'): ") or "default" if interactive else "default")
        logging.info("Fetching logs for pod '%s' in namespace '%s'.", pod_name, ns)
        try:
            logs_data = core_v1.read_namespaced_pod_log(name=pod_name, namespace=ns, tail_lines=100)
            logging.info("Fetched logs for pod '%s'.", pod_name)
            print(f"Logs for pod '{pod_name}':\n{logs_data}")
        except ApiException as e:
            logging.error("Error fetching logs for pod '%s': %s", pod_name, e)
            print(f"Error: Could not fetch logs for pod '{pod_name}'.")
            sys.exit(1)


def main():
    # Preprocess sys.argv to capture and remove '--interactive' regardless of its position.
    interactive_flag = "--interactive" in sys.argv
    sys.argv = [arg for arg in sys.argv if arg != "--interactive"]

    # Setup logging: both operations and errors are logged to 'sre.log'
    logging.basicConfig(
        filename='sre.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logging.info("Starting SRE CLI tool.")

    parser = argparse.ArgumentParser(
        description='SRE CLI tool for managing Kubernetes deployments.'
    )
    subparsers = parser.add_subparsers(dest='command', help='Available Commands')
    subparsers.required = True

    # "list" command
    parser_list = subparsers.add_parser('list', help='List deployments in the cluster')
    parser_list.add_argument('--namespace', type=str, help='Specify a namespace to list deployments')

    # "scale" command
    parser_scale = subparsers.add_parser('scale', help='Scale a deployment')
    parser_scale.add_argument('--deployment', type=str, help='Name of the deployment to scale')
    parser_scale.add_argument('--replicas', type=int, help='Number of replicas to scale to')
    parser_scale.add_argument('--namespace', type=str, help='Namespace of the deployment')

    # "info" command
    parser_info = subparsers.add_parser('info', help='Display detailed information about a deployment')
    parser_info.add_argument('--deployment', type=str, help='Name of the deployment')
    parser_info.add_argument('--namespace', type=str, help='Namespace of the deployment')

    # "diagnostic" command
    parser_diag = subparsers.add_parser('diagnostic', help='Run diagnostics on a deployment')
    parser_diag.add_argument('--deployment', type=str, help='Name of the deployment to diagnose')
    parser_diag.add_argument('--namespace', type=str, help='Namespace of the deployment')
    parser_diag.add_argument('--pod', action='store_true', help='Include pod-level diagnostics')

    # "rollout" command
    parser_rollout = subparsers.add_parser('rollout', help='Manage deployment rollouts (restart or monitor status)')
    parser_rollout.add_argument('action', type=str, choices=['restart', 'status'],
                                help='Action to perform on the deployment (restart/status)')
    parser_rollout.add_argument('--deployment', type=str, help='Name of the deployment for rollout action')
    parser_rollout.add_argument('--namespace', type=str, help='Namespace of the deployment')

    # "logs" command
    parser_logs = subparsers.add_parser('logs', help='Fetch logs for a specific deployment or pod')
    group = parser_logs.add_mutually_exclusive_group()
    group.add_argument('--deployment', type=str, help='Name of the deployment to fetch logs from')
    group.add_argument('--pod', type=str, help='Name of the pod to fetch logs from')
    parser_logs.add_argument('--namespace', type=str, help='Namespace of the deployment or pod')

    if argcomplete:
        argcomplete.autocomplete(parser)

    args = parser.parse_args()
    args.interactive = interactive_flag

    logging.info("Command received: %s", args.command)

    apps_v1, core_v1, custom_objects_api = init_kube_client()

    if args.command == 'list':
        list_deployments(args, apps_v1)
    elif args.command == 'scale':
        scale_deployment(args, apps_v1)
    elif args.command == 'info':
        info_deployment(args, apps_v1)
    elif args.command == 'diagnostic':
        diagnostic_deployment(args, apps_v1, core_v1, custom_objects_api)
    elif args.command == 'rollout':
        rollout_deployment(args, apps_v1, core_v1)
    elif args.command == 'logs':
        fetch_logs(args, apps_v1, core_v1)
    else:
        parser.print_help()

    logging.info("SRE CLI tool operation completed.")


if __name__ == '__main__':
    main()
