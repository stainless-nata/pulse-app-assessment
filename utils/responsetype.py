def response(message = None, data = None, status = 200):
    return {'data': data, 'status': status, 'message': message}