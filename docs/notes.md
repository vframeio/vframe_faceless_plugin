# Development Notes

- Use NGINX to rewrite HTML content
    - ngx_http_sub_module
    - https://nginx.org/en/docs/http/ngx_http_sub_module.html
    - potential issues: cpu resources, performance decrease

```
location / {
    sub_filter '<a href="http://127.0.0.1:8080/'  '<a href="https://$host/';
    sub_filter '<img src="http://127.0.0.1:8080/' '<img src="https://$host/';
    sub_filter_once on;
}
```

```
# rewrite HTML
location / {
    sub_filter "__faceless_tag__" "NGINX rewrote this";
}
```
