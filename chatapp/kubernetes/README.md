# Chatsasa

simple chat webapp

## Kubernetes Deployment

### Prerequisites

- **Kubernetes Cluster**: Ensure you have access to a Kubernetes cluster. If not, set up a cluster on your preferred platform like Google Kubernetes Engine (GKE), Amazon EKS, or Minikube for local development.
- **kubectl**: Install the Kubernetes command-line tool (`kubectl`) to interact with your Kubernetes cluster.

### Configuration Files

This project utilizes Kubernetes manifests for deployment. Here's a quick overview of the main configuration files:

- **`deployment.yaml`**: Defines the deployment details for your Flask application.
- **`service.yaml`**: Defines the Kubernetes service to expose your Flask application.

### Steps to Deploy

1. **Clone the Repository**
    ```bash
    git clone https://github.com/your-username/your-repo.git
    cd your-repo
    ```

2. **Deploy to Kubernetes**
    ```bash
    kubectl apply -f deployment.yaml
    kubectl apply -f service.yaml
    ```

### Accessing the Application

After successful deployment, you can access your Flask application:

- **Locally (Minikube)**: Run `minikube service <service-name>` to get the service URL.
- **Cloud Environment**: Use the external IP or domain associated with your service.

### Additional Notes

- **Customization**: Update the `deployment.yaml` as needed, such as image name/tag, resources, environment variables, etc.
- **Troubleshooting**: If you encounter issues, check the logs using `kubectl logs <pod-name>` or inspect the events with `kubectl describe <resource-name>`.

### Resources

- **Kubernetes Documentation**: [Official Kubernetes Documentation](https://kubernetes.io/docs/)
- **Flask Deployment on Kubernetes**: [Flask Deployment on Kubernetes Guide](https://www.example.com/flask-kubernetes-deployment-guide)
