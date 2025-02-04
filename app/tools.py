from flask import jsonify

def response_template(success, message, data=None, status_code=200):
    response = jsonify({"success": success, "message": message, "data": data})
    response.status_code = status_code
    return response
