# app.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_cors import CORS
from datetime import datetime, timezone
from dateutil import parser
import os
import shutil

app = Flask(__name__)
app.config.from_object('config.Config')

CORS(app)  # Enable CORS for all routes

db = SQLAlchemy(app)
migrate = Migrate(app, db)

from models import FileRecord

@app.route('/move_files', methods=['POST'])
def move_files():
    try:
        data = request.get_json()
        src_folder = data['src_folder']
        dest_folder = data['dest_folder']
        cutoff_date = parser.parse(data['cutoff_date'])

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        files_moved = []

        for filename in os.listdir(src_folder):
            file_path = os.path.join(src_folder, filename)
            if os.path.isfile(file_path):
                file_mod_time = datetime.fromtimestamp(os.path.getmtime(file_path), tz=timezone.utc)
                if file_mod_time < cutoff_date:
                    shutil.move(file_path, os.path.join(dest_folder, filename))
                    files_moved.append(filename)
                    new_record = FileRecord(
                        filename=filename,
                        src_folder=src_folder,
                        dest_folder=dest_folder,
                        moved_at=datetime.now(tz=timezone.utc),
                        isMoved=True
                    )
                    db.session.add(new_record)
                    db.session.commit()

        return jsonify({'files_moved': files_moved}), 200

    except Exception as e:
        app.logger.error(f"Error occurred: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/file_records', methods=['GET'])
def get_file_records():
    records = FileRecord.query.all()
    result = [{'id': record.id, 'filename': record.filename, 'src_folder': record.src_folder, 'dest_folder': record.dest_folder, 'moved_at': record.moved_at, 'isMoved': record.isMoved} for record in records]
    return jsonify(result)

@app.route('/search_records', methods=['GET'])
def search_records():
    filename = request.args.get('filename')
    isMoved = request.args.get('isMoved')
    moved_at = request.args.get('moved_at')
    performed_at = request.args.get('performed_at')

    query = FileRecord.query

    if filename:
        query = query.filter(FileRecord.filename.like(f"%{filename}%"))
    if isMoved:
        query = query.filter_by(isMoved=isMoved.lower() == 'true')
    if moved_at:
        moved_date = datetime.strptime(moved_at, '%Y-%m-%d')
        query = query.filter(db.func.date(FileRecord.moved_at) == moved_date)
    if performed_at:
        performed_date = datetime.strptime(performed_at, '%Y-%m-%d')
        query = query.filter(db.func.date(FileRecord.moved_at) == performed_date)

    records = query.all()
    result = [{'id': record.id, 'filename': record.filename, 'src_folder': record.src_folder, 'dest_folder': record.dest_folder, 'moved_at': record.moved_at, 'isMoved': record.isMoved} for record in records]
    
    return jsonify(result)

@app.route('/delete_record/<int:id>', methods=['DELETE'])
def delete_record(id):
    record = FileRecord.query.get_or_404(id)
    db.session.delete(record)
    db.session.commit()
    return jsonify({'message': 'Record deleted successfully'}), 200

if __name__ == '__main__':
    app.run(debug=True)
