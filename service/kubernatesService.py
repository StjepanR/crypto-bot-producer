import datetime
import logging

import pytz
from kubernetes import client, config


class KubernetesService:

    def __init__(self):
        config.load_kube_config()
        self.api = client.AppsV1Api()
        self.namespace = "default"

    def create_deployment_object(self, name, image, port, deployment_name):
        # Get metadata
        producer = self.api.list_namespaced_deployment(namespace="default", label_selector="type=producer")
        print(producer)

        # Configure Pod template container
        container = client.V1Container(
            name=name,
            image=image,
            ports=[client.V1ContainerPort(container_port=port)],
            resources=client.V1ResourceRequirements(
                requests={"cpu": "100m", "memory": "200Mi"},
                limits={"cpu": "500m", "memory": "500Mi"},
            ),
        )

        # Create and configure a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels=
            {
                "app.kubernetes.io/instance": "",
                "type": "worker"
            }),
            spec=client.V1PodSpec(containers=[container]),
        )

        # Create the specification of deployment
        spec = client.V1DeploymentSpec(
            replicas=1, template=template, selector=
            {
                "matchLabels": {"type": "worker"}
            }
        )

        # Instantiate the deployment object
        deployment = client.V1Deployment(
            api_version="apps/v1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=deployment_name),
            spec=spec,
        )

        return deployment

    def create_deployment(self, deployment, deployment_name):
        try:
            response = self.api.create_namespaced_deployment(
                body=deployment, namespace=self.namespace
            )

            logging.info("deployment: " + deployment_name + " created")
            logging.info(
                "namespace: " + response.metadata.namespace + "\nname: " + response.metadata.name + "\nrevision: " + response.metadata.generation + "\nimage: " +
                response.spec.template.spec.containers[0].image)
        except:
            logging.error("failed to create deployment: " + deployment_name)
            raise RuntimeError("failed to create deployment: " + deployment_name)

    def update_deployment(self, deployment, deployment_name):
        try:
            response = self.api.patch_namespaced_deployment(
                name=deployment_name, namespace=self.namespace, body=deployment
            )

            logging.info("deployment: " + deployment_name + " restarted")
            logging.info(
                "namespace: " + response.metadata.namespace + "\nname: " + response.metadata.name + "\nrevision: " + response.metadata.generation + "\nimage: " +
                response.spec.template.spec.containers[0].image)
        except:
            logging.error("failed to update deployment: " + deployment_name)
            raise RuntimeError("failed to update deployment: " + deployment_name)

    def restart_deployment(self, deployment, deployment_name):
        try:
            deployment.spec.template.metadata.annotations = {
                "kubectl.kubernetes.io/restartedAt": datetime.datetime.now(tz=pytz.UTC)
                .isoformat()
            }

            response = self.api.patch_namespaced_deployment(
                name=deployment_name, namespace=self.namespace, body=deployment
            )

            logging.info("deployment: " + deployment_name + " restarted")
            logging.info(
                "namespace: " + response.metadata.namespace + "\nname: " + response.metadata.name + "\nrevision: " + response.metadata.generation + "\nimage: " +
                response.spec.template.spec.containers[0].image)
        except:
            logging.error("failed to restart deployment: " + deployment_name)
            raise RuntimeError("failed to restart deployment: " + deployment_name)

    def delete_deployment(self, deployment_name):
        try:
            response = self.api.delete_namespaced_deployment(
                name=deployment_name,
                namespace="default",
                body=client.V1DeleteOptions(
                    propagation_policy="Foreground", grace_period_seconds=5
                ),
            )
            logging.info("deployment: " + deployment_name + " deleted")
            logging.info(
                "namespace: " + response.metadata.namespace + "\nname: " + response.metadata.name + "\nrevision: " + response.metadata.generation + "\nimage: " +
                response.spec.template.spec.containers[0].image)
        except:
            logging.error("failed to delete deployment: " + deployment_name)
            raise RuntimeError("failed to delete deployment: " + deployment_name)
