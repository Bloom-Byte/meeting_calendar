# Deploying the App with Dockerfile and Nginx as Reverse Proxy

This guide outlines the steps to deploy the application using Docker and Nginx as a reverse proxy. 

## Prerequisites

Before you begin, ensure you have the following:

- Docker installed on your server
- Your application code packaged with a Dockerfile
- A domain name pointing to your server's IP address


The image is build and then used in the docker compose file. It contains directives on volumes and environment variable that the docker container will use.

Nginx should be install and the following directives added to a virtual host file in the /etc/nginx/sites-available folder

```
server {
    listen 80;
    server_name <your_domain>;

    location / {
        proxy_pass http://localhost:<host_port>;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
the nginx serves as a reverse proxy into the container. 
reload nginx and the app should be accessible through the servers public ip address.