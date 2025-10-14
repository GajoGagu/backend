# Nginx Reverse Proxy for gajogagu

This directory provides a production-ready Nginx setup to front the CRUD API and DL API hosted on separate servers.

## Files
- `nginx.conf` – main Nginx config that includes `conf.d` and `sites-enabled`
- `conf.d/common.conf` – gzip, client_max_body_size, websocket upgrade map
- `sites-available/gajogagu.conf` – HTTP server routing:
  - `/` → CRUD API origin
  - `/dl/` → DL API origin

## Configure origins
Edit `sites-available/gajogagu.conf` and replace placeholders:
- `CRUDE_API_HOST` → hostname/IP of CRUD server (e.g. `10.0.1.10` or `crud.internal`)
- `DL_API_HOST` → hostname/IP of DL server (e.g. `10.0.2.20`)
- `YOUR_DOMAIN_OR_IP` → public domain or IP

Example:
```
map "$host" $crud_api_origin { default http://10.0.1.10:8001; }
map "$host" $dl_api_origin   { default http://10.0.2.20:8002; }
server_name api.example.com;
```

## Install and enable
Copy files to `/etc/nginx` on the edge server:
```
sudo mkdir -p /etc/nginx/sites-available /etc/nginx/sites-enabled /etc/nginx/conf.d
sudo cp -r deploy/nginx/* /etc/nginx/
sudo ln -s /etc/nginx/sites-available/gajogagu.conf /etc/nginx/sites-enabled/gajogagu.conf
sudo nginx -t && sudo systemctl reload nginx
```

## TLS (HTTPS)
Use Certbot to obtain a certificate and enable HTTPS with redirect:
```
sudo apt-get update && sudo apt-get install -y certbot python3-certbot-nginx
sudo certbot --nginx -d YOUR_DOMAIN --redirect -m you@example.com --agree-tos --no-eff-email
```

## Notes
- CRUD API health at `/health` is proxied directly.
- Increase `client_max_body_size` in `conf.d/common.conf` if you upload large files.
- For WebSocket endpoints, upgrade headers are already set.
