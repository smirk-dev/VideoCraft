"""
Uvicorn configuration for handling large file uploads
"""

# Uvicorn configuration for large file uploads
UVICORN_CONFIG = {
    "host": "0.0.0.0",
    "port": 8001,
    "reload": False,
    "log_level": "info",
    "access_log": True,
    "use_colors": True,
    "loop": "auto",
    "http": "auto",
    "ws": "auto",
    "lifespan": "auto",
    "interface": "auto",
    "debug": False,
    "reload_dirs": None,
    "reload_includes": None,
    "reload_excludes": None,
    "reload_delay": 0.25,
    "workers": 1,
    "env_file": None,
    "log_config": None,
    "server_header": True,
    "date_header": True,
    "forwarded_allow_ips": None,
    "root_path": "",
    "limit_concurrency": None,
    "limit_max_requests": None,
    "timeout_keep_alive": 5,
    "timeout_notify": 30,
    "callback_notify": None,
    "ssl_keyfile": None,
    "ssl_certfile": None,
    "ssl_keyfile_password": None,
    "ssl_version": None,
    "ssl_cert_reqs": None,
    "ssl_ca_certs": None,
    "ssl_ciphers": "TLSv1",
    "h11_max_incomplete_event_size": 16384,
    # Increase these limits for large file uploads (2GB)
    "backlog": 2048,
    "header_timeout": 120,  # 2 minutes for headers
    "timeout_graceful_shutdown": 30,
    # Custom HTTP limits for large uploads
    "http_max_request_size": 2 * 1024 * 1024 * 1024,  # 2GB
    "http_max_field_size": 16384,
    "http_max_fields": 100,
}

# Additional configuration for handling large requests
LARGE_FILE_CONFIG = {
    "max_upload_size": 2 * 1024 * 1024 * 1024,  # 2GB
    "chunk_size": 1024 * 1024,  # 1MB chunks
    "timeout": 300,  # 5 minutes timeout for large uploads
    "max_retries": 3,
    "buffer_size": 8192 * 1024,  # 8MB buffer
}
