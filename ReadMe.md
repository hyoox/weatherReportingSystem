Sure, here's a step-by-step guide in Markdown format:

## Setting Up and Running the Weather Application

### Prerequisites

- Python 3.6 or higher installed
- OpenSSL installed (for generating SSL certificates)

### Steps

1. **Install necessary Python libraries**

    Open a terminal and run the following command to install the necessary Python libraries:

    ```bash
    pip install websockets asyncio
    ```

    If you're using a specific Python environment or if you have both Python 2 and Python 3 installed, you might need to use `pip3` instead of `pip`.

2. **Generate a self-signed SSL certificate**

    In the terminal, run the following command:

    ```bash
    openssl req -x509 -newkey rsa:4096 -keyout localhost-key.pem -out localhost.pem -days 365 -nodes
    ```

    This command will generate a `localhost.pem` file (the certificate) and a `localhost-key.pem` file (the private key). These files should be in the same directory as your `server.py` and `client.py` files.

3. **Run the server**

    In the terminal, navigate to the directory containing your `server.py` file and run the following command:

    ```bash
    python server.py
    ```

    If you have both Python 2 and Python 3 installed, you might need to use `python3` instead of `python`.

4. **Run the client**

    Open a new terminal, navigate to the directory containing your `client.py` file and run the following command:

    ```bash
    python client.py
    ```

    If you have both Python 2 and Python 3 installed, you might need to use `python3` instead of `python`.

5. **Use the application**

    In the client terminal, you can now enter the name of a city to get its weather. To exit the application, type 'quit'.
