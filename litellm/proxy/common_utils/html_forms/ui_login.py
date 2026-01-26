import base64
import os
from pathlib import Path

url_to_redirect_to = os.getenv("PROXY_BASE_URL", "")
server_root_path = os.getenv("SERVER_ROOT_PATH", "")
if server_root_path != "":
    url_to_redirect_to += server_root_path
url_to_redirect_to += "/login"

# Load logo as base64
logo_path = Path(__file__).parent / "logo.jpg"
logo_base64 = ""
if logo_path.exists():
    with open(logo_path, "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode("utf-8")

# Load favicon as base64
favicon_path = Path(__file__).parent / "favicon.png"
favicon_base64 = ""
if favicon_path.exists():
    with open(favicon_path, "rb") as f:
        favicon_base64 = base64.b64encode(f.read()).decode("utf-8")

logo_img_tag = f'<img src="data:image/jpeg;base64,{logo_base64}" alt="to64.ai" class="logo-img">' if logo_base64 else '<div class="logo">to64.ai</div>'
favicon_link = f'<link rel="icon" type="image/png" href="data:image/png;base64,{favicon_base64}">' if favicon_base64 else ''

html_form = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>to64 Login</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    {favicon_link}
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background-color: #f8fafc;
            margin: 0;
            padding: 20px;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            color: #333;
        }}

        form {{
            background-color: #fff;
            padding: 40px;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            width: 450px;
            max-width: 100%;
        }}

        .logo-container {{
            text-align: center;
            margin-bottom: 30px;
        }}

        .logo {{
            font-size: 24px;
            font-weight: 600;
            color: #1e293b;
        }}

        .logo-img {{
            max-width: 150px;
            max-height: 60px;
            object-fit: contain;
        }}

        h2 {{
            margin: 0 0 10px;
            color: #1e293b;
            font-size: 28px;
            font-weight: 600;
            text-align: center;
        }}

        .subtitle {{
            color: #64748b;
            margin: 0 0 20px;
            font-size: 16px;
            text-align: center;
        }}

        .info-box {{
            background-color: #f1f5f9;
            border-radius: 6px;
            padding: 20px;
            margin-bottom: 30px;
            border-left: 4px solid #2563eb;
        }}

        .info-header {{
            display: flex;
            align-items: center;
            margin-bottom: 12px;
            color: #1e40af;
            font-weight: 600;
            font-size: 16px;
        }}

        .info-header svg {{
            margin-right: 8px;
        }}

        .info-box p {{
            color: #475569;
            margin: 8px 0;
            line-height: 1.5;
            font-size: 14px;
        }}

        label {{
            display: block;
            margin-bottom: 8px;
            font-weight: 500;
            color: #334155;
            font-size: 14px;
        }}

        .required {{
            color: #dc2626;
            margin-left: 2px;
        }}

        input[type="text"],
        input[type="password"] {{
            width: 100%;
            padding: 10px 14px;
            margin-bottom: 20px;
            box-sizing: border-box;
            border: 1px solid #e2e8f0;
            border-radius: 6px;
            font-size: 15px;
            color: #1e293b;
            background-color: #fff;
            transition: border-color 0.2s, box-shadow 0.2s;
        }}

        input[type="text"]:focus,
        input[type="password"]:focus {{
            outline: none;
            border-color: #3b82f6;
            box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2);
        }}

        .toggle-password {{
            display: flex;
            align-items: center;
            margin-top: -15px;
            margin-bottom: 20px;
        }}

        .toggle-password input[type="checkbox"] {{
            margin-right: 8px;
            vertical-align: middle;
            width: 16px;
            height: 16px;
        }}

        .toggle-password label {{
            margin-bottom: 0;
            font-size: 14px;
            cursor: pointer;
            line-height: 1;
        }}

        input[type="submit"] {{
            background-color: #6466E9;
            color: #fff;
            cursor: pointer;
            font-weight: 500;
            border: none;
            padding: 10px 16px;
            transition: background-color 0.2s;
            border-radius: 6px;
            margin-top: 10px;
            font-size: 14px;
            width: 100%;
        }}

        input[type="submit"]:hover {{
            background-color: #4138C2;
        }}

        a {{
            color: #3b82f6;
            text-decoration: none;
        }}

        a:hover {{
            text-decoration: underline;
        }}

        code {{
            background-color: #f1f5f9;
            padding: 2px 4px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 13px;
            color: #334155;
        }}

        .help-text {{
            color: #64748b;
            font-size: 14px;
            margin-top: -12px;
            margin-bottom: 20px;
        }}
    </style>
</head>
<body>
    <form action="{url_to_redirect_to}" method="post">
        <div class="logo-container">
            {logo_img_tag}
        </div>
        <h2>Login</h2>
        <p class="subtitle">Access your to64 VPA Admin UI.</p>
        <div class="info-box">
            <div class="info-header">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <circle cx="12" cy="12" r="10"></circle>
                    <line x1="12" y1="16" x2="12" y2="12"></line>
                    <line x1="12" y1="8" x2="12.01" y2="8"></line>
                </svg>
                Default Credentials
            </div>
            <p>By default, Username is <code>admin</code> and Password is your set Proxy <code>MASTER_KEY</code>.</p>
            <p>Need to set UI credentials or SSO? <a href="https://docs.to64.ai/docs/proxy/ui" target="_blank">Check the documentation</a>.</p>
        </div>
        <label for="username">Username<span class="required">*</span></label>
        <input type="text" id="username" name="username" required placeholder="Enter your username" autocomplete="username">

        <label for="password">Password<span class="required">*</span></label>
        <input type="password" id="password" name="password" required placeholder="Enter your password" autocomplete="current-password">
        <div class="toggle-password">
            <input type="checkbox" id="show-password" onclick="togglePasswordVisibility()">
            <label for="show-password">Show password</label>
        </div>
        <input type="submit" value="Login">
    </form>
    <script>
        function togglePasswordVisibility() {{
            var passwordField = document.getElementById("password");
            passwordField.type = passwordField.type === "password" ? "text" : "password";
        }}
    </script>
</body>
</html>
"""
