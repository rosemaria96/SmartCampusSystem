import os
import re

# List of files to process
files_to_fix = [
    r"frontend\templates\admin\admin_academic.html",
    r"frontend\templates\admin\admin_attendance.html",
    r"frontend\templates\admin\admin_dashboard.html",
    r"frontend\templates\admin\admin_fee_payment.html",
    r"frontend\templates\admin\admin_noti.html",
    r"frontend\templates\admin\admin_qn_bank.html",
    r"frontend\templates\admin\admin_timetable.html",
    r"frontend\templates\admin\admin_user_management.html",
    r"frontend\templates\dashboard\dashboard.html",
    r"frontend\templates\student\student_academics.html",
    r"frontend\templates\student\student_attendance.html",
    r"frontend\templates\student\student_dashboard.html",
    r"frontend\templates\student\student_fee_payment.html",
    r"frontend\templates\student\student_notifications.html",
    r"frontend\templates\student\student_question_bank.html",
    r"frontend\templates\student\student_timetable.html",
    r"frontend\templates\teacher\teacher_academics.html",
]

base_dir = r"d:\Projects\campus backup\Smart Campus System-zip 2\Smart Campus System"

def fix_file(rel_path):
    file_path = os.path.join(base_dir, rel_path)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find: onclick="window.location.href='{% url 'something' %}'" (with or without semicolon, maybe spaces)
    # capturing the url name.
    # We want to change {% url 'name' %} to {% url "name" %} AND ensure semicolon at end of JS statement.
    
    # Pattern 1: Match single quotes in Django tag inside single quoted JS string inside double quoted HTML attr
    # Look for: onclick="...'{% url '...' %}'..."
    
    pattern = re.compile(r"""(onclick\s*=\s*['"]window\.location\.href\s*=\s*')\{\%\s*url\s*'([^']+)'\s*\%\}(['"](?:;?))""")
    
    # Logic:
    # Group 1: onclick="window.location.href='
    # Group 2: The url name (e.g. login)
    # Group 3: The closing quote of JS string and optional semicolon. 
    # Note: HTML attr closing quote is outside this match usually, but we need to be careful.
    
    # Actually, let's look at the specific structure we have:
    # onclick="window.location.href='{% url 'name' %}'"
    # onclick="window.location.href='{% url 'name' %}';"
    
    # Replacement: Group 1 + {% url "Group 2" %} + ' ; (ensure semicolon) + (keep HTML quote if captured? No, regex above has issues)
    
    # Better Pattern:
    # Match the specific phrase: {% url 'name' %}
    # BUT only when inside a line that has onclick="...
    # Since we can't easily do lookbehind for variable length, let's iterate lines.
    
    new_lines = []
    modified = False
    
    lines = content.splitlines(keepends=True)
    for line in lines:
        if 'onclick="window.location.href=' in line and '{% url' in line:
            # Check if it has single quotes in url tag
            # Example: ...href='{% url 'login' %}...
            
            # Replace 'name' with "name" inside the url tag
            # And ensure semicolon before the closing '
            
            # Simple replacement of quotes first
            # We want regex matches for {% url '...' %}
            def replace_url_tag(match):
                url_name = match.group(1)
                return f'{{% url "{url_name}" %}}'
            
            new_line = re.sub(r"\{\%\s*url\s*'([^']+)'\s*\%\}", replace_url_tag, line)
            
            # Now ensure semicolon.
            # Look for: %}'" or %}' " or %}'<
            # We want: %}';"
            
            if "%}'" in new_line and "%}';" not in new_line:
                 new_line = new_line.replace("%}'", "%}';")
            
            if new_line != line:
                line = new_line
                modified = True
        
        new_lines.append(line)

    if modified:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
        print(f"Fixed: {rel_path}")
    else:
        print(f"No changes matched/needed: {rel_path}")

for f_path in files_to_fix:
    fix_file(f_path)
