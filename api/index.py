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
        self.wfile.write('Hello, world!'.encode('utf-8'))
        return
    def get_account_balance(self):
        headers = {
            'Accept': 'application/json',
            'auth-token': os.getenv('METAAPI_TOKEN')  
        }
        
        try:
            get_balance_url=f"https://mt-client-api-v1.london.agiliumtrade.ai/users/current/accounts/6d01a31f-1091-448d-a8eb-549f2e743e67/account-information"
            response = requests.get(get_balance_url, headers=headers)
            
            # Check if request was successful
            if response.status_code == 200:
                data = response.json()
                return data.get('balance')  
            else:
                print(f"Error: API request failed with status code {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching balance: {str(e)}")
            return None
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
            lot=received_json.get('lot')
            sl=received_json.get('sl')
            tp=received_json.get('tp')
            symbol=received_json.get('Symbol')
            
            balance=self.get_account_balance()
            # Define the API endpoint where you want to forward the request
            forward_url = f"https://mt-client-api-v1.london.agiliumtrade.ai/users/current/accounts/6d01a31f-1091-448d-a8eb-549f2e743e67/trade"  # Replace with your actual API endpoint
            balance2= float(balance) 
            buy_json={
               "symbol": symbol,
               "actionType": "ORDER_TYPE_BUY",
               "volume": round(lot*balance2, 2),
               "stopLoss": sl,
               "takeProfit": float(tp),
               "takeProfitUnits": "ABSOLUTE_PRICE"
            }
            
            headers = {
                'Accept': 'application/json',
                'auth-token':os.getenv('METAAPI_TOKEN'),
                'Content-Type':'application/json'
                # Add any other required headers here
            }
            
            response = requests.post(
                forward_url,
                json=buy_json,
                headers=headers
            )
            
            execution_duration = (time.time() - start_time) * 1000
            timestamp=timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            # Send response back to the original client
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            
            # You can customize the response based on the forwarded request's response
            response_data = {
                "message": "POST received and forwarded",
                "forward_status": response.status_code,
                "received_json":received_json,
                "buy_json": buy_json, 
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
        
        
