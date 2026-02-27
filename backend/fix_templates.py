import os

# Paths
base_dir = r"c:\Users\Hp\Desktop\SmartCampusSystem-main\Frontend\templates\admin"
timetable_creation_path = os.path.join(base_dir, "timetable_creation.html")
academic_form_path = os.path.join(base_dir, "forms", "academic_form.html")

# Content for timetable_creation.html
timetable_content = """{% extends 'base.html' %}
{% load static %}

{% block title %}Create Timetable | Admin Portal{% endblock %}
{% block portal_name %}Admin Portal{% endblock %}

{% block sidebar %}
{% include 'partials/sidebar_admin.html' %}
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-12">
        <div class="content-card">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h4 class="fw-bold mb-0">Create Timetable Grid</h4>
                <a href="{% url 'manage_timetable' %}" class="btn btn-outline-secondary btn-sm">
                    <i class="bi bi-arrow-left me-2"></i>Back
                </a>
            </div>

            <form method="GET" class="mb-4 row g-3">
                <div class="col-md-4">
                    <label class="form-label">Course</label>
                    <select name="course" class="form-select" onchange="this.form.submit()">
                        <option value="">Select Course</option>
                        {% for c in courses %}
                        <option value="{{ c.id }}" {% if selected_course_id == c.id %}selected{% endif %}>{{ c.course_name }}</option>
                        {% endfor %}
                    </select>
                </div>
                <div class="col-md-4">
                    <label class="form-label">Semester</label>
                    <select name="semester" class="form-select" onchange="this.form.submit()">
                        <option value="">Select Semester</option>
                        {% for s in semesters %}
                        <option value="{{ s.id }}" {% if selected_semester_id == s.id %}selected{% endif %}>Semester {{ s.semester_number }}</option>
                        {% endfor %}
                    </select>
                </div>
            </form>

            {% if selected_semester_id %}
            <form method="POST">
                {% csrf_token %}
                <input type="hidden" name="semester_id" value="{{ selected_semester_id }}">
                <div class="table-responsive">
                    <table class="table table-bordered text-center align-middle">
                        <thead class="table-light">
                            <tr>
                                <th style="width: 10%;">Day</th>
                                <th>9:00 - 10:00</th>
                                <th>10:00 - 10:30</th>
                                <th style="width: 50px;" class="bg-secondary text-white small vertical-text">Break</th>
                                <th>11:00 - 12:00</th>
                                <th>12:00 - 1:00</th>
                                <th style="width: 50px;" class="bg-secondary text-white small vertical-text">Lunch</th>
                                <th>2:00 - 3:00</th>
                                <th>3:00 - 4:00</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for day in days %}
                            <tr>
                                <td class="fw-bold">{{ day }}</td>
                                {% for slot in slots %}
                                {% if slot.is_break %}
                                <td class="bg-secondary"></td>
                                {% else %}
                                <td class="p-1">
                                    <div class="d-flex flex-column gap-1">
                                        <select name="subject_{{ day }}_{{ slot.start }}"
                                            class="form-select form-select-sm" required>
                                            <option value="NULL">-- Null --</option>
                                            {% for sub in subjects %}
                                            <option value="{{ sub.id }}">{{ sub.subject_code }}</option>
                                            {% endfor %}
                                        </select>
                                        <select name="teacher_{{ day }}_{{ slot.start }}"
                                            class="form-select form-select-sm">
                                            <option value="">-- Teacher --</option>
                                            {% for t in teachers %}
                                            <option value="{{ t.id }}">{{ t.name }}</option>
                                            {% endfor %}
                                        </select>
                                    </div>
                                </td>
                                {% endif %}
                                {% endfor %}
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>

                <div class="d-grid gap-2 mt-4">
                    <button type="submit" class="btn btn-black"
                        onclick="return confirm('This will overwrite existing timetable entries for this semester. Continue?')">Save
                        Timetable</button>
                </div>
            </form>
            {% else %}
            <div class="alert alert-info">Please select a Course and Semester to create the timetable.</div>
            {% endif %}
        </div>
    </div>
</div>

<style>
    .vertical-text {
        writing-mode: vertical-lr;
        text-orientation: mixed;
        padding: 5px !important;
    }
</style>
{% endblock %}
"""

# Content for academic_form.html
academic_form_content = """{% extends 'base.html' %}
{% load static %}

{% block title %}{{ title }} | Admin Portal{% endblock %}
{% block portal_name %}Admin Portal{% endblock %}

{% block sidebar %}
{% include 'partials/sidebar_admin.html' %}
{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="content-card">
            <div class="d-flex justify-content-between align-items-center mb-4">
                <h4 class="fw-bold mb-0">{{ title }}</h4>
                <a href="{% url 'manage_academics' %}" class="btn btn-outline-secondary btn-sm">
                    <i class="bi bi-arrow-left me-2"></i>Back
                </a>
            </div>

            <form method="POST" class="needs-validation" novalidate>
                {% csrf_token %}

                {% for field in form %}
                <div class="mb-3">
                    <label for="{{ field.id_for_label }}" class="form-label text-muted small fw-bold">{{ field.label }}</label>
                    {{ field }}
                    {% if field.errors %}
                    <div class="text-danger small mt-1">
                        {{ field.errors|striptags }}
                    </div>
                    {% endif %}
                    {% if field.help_text %}
                    <div class="form-text">{{ field.help_text }}</div>
                    {% endif %}
                </div>
                {% endfor %}

                <div class="d-grid gap-2 mt-4">
                    <button type="submit" class="btn btn-black">Save Changes</button>
                    <a href="{% url 'manage_academics' %}" class="btn btn-light border">Cancel</a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}

{% block scripts %}
<script>
    document.addEventListener('DOMContentLoaded', function () {
        const courseSelect = document.getElementById('id_course');
        const semesterSelect = document.getElementById('id_semester');

        if (courseSelect && semesterSelect) {
            courseSelect.addEventListener('change', function () {
                const courseId = this.value;
                semesterSelect.innerHTML = '<option value="">---------</option>';

                if (courseId) {
                    fetch(`/api/get-semesters/?course_id=${courseId}`)
                        .then(response => response.json())
                        .then(data => {
                            data.forEach(semester => {
                                const option = document.createElement('option');
                                option.value = semester.id;
                                option.textContent = `Semester ${semester.semester_number}`;
                                semesterSelect.appendChild(option);
                            });
                        })
                        .catch(error => console.error('Error fetching semesters:', error));
                }
            });
        }
    });
</script>
{% endblock %}
"""

# Write files
print(f"Writing to {timetable_creation_path}...")
with open(timetable_creation_path, "w", encoding='utf-8') as f:
    f.write(timetable_content)
print("Done.")

print(f"Writing to {academic_form_path}...")
with open(academic_form_path, "w", encoding='utf-8') as f:
    f.write(academic_form_content)
print("Done.")
