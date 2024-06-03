import requests

# The URL to which the POST request will be sent
url = 'http://127.0.0.1:5000/webhook'

# The payload (data) to be sent in the POST request
payload = {
    'key1': 'value1',
    'key2': 'value2'
}

# Make the POST request
response = requests.post(url, data=payload)

# Print the response from the server
print('Status Code:', response.status_code)
print('Response Text:', response.text)
