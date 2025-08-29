from django.http import HttpResponse

def home(request):
    return HttpResponse("""
    <html>
      <head><title>Cleaning Platform</title></head>
      <body style='font-family:system-ui,Arial,sans-serif;margin:2rem'>
        <h1>Cleaning Platform</h1>
        <p>Heroku-ready Django starter with ops app and homepage.</p>
        <p>Log into <a href='/admin/'>/admin</a> after running migrations.</p>
      </body>
    </html>
    """)
