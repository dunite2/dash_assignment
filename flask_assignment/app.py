from flask import Flask, request, render_template, send_file, flash, redirect, url_for
from PIL import Image
import pyqrcode
import os
import io
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Change this in production

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'webp'}
OUTPUT_FORMATS = ['PNG', 'JPEG', 'GIF', 'BMP', 'TIFF', 'WEBP']

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def index():
    """Display usage instructions for all routes"""
    return render_template('index.html', output_formats=OUTPUT_FORMATS)

@app.route('/convert', methods=['POST'])
def convert_image():
    """Convert an image from one format to another using Pillow"""
    try:
        # Check if file was uploaded
        if 'image' not in request.files:
            flash('No image file provided')
            return redirect(url_for('index'))
        
        file = request.files['image']
        output_format = request.form.get('output_format', 'PNG').upper()
        
        # Check if file is selected
        if file.filename == '':
            flash('No file selected')
            return redirect(url_for('index'))
        
        # Check if output format is valid
        if output_format not in OUTPUT_FORMATS:
            flash(f'Invalid output format. Supported formats: {", ".join(OUTPUT_FORMATS)}')
            return redirect(url_for('index'))
        
        # Check if file is allowed
        if file and allowed_file(file.filename):
            # Open and convert the image
            img = Image.open(file.stream)
            
            # Convert to RGB if saving as JPEG (JPEG doesn't support transparency)
            if output_format == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Save converted image to memory
            img_buffer = io.BytesIO()
            img.save(img_buffer, format=output_format)
            img_buffer.seek(0)
            
            # Generate filename
            original_name = secure_filename(file.filename)
            name_without_ext = os.path.splitext(original_name)[0]
            new_filename = f"{name_without_ext}_converted.{output_format.lower()}"
            
            return send_file(
                img_buffer,
                as_attachment=True,
                download_name=new_filename,
                mimetype=f'image/{output_format.lower()}'
            )
        
        else:
            flash('Invalid file type. Supported formats: PNG, JPG, JPEG, GIF, BMP, TIFF, WEBP')
            return redirect(url_for('index'))
    
    except Exception as e:
        flash(f'Error converting image: {str(e)}')
        return redirect(url_for('index'))

@app.route('/generate_qr', methods=['GET', 'POST'])
def generate_qr():
    """Generate QR code using pyqrcode package"""
    if request.method == 'GET':
        return render_template('qr_form.html')
    
    try:
        # Get user input
        text_data = request.form.get('text_data', '').strip()
        error_correction = request.form.get('error_correction', 'M')
        scale = int(request.form.get('scale', 8))
        
        if not text_data:
            flash('Please provide text data to generate QR code')
            return redirect(url_for('generate_qr'))
        
        # Generate QR code using pyqrcode
        qr = pyqrcode.create(text_data, error=error_correction)
        
        # Create PNG buffer
        buffer = io.BytesIO()
        qr.png(buffer, scale=scale)
        buffer.seek(0)
        
        # Generate filename
        safe_text = "".join(c for c in text_data[:20] if c.isalnum() or c in (' ', '-', '_')).rstrip()
        filename = f"qr_code_{safe_text.replace(' ', '_')}.png"
        
        return send_file(
            buffer,
            as_attachment=True,
            download_name=filename,
            mimetype='image/png'
        )
    
    except Exception as e:
        flash(f'Error generating QR code: {str(e)}')
        return redirect(url_for('generate_qr'))

if __name__ == '__main__':
    app.run(debug=True)
