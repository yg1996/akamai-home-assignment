#!/usr/bin/env python3
"""
test_sre.py

Unit tests for key CLI functionalities of the SRE CLI tool.

This file contains a simplified suite of tests that simulate the main functionalities
of the CLI tool by using dummy Kubernetes API client objects. The tests focus on the 
following functionalities:
 - Listing deployments.
 - Scaling deployments.
 - Displaying deployment information.
 - Monitoring rollout status with simulated state transitions.
 - Fetching logs from a deployment and from a specific pod.

For the rollout status test, a side effect is applied to simulate that after a few iterations,
the rollout condition becomes complete, preventing an infinite or resource‐intensive busy loop.
Each test captures stdout output using StringIO and validates expected output strings.
"""

import unittest
from io import StringIO
from contextlib import redirect_stdout
from types import SimpleNamespace
from unittest.mock import patch

# Import CLI functions from your sre.py file.
from sre import list_deployments, scale_deployment, info_deployment, rollout_deployment, fetch_logs

# --- Dummy classes to simulate Kubernetes API responses ---

class DummyDeployment:
    """
    DummyDeployment simulates a Kubernetes Deployment object with the minimal attributes
    required to test our CLI tool's functionalities.
    """
    def __init__(self, name, namespace, replicas=3, updated_replicas=1, available_replicas=1,
                 observed_generation=1, generation=1, labels=None):
        # Metadata includes the name, namespace, labels, and creation timestamp.
        self.metadata = SimpleNamespace(
            name=name,
            namespace=namespace,
            labels=labels if labels else {},
            creation_timestamp="2025-01-01T00:00:00Z"
        )
        # The generation attribute is required by the rollout status check.
        self.metadata.generation = generation
        # Spec contains the desired number of replicas and a selector for matching pods.
        self.spec = SimpleNamespace(
            replicas=replicas,
            selector=SimpleNamespace(match_labels=labels if labels else {})
        )
        # Status simulates the observed state of the deployment.
        self.status = SimpleNamespace(
            available_replicas=available_replicas,
            updated_replicas=updated_replicas,
            observed_generation=observed_generation
        )

class DummyAppsV1:
    """
    DummyAppsV1 simulates the Kubernetes AppsV1 API client.
    """
    def __init__(self, deployment):
        self.deployment = deployment

    def read_namespaced_deployment(self, name, namespace):
        # Return the dummy deployment if name and namespace match.
        if self.deployment.metadata.name == name and self.deployment.metadata.namespace == namespace:
            return self.deployment
        raise Exception("Deployment not found")

    def list_namespaced_deployment(self, namespace, **kwargs):
        # Return the dummy deployment if the namespace matches.
        if self.deployment.metadata.namespace == namespace:
            return SimpleNamespace(items=[self.deployment])
        return SimpleNamespace(items=[])

    def patch_namespaced_deployment_scale(self, name, namespace, body):
        # Simulate patching by updating the replica count.
        self.deployment.spec.replicas = body["spec"]["replicas"]

    def patch_namespaced_deployment(self, name, namespace, body):
        # Simulate a restart operation.
        return self.deployment

class DummyPod:
    """
    DummyPod simulates a Kubernetes Pod object with minimal attributes.
    """
    def __init__(self, name):
        self.metadata = SimpleNamespace(name=name)
        # Assume the pod is running and ready.
        container_status = SimpleNamespace(ready=True, state=SimpleNamespace(waiting=None, terminated=None))
        self.status = SimpleNamespace(phase="Running", container_statuses=[container_status])

class DummyCoreV1:
    """
    DummyCoreV1 simulates the Kubernetes CoreV1 API client.
    """
    def __init__(self, pods):
        self.pods = pods

    def list_namespaced_pod(self, namespace, label_selector):
        # For simplicity, ignore the label_selector and return all dummy pods.
        return SimpleNamespace(items=self.pods)

    def read_namespaced_pod_log(self, name, namespace, tail_lines):
        # Return a dummy log string.
        return f"Dummy log for pod {name}"

class DummyCustomObjectsAPI:
    """
    DummyCustomObjectsAPI simulates the Kubernetes CustomObjects API for fetching pod metrics.
    """
    def list_namespaced_custom_object(self, group, version, namespace, plural):
        return {"items": [{"metadata": {"name": "pod1"},
                            "containers": [{"usage": {"cpu": "100m", "memory": "50Mi"}}]}]}

