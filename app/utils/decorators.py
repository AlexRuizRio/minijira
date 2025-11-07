from functools import wraps
from flask import session, redirect, url_for, flash

def role_required(*required_roles, redirect_to='project_bp.index'):
    """Decorador para restringir acceso a usuarios con ciertos roles."""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_roles = session.get('roles', [])
            if not any(r in user_roles for r in required_roles):
                flash('No tienes permiso para acceder a esta sección.', 'danger')
                return redirect(url_for(redirect_to))
            return f(*args, **kwargs)
        return decorated_function
    return decorator
