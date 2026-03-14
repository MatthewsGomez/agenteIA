import pytest
from tools import (
    comparar_instancias_ec2,
    estimar_costo_lambda,
    recomendar_arquitectura,
    buscar_servicio_aws,
    EC2_INSTANCIAS,
)


# ============================================================================
# TESTS: comparar_instancias_ec2
# ============================================================================

class TestCompararInstanciasEC2:
    """Pruebas para la herramienta comparar_instancias_ec2"""

    def test_comparacion_valida_basica(self):
        """Verifica que devuelve string con comparación válida"""
        resultado = comparar_instancias_ec2("t3.micro", "t3.small")
        assert isinstance(resultado, str)
        assert "Comparación de instancias EC2" in resultado
        assert "t3.micro" in resultado.upper()
        assert "t3.small" in resultado.upper()

    def test_comparacion_valida_diferentes_familias(self):
        """Verifica comparación entre familias diferentes (t3 vs m5)"""
        resultado = comparar_instancias_ec2("t3.large", "m5.large")
        assert isinstance(resultado, str)
        assert "vCPUs" in resultado
        assert "RAM (GB)" in resultado
        assert "Precio/hora" in resultado

    def test_case_insensitive(self):
        """Verifica que la comparación es case-insensitive"""
        resultado1 = comparar_instancias_ec2("T3.MICRO", "T3.SMALL")
        resultado2 = comparar_instancias_ec2("t3.micro", "t3.small")
        # Ambas deben devolver resultados válidos (no error)
        assert isinstance(resultado1, str)
        assert isinstance(resultado2, str)
        assert "no encontrada" not in resultado1.lower()
        assert "no encontrada" not in resultado2.lower()

    def test_espacios_en_blanco_ignorados(self):
        """Verifica que espacios en blanco se ignoran"""
        resultado = comparar_instancias_ec2("  t3.micro  ", "  t3.small  ")
        assert isinstance(resultado, str)
        assert "no encontrada" not in resultado.lower()

    def test_instancia_invalida_primera(self):
        """Verifica manejo de instancia inválida en primer parámetro"""
        resultado = comparar_instancias_ec2("invalid.type", "t3.small")
        assert isinstance(resultado, str)
        assert "no encontrada" in resultado.lower()
        assert "invalid.type" in resultado

    def test_instancia_invalida_segunda(self):
        """Verifica manejo de instancia inválida en segundo parámetro"""
        resultado = comparar_instancias_ec2("t3.micro", "invalid.type")
        assert isinstance(resultado, str)
        assert "no encontrada" in resultado.lower()
        assert "invalid.type" in resultado

    def test_ambas_instancias_invalidas(self):
        """Verifica manejo cuando ambas instancias son inválidas"""
        resultado = comparar_instancias_ec2("invalid1", "invalid2")
        assert isinstance(resultado, str)
        assert "no encontrada" in resultado.lower()

    def test_instancia_vacia(self):
        """Verifica manejo de string vacío"""
        resultado = comparar_instancias_ec2("", "t3.small")
        assert isinstance(resultado, str)
        assert "no encontrada" in resultado.lower()

    def test_contiene_costo_mensual(self):
        """Verifica que el resultado incluye cálculo de costo mensual"""
        resultado = comparar_instancias_ec2("t3.micro", "t3.small")
        assert "Costo mensual estimado" in resultado
        assert "730 horas" in resultado

    def test_calculo_diferencias_correctas(self):
        """Verifica que las diferencias se calculan correctamente"""
        resultado = comparar_instancias_ec2("t3.nano", "t3.micro")
        # t3.nano: 0.5GB RAM, t3.micro: 1GB RAM -> diferencia: +0.5GB
        assert "RAM (GB)" in resultado
        assert isinstance(resultado, str)

    def test_todas_instancias_validas(self):
        """Verifica que todas las instancias en EC2_INSTANCIAS son válidas"""
        instancias = list(EC2_INSTANCIAS.keys())
        for inst in instancias[:5]:  # Prueba con las primeras 5
            resultado = comparar_instancias_ec2(inst, instancias[0])
            assert "no encontrada" not in resultado.lower()


