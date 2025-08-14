from flask import Flask, render_template, request, jsonify
from nlp_parser import parse_question

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    question = (request.form.get('question') or '').strip()
    if not question:
        return jsonify({"error": "Question is required."}), 400
    try:
        answer = parse_question(question)
        # Normalize error shape coming from parser
        if isinstance(answer, list) and len(answer) == 1 and isinstance(answer[0], dict) and 'error' in answer[0]:
            return jsonify({"error": answer[0]['error']}), 400
        return jsonify({"data": answer})
    except Exception as e:
        app.logger.exception("Error handling /ask request")
        return jsonify({"error": "Internal server error.", "details": str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    app.run(debug=True)
