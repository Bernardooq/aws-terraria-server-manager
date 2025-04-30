import boto3
import json
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb')
tabla = dynamodb.Table('users_luisda')

def lambda_handler(event, context):
    if 'User' not in event:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'No se proporcionó un cuerpo en la solicitud'})
        }

    user = event['User']
    email = user.get('email')
    password = user.get('password')
    username = user.get('username')

    if not email or not password or not username:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Faltan datos requeridos'})
        }

    try:
        # Verificar si ya existe
        response = tabla.get_item(Key={'email': email})
        if 'Item' in response:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': 'El usuario ya existe'})
            }

        # Insertar nuevo usuario
        tabla.put_item(Item={
            'email': email,
            'password': password,
            'username': username,
            'Instances': []
        })

        return {
            'statusCode': 201,
            'body': json.dumps({'message': 'Usuario creado con exito'})
        }

    except ClientError as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'Error en la base de datos', 'details': str(e)})
        }