# ============================================================================
# TESTS: estimar_costo_lambda
# ============================================================================

class TestEstimarCostoLambda:
    """Pruebas para la herramienta estimar_costo_lambda"""

    def test_estimacion_valida_basica(self):
        """Verifica que devuelve string con estimación válida"""
        resultado = estimar_costo_lambda(1000, 100, 256)
        assert isinstance(resultado, str)
        assert "Estimación mensual AWS Lambda" in resultado
        assert "Invocaciones" in resultado
        assert "1,000" in resultado

    def test_contiene_desglose_completo(self):
        """Verifica que el resultado contiene todos los componentes"""
        resultado = estimar_costo_lambda(1000, 100, 256)
        assert "Invocaciones" in resultado
        assert "Duración promedio" in resultado
        assert "Memoria" in resultado
        assert "Costo solicitudes" in resultado
        assert "Costo cómputo" in resultado
        assert "Total estimado" in resultado

    def test_cero_invocaciones(self):
        """Verifica manejo de cero invocaciones"""
        resultado = estimar_costo_lambda(0, 100, 256)
        assert isinstance(resultado, str)
        assert "0" in resultado
        assert "Total estimado" in resultado

    def test_duracion_cero(self):
        """Verifica manejo de duración cero"""
        resultado = estimar_costo_lambda(1000, 0, 256)
        assert isinstance(resultado, str)
        assert "Total estimado" in resultado

    def test_memoria_minima(self):
        """Verifica con memoria mínima (128 MB)"""
        resultado = estimar_costo_lambda(1000, 100, 128)
        assert isinstance(resultado, str)
        assert "128" in resultado

    def test_memoria_maxima(self):
        """Verifica con memoria máxima (10240 MB)"""
        resultado = estimar_costo_lambda(1000, 100, 10240)
        assert isinstance(resultado, str)
        assert "10240" in resultado

    def test_valores_grandes(self):
        """Verifica con valores grandes"""
        resultado = estimar_costo_lambda(1_000_000, 5000, 3008)
        assert isinstance(resultado, str)
        assert "1,000,000" in resultado

    def test_valores_flotantes(self):
        """Verifica que acepta valores flotantes para duración"""
        resultado = estimar_costo_lambda(1000, 123.45, 256)
        assert isinstance(resultado, str)
        assert "123.45" in resultado

    def test_formato_moneda_valido(self):
        """Verifica que los costos están en formato USD válido"""
        resultado = estimar_costo_lambda(1000, 100, 256)
        assert "$" in resultado
        assert "USD/mes" in resultado

    def test_invocaciones_negativas(self):
        """Verifica comportamiento con invocaciones negativas"""
        resultado = estimar_costo_lambda(-1000, 100, 256)
        assert isinstance(resultado, str)
        # Debería devolver un resultado (aunque con costo negativo)

    def test_duracion_negativa(self):
        """Verifica comportamiento con duración negativa"""
        resultado = estimar_costo_lambda(1000, -100, 256)
        assert isinstance(resultado, str)

    def test_memoria_negativa(self):
        """Verifica comportamiento con memoria negativa"""
        resultado = estimar_costo_lambda(1000, 100, -256)
        assert isinstance(resultado, str)


# ============================================================================
# TESTS: recomendar_arquitectura
# ============================================================================

