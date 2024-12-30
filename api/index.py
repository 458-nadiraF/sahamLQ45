from http.server import BaseHTTPRequestHandler
import json
import requests
import traceback
import os
import time

class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type','text/plain')
        self.end_headers()
        self.wfile.write('LQ45 Stock webhook handler'.encode('utf-8'))
        return
    def do_POST(self):
        # terima alert dr tv
      
        try:
            start_time = time.time()
            content_length = int(self.headers.get('Content-Length', 0))  # Default to 0 if not present
            if content_length > 0:
                post_data = self.rfile.read(content_length).decode('utf-8')  # Decode bytes to string
            else:
                post_data = ""  # No data sent
            
            if not post_data.strip():  # Check if the body is empty or whitespace
                raise ValueError("Empty request body")
            
            # Parse JSON
            received_json = json.loads(post_data)
            #received_json = json.loads(post_data.decode('utf-8'))
            price=received_json.get('price')
            symbol=received_json.get('Symbol')
            try:
                add=received_json.get('add')
                add2=received_json.get('add2')
            except:
                add=""
                add2=""
            forward_url=os.getenv('TELEGRAM_API')
            timestamp=timestamp = time.strftime("%m/%d/%Y %H:%M:%S", time.localtime())
            # Define the API endpoint where you want to forward the request
            textContent=f"Alert: screener LQ45 M15 A: Any alert() function call \nBUY {symbol} {price} {add} {add2}\n{timestamp}"
            params={
               "chat_id": f"{os.getenv('CHAT_ID')}",
               "text": textContent
            }
            
            response = requests.post(
                forward_url,
                params=params
            )
            
            execution_duration = (time.time() - start_time) * 1000
            # Send response back to the original client
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # You can customize the response based on the forwarded request's response
            response_data = {
                "message": "POST received and forwarded",
                "forward_status": response.status_code,
                "received_json":received_json,
                "buy_json": params, 
                "forward_response": response.json()  # Include this if you want to return the forwarded API's response
            }
            self.wfile.write(json.dumps(response_data).encode())
            log_message = (
                f"Execution Duration: {execution_duration}ms\n"
                f"Response Content: {response_data}\n"
                "-------------------------------------------\n"
            )
            headers2 = {
                'Accept': 'application/json',
                'Content-Type':'application/json'
                # Add any other required headers here
            }
            response = requests.post(
                    os.getenv('SPREADSHEET'),
                    json=log_message,
                    headers=headers2
                )
            
            
        except Exception as e:
            # Handle any errors
            self.send_response(500)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            error_response = {
                "error": str(e),
                "message": "Error processing request",
                "log_file": open(LOG_FILE_PATH).read()
            }
            traceback.print_exc()
            self.wfile.write(json.dumps(error_response).encode())
        
        
