from flask import Flask, jsonify, request
import pandas as pd
import os
import mysql.connector

app = Flask(__name__)
# dir = "/data/flask-api/data/extratoNov.xlsx"
# file = "extratoNov.xlsx"
# Database config with env. variables
db_config = {
    "host": os.getenv("DB_HOST", "db"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "SenhaSQL#3"),
    "database": os.getenv("DB_NAME", "finance_db")
}

def get_db_connection():
    return mysql.connector.connect(**db_config)

# Load statement
def load_statement(file_path):
    df = pd.read_excel(file_path)
    df['Data'] = pd.to_datetime(df['Data'], format='%d/%m/%Y', errors='coerce')  # Convert to datetime
    df.dropna(subset=['Data'], inplace=True)  # Remove lines with empty Date
    return df

@app.route('/statement', methods=['GET'])
def get_statement():
    df = load_statement("/data/flask-api/data/extratoNov.xlsx")
    return jsonify(df.to_dict(orient="records"))

@app.route('/save-statement/<int:user_id>', methods=['POST'])
def save_statement(user_id):
    data = load_statement("/data/flask-api/data/extratoNov.xlsx")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        for _, row in data.iterrows():
            cursor.execute(
                "INSERT INTO transactions (user_id, description, amount, date, category) VALUES (%s, %s, %s, %s, %s)",
                (user_id, row["Descrição"], row["Valor (R$)"], row["Data"], row.get("Categoria"))
            )
    except mysql.connector.errors.IntegrityError:
        # Ignora duplicatas por causa da restrição UNIQUE
        pass

    conn.commit()
    cursor.close()
    conn.close()
    
    return jsonify({"message": "Extrato salvo com sucesso!"}), 201

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0")