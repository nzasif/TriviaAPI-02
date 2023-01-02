import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
import random
from flask_cors import CORS
from sqlalchemy.orm import load_only
from sqlalchemy import select

from models import setup_db, db, Question, Category

QUESTIONS_PER_PAGE = 10

def paginate_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]
    return current_questions

def create_app(test_config=None):
    # create and configure the app
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
        categories = db.session.query(Category).order_by(Category.id).all()
    
        if len(categories) == 0:
            abort(404)

        return jsonify ({
            'success': True,
            'categories': {item.id: item.type for item in categories}
        })
    
    # this return questions list
    @app.route('/questions')
    def get_questions():
        selection = Question.query.order_by(Question.id).all()
        current_questions = paginate_questions(request, selection)

        if len(current_questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_questions,
            'total_questions': len(selection),
            'current_category': [],
            'categories': [cat.type for cat in Category.query.all()],
        }), 200

    # delete question by id
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_question(question_id):
        try:
            question = Question.query.filter(
                Question.id == question_id).one_or_none()

            if question is None:
                abort(404)

            question.delete()
            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate_questions(request, selection)
            return jsonify({
                'success': True,
                'deleted': question_id,
                'questions': current_questions,
                'total_questions': len(selection)
            })

        except Exception:
            abort(422)
    
    # POST a new question/ or search for questions
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()

        new_question = body.get('question', None)
        new_answer = body.get('answer', None)
        new_category = body.get('category', None)
        new_difficulty = body.get('difficulty', None)
        search = body.get('searchTerm', None)

        try:
            if search:
                questions = Question.query.filter(
                    Question.question.ilike(f'%{search}%')
                ).all()

                current_questions = [question.format()
                                     for question in questions]
                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(current_questions),
                })

            else:
                question = Question(
                    question=new_question,
                    answer=new_answer,
                    category=new_category,
                    difficulty=new_difficulty
                )
                question.insert()

                selection = Question.query.order_by(Question.id).all()
                current_questions = paginate_questions(request, selection)

                return jsonify({
                    'success': True,
                    'questions': current_questions,
                    'total_questions': len(Question.query.all())
                })
        except Exception:
            abort(422)

    @app.route('/categories/<int:category_id>/questions')
    def category_questions(category_id):
        try:
            selection = Question.query.filter(category_id == Question.category).all()
    
            current_questions = paginate_questions(request, selection)
            categories = Category.query.all()

            if category_id > len(categories):
                abort(404)

            return jsonify({
                    "success": True,
                    "questions": list(current_questions),
                    "total_questions": len(selection),
                    "current_category": [cat.type for cat in categories if cat.id == category_id ]
                })
        except:
            abort(404)

    @app.route('/quizzes', methods=['POST'])
    def start_trivia():
        try:
            body = request.get_json()
            quiz_category = body.get('quiz_category')
            previous_questions = body.get('previous_questions')
            category_id = quiz_category['id']
            
            if category_id == 0:
                questions = Question.query.filter(Question.id.notin_(previous_questions), 
                Question.category == category_id).all()
            else:
                questions = Question.query.filter(Question.id.notin_(previous_questions), 
                Question.category == category_id).all()
            question = None
            if(questions):
                question = random.choice(questions)

            return jsonify({
                'success': True,
                'question': question.format()
            })
        except:
            abort(422)
    @app.errorhandler(404)
    def not_found(error):
        return( 
            jsonify({'success': False, 'error': 404,'message': 'resource not found'}),
            404
        )
    
    @app.errorhandler(422)
    def unprocessed(error):
        return(
            jsonify({'success': False, 'error': 422,'message': 'request cannot be processed'}),
            422
        )

    @app.errorhandler(400)
    def bad_request(error):
        return(
            jsonify({'success': False, 'error': 400,'message': 'bad request'}),
            400
        )

    @app.errorhandler(405)
    def not_allowed(error):
        return(
            jsonify({'success': False, 'error': 405,'message': 'method not alllowed'}),
            405
        )

    return app


