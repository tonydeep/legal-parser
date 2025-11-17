#!/usr/bin/env python3
"""
Vietnamese Legal Parser Web Demo
Flask backend API for parsing Vietnamese legal documents
"""

import os
import sys
import json
import traceback
from pathlib import Path
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Flask, render_template, request, jsonify, send_file

# Add current directory to path for parser imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from document_parser import VietnameseLegalParser, ParsedDocument
from cypher_generator import CypherGenerator

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['OUTPUT_FOLDER'] = 'outputs'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Allowed file extensions
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'docx', 'html', 'htm'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_file(filepath):
    """Extract text from various file formats"""
    ext = filepath.rsplit('.', 1)[1].lower()
    
    if ext == 'txt':
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    
    elif ext == 'pdf':
        try:
            import pdfplumber
            text = []
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text.append(page_text)
            return '\n'.join(text)
        except ImportError:
            return "Error: pdfplumber not installed. Run: pip install pdfplumber --break-system-packages"
    
    elif ext in ['docx']:
        try:
            from docx import Document
            doc = Document(filepath)
            text = [para.text for para in doc.paragraphs]
            return '\n'.join(text)
        except ImportError:
            return "Error: python-docx not installed. Run: pip install python-docx --break-system-packages"
    
    elif ext in ['html', 'htm']:
        try:
            from bs4 import BeautifulSoup
            with open(filepath, 'r', encoding='utf-8') as f:
                soup = BeautifulSoup(f, 'html.parser')
                for script in soup(['script', 'style']):
                    script.decompose()
                return soup.get_text(separator='\n', strip=True)
        except ImportError:
            return "Error: beautifulsoup4 not installed. Run: pip install beautifulsoup4 lxml --break-system-packages"
    
    return "Unsupported file format"

@app.route('/')
def index():
    """Main page"""
    return render_template('index.html')

@app.route('/api/parse', methods=['POST'])
def parse_document():
    """
    Parse document and return JSON summary
    Accepts: file upload or text content
    """
    try:
        text_content = None
        source = None
        
        # Check if file uploaded
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                
                # Extract text
                text_content = extract_text_from_file(filepath)
                source = filename
        
        # Check if text pasted
        elif 'text' in request.form or 'text' in request.json:
            data = request.json if request.is_json else request.form
            text_content = data.get('text', '')
            source = 'pasted_text'
        
        if not text_content:
            return jsonify({'error': 'No content provided'}), 400
        
        # Parse document
        parser = VietnameseLegalParser()
        parsed_doc = parser.parse_text(text_content)
        
        # Generate JSON summary
        json_summary = json.loads(parser.to_json_summary())
        
        # Store parsed doc for later use
        session_id = f"session_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        session_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{session_id}.json")
        
        with open(session_file, 'w', encoding='utf-8') as f:
            json.dump({
                'source': source,
                'timestamp': datetime.now().isoformat(),
                'parsed_doc': {
                    'metadata': json_summary['metadata'],
                    'structure': json_summary['structure_summary'],
                    'definitions': json_summary['definitions'],
                    'cross_references': json_summary['cross_references']
                }
            }, f, ensure_ascii=False, indent=2)
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'source': source,
            'summary': json_summary
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/generate-cypher', methods=['POST'])
def generate_cypher():
    """
    Generate Cypher script from parsed document
    Requires: text content or session_id
    """
    try:
        data = request.json if request.is_json else request.form
        
        # Get text content
        if 'text' in data:
            text_content = data['text']
            
            # Parse document
            parser = VietnameseLegalParser()
            parsed_doc = parser.parse_text(text_content)
        
        elif 'session_id' in data:
            session_id = data['session_id']
            session_file = os.path.join(app.config['OUTPUT_FOLDER'], f"{session_id}.json")
            
            if not os.path.exists(session_file):
                return jsonify({'error': 'Session not found'}), 404
            
            # Reload and parse again (since we can't serialize the full ParsedDocument)
            with open(session_file, 'r', encoding='utf-8') as f:
                session_data = json.load(f)
            
            # Need original text - for now return error
            return jsonify({'error': 'Please provide text content for Cypher generation'}), 400
        
        else:
            return jsonify({'error': 'No content or session provided'}), 400
        
        # Generate Cypher
        generator = CypherGenerator(parsed_doc)
        cypher_script = generator.generate_all()
        cypher_summary = json.loads(generator.to_json_summary())
        
        # Save Cypher script
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        cypher_filename = f"import_{timestamp}.cypher"
        cypher_filepath = os.path.join(app.config['OUTPUT_FOLDER'], cypher_filename)
        
        with open(cypher_filepath, 'w', encoding='utf-8') as f:
            f.write(cypher_script)
        
        return jsonify({
            'success': True,
            'filename': cypher_filename,
            'summary': cypher_summary,
            'download_url': f'/api/download/{cypher_filename}'
        })
    
    except Exception as e:
        return jsonify({
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/download/<filename>')
def download_file(filename):
    """Download generated Cypher file"""
    filepath = os.path.join(app.config['OUTPUT_FOLDER'], secure_filename(filename))
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'timestamp': datetime.now().isoformat(),
        'parser_available': True
    })

if __name__ == '__main__':
    # Create directories
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['OUTPUT_FOLDER'], exist_ok=True)
    
    # Run server
    app.run(host='0.0.0.0', port=5000, debug=True)
