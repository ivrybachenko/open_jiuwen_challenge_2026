# Extract the port value from the [server] section of config.ini
# Parse the INI file to find the port in the [server] section

python3 << 'EOF'
import configparser

config = configparser.ConfigParser()
config.read('config.ini')

if 'server' in config:
    if 'port' in config['server']:
        port = config['server']['port']
        with open('answer.txt', 'w') as f:
            f.write(port)
        print(f"Port found: {port}")
    else:
        with open('answer.txt', 'w') as f:
            f.write("IMPOSSIBLE\nNo port key in [server] section")
        print("No port key in [server] section")
else:
    with open('answer.txt', 'w') as f:
        f.write("IMPOSSIBLE\nNo [server] section in config.ini")
    print("No [server] section in config.ini")
EOF