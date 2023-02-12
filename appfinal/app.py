import warnings
warnings.filterwarnings('ignore', category=FutureWarning)
from flask import abort, render_template, Flask
import logging
import db

APP = Flask(__name__)

# Start page
@APP.route('/')
def index():
    stats = {}
    x = db.execute('SELECT COUNT(*) AS Cars FROM cars').fetchone()
    stats.update(x)
    x = db.execute('SELECT COUNT(*) AS Makes FROM makes').fetchone()
    stats.update(x)
    x = db.execute('SELECT COUNT(*) AS Grupos FROM grupos').fetchone()
    stats.update(x)
    logging.info(stats)
    return render_template('index.html',stats=stats)

@APP.route('/cars/')
def list_cars():
    cars = db.execute(
      '''
      SELECT CarCode, Model, Generation, YearFrom, YearTo, Trim, MotorType, Cylinders, EngineType
      FROM cars
      ORDER BY CarCode
      ''').fetchall()
    return render_template('car-list.html', cars=cars)

@APP.route('/cars/<int:code>/')
def get_car(code):
    car = db.execute(
      '''
      SELECT CarCode, Model, Generation, YearFrom, YearTo, Trim, MotorType, Cylinders, EngineType
      FROM cars
      WHERE CarCode = %s
      ''', code).fetchone()

    if car is None:
          abort(404, 'Car Code {} does not exist.'.format(code))

    makes = db.execute(
       '''
       SELECT Make_Id, Make
       FROM cars NATURAL JOIN makes
       WHERE CarCode = %s
       ''', code).fetchone()

    bodytypes = db.execute(
      '''
      SELECT Code, Name
      FROM cars JOIN bodytype ON(cars.BodyType=bodytype.Code)
      WHERE CarCode = %s
      ''', code).fetchone()

    return render_template('car.html', car=car, makes=makes, bodytypes=bodytypes)

@APP.route('/cars/search/<expr>/')
def search_car(expr):
  search = { 'expr': expr }
  expr = '%' + expr + '%'
  cars = db.execute(
      '''
      SELECT CarCode, Make_Id, Model, Trim, Generation
      FROM cars
      WHERE Model LIKE %s
      ''', expr).fetchall()

  return render_template('car-search.html',search=search,cars=cars,)



#Makes
@APP.route('/makes/')
def list_makes():
    makes = db.execute('''
      SELECT Make_Id, Make, Found_Year, OgCountry
      FROM makes
      ORDER BY Make_Id
    ''').fetchall()
    return render_template('make-list.html', makes=makes)

@APP.route('/makes/<int:id>/')
def get_make(id):   #em vez de view_movies_by_actor
  make = db.execute(
    '''
    SELECT Make_Id, Make, Found_Year, CON.Country
    FROM MAKES JOIN CON ON MAKES.OgCountry=CON.Country_Id
    WHERE Make_Id = %s
    ''', id).fetchone()   #id??

  if make is None:
      abort(404, 'Make id {} does not exist.'.format(id))

  groups = db.execute(
    '''
    SELECT Group_Id, GroupName
    FROM makes JOIN grupos ON (makes.Subsidiary=grupos.Group_Id)
    WHERE Make_Id = %s
    ''', id).fetchone()

  BrandBodyTypes=db.execute(
    '''
    SELECT BodyType, Name
    FROM BTMAKES JOIN BODYTYPE ON (BTMAKES.BodyType=BODYTYPE.Code)
    WHERE Make_Id = %s
    ''', id).fetchall()

  return render_template('make.html',
           make=make, groups=groups, BBT=BrandBodyTypes )

@APP.route('/makes/search/<expr>/')
def search_make(expr):
  search = { 'expr': expr }
  # SQL INJECTION POSSIBLE! - avoid this!
  makes = db.execute(
      ' SELECT Make_Id, Make'
      ' FROM makes '
      ' WHERE Make LIKE \'%' + expr + '%\''
    ).fetchall()

  return render_template('make-search.html',
           search=search,makes=makes)

# Grupos
@APP.route('/groups/')
def list_groups():
    groups = db.execute('''
      SELECT Group_Id, GroupName, Found_Year
      FROM grupos
      ORDER BY Group_Id
    ''').fetchall()
    return render_template('group-list.html', groups=groups)

@APP.route('/groups/<int:id>/')
def get_group(id):
  group = db.execute(
    '''
    SELECT Group_Id, GroupName,Found_Year
    FROM grupos 
    WHERE Group_Id = %s
    ''', id).fetchone()

  if group is None:
     abort(404, 'Group id {} does not exist.'.format(id))

  makes = db.execute(
    '''
    SELECT Make, Make_Id
    FROM makes
    WHERE Subsidiary = %s
    ORDER BY Make
    ''', id).fetchall()

  lider=db.execute(
    '''
    SELECT Make_Id,Make
    FROM LEADER NATURAL JOIN MAKES
    WHERE Group_Id = %s
    ''', id).fetchall()

  coun=db.execute(
    '''
    SELECT CON.Country
    FROM COUNTRIES JOIN CON ON (COUNTRIES.Country=CON.Country_Id)
    WHERE Group_Id = %s
    ''', id).fetchall()


  return render_template('group.html',group=group, makes=makes, lider=lider, country=coun)


# Bodytypes
@APP.route('/bodytypes')
def list_bodytype():
  bodytype = db.execute(
      '''
      SELECT Code, Name
      FROM bodytype
      ORDER BY CODE
      ''').fetchall()

  return render_template('bodytype-list.html', bodytypes=bodytype)


@APP.route('/bodytypes/<int:id>/')
def get_bodytype(id):
  bodytype = db.execute(
      '''
      SELECT Code, Name
      FROM bodytype
      WHERE Code = %s
      ''', id).fetchone()

  if bodytype is None:
     abort(404, 'Bodytype id {} does not exist.'.format(id))

  return render_template('bodytype.html', bodytype=bodytype)


