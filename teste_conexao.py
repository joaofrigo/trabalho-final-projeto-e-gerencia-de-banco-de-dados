import mysql.connector

try:
    conn = mysql.connector.connect(
        host='192.168.100.56',  
        user='host',            
        password='963852741',   
        database='escalas'
    )
    print("Conexão remota bem-sucedida!")
except mysql.connector.Error as err:
    print(f"Erro ao conectar: {err}")
finally:
    if 'conn' in locals() and conn.is_connected():
        conn.close()
