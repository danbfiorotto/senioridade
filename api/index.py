from http.server import BaseHTTPRequestHandler
import json
from src.app import main
import streamlit.web.bootstrap as bootstrap
import sys
import io
from contextlib import redirect_stdout

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Capture Streamlit's output
        captured_output = io.StringIO()
        with redirect_stdout(captured_output):
            # Run Streamlit app
            sys.argv = ["streamlit", "run", "src/app.py"]
            bootstrap.run(main, "", [], [])

        # Get the HTML output
        html_output = captured_output.getvalue()

        # Send response
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html_output.encode())
        return 