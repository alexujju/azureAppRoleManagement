
# Azure App Role Management 🚀

A Python Flask application to manage **Azure AD App Role Assignments** using the **Microsoft Graph API**, containerized and deployed on **Kubernetes** for scalability and DevOps excellence.

## 🌟 Features

- 🔐 Azure AD Authentication using **MSAL**
- 👥 View, assign, and remove **app roles** for users
- 🧾 Centralized token management
- 📦 Containerized using **Docker**
- ☸️ Deployed on **Kubernetes**
- 🔒 Configurable via **environment variables**, ConfigMaps, and Secrets

---

## 🧱 Project Structure

```
azureAppRoleManagement/
├── app/                      # Flask app and logic
│   ├── auth_helper.py        # Token acquisition logic
│   ├── graph_helper.py       # Microsoft Graph API calls
│   ├── routes.py             # Flask routes and views
│   └── templates/            # HTML templates
├── Dockerfile                # Container build instructions
├── k8s/
│   ├── deployment.yaml       # Kubernetes deployment
│   ├── service.yaml          # Kubernetes service
│   └── configmap.yaml        # App configuration
├── requirements.txt
└── README.md
```

---

## 🐳 Containerization with Docker

### Build the Docker image

```bash
docker build -t alexujju/azure-role-manager:latest .
```

### Push to DockerHub

```bash
docker push alexujju/azure-role-manager:latest
```

---

## ☸️ Deploy on Kubernetes

### 1. Create ConfigMap and Secret

```bash
kubectl apply -f k8s/configmap.yaml
kubectl create secret generic azure-secrets \
  --from-literal=CLIENT_ID=your-client-id \
  --from-literal=CLIENT_SECRET=your-client-secret \
  --from-literal=TENANT_ID=your-tenant-id
```

### 2. Deploy the application

```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
```

### 3. Access the app

If using a LoadBalancer or Ingress, navigate to the external IP:

```
http://<EXTERNAL-IP>:<PORT>
```

---

## 🔧 Environment Variables

These should be passed via Kubernetes ConfigMap or `.env` for local development:

| Variable               | Description                     |
|------------------------|---------------------------------|
| CLIENT_ID              | Azure AD app client ID          |
| CLIENT_SECRET          | Azure AD app client secret      |
| TENANT_ID              | Azure AD tenant ID              |
| GRAPH_SCOPE            | Microsoft Graph API scope       |
| SERVICE_PRINCIPAL_ID   | App's service principal ID      |

---

## 📸 UI Snapshot

> ![image](https://github.com/user-attachments/assets/a666dbdc-bef3-4d18-b4ef-da0ddd132ade)


---

## 📌 Useful Links

- [Microsoft Graph API Docs](https://learn.microsoft.com/en-us/graph/api/resources/approleassignment)
- [MSAL Python Library](https://pypi.org/project/msal/)
- [Azure App Roles](https://learn.microsoft.com/en-us/azure/active-directory/develop/howto-add-app-roles-in-azure-ad-apps)

---

## 🤝 Contributing

Pull requests and issues are welcome. Please fork the repo and open a PR with improvements or bug fixes.

---

## 📄 License

MIT License

---

## 🙌 Acknowledgements

This project is part of my learning journey in **DevOps**, combining identity access control with production-grade deployment practices.
