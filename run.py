from app import create_app

app = create_app()

if __name__ == "__main__":
    # for teaching purpose only, do not expose publicly
    app.run(host="127.0.0.1", port=5001, debug=True)
