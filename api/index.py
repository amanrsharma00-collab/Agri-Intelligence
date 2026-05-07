from http.server import BaseHTTPRequestHandler
import json
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from agri_mcp_server import run_tool, list_tools

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path == '/' or self.path == '/api':
            response = {
                "server": "Agri Intelligence MCP Server",
                "version": "1.0.0",
                "status": "running",
                "coverage": "Chhattisgarh, India",
                "endpoints": {
                    "tools": "/api/tools",
                    "mandi_prices": "/api/tools/get_mandi_prices?district=Raipur",
                    "weather": "/api/tools/get_weather_advisory?district=Bastar",
                    "schemes": "/api/tools/get_agri_schemes?farmer_type=small&crop=paddy&district=Surguja",
                    "crop_advisory": "/api/tools/get_crop_advisory?crop=paddy&stage=sowing&district=Raipur",
                    "distress_risk": "/api/tools/assess_distress_risk?district=Bastar&crop=paddy&landholding_acres=2.5",
                    "dashboard": "/api/tools/get_district_dashboard?district=Bastar"
                }
            }
            self._send_json(response)

        elif self.path == '/api/tools':
            self._send_json(list_tools())

        elif self.path.startswith('/api/tools/'):
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(self.path)
            tool_name = parsed.path.replace('/api/tools/', '')
            params = {k: v[0] for k, v in parse_qs(parsed.query).items()}

            # Convert numeric params
            if 'landholding_acres' in params:
                params['landholding_acres'] = float(params['landholding_acres'])

            result = run_tool(tool_name, **params)
            self._send_json(result)

        else:
            self._send_json({"error": "Endpoint not found"}, 404)

    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body)
            tool_name = data.get('tool')
            params = data.get('params', {})
            if 'landholding_acres' in params:
                params['landholding_acres'] = float(params['landholding_acres'])
            result = run_tool(tool_name, **params)
            self._send_json(result)
        except Exception as e:
            self._send_json({"error": str(e)}, 400)

    def _send_json(self, data, status=200):
        response = json.dumps(data, ensure_ascii=False, indent=2)
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(response.encode())

    def log_message(self, format, *args):
        pass
