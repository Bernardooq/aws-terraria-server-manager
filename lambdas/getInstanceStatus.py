import boto3 
import json 
import time 
from datetime import datetime, timedelta 
from botocore.exceptions import ClientError 

# Clientes de AWS  
dynamodb = boto3.resource('dynamodb') #DYNAMO 
tabla = dynamodb.Table('users_luisda') #Tabla de dynamo 
ec2 = boto3.client('ec2') #EC2 
cloudwatch = boto3.client('cloudwatch') #nos conectamos a CLOUD WATCH para métricas 


# Función para obtener promedio de CPU 
def get_metric_average(metric_name, namespace, dimensions): 
    end_time = datetime.utcnow() 
    start_time = end_time - timedelta(hours=12) #Especificamos un tiempo (ultimas 12 horas) 

    #Llamamos a CloudWatch para que nos regrese las metricas deseadas 
    response = cloudwatch.get_metric_statistics( 
        Namespace=namespace, 
        MetricName=metric_name, 
        Dimensions=dimensions, 
        StartTime=start_time, 
        EndTime=end_time, 
        Period=300, 
        Statistics=['Average'] 
    ) 

    #filtramos los puros datos de la respuesta 
    datapoints = response.get('Datapoints', []) 
    if not datapoints: 
        return None 
    #Retornamos los datos 
    return round(sorted(datapoints, key=lambda x: x['Timestamp'], reverse=True)[0]['Average'], 2) 

 
def lambda_handler(event, context): 

    try: 
        body = json.loads(event['body'])  
        user = body.get('User') #Obtenemos el usuario 

        #Si no estamos logeados 
        if not user: 
            return { 
                "statusCode": 400, 
                "body": json.dumps({"error": "No se proporcionó un usuario válido"}), 
                "headers": { 
                    "Access-Control-Allow-Origin": "*", 
                    "Access-Control-Allow-Headers": "Content-Type", 
                    "Access-Control-Allow-Methods": "OPTIONS,POST" 
                } 
            } 

        email = user.get("email") #Obtenemos el email 
        password = user.get("password") #Obtenemos password 

        #Validamos la existencia del email y password 
        if not email or not password: 

            return { 
                'statusCode': 400, 
                'body': json.dumps({'error': 'Faltan datos requeridos'}), 
                'headers': { 
                    "Access-Control-Allow-Origin": "*", 
                    "Access-Control-Allow-Headers": "Content-Type", 
                    "Access-Control-Allow-Methods": "OPTIONS,POST" 
                } 
            } 

        response = tabla.get_item(Key={'email': email}) #Obtenemos si el usuario si esta en la tabla 
        if 'Item' not in response or response['Item']['password'] != password: #Validamos si la contraseña es correcta y el usuario existe 
            return { 
                'statusCode': 400, 
                'body': json.dumps({'error': 'El usuario no existe o la contraseña es incorrecta'}), 
                'headers': { 
                    "Access-Control-Allow-Origin": "*", 
                    "Access-Control-Allow-Headers": "Content-Type", 
                    "Access-Control-Allow-Methods": "OPTIONS,POST" 
                } 
            } 

        # Obtenemos las instancias del usuario 
        isinstances = response['Item'].get('Instances', []) 
        if not isinstances: 
            return { 
                'statusCode': 400, 
                'body': json.dumps({'error': 'No hay instancias asociadas al usuario'}), 
                'headers': { 
                    "Access-Control-Allow-Origin": "*", 
                    "Access-Control-Allow-Headers": "Content-Type", 
                    "Access-Control-Allow-Methods": "OPTIONS,POST" 
                } 
            } 

        instance_ids = [inst['instance_id'] for inst in isinstances] #Obtenemos su id 
        response = ec2.describe_instances(InstanceIds=instance_ids)   

        instances_info = [] 
        for reservation in response['Reservations']: 
            for instance in reservation['Instances']: 
                instance_id = instance['InstanceId']  
                game_name = next((inst['game'] for inst in isinstances if inst['instance_id'] == instance_id), 'No Game') #Obtenemos el servidor 

                # Obtener rendimiento CPU 
                cpu_utilization = get_metric_average( 
                    metric_name='CPUUtilization', 
                    namespace='AWS/EC2', 
                    dimensions=[{'Name': 'InstanceId', 'Value': instance_id}] 
                ) 

                #Obtenemos la información completa de la instancia 
                info = { 
                    'InstanceId': instance_id, 
                    'game': game_name, 
                    'PublicIpAddress': instance.get('PublicIpAddress', 'No Public IP'), 
                    'State': instance['State']['Name'], 
                    'cpuUtilization': f"{cpu_utilization}%" if cpu_utilization is not None else 'No data' 
                } 
                instances_info.append(info) 
        #Si todo función regresamos 200 y la información de todas las instancias del usuario 

        return { 
            'statusCode': 200, 
            'headers': { 
                "Access-Control-Allow-Origin": "*", 
                "Access-Control-Allow-Headers": "Content-Type", 
                "Access-Control-Allow-Methods": "OPTIONS,POST" 
            }, 
            'body': json.dumps({'instances': instances_info}) 

        } 

    #Excepción de conexion con DYNAMO 
    except ClientError as e: 
        return { 
            'statusCode': 500, 
            'body': json.dumps({'error': 'Error en la base de datos', 'details': str(e)}), 
            'headers': { 
                "Access-Control-Allow-Origin": "*", 
                "Access-Control-Allow-Headers": "Content-Type", 
                "Access-Control-Allow-Methods": "OPTIONS,POST" 
            } 
        } 

    #Error de conexión 
    except Exception as e: 
        return { 
            "statusCode": 500, 
            "body": json.dumps({"error": str(e)}), 
            "headers": { 
                "Access-Control-Allow-Origin": "*", 
                "Access-Control-Allow-Headers": "Content-Type", 
                "Access-Control-Allow-Methods": "OPTIONS,POST" 
            } 
        } 

 