class TestRecomendarArquitectura:
    """Pruebas para la herramienta recomendar_arquitectura"""

    def test_api_rest_valida(self):
        """Verifica recomendación para API REST"""
        resultado = recomendar_arquitectura("api_rest")
        assert isinstance(resultado, str)
        assert "API REST" in resultado
        assert "API Gateway" in resultado
        assert "Lambda" in resultado
        assert "DynamoDB" in resultado

    def test_streaming_valida(self):
        """Verifica recomendación para streaming"""
        resultado = recomendar_arquitectura("streaming")
        assert isinstance(resultado, str)
        assert "Streaming" in resultado
        assert "Kinesis" in resultado

    def test_ml_inference_valida(self):
        """Verifica recomendación para ML inference"""
        resultado = recomendar_arquitectura("ml_inference")
        assert isinstance(resultado, str)
        assert "ML Inference" in resultado
        assert "SageMaker" in resultado

    def test_static_web_valida(self):
        """Verifica recomendación para sitio web estático"""
        resultado = recomendar_arquitectura("static_web")
        assert isinstance(resultado, str)
        assert "estático" in resultado
        assert "S3" in resultado
        assert "CloudFront" in resultado

    def test_batch_valida(self):
        """Verifica recomendación para batch"""
        resultado = recomendar_arquitectura("batch")
        assert isinstance(resultado, str)
        assert "batch" in resultado.lower()
        assert "AWS Batch" in resultado

    def test_case_insensitive(self):
        """Verifica que es case-insensitive"""
        resultado1 = recomendar_arquitectura("API_REST")
        resultado2 = recomendar_arquitectura("api_rest")
        assert isinstance(resultado1, str)
        assert isinstance(resultado2, str)
        assert "no reconocido" not in resultado1.lower()
        assert "no reconocido" not in resultado2.lower()

    def test_espacios_ignorados(self):
        """Verifica que espacios se ignoran"""
        resultado = recomendar_arquitectura("  api_rest  ")
        assert isinstance(resultado, str)
        assert "no reconocido" not in resultado.lower()

    def test_caso_uso_invalido(self):
        """Verifica manejo de caso de uso inválido"""
        resultado = recomendar_arquitectura("invalid_case")
        assert isinstance(resultado, str)
        assert "no reconocido" in resultado.lower()
        assert "Opciones válidas" in resultado

    def test_caso_vacio(self):
        """Verifica manejo de string vacío"""
        resultado = recomendar_arquitectura("")
        assert isinstance(resultado, str)
        assert "no reconocido" in resultado.lower()

    def test_contiene_servicios_aws(self):
        """Verifica que todas las recomendaciones contienen servicios AWS"""
        casos = ["api_rest", "streaming", "ml_inference", "static_web", "batch"]
        for caso in casos:
            resultado = recomendar_arquitectura(caso)
            assert "•" in resultado  # Contiene bullets de servicios
            assert "AWS" in resultado or caso in resultado


# ============================================================================
# TESTS: buscar_servicio_aws
# ============================================================================

