import boto3
import json
from botocore.exceptions import ClientError
import time

# Inicializar recurso DynamoDB
dynamodb = boto3.resource('dynamodb')
tabla = dynamodb.Table('users_luisda')

# Cabeceras CORS comunes
cors_headers = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'OPTIONS,POST'
}

def lambda_handler(event, context):
    start_time = time.time()  # Registrar el tiempo de inicio
    print("Evento recibido:", event)

    # Validar entrada
    if 'User' not in event:
        print("Falta el campo 'User'")
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({'error': 'No se proporcionó el campo "User" en la solicitud'})
        }

    email = event["User"].get("email") #Obtenemos email
    password = event["User"].get("password") #Obtenemos password

    #Validamos que si existan
    if not email or not password:
        print("Faltan email o password")
        return {
            'statusCode': 400,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Faltan datos requeridos: email o password'})
        }

    try:
        print(f"Consultando usuario con email: {email}")
        response = tabla.get_item(Key={'email': email}) #Obtenemos el email de la tabla
        print("Consulta a DynamoDB completada en", time.time() - start_time, "segundos")

        #Sino encuentra el email
        if 'Item' not in response:
            print("Usuario no encontrado")
            return {
                'statusCode': 404,
                'headers': cors_headers,
                'body': json.dumps({'error': 'El usuario no existe'})
            }

        user_data = response['Item'] #Si encuentra el email regresa sus datos
        print("Datos obtenidos del usuario:", user_data)

        if user_data.get('password') != password: #Ahora validamos si la contraseña es correcta
            print("Contraseña incorrecta")
            return {
                'statusCode': 401,
                'headers': cors_headers,
                'body': json.dumps({'error': 'Contraseña incorrecta'})
            }

        print("Autenticación exitosa") #Validamo el login
        return {
            'statusCode': 200,
            'headers': cors_headers,
            #Regresamos la información personal del usuario para las variables globales
            'body': json.dumps({
                'username': user_data.get('username'),
                'email': user_data.get('email'),
                'instances': user_data.get('Instances', []),
                'message': 'Usuario autenticado correctamente'
            })
        }

    #Manejamos excepciones de conexión
    
    except ClientError as e:
        print("Error al consultar DynamoDB:", str(e))
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Error en la base de datos', 'details': str(e)})
        }

    except Exception as e:
        print("Error inesperado:", str(e))
        return {
            'statusCode': 500,
            'headers': cors_headers,
            'body': json.dumps({'error': 'Error inesperado', 'details': str(e)})
        }
