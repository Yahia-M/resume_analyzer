from pyngrok import conf, ngrok

def setup_ngrok_tunnel():
    NGROK_AUTHTOKEN = "1n76FUumd6izNoyPXqq5DFZcCw8_4NDTBxaXbgfGwyEEh6oiF"
    conf.get_default().auth_token = NGROK_AUTHTOKEN

    tunnel_config = {
        "name": "streamlit-tunnel",
        "addr": "8504",
        "proto": "http"
    }

    public_url = ngrok.connect(**tunnel_config)
    print(f"Streamlit App URL: {public_url}")