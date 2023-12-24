from flask import Flask



app = Flask(__name__)

@app.route("/")
def hello_world():
    return "<h3>Hello, World!</h3>"

@app.route("/hi",methods=["GET","POST"])
def hi():
    return "hi hi"

@app.route("/hi",methods=["GET","POST"],endpoint="hi2") #endpoint没有定义的时候后定义本身的函数，特别指定就会只想指定的函数
def hi2():
    return "hi2 hi2"


@app.route("/count/<int:id>",methods=["GET"])  #int:id 表明id是int类型，也可以string、float、path
def count(id):
    return f"ID:{id}"

###############################BaseConverter######################
from werkzeug.routing import BaseConverter

class RegexConter(BaseConverter):
    '''自定义转化器'''
    def __init__(self,map,regex):
        super(RegexConter,self).__init__(map)
        self.regex = regex

#将自定义的转化器应用到flask应用中
app.url_map.converters["re"] = RegexConter

# 输入值的正则过滤
@app.route('/index/<re("\d{1,10}"):value>')
def index(value):
    return f"index value:{value}"

###############################返回渲染模板######################
from flask import  render_template,request,redirect,url_for

@app.route("/template",methods=["GET","POST"])
def template():
    if request.method == "GET":
        return render_template("index.html")

    elif request.method == "POST":
        print(11111,request.form)
        name = request.form.get("name")
        password = request.form.get("password")
        return f"<p>POST:{name} {password}</p>"

#重定向1
@app.route("/baidu")
def baidu():
    return redirect("https://www.baidu.com")

#重定向2
@app.route('/redi')
def redi():
    return redirect(url_for('template')) #url_for里的是函数名

###############################JSON######################

from flask import jsonify,abort

app.config["JSON_AS_ASCII"] = False #ensure_ascii=False

@app.route("/json")
def reponse_json():
    res = {"name":"张三","age":19}
    #方式1
    # response = make_response(json.dumps(res,ensure_ascii=False))  #ensure_ascii 不让中文转为ascii
    # response.mimetype = "application/json"
    # return response
    #方式2
    return jsonify(res)

@app.route("/nofuond")
def found():
    abort(404)
    return "Nofound"

#定义404错误 方法1
# @app.errorhandler(404)
# def err_404(err):
#     return "网页请求错误:%s" % err

#方法2
@app.errorhandler(404)
def handle_err_404(err):
    return render_template("404.html")

###############################Jinjia2######################

@app.route("/data")
def response_data():
    data = {
        "name":"张三",
        "age":19,
        "mylist":[1,2,3,"tom","lili","That's a cat"]
    }
    return render_template("introduce.html",data=data)

def list_sep(li):
    if type(li) == list:
        res = li[::2]
    else:
        res = li
    return res

#自定义过滤器，可给前端使用
app.add_template_filter(list_sep,"li2")

###############################表单Form校验######################

from flask_wtf import FlaskForm
from wtforms import StringField,PasswordField,SubmitField
from wtforms.validators import DataRequired,EqualTo

#CSRF
app.config["SECRET_KEY"] = "SOMEOFKEYSANYONE"

#定义表单类型
class Register(FlaskForm):
    user_name = StringField(label="用户名",validators=[DataRequired("用户名不能为空")])
    password = PasswordField(label="密码",validators=[DataRequired("密码不能为空")])
    remember = PasswordField(label="密码",validators=[DataRequired("密码不一致"),EqualTo("password")])
    submit = SubmitField(label="提交")

@app.route("/register",methods=["GET","POST"])
def register():
    form = Register()
    if request.method == "GET":
        return render_template("register.html",form=form)

    if request.method == "POST":
        user_name = form.user_name.data
        password = form.password.data
        remember = form.remember.data
        print(111111111, user_name, password, remember)
        # validate_on_submit 校验器
        if form.validate_on_submit():
            return render_template("register.html",form=form)
        return render_template("404.html")

###############################mysql数据库######################
from flask_sqlalchemy import SQLAlchemy

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:root@127.0.0.1:3306/flaskdb"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]= False   # 动态追踪修改,⼀般情况下设置False
app.config["SQLALCHEMY_ECHO"]= True   #显示生成的SQL语句，可用于调试

db = SQLAlchemy()

#创建数据库表
class Role(db.Model):
    '''角色表'''
    __tablename__ = 'role' #表名
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(128),unique=True)

class User(db.Model):
    '''用户表'''
    __tablename__ = 'user'
    id = db.Column(db.Integer,primary_key = True)
    name = db.Column(db.String(128),unique=True)
    password = db.Column(db.String(128))
    role_id = db.Column(db.Integer,db.ForeignKey('role.id'))
    def __repr__(self):
        return f'<User {self.name!r}>'


# 初始化数据库
with app.app_context() as ctx:
    ctx.push()   #需要保证上下管理器不为空，否则报RuntimeError: Working outside of application context.
    db.init_app(app)
    db.drop_all()
    db.create_all()


def  insert_db():
    role1 = Role(name="admin")
    role2 = Role(name="guest")
    db.session.add_all([role1,role2])
    db.session.commit()
    usr1 = User(name="zhangsan",password="a123456",role_id=role1.id)
    usr2 = User(name="tom",password="a123456",role_id=role2.id)
    usr3 = User(name=r"小明",password="a123456",role_id=role2.id)
    db.session.add_all([usr1,usr2,usr3])
    db.session.commit()
    print("All user: ",User.query.all())
    res = Role.query.filter(Role.name == "guest").first()
    print("Guest:",res)

@app.route("/db",methods=["GET","POST"])
def db_page():
    form = Register()
    if request.method == "GET":
        return render_template("db.html", form=form)
    if request.method == "POST":
        print(111111111, form.user_name.data,2222,form.password.data)
        print(33333,request.form.user_nmae,request.form.passwrod)
        usr = User(
            name=form.user_name.data,
            password=form.password.data,
            role_id = 2
                   )
        # validate_on_submit 校验器
        db.session.add(usr)
        db.session.commit()
        res = User.query.filter(User.role_id==2).all()
        print("All guest:", res)
        return render_template("db.html", form=form)
    return render_template("404.html")


if __name__ == "__main__":
    insert_db()
    app.run()