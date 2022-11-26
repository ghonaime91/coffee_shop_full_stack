import sys
from flask import(
    Flask,
    request,
    jsonify,
    abort
)

from flask_cors import CORS
from .database.models import db_drop_and_create_all, setup_db, Drink

from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
 uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
!! Running this function will add one
'''
# with app.app_context():
#     db_drop_and_create_all()

# ROUTES
'''
 implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''

@app.route('/drinks')
def drinks():
    
    try:
        drinks   = Drink.query.all()
        
        return jsonify({
        "success": True,
        "drinks": [drink.short() for drink in drinks]
        }),200

    except Exception:
        print(sys.exc_info())
        abort(404)


'''
 implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth("get:drinks-detail")
def drinks_detail(jwt):
    try:
        drinks  = Drink.query.all()
    
        return jsonify({
            "success": True,
            "drinks": [drink.long() for drink in drinks]
        }),200

    except Exception:
        print(sys.exc_info())
        abort(404)


'''
  implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def post_drink(jwt):
    drink_data = request.get_json()

    if not ('title' in drink_data and 'recipe' in drink_data):
        abort(422)

    try:
        drink = Drink(
            title = drink_data.get('title'),
            recipe = drink_data.get('recipe')
            )
        drink.insert()

        print(drink.long())

        return jsonify({
        "success": True,
        "drinks": [drink.long()]
        }),200

    except Exception:
        print(sys.exc_info())
        abort(422)




'''
  implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''

@app.route("/drinks/<id>", methods=['PATCH'])
@requires_auth("patch:drinks")
def update_drink(jwt,id):
    drink_to_update = Drink.query.get_or_404(id)
    try:        
        new_data = request.get_json()
        
        if not('title' in new_data or 'recipe' in new_data):
            abort(422)
        
        title = new_data.get('title')
        recipe = new_data.get('recipe')
        
        if title:
            drink_to_update.title  = new_data.get('title')
        if recipe:
            drink_to_update.recipe = new_data.get('recipe')
            
        drink_to_update.update()
        
        return jsonify({
            "success":True,
            'drinks' :[drink_to_update.long()]
        }),200

    except Exception:
        print(sys.exc_info())
        abort(422)

'''
 implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>',methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drink(jwt,id):
    drink_to_delete = Drink.query.get_or_404(id)

    try:
        drink_to_delete.delete()
        return jsonify({
            "success":True,
            "delete":drink_to_delete.id
        }),200

    except Exception:
        print(sys.exc_info())
        abort(422)


# Error Handling

@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False,
        "error": 422,
        "message": "unprocessable"
    }), 422


'''
 implement error handler for 404
    error handler should conform to general task above
'''

@app.errorhandler(404)
def not_found(err):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404

'''
 implement error handler for 405
    error handler for Method Not Allowed
'''

@app.errorhandler(405)
def not_found(err):
    return jsonify({
        "success": False,
        "error": 405,
        "message": "Method Not Allowed"
    }), 405

'''
 implement error handler for AuthError
    error handler should conform to general task above
'''
@app.errorhandler(AuthError)
def handle_auth_error(err):
    
    return jsonify({
        "success": False,
        "error": err.status_code,
        'message': err.error
    }), err.status_code



