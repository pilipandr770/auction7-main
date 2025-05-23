from app import create_app
import os

app = create_app()

if __name__ == "__main__":
    # Default port is set to 5050 for development, 10000 for production
    default_port = int(os.environ.get("PORT", 10000)) if os.environ.get("RENDER") else 5050
    port = int(os.environ.get("PORT", default_port))
    print(f"Starting server on port {port}")
    app.run(host="0.0.0.0", port=port, debug=False)