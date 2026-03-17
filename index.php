<?php
/**
 * Laragon index file for MiniScrape
 * This file will redirect to the Flask application or provide instructions
 */

// Check if Flask server is running
$flask_running = @file_get_contents('http://localhost:5000');

if ($flask_running !== false) {
    // If Flask is running, redirect to the application
    header('Location: http://localhost:5000');
    exit;
} else {
    // If Flask is not running, show instructions
    ?>
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>MiniScrape - Web Application</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }
            
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 20px;
            }
            
            .container {
                background: white;
                border-radius: 12px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                max-width: 600px;
                width: 100%;
                padding: 40px;
            }
            
            h1 {
                color: #333;
                margin-bottom: 20px;
                font-size: 2.5em;
                text-align: center;
            }
            
            .instructions {
                background: #f8f9fa;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            
            .instructions h2 {
                color: #495057;
                margin-bottom: 15px;
                font-size: 1.2em;
            }
            
            .instructions ul {
                list-style: none;
                padding-left: 0;
            }
            
            .instructions li {
                padding: 10px 0;
                border-bottom: 1px solid #dee2e6;
            }
            
            .instructions li:last-child {
                border-bottom: none;
            }
            
            .instructions li::before {
                content: '→ ';
                color: #007bff;
                font-weight: bold;
            }
            
            .button {
                display: inline-block;
                background: #007bff;
                color: white;
                padding: 12px 24px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 500;
                transition: background 0.3s;
                margin: 5px;
            }
            
            .button:hover {
                background: #0056b3;
            }
            
            .button.secondary {
                background: #6c757d;
            }
            
            .button.secondary:hover {
                background: #545b62;
            }
            
            .buttons {
                text-align: center;
                margin-top: 20px;
            }
            
            .status {
                text-align: center;
                padding: 10px;
                background: #ffc107;
                color: #333;
                border-radius: 6px;
                margin-bottom: 20px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>MiniScrape</h1>
            
            <div class="status">
                <strong>Flask Server is NOT running</strong>
            </div>
            
            <div class="instructions">
                <h2>To start the MiniScrape application:</h2>
                <ul>
                    <li>Open a command prompt or terminal</li>
                    <li>Navigate to the MiniScrape project directory</li>
                    <li>Run: <code>python app.py</code></li>
                    <li>Wait for the server to start (you will see "Debugger is active!")</li>
                    <li>Refresh this page</li>
                </ul>
            </div>
            
            <div class="instructions">
                <h2>Alternative Methods:</h2>
                <ul>
                    <li>Double-click <code>run.bat</code> to start the application</li>
                    <li>Use <code>main.py</code> for the interactive CLI interface</li>
                    <li>Run tests using <code>python test_comprehensive.py</code></li>
                </ul>
            </div>
            
            <div class="buttons">
                <a href="http://localhost:5000" class="button">Try Again</a>
                <a href="#" class="button secondary" onclick="window.location.reload()">Refresh Page</a>
            </div>
        </div>
    </body>
    </html>
    <?php
}
?>
