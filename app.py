#!/usr/bin/env python3
"""
MiniScrape Web Application
A Flask-based web interface for company information scraping
"""

import os
import sys
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import TextAreaField, SubmitField, RadioField
from wtforms.validators import DataRequired
import pandas as pd
from io import BytesIO
import tempfile
import threading
import time

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from fast_scraper import scrape
from main import load_queries

app = Flask(__name__)
app.config['SECRET_KEY'] = 'miniscrape-secret-key'
app.config['UPLOAD_FOLDER'] = tempfile.gettempdir()


class ScrapingForm(FlaskForm):
    """Form for scraping URLs"""
    urls = TextAreaField('Web Addresses (one per line or comma-separated)', 
                       validators=[DataRequired()])
    file = FileField('Or upload file (.txt or .xlsx)', 
                    validators=[FileAllowed(['txt', 'xlsx', 'xls'], 'Text or Excel files only')])
    search_mode = RadioField('Search mode',
                    choices=[('fast', 'Fast (homepage parse only)'), ('deep', 'Deep (CH + search + AI)')],
                    default='fast',
                    validators=[DataRequired()])
    submit = SubmitField('Scrape')


class ResultsForm(FlaskForm):
    """Form for results"""
    export_csv = SubmitField('Export to CSV')
    export_xlsx = SubmitField('Export to Excel')


@app.route('/', methods=['GET', 'POST'])
def index():
    """Main page with scraping form"""
    form = ScrapingForm()
    print("Form submitted:", request.method)
    print("Form data:", request.form)
    print("Form errors:", form.errors)
    if form.validate_on_submit():
        # Get URLs from form
        urls = []
        
        # From text area
        if form.urls.data.strip():
            # Split by commas or newlines
            raw_text = form.urls.data.strip()
            # Replace newlines with commas and split
            for url in raw_text.replace('\n', ',').split(','):
                url = url.strip()
                if url:
                    # Add http:// if no protocol is specified
                    if not url.startswith('http://') and not url.startswith('https://'):
                        url = 'https://' + url
                    urls.append(url)
        
        # From file
        if form.file.data:
            # Save file temporarily
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_upload')
            form.file.data.save(temp_path)
            
            try:
                file_urls = load_queries(temp_path)
                urls.extend(file_urls)
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except:
                        pass
        
        # Remove duplicates
        urls = list(dict.fromkeys(urls))
        
        if not urls:
            flash('Please enter at least one URL or upload a file with URLs', 'error')
            return render_template('index.html', form=form)
        
        scrape_mode = form.search_mode.data or 'fast'
        scrape_fn = None
        if scrape_mode == 'deep':
            from scraper import scrape as deep_scrape
            scrape_fn = deep_scrape
        else:
            from fast_scraper import scrape as fast_scrape
            scrape_fn = fast_scrape

        # Scrape URLs (in background or foreground)
        results = []
        for url in urls:
            try:
                result = scrape_fn(url)
                results.append({
                    'url': url,
                    'company_name': result.get('company_name', ''),
                    'address': result.get('address', ''),
                    'officer': result.get('officer', ''),
                    'source': result.get('source', ''),
                    'search_mode': scrape_mode
                })
            except Exception as e:
                results.append({
                    'url': url,
                    'company_name': f'ERROR: {str(e)}',
                    'address': '',
                    'officer': '',
                    'source': ''
                })
        
        # Store results in session or temp file
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8-sig')
        df = pd.DataFrame(results)
        df.to_csv(temp_file.name, index=False)
        temp_file.close()
        
        # Parse officers into first/last name
        results_with_names = []
        for result in results:
            officer = result['officer']
            first = ''
            last = ''
            if officer and not officer.startswith('ERROR'):
                parts = officer.split()
                if len(parts) >= 2:
                    first = parts[0]
                    last = ' '.join(parts[1:])
                elif parts:
                    first = parts[0]
            
            results_with_names.append({
                **result,
                'officer_first': first,
                'officer_last': last
            })
        
        return render_template('results.html', results=results_with_names, csv_file=os.path.basename(temp_file.name))
    
    return render_template('index.html', form=form)


