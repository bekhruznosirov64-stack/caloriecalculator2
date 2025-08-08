from flask import Flask, render_template, request
import openai

app = Flask(__name__)

openai.api_key = "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"
openai.api_base = "ht tps://api.groq.com/openai/v1"

def calculate_calories(age, gender, height, weight, activity):
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    maintenance = round(bmr * activity)
    mild_loss = round(maintenance * 0.9)
    weight_loss = round(maintenance * 0.79)
    extreme_loss = max(round(maintenance * 0.59), 1425)
    mild_gain = round(maintenance * 1.1)
    weight_gain = round(maintenance * 1.21)
    fast_gain = round(maintenance * 1.41)

    return {
        "Maintain": maintenance,
        "Mild Loss": mild_loss,
        "Loss": weight_loss,
        "Extreme Loss": extreme_loss,
        "Mild Gain": mild_gain,
        "Gain": weight_gain,
        "Fast Gain": fast_gain
    }

def zigzag_schedule(base_calories):
    high = round(base_calories * 1.1)
    low = round(base_calories * 0.8)
    return {
        "Sunday": high,
        "Monday": low,
        "Tuesday": low,
        "Wednesday": high,
        "Thursday": low,
        "Friday": low,
        "Saturday": high
    }

def get_meal_tip_groq(goal, cal_target):
    prompt = f"Give a 1-day meal plan for someone targeting '{goal}' with {cal_target} calories per day."
    try:
        response = openai.ChatCompletion.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a helpful dietitian."},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Error: {e}"


@app.route('/', methods=['GET', 'POST'])
def index():
    result = {}
    schedules = {}
    meal_plans = {}
    if request.method == 'POST':
        age = int(request.form['age'])
        gender = request.form['gender']
        height = int(request.form['height'])
        weight = int(request.form['weight'])
        activity = float(request.form['activity'])

        result = calculate_calories(age, gender, height, weight, activity)

        for goal, cal in result.items():
            schedules[goal] = zigzag_schedule(cal)
            meal_plans[goal] = get_meal_tip_groq(goal, cal)

    return render_template("index.html", result=result, schedules=schedules, meals=meal_plans)

if __name__ == '__main__':
    app.run(debug=True)
