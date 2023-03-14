from flask import Flask, request, render_template, send_file, abort, jsonify, session
from inference import vits_inference
import baidu_translate
import openai_api
from io import BytesIO
import waitress

vits_model = vits_inference("atri")

app = Flask(__name__)
app.config.from_object("config")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/synthesis", methods=["GET"])
def synthesis():
    text = request.args.get("text", type=str)
    try:
        output_audio = BytesIO()
        vits_model.synthesis(output_audio, text, -1)
        return send_file(output_audio, mimetype="audio/wav")
    except:
        abort(500)


@app.route("/translate", methods=["GET"])
def translate():
    text = request.args.get("text", type=str)
    return jsonify(baidu_translate.translate(text))


@app.route("/transcript", methods=["POST"])
def transcript():
    language = request.args.get("language", default="", type=str)
    audio = BytesIO(request.files["audio"].stream.read())
    audio.name = "audio.wav"
    return jsonify(openai_api.transcript(audio, language))


@app.route("/chat_complete", methods=["GET"])
def chat_complete():
    context = session.get("context", [])
    text = request.args.get("text", type=str)
    if text.strip():
        new_context, message = openai_api.chat_complete(context, text)
        if message:
            session["context"] = new_context
            return jsonify(code=0, message=message)
        else:
            return jsonify(code=500)
    else:
        return jsonify(code=400)


@app.route("/reset_context", methods=["GET"])
def reset_context():
    session["context"] = []
    return jsonify(code=0)


if __name__ == "__main__":
    # app.run(debug=False, host="0.0.0.0", port=8080)
    waitress.serve(app, host="0.0.0.0", port=8080)
