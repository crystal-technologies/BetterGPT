from flask import Flask, request, render_template, send_file
import datetime
import threading
import CRYSTAL

app = Flask(__name__)

def get_time():
    currentTime = datetime.datetime.now()
    formatted_time = "{}:{}:{} {}"

    if currentTime.hour < 13:
        hour = currentTime.hour
        meredian = "AM"
    else:
        hour = currentTime.hour - 12
        meredian = "PM"

    formatted_time = f"{hour}:{currentTime.minute}:{currentTime.second} {meredian}"
    return formatted_time

@app.after_request
def add_ngrok_header(response):
    response.headers['ngrok-skip-browser-warning'] = 'true'
    return response

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/reply.txt')
def serve_reply():
    return send_file('reply.txt')

@app.route('/write-file', methods=['POST'])
def write_file():
    data = request.get_json()
    filename = data.get('filename')
    file_content = data.get('data')

    try:
        with open(filename, 'w') as file:
            file.write(file_content)
        return 'File written successfully', 200
    except Exception as e:
        return str(e), 500

def flask_app_runner():
    app.run(port=7777)

def answer():
    chat_history = []
    while True:
        with open('query.txt', 'r') as query_file:
            query_data = query_file.read()
        with open('parameters.txt', 'r') as param_file:
            params = [float(parameter) if "." in parameter else int(parameter) for parameter in param_file.readlines()]
        if query_data != "":
            response, chat_history = CRYSTAL.ask_crystal(query_data, chat_history, f"Time: {get_time()}", username="User", finetune_param=params)
            with open("query.txt", "w") as clear_file:
                clear_file.write("")
        else:
            pass



if __name__ == '__main__':
    flask_thread = threading.Thread(target=flask_app_runner)
    flask_thread.start()

    main_thread = threading.Thread(target=answer)
    main_thread.start()
