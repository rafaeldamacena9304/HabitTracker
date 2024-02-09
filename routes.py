from flask import Blueprint, render_template, request, url_for, redirect
import datetime
from pymongo import MongoClient
from flask import current_app
import uuid



pages = Blueprint("habits",__name__, template_folder="templates", static_folder="static")


def today_at_midnight():
    today = datetime.datetime.today()
    return datetime.datetime(today.year, today.month, today.day)





@pages.context_processor
def add_date_range():
    def date_range(start: datetime.datetime):
        dates = [start + datetime.timedelta(days=diff) for diff in range(-3, 4)]
        return dates
    return {"date_range": date_range}




@pages.route("/")
def index():
    date_str = request.args.get("date")
    if date_str:
        selected_date = datetime.datetime.fromisoformat(date_str)
    else:
        selected_date = today_at_midnight()

#a lista completions será cada habit digitado e encontrado na data atual.
#aqui estou fazendo a lista do banco de dados encontrar o habit escrito na data em questão
    habits_on_date = current_app.db.habits.find({"added": {"$lte": selected_date}})

    completions = [
    habit["habit"] for habit in current_app.db.completions.find({"date": selected_date}) 
]


    return render_template("index.html", habits=habits_on_date, title="Habit Tracker - Home", selected_date=selected_date, completions=completions)




@pages.route("/add", methods=["GET", "POST"])
def add_habit():
    today = today_at_midnight()
    #se o formulário for enviado pelo usuário, então serão inseridas as informações no banco de dados: 
    #um _id único será criado, a data atual, e o habit escrito pelo usuário.
    if request.form: 
        current_app.db.habits.insert_one(
            {"_id": uuid.uuid4().hex, "added": today, "name": request.form.get("habit")}
        )

    return render_template("add_habit.html", title="Habit Tracker - Add Habit", selected_date=today)




@pages.post("/complete")
def complete():
    date_string = request.form.get("date") #pegarei uma data em forma de string, já que converti pra aparecer isso no site
    date = datetime.datetime.fromisoformat(date_string) #irei transformar de novo a string em formato certo p mandar pro dicionario
    habit = request.form.get("habitId") #irei pegar elemento com name="habitCompleted"
    current_app.db.completions.insert_one({"date": date, "habit": habit}) #vou colocar o hábito no dicionario contendo a data, exemplo: {"date":habit}
    #estou associando a data com o habito.
    return redirect(url_for("habits.index", date=date_string)) #date string= selected date


