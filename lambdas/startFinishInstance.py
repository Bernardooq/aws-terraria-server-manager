import boto3
import json

#Conexión con EC2
ec2 = boto3.client('ec2')

def lambda_handler(event, context):
    try:
        body = json.loads(event["body"])

        #Si el parametro instance no esta en el JSON
        if 'Instance' not in body:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'No se proporcionó una instancia'})
            }

        instance_id = body["Instance"]["id"] #Obtenemos el id de la instancia
        status = body["Instance"]["status"] # Obtenemos su estatus al que se va a cambiar

        #Dependiendo de su estatus start o stop instance
        if status == "ON":
            ec2.start_instances(InstanceIds=[instance_id])
            message = f'Instancia {instance_id} encendida'
        elif status == "OFF":
            ec2.stop_instances(InstanceIds=[instance_id])
            message = f'Instancia {instance_id} apagada'
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({'error': 'Estado inválido. Usa ON u OFF'})
            }

        #Regresamos si prendimos o apagamos la instancia
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': '*'
            },
            'body': json.dumps({'message': message})
        }

    #Mala conexión
    except Exception as e:
        return {
            'statusCode': 500,
            'headers': {
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({'error': str(e)})
        }
