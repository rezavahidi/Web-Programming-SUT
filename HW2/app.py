from flask import Flask, jsonify, request, abort
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///forms.db'
db = SQLAlchemy(app)

class Field(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    label = db.Column(db.String(100), nullable=False)
    field_type = db.Column(db.String(50), nullable=False)
    form_id = db.Column(db.Integer, db.ForeignKey('form.id'), nullable=False)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'label': self.label,
            'type': self.field_type
        }

class Form(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    publication_status = db.Column(db.Boolean, default=False)
    fields = db.relationship('Field', backref='form', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'publication_status': self.publication_status,
            'fields': [field.to_dict() for field in self.fields]
        }

with app.app_context():
    db.create_all()

@app.route('/forms/', methods=['GET'])
def get_forms():
    forms = Form.query.all()
    return jsonify([form.to_dict() for form in forms])

@app.route('/forms/', methods=['POST'])
def create_form():
    data = request.get_json()
    if not data or not 'name' in data:
        abort(400, description="Invalid data")

    new_form = Form(name=data['name'])

    if 'fields' in data:
        for field_data in data['fields']:
            field = Field(
                name=field_data['name'],
                label=field_data['label'],
                field_type=field_data['type'],
                form=new_form 
            )
            db.session.add(field)

    db.session.add(new_form)
    db.session.commit()

    return jsonify(new_form.to_dict()), 201

@app.route('/forms/<int:id>', methods=['GET'])
def get_form(id):
    form = Form.query.get_or_404(id)
    return jsonify(form.to_dict())

@app.route('/forms/<int:id>', methods=['PUT'])
def update_form(id):
    form = Form.query.get_or_404(id)
    data = request.get_json()

    if 'name' in data:
        form.name = data['name']
    if 'fields' in data:
        form.fields = []
        for field_data in data['fields']:
            field = Field(name=field_data['name'], label=field_data['label'], field_type=field_data['type'], form_id=form.id)
            form.fields.append(field)

    db.session.commit()
    return jsonify(form.to_dict())

@app.route('/forms/<int:id>', methods=['DELETE'])
def delete_form(id):
    form = Form.query.get_or_404(id)
    db.session.delete(form)
    db.session.commit()
    return '', 204

@app.route('/forms/<int:id>/publish', methods=['POST'])
def publish_form(id):
    form = Form.query.get_or_404(id)
    form.publication_status = not form.publication_status
    db.session.commit()
    return jsonify(form.to_dict())

@app.route('/forms/published', methods=['GET'])
def get_published_forms():
    published_forms = Form.query.filter_by(publication_status=True).all()
    return jsonify([form.to_dict() for form in published_forms])

if __name__ == '__main__':
    app.run(debug=True)