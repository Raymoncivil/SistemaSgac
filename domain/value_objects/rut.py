"""
domain/value_objects/rut.py — RUT chileno como Value Object.
Encapsula la lógica de validación del RUT chileno (módulo 11).
No depende de nada externo.
"""

import re
from ..exceptions import (
    InvalidRUTException,
    InvalidRUTFormatException,
    InvalidRUTDVException
)


class RUT:
    """
    Value Object: RUT chileno.
    
    Validación mediante algoritmo módulo 11:
    - Extrae dígitos del RUT (sin puntos ni guiones)
    - Calcula dígito verificador esperado
    - Compara con el dígito proporcionado
    
    Ejemplo válido: 12345678-9 → 123456789
    """
    
    @staticmethod
    def validate(rut_str: str) -> bool:
        """
        Valida un RUT chileno usando algoritmo módulo 11.
        
        Args:
            rut_str: RUT en formato "12345678-9" o "12345678-K" o "123456789"
        
        Returns:
            Boolean indicando si es válido
        
        Raises:
            InvalidRUTException si el RUT es inválido
        """
        # Limpiar formato: remover puntos, guión, espacios
        rut_clean = rut_str.replace(".", "").replace("-", "").replace(" ", "").upper()
        
        # Validar que tenga al menos 8 caracteres (7 dígitos + 1 DV)
        if len(rut_clean) < 8:
            raise InvalidRUTFormatException(f"RUT debe tener al menos 8 caracteres, recibido: {rut_str}")
        
        # Separar cuerpo (primeros 7-8 dígitos) y dígito verificador (último carácter)
        body = rut_clean[:-1]
        dv_provided = rut_clean[-1]
        
        # El cuerpo debe ser todos dígitos
        if not body.isdigit():
            raise InvalidRUTFormatException(f"RUT debe contener solo dígitos (excepto DV), recibido: {rut_str}")
        
        # Calcular dígito verificador esperado
        dv_expected = RUT._calculate_dv(body)
        
        # Comparar
        if dv_provided != dv_expected:
            raise InvalidRUTDVException(
                f"RUT inválido. Dígito verificador esperado: {dv_expected}, recibido: {dv_provided} en {rut_str}"
            )
        
        return True
    
    @staticmethod
    def _calculate_dv(body: str) -> str:
        """
        Calcula el dígito verificador usando módulo 11.
        
        Algoritmo:
        1. Pond erado descendente: [...6, 7, 2, 3, 4, 5, 6, 7]
        2. Multiplica cada dígito por su ponderación
        3. Suma todos los resultados
        4. Calcula: 11 - (suma % 11)
        5. Si resultado es 11 → DV = 0
        6. Si resultado es 10 → DV = K
        7. Sino → DV = el resultado
        """
        multipliers = [2, 3, 4, 5, 6, 7]
        suma = 0
        
        # Procesar de derecha a izquierda (reverso)
        for i, digit_char in enumerate(reversed(body)):
            digit = int(digit_char)
            multiplier = multipliers[i % 6]
            suma += digit * multiplier
        
        dv = 11 - (suma % 11)
        
        if dv == 11:
            return "0"
        elif dv == 10:
            return "K"
        else:
            return str(dv)
    
    @staticmethod
    def clean_format(rut_str: str) -> str:
        """
        Limpia y standardiza el formato del RUT.
        De "12.345.678-9" a "123456789"
        """
        rut_clean = rut_str.replace(".", "").replace("-", "").replace(" ", "").upper()
        return rut_clean
