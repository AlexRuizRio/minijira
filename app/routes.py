from flask import Blueprint, render_template, request, redirect, url_for
from app import db
from app.models.project_model import Project

project_bp = Blueprint('project_bp', __name__)

# Dashboard / lista de proyectos
@project_bp.route('/')
def index():
    proyectos = Project.query.all()
    return render_template('projects/index.html', proyectos=proyectos)