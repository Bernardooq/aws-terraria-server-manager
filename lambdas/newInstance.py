import boto3
import time
import json
from botocore.exceptions import ClientError

dynamodb = boto3.resource('dynamodb') #conexión con DYNAMO
tabla = dynamodb.Table('users_luisda') #conexión con la tabla de DYNAMO

def lambda_handler(event, context):
    # Manejo de CORS preflight
    if event['httpMethod'] == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {        # Estos headers nos sirven para permitir el acceso desde el navegador al API desde cualquier dominio y evitar problemas con los CORS
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            'body': json.dumps('CORS preflight OK')
        }

    # Obtener el cuerpo de la solicitud (ahora el cuerpo es un JSON)
    body = json.loads(event["body"])

    if 'User' not in body: #Manejo de error en la solicitud 
        return {
            'statusCode': 400,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            'body': json.dumps({'error': 'No se proporcionó un cuerpo en la solicitud'})
        }

    email = body["User"]["email"] #obtenemos el email
    password = body["User"]["password"] #obtenemos el password
    
    #Manejamos error de falta de parámetros
    if not email or not password:
        return {
            'statusCode': 400,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            'body': json.dumps({'error': 'Faltan datos requeridos'})
        }
    
    game = body["game"] #Obtenemos el juego que se va a levantar
    try:
        response = tabla.get_item(Key={'email': email})
        if 'Item' not in response or response['Item']['password'] != password: #Validamos contraseña
            return {
                'statusCode': 400,
                'headers': {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                'body': json.dumps({'error': 'El usuario no existe o la contraseña es incorrecta'})
            }

        #Dependiendo el juego se mapea con el ID de la imagen con el servidor ya instalado
        ami_map = {
            "terraria": "ami-02af08be27104ae31"     
        }

        #Si el juego no existe en nuestros servidores
        if game not in ami_map:
            return {
                'statusCode': 400,
                'headers': {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "*",
                    "Access-Control-Allow-Methods": "OPTIONS,POST"
                },
                'body': json.dumps({'error': f"Juego '{game}' no soportado"})
            }


        nombre_instancia = f"Servidor-{game}-{int(time.time())}" #Creamos el nombre del servidor
        ec2 = boto3.client('ec2') #Nos conectamos con EC2
        
        #Ejecutamos run_instances que crea las instancias
        response = ec2.run_instances(
            ImageId=ami_map[game], #Imagen
            InstanceType='t2.micro', #Tipo de instancia
            MinCount=1,
            MaxCount=1,
            KeyName='vockey', #LLave
            SecurityGroupIds=['sg-036644a87719e8cad'], 
            SubnetId='subnet-02b8b5064491aec02',
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Name', 'Value': nombre_instancia}]
            }]
        )

        #Obtenemos los parámetros de la instancia para mandarsela al usuario
        instance_id = response['Instances'][0]['InstanceId']
        ec2_resource = boto3.resource('ec2')
        instance = ec2_resource.Instance(instance_id)
        instance.wait_until_running()
        instance.load()
        ip = instance.public_ip_address
        
        # Actualizar la base de datos con la nueva instancia y asociar el juego
        tabla.update_item(
            Key={'email': email},
            UpdateExpression='SET Instances = list_append(Instances, :new_instance)',
            ExpressionAttributeValues={
                ':new_instance': [{
                    'instance_id': instance_id,
                    'game': game,  # Aquí guardamos el nombre del juego junto con la instancia
                    'public_ip': ip
                }]
            }
        )

        #Regresamos la informción vital para el usuario
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST",
                "Content-Type": "application/json"
            },
            "body": json.dumps({
                "game": game, #EL juego con el servidor
                "instance_id": instance_id, #El ID de la instancia
                "public_ip": ip #Su ip para poderse conectar
            })
        }

    #Manejamos exception de error con el cliente
    except ClientError as e:
        return {
            'statusCode': 500,
            'headers': {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,POST"
            },
            'body': json.dumps({'error': 'Error en la base de datos', 'details': str(e)})
        }