@app.route('/export/<filename>')
def export(filename):
    """Export results to file"""
    file_path = os.path.join(tempfile.gettempdir(), filename)
    
    if not os.path.exists(file_path):
        flash('File not found', 'error')
        return redirect('/')
    
    try:
        # Determine export format from query string
        format_ = request.args.get('format', 'csv')
        
        if format_ == 'xlsx':
            # Convert CSV to Excel
            df = pd.read_csv(file_path)
            output = BytesIO()
            df.to_excel(output, index=False)
            output.seek(0)
            return send_file(
                output,
                as_attachment=True,
                download_name='miniscrape_results.xlsx',
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
        else:
            # Return CSV directly
            return send_file(
                file_path,
                as_attachment=True,
                download_name='miniscrape_results.csv',
                mimetype='text/csv'
            )
    
    except Exception as e:
        flash(f'Error exporting file: {str(e)}', 'error')
        return redirect('/')
    finally:
        # Cleanup
        try:
            os.remove(file_path)
        except:
            pass


@app.route('/scrape/<path:url>', methods=['GET'])
def scrape_single(url):
    """Scrape a single URL (API endpoint)"""
    try:
        from urllib.parse import unquote
        url = unquote(url)
        result = scrape(url)
        
        # Parse officer name
        officer = result.get('officer', '')
        first = ''
        last = ''
        if officer:
            parts = officer.split()
            if len(parts) >= 2:
                first = parts[0]
                last = ' '.join(parts[1:])
            elif parts:
                first = parts[0]
        
        return jsonify({
            'url': url,
            'company_name': result.get('company_name', ''),
            'address': result.get('address', ''),
            'officer_first': first,
            'officer_last': last,
            'officer': officer,
            'source': result.get('source', '')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/feedback', methods=['POST'])
def feedback():
    """Save corrected data so the scraper learns from mistakes."""
    payload = request.get_json(silent=True) or {}
    url = payload.get('url') or ''
    company_name = payload.get('company_name', '').strip()
    address = payload.get('address', '').strip()
    officer = payload.get('officer', '').strip()

    if not url or not company_name or not address or not officer:
        return jsonify({'success': False, 'message': 'url, company_name, address, officer required'}), 400

    try:
        from scraper import store_learning_correction as sc_store
        from fast_scraper import store_learning_correction as fs_store
        sc_ok = sc_store(url, {
            'company_name': company_name,
            'address': address,
            'officer': officer,
            'source': 'UserCorrection'
        })
        fs_ok = fs_store(url, {
            'company_name': company_name,
            'address': address,
            'officer': officer,
            'source': 'UserCorrection'
        })
        if sc_ok or fs_ok:
            return jsonify({'success': True, 'message': 'Feedback saved successfully'})
        return jsonify({'success': False, 'message': 'Failed to save feedback'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/correct', methods=['POST'])
def correct_result():
    data = request.get_json(silent=True) or {}
    url = data.get('url')
    company_name = data.get('company_name', '').strip()
    address = data.get('address', '').strip()
    officer = data.get('officer', '').strip()

    if not url or not company_name or not address or not officer:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    try:
        from scraper import store_learning_correction as sc_store
        from fast_scraper import store_learning_correction as fs_store
        sc_ok = sc_store(url, {
            'company_name': company_name,
            'address': address,
            'officer': officer,
            'source': 'UserCorrect'
        })
        fs_ok = fs_store(url, {
            'company_name': company_name,
            'address': address,
            'officer': officer,
            'source': 'UserCorrect'
        })
        if sc_ok or fs_ok:
            return jsonify({'success': True, 'message': 'Correction cached'})
        return jsonify({'success': False, 'message': 'Could not cache correction'}), 500
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/clear_and_retry', methods=['POST'])
def clear_and_retry():
    data = request.get_json(silent=True) or {}
    urls = data.get('urls', [])
    mode = data.get('mode', 'fast')
    if not urls or not isinstance(urls, list):
        return jsonify({'success': False, 'message': 'Missing urls list'}), 400

    def parse_officer(officer):
        if not officer or not isinstance(officer, str):
            return '', ''
        parts = officer.strip().split()
        if len(parts) >= 2:
            return parts[0], ' '.join(parts[1:])
        if parts:
            return parts[0], ''
        return '', ''

    try:
        from scraper import clear_learning_entry as sc_clear, scrape as deep_scrape
        from fast_scraper import clear_learning_entry as fs_clear, scrape as fast_scrape

        results = []

        for url in urls:
            sc_clear(url)
            fs_clear(url)

            primary_fn = deep_scrape if mode == 'deep' else fast_scrape
            fallback_fn = fast_scrape if mode == 'deep' else deep_scrape

            res = primary_fn(url)
            needs_fallback = False
            if not res.get('company_name') or res.get('company_name').startswith('ERROR') or not res.get('address'):
                needs_fallback = True

            if needs_fallback:
                fallback_res = fallback_fn(url)
                if fallback_res and (fallback_res.get('company_name') or fallback_res.get('address') or fallback_res.get('officer')):
                    # keep corrected source if produced by user correction
                    res = fallback_res

            officer_first, officer_last = parse_officer(res.get('officer', ''))
            results.append({
                'url': url,
                'company_name': res.get('company_name', ''),
                'address': res.get('address', ''),
                'officer': res.get('officer', ''),
                'officer_first': officer_first,
                'officer_last': officer_last,
                'source': res.get('source', ''),
                'search_mode': mode
            })

        return jsonify({'success': True, 'results': results})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/about')
def about():
    """About page"""
    return render_template('about.html')


@app.errorhandler(404)
def not_found(error):
    """404 error handler"""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(error):
    """500 error handler"""
    return render_template('500.html'), 500


if __name__ == '__main__':
    # Run on 0.0.0.0 to be accessible from network
    app.run(host='0.0.0.0', port=5000, debug=True)