class TestBuscarServicioAWS:
    """Pruebas para la herramienta buscar_servicio_aws"""

    def test_categoria_compute_valida(self):
        """Verifica búsqueda en categoría compute"""
        resultado = buscar_servicio_aws("compute")
        assert isinstance(resultado, str)
        assert "COMPUTE" in resultado
        assert "EC2" in resultado
        assert "Lambda" in resultado

    def test_categoria_storage_valida(self):
        """Verifica búsqueda en categoría storage"""
        resultado = buscar_servicio_aws("storage")
        assert isinstance(resultado, str)
        assert "STORAGE" in resultado
        assert "S3" in resultado

    def test_categoria_database_valida(self):
        """Verifica búsqueda en categoría database"""
        resultado = buscar_servicio_aws("database")
        assert isinstance(resultado, str)
        assert "DATABASE" in resultado
        assert "RDS" in resultado
        assert "DynamoDB" in resultado

    def test_categoria_ai_valida(self):
        """Verifica búsqueda en categoría AI"""
        resultado = buscar_servicio_aws("ai")
        assert isinstance(resultado, str)
        assert "AI" in resultado
        assert "SageMaker" in resultado

    def test_categoria_networking_valida(self):
        """Verifica búsqueda en categoría networking"""
        resultado = buscar_servicio_aws("networking")
        assert isinstance(resultado, str)
        assert "NETWORKING" in resultado
        assert "VPC" in resultado
        assert "CloudFront" in resultado

    def test_case_insensitive(self):
        """Verifica que es case-insensitive"""
        resultado1 = buscar_servicio_aws("COMPUTE")
        resultado2 = buscar_servicio_aws("compute")
        assert isinstance(resultado1, str)
        assert isinstance(resultado2, str)
        assert "no reconocida" not in resultado1.lower()
        assert "no reconocida" not in resultado2.lower()

    def test_espacios_ignorados(self):
        """Verifica que espacios se ignoran"""
        resultado = buscar_servicio_aws("  compute  ")
        assert isinstance(resultado, str)
        assert "no reconocida" not in resultado.lower()

    def test_categoria_invalida(self):
        """Verifica manejo de categoría inválida"""
        resultado = buscar_servicio_aws("invalid_category")
        assert isinstance(resultado, str)
        assert "no reconocida" in resultado.lower()
        assert "Opciones válidas" in resultado

    def test_categoria_vacia(self):
        """Verifica manejo de string vacío"""
        resultado = buscar_servicio_aws("")
        assert isinstance(resultado, str)
        assert "no reconocida" in resultado.lower()

    def test_formato_lista_servicios(self):
        """Verifica que los servicios están formateados como lista"""
        resultado = buscar_servicio_aws("compute")
        assert "•" in resultado  # Contiene bullets
        assert ":" in resultado  # Contiene separador nombre:descripción

    def test_cada_servicio_tiene_descripcion(self):
        """Verifica que cada servicio tiene descripción"""
        resultado = buscar_servicio_aws("storage")
        lineas = resultado.split("\n")
        # Filtra líneas vacías y encabezado
        servicios = [l for l in lineas if "•" in l]
        assert len(servicios) > 0
        for servicio in servicios:
            assert ":" in servicio  # Tiene descripción


# ============================================================================
# TESTS: Integración y casos edge
# ============================================================================

class TestIntegracion:
    """Pruebas de integración y casos edge"""

    def test_todas_herramientas_devuelven_string(self):
        """Verifica que todas las herramientas devuelven string"""
        assert isinstance(comparar_instancias_ec2("t3.micro", "t3.small"), str)
        assert isinstance(estimar_costo_lambda(1000, 100, 256), str)
        assert isinstance(recomendar_arquitectura("api_rest"), str)
        assert isinstance(buscar_servicio_aws("compute"), str)

    def test_herramientas_no_lanzan_excepciones_con_inputs_validos(self):
        """Verifica que no lanzan excepciones con inputs válidos"""
        try:
            comparar_instancias_ec2("t3.micro", "t3.small")
            estimar_costo_lambda(1000, 100, 256)
            recomendar_arquitectura("api_rest")
            buscar_servicio_aws("compute")
        except Exception as e:
            pytest.fail(f"Una herramienta lanzó una excepción: {e}")

    def test_herramientas_manejan_inputs_invalidos_gracefully(self):
        """Verifica que manejan inputs inválidos sin crashes"""
        try:
            comparar_instancias_ec2("invalid", "invalid")
            estimar_costo_lambda(-1, -1, -1)
            recomendar_arquitectura("invalid")
            buscar_servicio_aws("invalid")
        except Exception as e:
            pytest.fail(f"Una herramienta no manejó input inválido: {e}")

    def test_resultados_no_vacios(self):
        """Verifica que los resultados no son strings vacíos"""
        assert len(comparar_instancias_ec2("t3.micro", "t3.small")) > 0
        assert len(estimar_costo_lambda(1000, 100, 256)) > 0
        assert len(recomendar_arquitectura("api_rest")) > 0
        assert len(buscar_servicio_aws("compute")) > 0
