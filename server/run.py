from app import app, config

app.run(host=config["ip_address"], port=config["port"], debug=True)