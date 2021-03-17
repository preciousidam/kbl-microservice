from flask import url_for, redirect, request, render_template, flash
from flask_admin import AdminIndexView, expose
from flask_admin.contrib.sqla import ModelView
from flask_login import current_user, LoginManager, logout_user, login_user
from werkzeug.security import generate_password_hash, check_password_hash
from .models.User import Role, User, Permissions, UserRole, ResetToken, Role
from .models.Properties import Property, Price
from .models.Report import Report
from .util.instances import db
from .models.CloudinaryFileField import CLoudinaryFileUploadField



def initializeLogin(app):
    login_manager = LoginManager()
    login_manager.init_app(app)

    # Create user loader function
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(user_id)

def initializeAdmin(admin):
    admin.add_view(UserAdminView(User, db.session, name="Users", url="users",menu_icon_value="fa-users",menu_icon_type="fas"))
    #admin.add_view(RoleAdminView(Role, db.session, category="Users", name="Roles", url="roles"))
    #admin.add_view(MyModelView(ResetToken, db.session, category="Users", name="Reset-tokens", url="reset-tokens"))
    admin.add_view(PropertyAdmin(Property, db.session, name="Properties",menu_icon_value="fa-building",menu_icon_type="fas", url="properties"))
    admin.add_view(ReportView(Report, db.session, name='Reports',menu_icon_value="fa-file-pdf",menu_icon_type="fas", url="reports"))


class MyModelView(ModelView):
    create_template = 'admin/create.html'
    form_excluded_columns = ('created_at', 'updated_at')
    def is_accessible(self):
        if current_user and current_user.is_authenticated:
            userRole = UserRole.query.filter_by(user_id=current_user.id).first().json()
            return current_user.is_authenticated and userRole.get('role') == 'admin'

        else:
            False

    def is_visible(self):
        return True

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('admin.login_view', next=request.url))

class MyAdminIndexView(AdminIndexView):
    @expose('/')
    def index(self):
        if not current_user.is_authenticated:
            return redirect(url_for('.login_view'))

        
        return super(MyAdminIndexView, self).index()

    @expose('/login/', methods=('GET', 'POST'))
    def login_view(self):
        next = request.args.get('next')
        if current_user.is_authenticated:
            return redirect(url_for('.index'))

        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')

            if not email:
                flash('Email not provided')
                return render_template('admin/login.html')
            if not password:
                flash('Password not provided')
                return render_template('admin/login.html')

            user = User.query.filter_by(email=email.lower()).first()

            if user is None:
                flash('User with this email does not exist')
                return render_template('admin/login.html')

            if user.checkPassword(password) is False:
                flash('Invalid password')
                return render_template('admin/login.html')
            
            login_user(user)
            flash('Logged In successful')
            return redirect(next or url_for('.index'))

        return render_template('admin/login.html')

    @expose('/logout/', methods=('GET', 'POST'))
    def logout_view(self):
        logout_user()
        return redirect(url_for('.index'))


class RoleAdminView(MyModelView):
    form_choices = {'permissions': [(Permissions.READ, "Read"), (Permissions.WRITE, 'Write')]}

class UserAdminView(MyModelView):
    
    #form_args ={'is_active': dict(description='Check instead of deleting user to deactivate user')}
    column_auto_select_related = True
    column_hide_backrefs = False
    column_exclude_list=('password', 'updated_at')
    inline_models = (UserRole,)
    column_labels = {'phone': 'Phone Number', 'is_active': 'Active'}
    column_sortable_list = ('name', 'email', 'username',)
    column_searchable_list = ('name', 'email','username',)
    column_default_sort = [('name',False), ('email',False)]
    column_editable_list = ('name', 'username', 'email',)
    can_delete = False
    form_columns = ('name', 'email', 'username', 'phone', 'password', 'is_active')
    form_widget_args = dict(
        name=dict(column_class='col-md-12'),
        email=dict(column_class='col-md-12'),
        username=dict(column_class='col-md-6'),
        password=dict(column_class='col-md-6'),
        is_active=dict(column_class='col-md-6'),
        roles=dict(column_class='col-md-12'),
    )
    
    def on_form_prefill(self, form, id):
        form.password.render_kw = {'readonly': True}

    def on_model_change(self, form, model, is_created):
        if is_created:
            model.password = generate_password_hash(model.password)

class PropertyAdmin(MyModelView):
    form_choices = {'area': [('ikoyi', 'Ikoyi'), ('vi', 'Victoria Island'), ('lekki', 'Lekki'), ('oniru', 'Oniru')],
                    'state': [('lagos', 'Lagos')],
                    'bedrooms': [(1,'1 Bedroom'), (2, '2 Bedroom'), (3, '3 Bedroom'), (4, '4 Bedroom'), (5, '5 Bedroom'), (6, '6 Bedroom'), (7, '7 Bedroom')],
                    'type': [('Flat','Flat'), ('pent house', 'Pent House'), ('terrace', 'Terrace'), ("duplex", 'Duplex'), ("maisonette", 'Maisonette')]
                    }
    
    column_auto_select_related = True
    inline_models = [(Price,dict(
        form_columns=['id', 'year', 'amount'],
        form_widget_args= {
            'year': {
                'column_class': 'col-md-6'
            },
            'amount': {
                'column_class': 'col-md-6'
            }
        }
    ))]
    column_labels = {'built': 'Year built', 'serv_charge': 'Service charge'}
    column_sortable_list = ('area', 'bedrooms', 'name', 'built',)
    column_searchable_list = ('name', 'area', 'address', 'type')
    column_exclude_list=('created_at', 'updated_at', 'units', 'serv_charge', 'sale_price', 'facilities', 'floors', 'land_size')
    column_default_sort = ('name',False)
    can_export = True
    column_editable_list = ('name', 'bedrooms', 'address', 'area', 'serv_charge', 'type', 'sale_price')
    form_columns  = ('name', 'address', 'area', 'state', 'bedrooms','type', 'units', 'built', 'floors', 'land_size', 'sale_price', 'serv_charge', 'facilities')
    form_widget_args = {
        'facilities': {
            'rows': 6,
            'column_class': 'col-md-12'
        },
        'name': {
            'column_class': 'col-md-12'
        },
        'type': {
            'column_class': 'col-md-3'
        },
        'address': {
            'column_class': 'col-md-6'
        },
        'area': {
            'column_class': 'col-md-3'
        },
        'state': {
            'column_class': 'col-md-3'
        },
        'units': {
            'column_class': 'col-md-3'
        },
        'built': {
            'column_class': 'col-md-3'
        },
        'bedrooms': {
            'column_class': 'col-md-3'
        },
        'land_size': {
            'column_class': 'col-md-3'
        },
        'floors': {
            'column_class': 'col-md-3'
        },
        'serv_charge': {
            'column_class': 'col-md-3'
        },
        'sale_price': {
            'column_class': 'col-md-3'
        },
        'rents': {
            'column_class': 'col-md-12'
        }
    }

class ReportView(MyModelView):

    form_overrides = dict(file= CLoudinaryFileUploadField)
    column_exclude_list= ('created_at', 'updated_at')
    form_args = dict(file=dict( 
        base_path='https://res.cloudinary.com/kblinsurance/raw/upload/v1608312210/',
        ))

    form_widget_args = dict(
        title=dict(column_class="col-md-12"),
        description=dict(column_class="col-md-12"),
        date=dict(column_class="col-md-6"),
        file=dict(column_class="col-md-6"),
    )