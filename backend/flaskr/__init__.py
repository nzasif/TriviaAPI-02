import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
from flask_cors import CORS
from sqlalchemy.orm import load_only
from sqlalchemy import select

from models import setup_db, db, Question, Category

NO_QUESTIONS_PER_PAGE = 10

# pagination setup
def get_paginated_qs(request, qsQuery):
    page = request.args.get('page', 1, type = int)
    
    start = (page - 1) * NO_QUESTIONS_PER_PAGE
    
    end = start + NO_QUESTIONS_PER_PAGE

    qs = [q.format() for q in qsQuery]

    current_qs = qs[start:end]
    
    return current_qs

def create_app(test_config=None):
    app = Flask(__name__)
    setup_db(app)

    CORS(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # get request for categories
    @app.route('/categories')
    def get_categories():
        categories_list = db.session.query(Category).order_by(Category.id).all()
    
        if len(categories_list) == 0:
            abort(404)

        return jsonify ({
            'success': True,
            'categories': {item.id: item.type for item in categories_list}
        })
    
    # This endpoint will return questions list
    @app.route('/questions')
    def get_trivia_questions():

        qsQuery = Question.query.order_by(Question.id).all()

        current_qs = get_paginated_qs(request, qsQuery)

        all_categories = Category.query.all()

        total_qs = len(qsQuery)

        if total_qs == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_qs,
            'total_questions': total_qs,
            'current_category': [],
            'categories': [cat.type for cat in all_categories],
        }), 200

    # remove question by id
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def remove_question(question_id):
        try:
            q = Question.query.filter(Question.id == question_id).one_or_none()

            # if there is no question then show 404 page
            if q == None:
                abort(404)
            
            # delete the question
            q.delete()

            # after deleting the question, requery the questions
            qsQuery = Question.query.order_by(Question.id).all()
            
            # paginate them before returning
            current_qs = get_paginated_qs(request, qsQuery)
            
            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_qs,
                'total_questions': len(qsQuery)
            })

        except Exception:
            abort(422)
    
    # POST a new question, and return new paginated list of questions
    @app.route('/questions', methods=['POST'])
    def add_new_question():

        # get json from the request body
        req_body = request.get_json()

        # get individual fields from the request body
        new_q = req_body.get('question', None)
        new_ans = req_body.get('answer', None)
        new_cat = req_body.get('category', None)
        new_difficulty = req_body.get('difficulty', None)

        try:
            ## initialize a new question
            question = Question(
                    question = new_q,
                    answer = new_ans,
                    category = new_cat,
                    difficulty = new_difficulty
                )
            # insert it into the db
            question.insert()

            # after inerting new question, re query the questions again
            qsQuery = Question.query.order_by(Question.id).all()
            
            current_qs = get_paginated_qs(request, qsQuery)

            qs_count = len(Question.query.all())

            return jsonify({
                'success': True,
                'questions': current_qs,
                'total_questions': qs_count
            })
                
        except Exception:
            abort(422)
    
    #####################################################################
    # This end point will return search result based on the search term #
    #####################################################################
    @app.route('/search')
    def search_question():
        req_body = request.get_json()
        search = req_body.get('searchTerm', None)

        if search:
            qs = Question.query.filter(Question.question.ilike(f'%{search}%')).all()
            current_qs = [question.format() for question in qs]
            total_qs = len(current_qs)

            return jsonify({
                'success': True,
                'questions': current_qs,
                'total_questions': total_qs,
            })           
    # get questions of a specific category
    @app.route('/categories/<int:cat_id>/questions')
    def questions_in_cat(cat_id):
        try:
            qsQuery = Question.query.filter(cat_id == Question.category).all()
    
            current_qs = get_paginated_qs(request, qsQuery)

            all_categories = Category.query.all()
            
            qs_list = list(current_qs)

            if cat_id > len(all_categories):
                abort(404)

            return jsonify({
                    "success": True,
                    "questions": qs_list,
                    "total_questions": len(qsQuery),
                    "current_category": [cat.type for cat in all_categories if cat.id == cat_id ]
                })
        except:
            abort(404)

    # ############################### #
    #         start the quizz         #
    # ############################### #
    @app.route('/quizzes', methods=['POST'])
    def start_trivia_quizz():
        try:
            req_body = request.get_json()
            quiz_category = req_body.get('quiz_category')
            prev_qs = req_body.get('previous_questions')
            cat_id = quiz_category['id']
            
            if cat_id == 0:
                qs = Question.query.filter(Question.id.notin_(prev_qs), 
                Question.category == cat_id).all()
            else:
                qs = Question.query.filter(Question.id.notin_(prev_qs)).all()
                
            q = None

            if(qs):
                q = random.choice(qs)

            return jsonify({
                'success': True,
                'question': q.format()
            })
        except:
            abort(422)

    # Error handler
    @app.errorhandler(404)
    def not_found(error):
        return( 
            jsonify({'success': False, 'error': 404,'message': 'requestedresource not found'}),
            404
        )
    
    @app.errorhandler(422)
    def unprocessed(error):
        return(
            jsonify({'success': False, 'error': 422,'message': 'your request cannot be processed'}),
            422
        )

    @app.errorhandler(400)
    def bad_request(error):
        return(
            jsonify({'success': False, 'error': 400,'message': 'this is a bad request'}),
            400
        )

    @app.errorhandler(405)
    def not_allowed(error):
        return(
            jsonify({'success': False, 'error': 405,'message': 'this method is not alllowed'}),
            405
        )

    return app

