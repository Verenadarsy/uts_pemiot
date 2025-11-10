from flask import Flask, request, jsonify, render_template
from config import get_db_connection

app = Flask(__name__, static_folder='static', template_folder='templates')

# Route utama (dashboard)
@app.route('/')
def index():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM data_sensor ORDER BY id DESC LIMIT 20")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return render_template('index.html', data=data)


# Route API untuk data ringkasan JSON
@app.route('/api/data')
def get_summary_data():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM data_sensor ORDER BY id DESC LIMIT 100")
    data = cur.fetchall()

    suhu_values = [row['suhu'] for row in data]
    suhumax = max(suhu_values)
    suhumin = min(suhu_values)
    suhurata = sum(suhu_values) / len(suhu_values)

    for row in data:
        if row.get("timestamp") is not None:
            row["timestamp"] = row["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

    cur.execute("""
        SELECT DATE_FORMAT(timestamp, '%m-%Y') AS month_year
        FROM data_sensor
        WHERE suhu = (SELECT MAX(suhu) FROM data_sensor)
    """)
    month_year_rows = cur.fetchall()

    month_year_list = [{"month_year": row["month_year"]} for row in month_year_rows]

    # format JSON final
    result = {
        "suhumax": suhumax,
        "suhumin": suhumin,
        "suhurata": round(suhurata, 2),
        "nilai_suhu_max_humid_max": data,
        "month_year_max": month_year_list
    }

    cur.close()
    conn.close()

    return jsonify(result)


# Route untuk menerima data dari ESP32 (POST)
@app.route('/api/sensor', methods=['POST'])
def receive_sensor_data():
    try:
        data = request.json
        suhu = data.get('suhu')
        humidity = data.get('humidity')
        lux = data.get('lux')

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO data_sensor (suhu, humidity, lux) VALUES (%s, %s, %s)",
            (suhu, humidity, lux)
        )
        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'status': 'success', 'message': 'Data tersimpan'}), 201

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


# Route untuk mengambil data sensor (GET)
@app.route('/api/sensor', methods=['GET'])
def get_sensor_data():
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)
    cur.execute("SELECT * FROM data_sensor ORDER BY id DESC LIMIT 10")
    data = cur.fetchall()

    # amankan timestamp saat return
    for row in data:
        if row.get("timestamp") is not None:
            row["timestamp"] = row["timestamp"].strftime("%Y-%m-%d %H:%M:%S")

    cur.close()
    conn.close()
    return jsonify(data)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
