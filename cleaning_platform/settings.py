CSRF_TRUSTED_ORIGINS = [
    "https://*.herokuapp.com",
]
_host = os.environ.get("ALLOWED_HOST")
if _host:
    CSRF_TRUSTED_ORIGINS.append(f"https://{_host}")
