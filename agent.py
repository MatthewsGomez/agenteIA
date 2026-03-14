from strands import Agent
from strands_tools import calculator, current_time
from tools import buscar_servicio_aws, comparar_instancias_ec2, estimar_costo_lambda, recomendar_arquitectura

SYSTEM_PROMPT = """
Eres CloudArquitecto, un experto en Amazon Web Services.
Respondes de forma concisa y practica, siempre en espanol.
Cuando alguien te pregunta algo tecnico, das ejemplos concretos.

Tienes acceso a las siguientes capacidades:
- estimar_costo_lambda: calcula el costo mensual de una funcion Lambda
- recomendar_arquitectura: sugiere arquitecturas AWS segun el caso de uso
- buscar_servicio_aws: lista servicios AWS por categoria
- comparar_instancias_ec2: compara caracteristicas y precios de dos instancias EC2
- calculator: realiza calculos matematicos
- current_time: obtiene la fecha y hora actual
"""

agent = Agent(
    system_prompt=SYSTEM_PROMPT,
    tools=[estimar_costo_lambda, recomendar_arquitectura, buscar_servicio_aws, comparar_instancias_ec2, calculator, current_time],
)


if __name__ == "__main__":
    print("=== CloudArquitecto esta listo ===")
    print("Escribe 'salir' para terminar.\n")

    while True:
        user_input = input("Tu: ").strip()
        if not user_input:
            continue
        if user_input.lower() == "salir":
            print("Hasta luego!")
            break
        print()
        agent(user_input)
        print()
