import datetime
import logging
import pytz

from kubernetes import client, config
from config.config import Config


class KubernetesService:

    def __init__(self):
        config.load_incluster_config()
        self.api = client.AppsV1Api()
        self.namespace = "default"
        self.config = Config()

    def create_deployment_object(self, name, image, port, deployment_name, topic, model, frequency, steps, epochs, window_size, batch_size, scaler):
        # Get metadata
        producer = self.api.list_namespaced_deployment(namespace="default",
                                                       label_selector="type=producer")  # V1DeploymentList
        print(producer._metadata)

        # Create environment variables for container
        binance_api_secret_environment_variable = client.V1EnvVar(
            name="BINANCE_API_SECRET",
            value=self.config.binance_api_secret
        )

        binance_api_key_environment_variable = client.V1EnvVar(
            name="BINANCE_API_KEY",
            value=self.config.binance_api_key
        )

        kafka_broker_url_environment_variable = client.V1EnvVar(
            name="KAFKA_BROKER_URL",
            value=self.config.kafka_broker_url
        )

        kafka_topic_environment_variable = client.V1EnvVar(
            name="KAFKA_TOPIC",
            value=topic
        )

        model_environment_variable = client.V1EnvVar(
            name="MODEL",
            value=model
        )

        frequency_environment_variable = client.V1EnvVar(
            name="FREQUENCY",
            value=frequency
        )

        steps_environment_variable = client.V1EnvVar(
            name="STEPS",
            value=steps
        )

        epochs_environment_variable = client.V1EnvVar(
            name="EPOCHS",
            value=epochs
        )

        window_size_environment_variable = client.V1EnvVar(
            name="WINDOW_SIZE",
            value=window_size
        )

        batch_size_environment_variable = client.V1EnvVar(
            name="BATCH_SIZE",
            value=batch_size
        )

        scaler_environment_variable = client.V1EnvVar(
            name="SCALER",
            value=scaler
        )

        # Configure Pod template container
        container = client.V1Container(
            name=name,
            image=image,
            ports=[client.V1ContainerPort(container_port=port)],
            env=[
                binance_api_secret_environment_variable,
                binance_api_key_environment_variable,
                kafka_broker_url_environment_variable,
                kafka_topic_environment_variable,
                model_environment_variable,
                frequency_environment_variable,
                steps_environment_variable,
                epochs_environment_variable,
                window_size_environment_variable,
                batch_size_environment_variable,
                scaler_environment_variable
            ]
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
        logging.info("creating deployment :" + str(deployment_name))
        try:
            response = self.api.create_namespaced_deployment(
                body=deployment, namespace=self.namespace
            )

            logging.info("deployment: " + deployment_name + " created")
            logging.info("metadata: " + response.metadata.to_str())
        except Exception as e:
            logging.error("failed to create deployment: " + deployment_name, e)
            raise RuntimeError("failed to create deployment: " + deployment_name)

    def update_deployment(self, deployment, deployment_name):
        try:
            response = self.api.patch_namespaced_deployment(
                name=deployment_name, namespace=self.namespace, body=deployment
            )

            logging.info("deployment: " + deployment_name + " restarted")
            logging.info("metadata: " + response.metadata.to_str())
        except Exception as e:
            logging.error("failed to update deployment: " + deployment_name, e)
            raise RuntimeError("failed to update deployment: " + deployment_name)

    def restart_deployment(self, deployment, deployment_name):
        logging.info("restarting deployment :" + str(deployment_name))
        try:
            deployment.spec.template.metadata.annotations = {
                "kubectl.kubernetes.io/restartedAt": datetime.datetime.now(tz=pytz.UTC)
                .isoformat()
            }

            response = self.api.patch_namespaced_deployment(
                name=deployment_name, namespace=self.namespace, body=deployment
            )

            logging.info("deployment: " + deployment_name + " restarted")
            logging.info("metadata: " + response.metadata.to_str())
        except Exception as e:
            logging.error("failed to restart deployment: " + deployment_name, e)
            raise RuntimeError("failed to restart deployment: " + deployment_name)

    def delete_deployment(self, deployment_name):
        logging.info("deleting deployment :" + str(deployment_name))
        try:
            response = self.api.delete_namespaced_deployment(
                name=deployment_name,
                namespace="default",
                body=client.V1DeleteOptions(
                    propagation_policy="Foreground", grace_period_seconds=5
                ),
            )
            logging.info("deployment: " + deployment_name + " deleted")
            logging.info("metadata: " + response.metadata.to_str())
        except Exception as e:
            logging.error("failed to delete deployment: " + deployment_name, e)
            raise RuntimeError("failed to delete deployment: " + deployment_name)