# --- Unit tests ---

class TestSreCliSimple(unittest.TestCase):
    """
    TestSreCliSimple contains unit tests for the SRE CLI tool functionalities.
    """
    def setUp(self):
        """
        Create a dummy deployment and associated dummy API clients. Also, initialize
        a basic args namespace to simulate command-line arguments.
        """
        self.deployment = DummyDeployment("test-deployment", "default", labels={"app": "test"})
        self.apps_v1 = DummyAppsV1(self.deployment)
        self.core_v1 = DummyCoreV1([DummyPod("pod1")])
        self.custom_objects_api = DummyCustomObjectsAPI()
        self.args = SimpleNamespace(
            interactive=False,
            deployment=None,
            replicas=None,
            namespace=None,
            pod=None,
            action=None
        )
    
    def test_list_deployments(self):
        """Test that list_deployments outputs the expected deployment name."""
        self.args.namespace = "default"
        f = StringIO()
        with redirect_stdout(f):
            list_deployments(self.args, self.apps_v1)
        output = f.getvalue()
        self.assertIn("test-deployment", output)
    
    def test_scale_deployment(self):
        """Test that scale_deployment updates the replicas to the expected value."""
        self.args.deployment = "test-deployment"
        self.args.replicas = 5
        self.args.namespace = "default"
        scale_deployment(self.args, self.apps_v1)
        self.assertEqual(self.deployment.spec.replicas, 5)
    
    def test_info_deployment(self):
        """Test that info_deployment outputs the correct deployment name and namespace."""
        self.args.deployment = "test-deployment"
        self.args.namespace = "default"
        f = StringIO()
        with redirect_stdout(f):
            info_deployment(self.args, self.apps_v1)
        output = f.getvalue()
        self.assertIn("test-deployment", output)
        self.assertIn("default", output)
    
    def test_rollout_deployment_status(self):
        """
        Test rollout_deployment for the 'status' action.
        A side effect is used to simulate the deployment status becoming complete after a few iterations.
        """
        self.deployment.spec.replicas = 3
        # Initially, the rollout is incomplete.
        self.deployment.status.updated_replicas = 1
        self.deployment.status.available_replicas = 1

        self.args.deployment = "test-deployment"
        self.args.namespace = "default"
        self.args.action = "status"

        call_count = [0]
        def side_effect_read_deployment(name, namespace):
            call_count[0] += 1
            if call_count[0] < 3:
                # Rollout remains incomplete.
                self.deployment.status.updated_replicas = 1
                self.deployment.status.available_replicas = 1
            else:
                # Mark rollout as complete.
                self.deployment.status.updated_replicas = self.deployment.spec.replicas
                self.deployment.status.available_replicas = self.deployment.spec.replicas
            return self.deployment

        with patch.object(self.apps_v1, "read_namespaced_deployment", side_effect=side_effect_read_deployment):
            with patch("time.sleep", return_value=None):
                f = StringIO()
                with redirect_stdout(f):
                    rollout_deployment(self.args, self.apps_v1, self.core_v1)
                output = f.getvalue()
                self.assertIn("Rollout successful", output)
    
    def test_fetch_logs_deployment(self):
        """Test that fetch_logs for a deployment outputs the expected log message."""
        self.args.deployment = "test-deployment"
        self.args.namespace = "default"
        self.args.pod = None
        f = StringIO()
        with redirect_stdout(f):
            fetch_logs(self.args, self.apps_v1, self.core_v1)
        output = f.getvalue()
        self.assertIn("Dummy log for pod pod1", output)
    
    def test_fetch_logs_pod(self):
        """Test that fetch_logs for a specific pod outputs the expected log message."""
        self.args.deployment = None  # Ensure deployment is not set.
        self.args.pod = "pod1"
        self.args.namespace = "default"
        f = StringIO()
        with redirect_stdout(f):
            fetch_logs(self.args, self.apps_v1, self.core_v1)
        output = f.getvalue()
        self.assertIn("Dummy log for pod pod1", output)

if __name__ == '__main__':
    print("==========================================")
    print(" Running SRE CLI Tool Unit Tests")
    print("==========================================\n")
    result = unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(TestSreCliSimple))
    print("\n==========================================")
    if result.wasSuccessful():
        print(" All tests passed!")
    else:
        print(" Some tests failed.")
    print("==========================================")
