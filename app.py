from flask import Flask, request, render_template
import game_data

app = Flask(__name__)

def clear_dlc(data):
	temp_data = data[:]
	new_data = []

	for row in temp_data:
		if row['dlc'] == False:
			stuff = row
			new_data.append(stuff)
	return new_data


@app.route('/', methods=['GET', 'POST'])
def home():
	error = None
	if request.method == 'POST':
		entry = request.form['game_name']
		dlc_checkbox = request.form.getlist('check')

		if not entry:
			error = 'Empty. Please try again.'
		else:
			data = game_data.get_data(entry)
			if not dlc_checkbox:
				data = clear_dlc(data)
				# data is now dlc free

			data.sort(key=lambda row: row['current_price'])

			if not data:
				data = [['No games of that name']]

			return render_template('home.html', entry=entry, data=data)

	return render_template('home.html', error=error)


if __name__ == '__main__':
	app.run(debug=True)
